import game
import words
import agents
import constants

SEED = 123

def test_display():
    word_list = words.main(25, seed=SEED)
    print(word_list)
    a_game = game.Game(word_list, seed=SEED)
    print(a_game.display(print_human_readable=True, show_code=True))

def test_play_one_round():
    guesser = agents.RandomGuesser()
    spymaster = agents.RandomSpymaster()
    word_list = words.main(25, seed=SEED)
    a_game = game.Game(word_list, seed=SEED)
    a_game.play_one_round(guesser, spymaster)

def test_play_deterministic():
    guesser = agents.RandomGuesser()
    spymaster = agents.RandomSpymaster()
    word_list = words.main(25, seed=SEED)
    a_game = game.Game(word_list, seed=SEED)
    winner = a_game.play(guesser, spymaster)
    print(f"winner: {winner}")

def test_play():
    guesser = agents.RandomGuesser()
    spymaster = agents.RandomSpymaster()
    word_list = words.main(25)
    a_game = game.Game(word_list)
    a_game.display(print_human_readable=True, show_code=False)
    a_game.display(print_human_readable=True, show_code=True)
    winner = a_game.play(guesser, spymaster)
    print(f"winner: {winner}")

def test_get_win_stats(n_games=100):
    word_list = words.main(25)
    win_stats = {"BLUE": 0, "RED": 0}
    for _ in range(n_games):
        guesser = agents.RandomGuesser()
        spymaster = agents.RandomSpymaster()
        a_game = game.Game(word_list)
        winner = a_game.play(guesser, spymaster)
        win_stats[winner] += 1
    print(f"win stats: {win_stats}")


def test_play_one_round_ai():
    guesser = agents.AIGuesser()
    spymaster = agents.AISpymaster()
    word_list = words.main(25, seed=SEED)
    a_game = game.Game(word_list, seed=SEED)
    result = a_game.play_one_round(guesser, spymaster)
    print(result)

def test_play_ai():
    guesser = agents.AIGuesser()
    spymaster = agents.AISpymaster()
    word_list = words.main(25, seed=SEED)
    a_game = game.Game(word_list, seed=SEED)
    result = a_game.play(guesser, spymaster, verbose=True, max_turns=20)
    print(result)

def test_rollout_ai():
    guesser = agents.AIGuesser()
    spymaster = agents.AISpymaster(verbose=True)
    word_list = words.main(25, seed=SEED)
    a_game = game.Game(word_list, seed=SEED)
    print("Playing round 1 and then rolling back")
    result = a_game.play_one_round(guesser, spymaster, rollback=True)
    print(a_game.display(print_human_readable=True, show_code=True))
    print(a_game.display(print_human_readable=True, show_code=False))
    print("playing round 2 and not back")
    result = a_game.play_one_round(guesser, spymaster, rollback=False)
    print("displaying board")
    print(a_game.display(print_human_readable=True, show_code=False))
    print(result)

def test_rollout_ai_against_basic_ai():
    guesser1 = agents.AIGuesser()
    spymaster1 = agents.AISpymaster()
    guesser2 = agents.AIGuesser()
    spymaster2 = agents.AISpymaster(verbose=False)
    word_list = words.main(25, seed=SEED)
    a_game = game.Game(word_list, seed=SEED)
    for i in range(10):
        print("Playing round 1 and then rolling back")
        _ = a_game.play_one_round(guesser1, spymaster1, rollback=True, override_curr_team="BLUE")
        _ = a_game.play_one_round(guesser1, spymaster1, rollback=True, override_curr_team="BLUE")

        print("playing round 2 and not back")
        n_blue_guesses, blue_result = a_game.play_one_round(guesser1, spymaster1, override_curr_team="BLUE")
        print(a_game.display(print_human_readable=True, show_code=False))
        n_red_guesses, red_result = a_game.play_one_round(guesser2, spymaster2, override_curr_team="RED")
        print(a_game.display(print_human_readable=True, show_code=False))
        print(f"{n_blue_guesses = }, {blue_result = }")
        print(f"{n_red_guesses = }, {red_result = }")
        curr_score = a_game.get_score()
        print(f"{curr_score = }")
        print(f"i: {i}")
        if curr_score["BLUE"] == constants.N_BLUE or curr_score["RED"] == constants.N_RED or blue_result == "LOSE" or red_result == "LOSE":
            break
        print("--*--*--*--*--*--*--*--*--")
    print(a_game.display(print_human_readable=True, show_code=False))
    print(a_game.get_score())

def test_prompts_ai_battle():
    # extra_prompt="Before responding, look at every single non-guessed word and explain why or why not the clue might apply."
    guesser1 = agents.AIGuesser()
    # extra_prompt="Before responding, list all the words on your team that have not been guessed yet which have (Unknown) in parentheses next to the word. Brainstorm 10 possible clues you could give. Then choose the best clue which isn't associated with any enemy, neutral, or assasin words.", verbose=False)
    spymaster1 = agents.AISpymaster()
    guesser2 = agents.AIGuesser()
    spymaster2 = agents.AISpymaster(verbose=False)
    word_list = words.main(25, seed=SEED)
    a_game = game.Game(word_list, seed=SEED)
    for i in range(10):
        n_blue_guesses, blue_result = a_game.play_one_round(guesser1, spymaster1, override_curr_team="BLUE")
        print(a_game.display(print_human_readable=True, show_code=False))
        n_red_guesses, red_result = a_game.play_one_round(guesser2, spymaster2, override_curr_team="RED")
        print(a_game.display(print_human_readable=True, show_code=False))
        print(f"{n_blue_guesses = }, {blue_result = }")
        print(f"{n_red_guesses = }, {red_result = }")
        curr_score = a_game.get_score()
        print(f"{curr_score = }")
        print(f"i: {i}")
        if curr_score["BLUE"] == constants.N_BLUE or curr_score["RED"] == constants.N_RED or blue_result == "LOSE" or red_result == "LOSE":
            break
        print("--*--*--*--*--*--*--*--*--")
    print(a_game.display(print_human_readable=True, show_code=False))
    print(a_game.get_score())

if __name__ == "__main__":
    # test_play_one_round()
    # test_play()
    # test_get_win_stats()
    # test_play_one_round_ai()
    # test_play_ai()
    # test_rollout_ai()
    # play_against_ai()
    test_rollout_ai_against_basic_ai()
    # test_prompts_ai_battle()
