A simple implementation of the Codenames board game for AI agents to play. This turns codenames from
a 4 player minimum game into a 2 player game. The AI doesn't have a body, so the human spymaster
has to read the output from the AI bot, take actions on it's behalf, and tell the AI what moves
the human guesser made.

Quickstart:
1. Set up a physical board on the table.
2. Make sure to set ANTHROPIC_API_KEY in your environment variables in a terminal. E.g.
```
export ANTHROPIC_API_KEY="sk-<your-key>"
```
3. Run `python play.py` to play against an AI agent.

Cluer:
* State = Board with annotations which are red, blue, neutral, or black. (TODO) A log of what the guesser speculates could be a word, but they decided not to choose it.
* Actions = one word, and a number which represents how many cards the other should guess.
Guesser: 
* State = Board. Previously chosen words, the clue word, and a number of how many guesses that clue word should correspond to.
* Actions = 1. guess a word. 2. end turn. 3. (TODO) think out loud.

Potential Improvements:
- [ ] Add support for more AI agent models.
- [ ] Train an agent to play code names.
- [ ] Add a linter to the codebase.
