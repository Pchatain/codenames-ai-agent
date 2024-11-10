import numpy as np

PATH_TO_WORDS = "codenames/wordlist/en-EN/default/wordlist.txt"

def main(n, seed=None):
    # Load words
    with open(PATH_TO_WORDS, "r", encoding="utf-8") as f:
        words = f.read().split("\n")
    # get n random words
    if seed is not None:
        np.random.seed(seed)
    chosen_words = np.random.choice(words, n, replace=False)
    return chosen_words

if __name__ == "__main__":
    main(25)