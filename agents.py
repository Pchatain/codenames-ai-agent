"""
A collection of agents to play the game
"""
import numpy as np
import anthropic

from game import Guesser, Spymaster
import constants

def get_anthropic_answer(client, system_prompt, message):
    response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1024,
            temperature=0.0,
            system=system_prompt,
            messages=[{"role": "user", "content": [{"type": "text", "text": message}]}]
        )
    response_str = response.content[0].text
    found_response = False
    tag_loc = response_str.find("<response>")
    response_returned = "No word found in response"
    if tag_loc != -1:
        found_response = True
        response_returned = response_str[tag_loc + 10: response_str.find("</response>")]
    return found_response, response_returned, response_str

class RandomGuesser(Guesser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_move(self, state):
        for word in state.words:
            if word not in state.guesses:
                return word, ""
        return constants.END_OF_TURN, ""

class RandomSpymaster(Spymaster):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_move(self, state):
        random_words = []
        for _ in range(25):
            random_words.append("".join(np.random.choice(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), 5)))
        for word in random_words:
            if word not in state.words:
                return word, ""
        assert False, "No valid clue givable. Something wrong."

class AISpymaster(Spymaster):
    def __init__(self, extra_prompt="", verbose=False, include_guesser_thoughts=False):
        super().__init__()
        self.system_prompt = """
        You are the spymaster in codeNames. Among the words that haven't been guessed (i.e. don't have a color next to them), think about which words can be related via a clue word. You can keep it simple and have the clue correspond to 1 word, or relate 2 words, or even 3 or 4 words. Give a final clue in this format: <response>Word,2</response>. The response should be the word and the number of words to guess with the tags around the answer.
        """
        self.client = anthropic.Anthropic()
        self.verbose = verbose
        self.system_prompt += extra_prompt
        self.include_guesser_thoughts = include_guesser_thoughts
    
    def get_rolled_back_info(self, state):
        msg = ""
        for result in state.rolled_back_results:
            clue_w, clue_n = result[0]
            guesses = result[1]
            guesser_thoughts = result[2]
            n_guesses_made = result[3][0]
            msg += f"When clue {clue_w} was given for {clue_n} words, the guesser made the following guesses: "
            n_good_guesses = 0
            for guess in guesses:
                msg += f"{guess} ({state.code[guess]}), "
                if state.code[guess] == state.curr_team:
                    n_good_guesses += 1
            if n_good_guesses == clue_n:
                msg += f"\n{clue_w} was perfect! All {clue_n} words were guessed."
            else:
                msg += f"\nA guess was wrong when clue {clue_w} was given for {clue_n} words."
        return msg

    def get_move(self, state):
        message = f"Board as the guesser sees it:\n{state.board}\n-------\nBoard with code: {state.board_with_code}\nYou on are on team {state.curr_team}"
        if self.include_guesser_thoughts and state.guesser_thoughts != []:
            message += f"\nGuesser's thoughts from this game have been: {state.guesser_thoughts}"
        if state.game_response != "":
            message += f"\n{state.game_response}"
        if hasattr(state, "rolled_back_results") and state.rolled_back_results:
            message += "\nWe simulated a version of yourself one or more times already. Here is the log of those previous simulated attempts:\n"
            message += self.get_rolled_back_info(state)
            message += "\nIf a simulation was good, you should give that clue again since last time it was just a simulation and this time is for real. Otherwise, consider revising either the clue word or the clue number and give a new clue."
        if self.verbose:
            print("🕵️ Message to spymaster:")
            print(message)
            print("🕵️-*- over.")
        assert isinstance(message, str)
        assert isinstance(self.system_prompt, str)
        success, response, thoughts = get_anthropic_answer(self.client, self.system_prompt, message)
        if self.verbose:
            print("🕵️ Response from spymaster:")
            print(response)
            print("🕵️-*- over.")
        return response.split(",")


class AIGuesser(Guesser):
    def __init__(self, extra_prompt=""):
        super().__init__()
        self.system_prompt = """
        You are the guesser in codeNames. Look at the board. Words with a color next to them have already been guessed, and can be ignored. Use the clue word to figure out which word is related. After thinking, write your guess as <response>Word</response>. The response should be the word with the tags around the answer. Do not include the tags around anything other than your answer.
        """
        self.client = anthropic.Anthropic()
        self.system_prompt += extra_prompt

    def get_move(self, state):
        message = f"Board:{state.board}\nYou were given the clue word: {state.clues[-1][0]} for {state.clues[-1][1]} words."
        if state.game_response != "":
            message += f"\n{state.game_response}"
        assert isinstance(message, str)
        assert isinstance(self.system_prompt, str)
        success, response, thoughts = get_anthropic_answer(self.client, self.system_prompt, message)
        return response, thoughts