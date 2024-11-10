import game
import agents
import words
import csv
import argparse
import tkinter as tk
from tkinter import messagebox


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rollout_attempts", type=int, default=0,
                       help="Number of simulated attempts to run before making the real move. "
                            "Higher values let the AI spymaster try out different moves before "
                            "committing to one.")
    args = parser.parse_args()
    play_against_ai(args.rollout_attempts)

def play_against_ai(rollout_attempts=0):
    SEED = 0
    guesser = agents.AIGuesser()
    spymaster = agents.AISpymaster()

    # Ask user whether to read from file or enter manually
    choice = input("Would you like to (1) read from board.csv or (2) enter board manually? Enter 1 or 2: ")
    if choice == "1":
        # Read from board.csv
        with open("board.csv", encoding="utf-8") as f:
            reader = csv.reader(f)
            words_list_entered = next(reader)
            code_entered = next(reader)
    else:
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

    # Ask user which team the AI should play as
    while True:
        ai_team = input("Should AI play as RED or BLUE? Enter R/B: ").upper()
        if ai_team == 'R':
            ai_team = "RED"
            break
        elif ai_team == 'B':
            ai_team = "BLUE"
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
    print(words_list_entered)
    print(code)
    a_game = game.Game(words=words_list_entered, code=code, seed=SEED)
    a_game.display(print_human_readable=True, show_code=True)
    while True:
        get_input = input("Enter one of:\n"
                         "  'q' to quit the game\n"
                         f"  'c' to have the AI make its move. AI team is {ai_team}\n"
                         "  a word from the board to make that guess from the human team\n"
                         "Your choice: ")
        if get_input == "q":
            break
        elif get_input == "c":
            for _ in range(rollout_attempts):
                result = a_game.play_one_round(guesser, spymaster, rollback=True, override_curr_team=ai_team)
            result = a_game.play_one_round(guesser, spymaster, override_curr_team=ai_team)
            print(result)
        else:
            guess = get_input
            print(a_game.guess_word([guess, ""]))
        print(a_game.display(print_human_readable=True, show_code=False))
            
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