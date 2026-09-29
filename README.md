# Advanced Blackjack Simulator

A terminal-based Blackjack simulator built in Python. This project utilizes a Monte Carlo probability engine to calculate the Expected Value (EV) of possible moves in real-time. It also includes an integrated Hi-Lo card counting system to dynamically adjust betting strategies based on shoe penetration.

## Features

- **Standard Casino Rules**: 6-deck shoe, dealer hits on soft 17, blackjack pays 3:2.
- **Monte Carlo Simulator**: Runs thousands of simulations per available move (Hit, Stand, Double, Split) to determine the mathematically optimal play.
- **Hi-Lo Card Counting**: Tracks all dealt cards to maintain a running and true count, offering dynamic bet multiplier recommendations.
- **No External Dependencies**: Built entirely using the Python Standard Library for maximum compatibility.

## Architecture

All logic, including the simulation engine, card counting mechanics, and the game loop, has been consolidated into a single executable script: `main.py`.

## Installation & Usage

No third-party packages or installations are necessary. 

Start a session by running:

```bash
python main.py
```

Follow the on-screen prompts to input bets and choose actions. The probability engine will continuously suggest the move with the highest Expected Value.

## License

MIT
