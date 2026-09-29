# Advanced Blackjack Simulator Project

This is a terminal-based Blackjack simulator designed to evaluate and suggest optimal moves in real-time through mathematical simulation.

## Core Capabilities

- **Probability Engine**: Operates a Monte Carlo simulation in the background, playing through thousands of scenarios for every possible action (Hit, Stand, Double, Split) to calculate the Expected Value (EV) instantly.
- **Dynamic Card Counting**: Implements the Hi-Lo counting system to track the running and true count, dynamically adjusting suggested betting amounts based on shoe penetration.
- **Standardized Rules**: Enforces standard casino rules including a 6-deck shoe, dealer hits on soft 17, and a 3:2 payout for Blackjack.

## Implementation Details

The project has been streamlined for ease of use and maximum compatibility. The entire game loop, probability engine, and counting logic are integrated directly into `main.py`. It utilizes standard terminal output, completely eliminating the need for third-party libraries.

## How to Play

The application is built entirely on the Python Standard Library. No external dependencies or `requirements.txt` installations are required. 

To launch the simulator, execute the following command:

```bash
python main.py
```
