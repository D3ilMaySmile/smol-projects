# Advanced Blackjack Simulator

Hey! This is a little project I built: a Blackjack simulator that runs right in your terminal. I wanted to see if I could build something that actually helps you figure out the best move in real-time.

## What it does

- **Monte Carlo Engine**: Behind the scenes, it runs thousands of simulations for every possible move (Hit, Stand, Double, Split) and tells you the Expected Value (EV) of each option instantly.
- **Card Counting**: It keeps track of the running and true count using the Hi-Lo system, and suggests how much you should bet based on the remaining shoe.
- **Terminal UI**: Uses the `rich` library to make the terminal output actually look good (colors, tables, etc.).
- **Real Casino Rules**: Standard 6-deck shoe, dealer hits on soft 17, 3:2 payout.

## Current Status

It's fully working! The entire game loop, probability engine, and UI are baked into the `main.py` file. You can just install the dependencies and run it.

## How to play

```bash
pip install -r requirements.txt
python main.py
```
