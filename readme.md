A simple implementation of the Codenames board game for AI agents to play. This turns codenames from
a 4 player minimum game into a 2 player game. The AI doesn't have a body, so the human spymaster
has to read the output from the AI bot, take actions on it's behalf, and tell the AI what moves
the human guesser made.

Installation:
1. Clone this repository with
```
git clone https://github.com/Pchatain/codenames-ai-agent.git
```
2. Download a Python version compatible with your system.
3. Run
```
pip install -r requirements.txt
```

Quickstart:
1. Set up a physical board on the table.
2. Make sure to set ANTHROPIC_API_KEY in your environment variables in a terminal. You can get one here https://www.anthropic.com/api
```
export ANTHROPIC_API_KEY="<you-key>"
```
3. Run `python play.py` to play against an AI agent.

Cluer:
* State = Board with annotations which are red, blue, neutral, or black.
* Actions = one word, and a number which represents how many cards the other should guess.

Guesser:
* State = Board as defined above, previously chosen words, the clue word, and a number of how many guesses that clue word should correspond to.
* Actions = 1. guess a word. 2. end turn.

Potential Improvements:
- [ ] Add support for more AI agent models.
- [ ] Train an agent to play the game.
- [ ] Add a linter to the codebase.
- [ ] Support boards of different sizes.
