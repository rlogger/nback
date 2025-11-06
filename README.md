# Dual N-Back Trainer

A command-line implementation of the dual N-Back working memory task. This game helps improve working memory and cognitive function by requiring players to track both visual positions and colors from N steps back in sequences.

## Usage

Run the game using Python:

```bash
python nback_game/nback.py
```

### Command Line Options

- `-n, --n-value N`: Set the N value (1-8, default: 2)
- `-g, --grid-size N`: Set the grid size (3-9, default: 8)
- `-t, --trials N`: Set number of trials (default: 20)
- `-d, --display-time N`: Set display time in seconds (default: 2.0)

Example:
```bash
python nback_game/nback.py -n 3 -g 6 -t 40 -d 1.5
```

### Controls

- `L`: Location/position match
- `A`: Color match
- `SPACE`: Both location and color match
- `Q`: Quit to menu
- `H`: Help
- `S`: View scores

## Features

- Dual N-Back training (position + color)
- Adjustable difficulty levels
- High score tracking
- Customizable grid size and trial count
- Interactive command-line interface
- Cross-platform support

## Requirements

- Python 3.7 or higher
- Terminal with ANSI color support 