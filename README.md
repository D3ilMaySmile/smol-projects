# bj sim

this is a simple blackjack simulator i made. it runs directly in the terminal and uses monte carlo simulations to tell you the best move to make based on expected value (ev). 

it also counts cards using the hi-lo system and tells you what to bet.

### features
- standard casino rules (6 decks, dealer hits soft 17, bj pays 3:2)
- monte carlo sim (runs lots of hands in the background to figure out the best move)
- card counting (tracks the true count and gives bet multipliers)
- no dependencies needed! just pure python.

### how to run
u don't need to install any special libraries anymore, i took out the rich library so it works anywhere.

```bash
python main.py
```

just follow the prompts in the terminal to play.

### note
everything is in `main.py`. i didn't split it into multiple files or modules cause it's easier to just run a single script for now.
