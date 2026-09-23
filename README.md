# Advanced Blackjack Simulator

A high-performance, terminal-based Blackjack simulator built in Python. This project utilizes a Monte Carlo probability engine to calculate the Expected Value (EV) of every possible move in real-time. It also includes an integrated Hi-Lo card counting system to dynamically adjust betting strategies based on shoe penetration and True Count.

## Features

- **Standard Casino Rules**: 6-deck shoe, dealer hits on soft 17, blackjack pays 3:2.
- **Monte Carlo Simulator**: Runs 3,000 simulations per available move (Hit, Stand, Double, Split) in under 0.5s to determine the statistically optimal play.
- **Hi-Lo Card Counting**: Tracks all dealt cards to maintain a running and true count, offering dynamic bet multiplier recommendations.
- **Rich Terminal UI**: Beautiful, colorized terminal interface using the `rich` Python library.
- **Analytics Logging**: Automatically records hand outcomes, profit/loss, and strategy alignment to `session_analytics.json`.

## Architecture

- `src/models.py`: Core components (`Card`, `Hand`, `Deck`).
- `src/simulator.py`: Monte Carlo probability engine for EV calculations.
- `src/counter.py`: Implementation of the Hi-Lo counting system.
- `src/game.py`: Main game loop, state management, and UI rendering.
- `main.py`: Entry point to launch the application.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_dir>
   ```

2. (Optional but recommended) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Start a session by running:

```bash
python main.py
```

Follow the on-screen prompts to input bets and choose actions (Hit, Stand, Double, Split). The probability engine will continuously suggest the move with the highest Expected Value.

## License

MIT
