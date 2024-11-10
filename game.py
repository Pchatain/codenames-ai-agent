"""
This is an implementation of code names
"""

from abc import ABC, abstractmethod
from typing import Tuple, List
import types
import tabulate
from colorama import Fore, Style
import random
import constants

MAX_TRIES = 5

class Guesser(ABC):
    @abstractmethod
    def get_move(self, state) -> Tuple[str, str]:
        """Returns guess and thoughts about that guess."""
        raise NotImplementedError()

class Spymaster(ABC):
    @abstractmethod
    def get_move(self, state) -> Tuple[str, int]:
        """Returns clue and number of words that clue is for."""
        raise NotImplementedError()

def generate_code(words):
    #TODO Have this work with board size of not just 25.
    assert len(words) == 25, "Haven't implemented code for board size other than 25 yet"
    n_blue = constants.N_BLUE
    n_red = constants.N_RED
    n_neutral = len(words) - n_blue - n_red - 1

    blue_words = words[:n_blue]
    red_words = words[n_blue:n_blue+n_red]
    neutral_words = words[n_blue+n_red:n_blue+n_red+n_neutral]
    assasin_word = words[n_blue+n_red+n_neutral]
    code = {}
    for word in blue_words:
        code[word] = "BLUE"
    for word in red_words:
        code[word] = "RED"
    for word in neutral_words:
        code[word] = "NEUTRAL"
    code[assasin_word] = "ASSASIN"
    return code

def get_color(key):
    """
    Given either BLUE, RED, ASSASIN (yellow), or NEUTRAL (black), return the color code
    """
    if key == "BLUE":
        return Fore.BLUE
    elif key == "RED":
        return Fore.RED
    elif key == "ASSASIN":
        return Fore.YELLOW
    elif key == "NEUTRAL":
        return Fore.BLACK
    else:
        return Fore.WHITE

