# bj simulator project

hey, so this is my blackjack simulator. i built it to see if i could code something that actually tells u the best mathematical move in real time while playing.

### what it does
- **sim engine**: it basically plays thousands of dummy hands in the background for every choice (hit, stand, double, split) and spits out the expected value (ev) instantly. 
- **card counting**: keeps the running and true count (hi-lo system) and suggests bets based on how hot the shoe is.
- **terminal ui**: just prints everything directly to the terminal. i got rid of the fancy third party libraries so it won't crash on windows anymore.

### current status
it works! the whole game loop, the probability engine, and the counting logic are all just baked right into `main.py`. 

### how to play
no requirements.txt needed, just run it:

```bash
python main.py
```
