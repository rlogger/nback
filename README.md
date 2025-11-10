# Dual N-Back Trainer

A beautiful, feature-rich command-line implementation of the dual N-Back working memory task. This game helps improve working memory and cognitive function by requiring players to track both visual positions and colors from N steps back in sequences.

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Dual N-Back Training** - Track both position and color sequences
- **Beautiful Terminal UI** - Colorful, polished interface with Unicode box-drawing characters
- **Progress Tracking** - Real-time accuracy and score display with progress bars
- **High Score System** - Persistent high score tracking across sessions
- **Customizable Settings** - Adjustable difficulty, grid size, trials, and timing
- **Interactive Menu** - Easy-to-use menu system for configuration
- **Auto-save Scores** - Automatically saves your best performances
- **Keyboard Controls** - Simple, intuitive keyboard-only interface
- **Visual Feedback** - Color-coded feedback and performance ratings
- **Performance Ratings** - Get rated from "Try Again" to "Outstanding!"

## Installation

### From PyPI (Recommended)

```bash
pip install nback-trainer
```

### From Source

```bash
git clone https://github.com/rlogger/nback.git
cd nback
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/rlogger/nback.git
cd nback
pip install -e .[dev]
```

## Quick Start

### Launch the Game

Simply run:

```bash
nback
```

Or:

```bash
nback-trainer
```

### Direct Game Start (Skip Menu)

You can start a game directly with custom settings:

```bash
nback -n 3 -g 6 -t 40 -d 1.5
```

## Usage

### Interactive Menu

When you launch the game without arguments, you'll see an interactive menu:

1. **Start New Game** - Configure and play
2. **View High Scores** - See your best performances
3. **Help & Instructions** - Learn how to play
4. **Exit** - Quit the game

### Command Line Options

```
Options:
  -n, --n-value N         Set the N value (1-8, default: 2)
  -g, --grid-size SIZE    Set the grid size (3-9, default: 8)
  -t, --trials N          Set number of trials (20, 30, 40, 50, 60, 80)
  -d, --display-time SEC  Set display time in seconds (default: 2.0)
  --version               Show version and exit
  -h, --help             Show help message
```

### Examples

**Easy game for beginners:**
```bash
nback -n 1 -g 5 -t 20 -d 3.0
```

**Standard training session:**
```bash
nback -n 2 -g 8 -t 30
```

**Expert challenge:**
```bash
nback -n 5 -g 9 -t 60 -d 1.5
```

## Controls

| Key | Action |
|-----|--------|
| `L` | Mark a **location/position** match |
| `A` | Mark a **color** match |
| `SPACE` | Mark **both** location and color match |
| `H` | Show help screen |
| `S` | View high scores |
| `Q` | Quit to menu |

## How to Play

### What is Dual N-Back?

Dual N-Back is a cognitive training exercise scientifically shown to improve working memory and fluid intelligence. In this game, you track two independent streams of information:

1. **Position Stream**: Where the dot appears on the grid
2. **Color Stream**: What color the dot is

### Objective

For each trial, you must identify if the current position and/or color matches the one from **N steps back**.

### Difficulty Levels

- **N=1**: Remember 1 step back (Beginner)
- **N=2**: Remember 2 steps back (Easy) - *Recommended start*
- **N=3**: Remember 3 steps back (Normal)
- **N=4+**: Advanced levels for serious training

### Training Tips

1. **Start small**: Begin with N=2 on a smaller grid (5×5 or 6×6)
2. **Focus**: Minimize distractions during training
3. **Regular practice**: 20-30 minutes per day yields best results
4. **Progression**: Increase N value when you consistently score >80%
5. **Stay relaxed**: Don't stress about mistakes, they're part of learning

## Scoring

- **Correct match**: +1 point (or +2 for both matches)
- **Missed match**: No points deducted
- **False positive**: No points deducted
- **Accuracy**: Score / Total Possible Matches × 100%

### Performance Ratings

- * **Try Again**: < 40%
- ** **Keep Practicing**: 40-59%
- *** **Good Job**: 60-74%
- **** **Excellent**: 75-89%
- ***** **Outstanding**: 90%+

## Requirements

- **Python**: 3.7 or higher
- **OS**: Linux, macOS, or any POSIX-compliant system
- **Terminal**: ANSI color support (most modern terminals)
- **Dependencies**: Python standard library only!

## High Scores

High scores are automatically saved to `~/.nback_scores.json` and tracked per configuration (N-value and grid size). View your best performances anytime from the menu or press `S` during gameplay.

## Development

### Building for PyPI

```bash
# Install build tools
pip install build twine

# Build the distribution
python -m build

# Check the distribution
twine check dist/*

# Upload to TestPyPI (for testing)
twine upload --repository testpypi dist/*

# Upload to PyPI (production)
twine upload dist/*
```

### Project Structure

```
nback/
├── nback_game/
│   ├── __init__.py
│   └── nback.py
├── pyproject.toml
├── LICENSE
├── README.md
├── MANIFEST.in
└── .gitignore
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by the original N-Back research on working memory training
- Built with Python's standard library for maximum compatibility
- Thanks to the cognitive science community for N-Back research

## Research

The N-Back task has been studied extensively in cognitive psychology:

- Improves working memory capacity
- May enhance fluid intelligence
- Strengthens executive function
- Potentially improves attention and concentration

## Bug Reports & Feature Requests

Please report bugs and request features via the [GitHub Issues](https://github.com/rlogger/nback/issues) page.

## Contact

For questions or feedback, please open an issue on GitHub.

---

**Made for cognitive enhancement enthusiasts**

Happy Training!
