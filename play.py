import game
import agents
import words
import csv
import argparse
import tkinter as tk
from tkinter import messagebox
from tqdm import tqdm


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rollout_attempts", type=int, default=2,
                       help="Number of simulated attempts to run before making the real move. "
                            "Higher values let the AI spymaster try out different moves before "
                            "committing to one.")
    args = parser.parse_args()
    play_against_ai(args.rollout_attempts)

def play_against_ai(rollout_attempts):
    SEED = 0
    guesser = agents.AIGuesser()
    spymaster = agents.AISpymaster()

    # Ask user whether to read from file or enter manually
    choice = input("Would you like to (1) use default board or (2) enter board manually? Enter 1 or 2: ")
    if choice == "1":
        # Read from board.csv
        with open("board.csv", encoding="utf-8") as f:
            reader = csv.reader(f)
            words_list_entered = next(reader)
            code_entered = next(reader)
    elif choice == "2":
        words_list_entered, code_entered = get_board_from_user()
        print("words_list_entered:")
        print(words_list_entered)
        print("code_entered:")
        print(code_entered)
        # Validate input
        if len(words_list_entered) != 25 or len(code_entered) != 25:
            raise ValueError("Must enter exactly 25 words and 25 code letters")
        if not all(c in ['b','r','y','n'] for c in code_entered):
            raise ValueError("Code letters must be b, r, y or n")
    else:
        raise ValueError("Invalid choice. Please enter 1 or 2.")

    # Ask user which team the AI should play as
    human_team = None
    while True:
        ai_team = input("Should AI play as RED or BLUE? Enter R/B: ").upper()
        if ai_team == 'R':
            ai_team = "RED"
            human_team = "BLUE"
            break
        elif ai_team == 'B':
            ai_team = "BLUE"
            human_team = "RED"
            break
        print("Invalid input. Please enter R or B.")

    code_colors = []
    for color in code_entered:
        if color == "b":
            code_colors.append("BLUE")
        elif color == "r":
            code_colors.append("RED")
        elif color == "y":
            code_colors.append("ASSASIN")
        else:
            code_colors.append("NEUTRAL")
    code = {word: color for word, color in zip(words_list_entered, code_colors)}
    a_game = game.Game(words=words_list_entered, code=code, seed=SEED)
    a_game.display(print_human_readable=True, show_code=True)
    _ = input("Above is the board. Each word is one of 4 colors: (Blue, Red, Yellow, Grey).\n"
              "Blue/Red are the words that the Blue/Red team is trying to guess.\n"
              "Neutral words are grey.\n"
              "Lastly, if a guesser guesses the yellow word, their team loses instantly.\n"
              "When guessing, if the guesser chooses a word that is not the same color as their "
              "team, or a neutral word, their turn ends.\nPress Enter to continue.")
    human_score, ai_score = 0, 0
    human_target, ai_target = code_colors.count(human_team), code_colors.count(ai_team)
    while True:
        get_input = input("Enter one of:\n"
                          "  a word from the board to make that guess from the human team\n"
                          f"  'c' to have the AI make its move. AI team is {ai_team}\n"
                          "  'q' to quit the game\n"
                          "Your choice: ")
        if get_input == "q":
            break
        elif get_input == "c":
            for _ in tqdm(range(rollout_attempts), desc=f"AI is considering {rollout_attempts} moves."):
                result = a_game.play_one_round(guesser, spymaster, rollback=True, override_curr_team=ai_team, verbose=False)
            result = a_game.play_one_round(guesser, spymaster, override_curr_team=ai_team, verbose=True)
            print(result)
        else:
            guess = get_input
            a_game.curr_team = human_team
            applied_guess, word_color = a_game.guess_word([guess, ""])
            if not applied_guess:
                continue
            print(word_color)
            if word_color == "ASSASIN":
                print("You lose because you guessed the assassin word!")
                break
            elif word_color == human_team:
                human_score += 1
            elif word_color == ai_team:
                ai_score += 1
        a_game.display(print_human_readable=True, show_code=False)
        if human_score == human_target:
            print(f"You win! You guessed all {human_target} words on the board.")
            break
        elif ai_score == ai_target:
            print(f"You lose! The AI guessed all {ai_target} words on the board.")
            break
            
    print(a_game.display(print_human_readable=True, show_code=True))
    print(a_game.display(print_human_readable=True, show_code=False))

def get_board_from_user():
    # Create GUI window for word and code input
    input_window = tk.Tk()
    input_window.title("Codenames Board Setup")
    
    # Create 5x5 grid for words
    word_entries = []
    tk.Label(input_window, text="Enter words:").grid(row=0, column=0, columnspan=5)
    for i in range(5):
        row = []
        for j in range(5):
            entry = tk.Entry(input_window, width=10)
            entry.grid(row=i+1, column=j, padx=2, pady=2)
            row.append(entry)
        word_entries.append(row)
        
    # Create 5x5 grid for codes    
    code_entries = []
    tk.Label(input_window, text="Enter codes (b=blue, r=red, y=assassin, n=neutral):").grid(row=6, column=0, columnspan=5)
    for i in range(5):
        row = []
        for j in range(5):
            entry = tk.Entry(input_window, width=2)
            entry.grid(row=i+7, column=j, padx=2, pady=2)
            row.append(entry)
        code_entries.append(row)
    
    words_list_entered = []
    code_entered = []
    def get_entries():
        for row in word_entries:
            for entry in row:
                words_list_entered.append(entry.get().strip())
        for row in code_entries:
            for entry in row:
                code_entered.append(entry.get().strip().lower())
        input_window.destroy()
        
    tk.Button(input_window, text="Submit", command=get_entries).grid(row=12, column=0, columnspan=5)
    input_window.mainloop()
    return words_list_entered, code_entered

if __name__ == "__main__":
    main()