class Game():
    def __init__(self, words, code=None, seed=None):
        self.curr_team = "BLUE"
        self.words = words
        if code is None:
            code = generate_code(words)
        self.code = code
        # scramble the order of the words
        if seed is not None:
            random.seed(seed)
        random.shuffle(self.words)
        self.game_response = ""

        # These are the state variables that control the current progress of the game.
        self.turns = 0
        self.guesses = [] # words
        self.guesser_thoughts = []
        self.clues = [] # tuples of (word, number)
        self.rolled_back_results = [] # tuple of (list of clues (word, number), list of guesses, list of guesser thoughts)
    
    def set_state(self, words, code):
        self.words = words
        self.code = code

    def get_guesser_state(self, print_human_readable=False):
        state = types.SimpleNamespace()
        state.curr_team = self.curr_team
        state.words = self.words
        state.board = self.display(print_human_readable=print_human_readable, show_code=False)
        state.guesses = self.guesses
        state.clues = self.clues
        state.game_response = self.game_response
        return state

    def get_spymaster_state(self, print_human_readable=False):
        state = types.SimpleNamespace()
        state.curr_team = self.curr_team
        state.words = self.words
        state.board = self.display(print_human_readable=print_human_readable, show_code=False)
        state.guesses = self.guesses
        state.clues = self.clues
        state.game_response = self.game_response

        state.code = self.code
        state.board_with_code = self.display(show_code=True)
        state.guesser_thoughts = self.guesser_thoughts
        state.rolled_back_results = self.rolled_back_results
        return state

    def guess_word(self, action: List[str]):
        """Returns: bool, response. True upon succesful guess, false on failed guess."""
        word, thoughts = action
        if self.curr_team == "BLUE":
            print(Fore.BLUE + f"Guessing {word}" + Style.RESET_ALL)
        else:
            print(Fore.RED + f"Guessing {word}" + Style.RESET_ALL)
        if word == constants.END_OF_TURN:
            return True, constants.END_OF_TURN
        if word not in self.code:
            return False, f"Word {word} not on the board. Pick a word on the board."
        if word in self.guesses:
            return False, f"Word {word} already guessed. Pick a word not already guessed."
        self.guesses.append(word)
        self.guesser_thoughts.append(thoughts)
        return True, self.code[word]

    def give_clue(self, action):
        """
        Stores the word along with the number of words that clue is for.
        """
        word, n = action
        if word in self.code:
            return False, f"Word {word} is already on the board. Pick a word not on the board."
        elif " " in word:
            return False, f"Word {word} contains a space. Pick a word without a space."
        elif "-" in word:
            return False, f"Word {word} contains a dash. Pick a word that isn't hyphonated"
        # TODO add more constraints here if we run into problems.
        if self.curr_team == "BLUE":
            print(Fore.BLUE + f"Giving clue {word},{n}" + Style.RESET_ALL)
        else:
            print(Fore.RED + f"Giving clue {word},{n}" + Style.RESET_ALL)
        self.clues.append((word, n))
        return True, f"{word},{n}"

    def display(self, print_human_readable=False, show_code=False):
        """
        If interactive mode, prints the board. 
        Args:
            show_code: bool, whether to reveal the code words as to the code master.
        Returns:
            ai readable formatted board state.
        """
        # Prepare the board data
        board_data = []
        ai_format = []
        for i in range(0, len(self.words), 5):  # stride words by 4
            row = []
            for word in self.words[i:i+5]:  # Get 4 words for the row
                if show_code or word in self.guesses:
                    if print_human_readable: row.append(get_color(self.code[word]) + word + Style.RESET_ALL)
                    ai_format.append(f"{word} ({self.code[word]})")
                else:
                    row.append(word)
                    ai_format.append(f"{word} (Unknown)")
            board_data.append(row)
        # Print the board using tabulate
        if print_human_readable: print(tabulate.tabulate(board_data, tablefmt="grid"))
        return ai_format
    
    def make_move(self, player, state_fn, move_fn):
        tries = 0
        made_move = False
        while tries < MAX_TRIES:
            move = player.get_move(state_fn())
            success, response = move_fn(move)
            if success:
                made_move = True
                break
            self.game_response += "\n" + response
            print(f"{tries = }, {response = }")
            tries += 1
        self.game_response = ""
        return made_move, response

    def play_one_round(self, guesser, spymaster, rollback=False, override_curr_team=None):
        """
        Args:
            guesser: obj, guesser agent
            spymaster: obj, spymaster agent
            rollback: bool, whether to rollback the game state to the previous round, so that the spymaster can see the guesser's thoughts.
            override_curr_team: str, if not None, the current team to play as.
        Returns:
            n_guesses_made: int, number of guesses made
            round_response: str, "LOSE", "handover", or constants.END_OF_TURN
        """
        if override_curr_team is not None:
            self.curr_team = override_curr_team
        clue_response = self.make_move(spymaster, self.get_spymaster_state, self.give_clue)
        print(clue_response)
        max_guesses = int(clue_response[1].split(",")[1])
        n_guesses_made = 0
        round_response = None
        while n_guesses_made < max_guesses:
            guess_response = self.make_move(guesser, self.get_guesser_state, self.guess_word)
            print(guess_response)
            if guess_response[1] == "ASSASIN":
                round_response = "LOSE"
                n_guesses_made += 1
            elif guess_response[1] == constants.END_OF_TURN:
                round_response = constants.END_OF_TURN
            elif guess_response[1] != self.curr_team:
                round_response = "handover"
                n_guesses_made += 1
            else:
                n_guesses_made += 1
                continue
            break
        if rollback:
            self.rolled_back_results.append((self.clues[-1], self.guesses[-n_guesses_made:], self.guesser_thoughts[-n_guesses_made:], (n_guesses_made, round_response)))
            self.guesses = self.guesses[:-n_guesses_made]
            self.guesser_thoughts = self.guesser_thoughts[:-n_guesses_made]
            self.clues = self.clues[:-1]
        else:
            # reset rolled back results after we play a round
            self.rolled_back_results = []
        return n_guesses_made, round_response

    def get_score(self):
        board_state = self.display()
        score = {"BLUE": 0, "RED": 0}
        score["BLUE"] = sum(1 for word in board_state if "BLUE" in word)
        score["RED"] = sum(1 for word in board_state if "RED" in word)
        return score

    def play(self, guesser, spymaster, verbose=False, max_turns=25):
        teams = ["BLUE", "RED"]
        curr_team = 0
        winner = None
        while self.turns < max_turns:
            self.curr_team = teams[curr_team]
            n_guesses_made, round_response = self.play_one_round(guesser, spymaster)
            print(f"round result: {n_guesses_made}, {round_response}")
            # get the real score by counting in board sate how many times blue or red are written
            real_score = self.get_score()
            if verbose:
                print(self.display(print_human_readable=True))
                print(f"{self.curr_team = }, {real_score = }")
            if round_response == "LOSE":
                winner = "BLUE" if self.curr_team == "RED" else "RED"
                break
            elif real_score["BLUE"] == 8:
                winner = "BLUE"
                break
            elif real_score["RED"] == 7:
                winner = "RED"
                break
            self.turns += 1
            curr_team = (curr_team + 1) % 2
        return winner