#!/usr/bin/env python3
"""
Dual N-Back Trainer

A command-line implementation of the dual N-Back working memory task.
Players must track both visual positions and colors from N steps back in sequences.

Usage:
    nback [options]
    python -m nback_game [options]

Options:
    -n, --n-value N       Set the N value (1-8, default: 2)
    -g, --grid-size N     Set the grid size (3-9, default: 8)
    -t, --trials N        Set number of trials (default: 20)
    -d, --display-time N  Set display time in seconds (default: 2.0)
    -h, --help           Show this help message

Controls:
    L                     Location/position match
    A                     Color match
    SPACE                 Both location and color match
    Q                     Quit to menu
    H                     Help
    S                     View scores
"""

import os
import random
import time
import sys
import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Union
import termios
import tty
import select

# Enhanced ANSI color codes with bright variants
ANSI_COLORS = {
    "RED": "\033[91m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "MAGENTA": "\033[95m",
    "CYAN": "\033[96m",
    "ORANGE": "\033[38;5;208m",
    "PINK": "\033[38;5;213m",
}

# UI Theme colors
THEME = {
    "HEADER": "\033[1;96m",      # Bright Cyan Bold
    "SUCCESS": "\033[1;92m",     # Bright Green Bold
    "ERROR": "\033[1;91m",       # Bright Red Bold
    "WARNING": "\033[1;93m",     # Bright Yellow Bold
    "INFO": "\033[1;94m",        # Bright Blue Bold
    "ACCENT": "\033[1;95m",      # Bright Magenta Bold
    "DIM": "\033[2m",            # Dim
    "BOLD": "\033[1m",           # Bold
    "RESET": "\033[0m",          # Reset
}

ANSI_RESET = "\033[0m"

# Decorative elements
SYMBOLS = {
    "DOT": "●",
    "ARROW": "→",
    "CHECK": "✓",
    "CROSS": "✗",
    "STAR": "★",
    "TROPHY": "🏆",
    "BRAIN": "🧠",
}


class NBackGame:
    """
    Dual N-Back training game implementation.

    This class handles the game logic, display, and user interaction for
    a dual N-Back cognitive training task that improves working memory.
    """

    def __init__(
        self,
        n: int = 2,
        grid_size: int = 8,
        trials: int = 20,
        display_time: float = 2.0
    ) -> None:
        """
        Initialize the N-Back game.

        Args:
            n: Number of steps back to remember (1-8)
            grid_size: Size of the grid (3-9)
            trials: Number of trials to play
            display_time: Time to display each position in seconds
        """
        self.n = n
        self.grid_size = grid_size
        self.trials = trials
        self.display_time = display_time

        # Game state
        self.sequence: List[Tuple[int, int]] = []  # Visual positions
        self.color_sequence: List[str] = []        # Color names
        self.score = 0
        self.total_matches = 0
        self.current_trial = 0
        self.is_running = True

        # High scores
        self.high_scores: Dict = self.load_high_scores()

    def load_high_scores(self) -> Dict:
        """
        Load high scores from file.

        Returns:
            Dictionary containing high score data
        """
        scores_file = Path.home() / '.nback_scores.json'
        if scores_file.exists():
            try:
                with open(scores_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"{THEME['WARNING']}Warning: Could not load scores: {e}{THEME['RESET']}")
                return {}
        return {}

    def save_high_score(self) -> None:
        """Save high score if it's a new record."""
        if self.total_matches == 0:
            return

        accuracy = (self.score / self.total_matches) * 100
        key = f"DN{self.n}_G{self.grid_size}"

        if key not in self.high_scores or accuracy > self.high_scores[key]['accuracy']:
            self.high_scores[key] = {
                'accuracy': accuracy,
                'score': self.score,
                'total': self.total_matches,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            scores_file = Path.home() / '.nback_scores.json'
            try:
                with open(scores_file, 'w', encoding='utf-8') as f:
                    json.dump(self.high_scores, f, indent=2)
            except IOError as e:
                print(f"{THEME['ERROR']}Error saving scores: {e}{THEME['RESET']}")

    def get_char(self) -> Optional[str]:
        """
        Get a single character from stdin without requiring Enter.

        Returns:
            Character pressed or None if no input within timeout
        """
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            if select.select([sys.stdin], [], [], 0.1)[0]:
                char = sys.stdin.read(1)
                return char.lower()
            return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def wait_for_key(self) -> str:
        """
        Wait for a single key press and return it.

        Returns:
            The pressed key as a lowercase string
        """
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            char = sys.stdin.read(1)
            return char.lower()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')

    def generate_position(self) -> Tuple[int, int]:
        """
        Generate a random position within the grid.

        Returns:
            Tuple of (row, column) coordinates
        """
        return (
            random.randint(0, self.grid_size - 1),
            random.randint(0, self.grid_size - 1)
        )

    def generate_color(self) -> str:
        """
        Randomly pick a color name for the color stream.

        Returns:
            Color name as string
        """
        return random.choice(list(ANSI_COLORS.keys()))

    def print_centered(self, text: str, width: Optional[int] = None) -> None:
        """
        Print text centered in the terminal.

        Args:
            text: Text to print
            width: Terminal width (auto-detected if None)
        """
        if width is None:
            width = os.get_terminal_size().columns
        print(text.center(width))

    def print_header(self, title: str) -> None:
        """
        Print a styled header.

        Args:
            title: Header title
        """
        width = os.get_terminal_size().columns
        print()
        print(f"{THEME['HEADER']}{'═' * width}{THEME['RESET']}")
        self.print_centered(f"{THEME['HEADER']}{SYMBOLS['BRAIN']} {title} {SYMBOLS['BRAIN']}{THEME['RESET']}")
        print(f"{THEME['HEADER']}{'═' * width}{THEME['RESET']}")
        print()

    def display_grid(
        self,
        position: Tuple[int, int],
        color: str,
        trial_num: Optional[int] = None
    ) -> None:
        """
        Display the current game state with the grid and position.

        Args:
            position: Current position as (row, column)
            color: Current color name
            trial_num: Current trial number (None for practice)
        """
        self.clear_screen()
        terminal_width = os.get_terminal_size().columns

        # Header
        self.print_centered(f"{THEME['HEADER']}╔═══════════════════════════════════════╗{THEME['RESET']}")
        self.print_centered(f"{THEME['HEADER']}║  DUAL N-BACK TRAINER  {SYMBOLS['BRAIN']}  Level: {self.n}  ║{THEME['RESET']}")
        self.print_centered(f"{THEME['HEADER']}╚═══════════════════════════════════════╝{THEME['RESET']}")
        print()

        if trial_num is not None:
            accuracy = (self.score / self.total_matches * 100) if self.total_matches > 0 else 0
            progress_bar = self._create_progress_bar(trial_num, self.trials, 30)
            self.print_centered(
                f"{THEME['INFO']}Trial: {trial_num}/{self.trials} {progress_bar} "
                f"Score: {THEME['SUCCESS']}{self.score}{THEME['RESET']}"
                f"{THEME['INFO']}/{self.total_matches} "
                f"({accuracy:.1f}%){THEME['RESET']}"
            )
            print()

        # Grid
        CELL_W = 7
        CELL_H = 3
        top_border = "╔" + ("═" * CELL_W + "╦") * (self.grid_size - 1) + "═" * CELL_W + "╗"
        mid_border = "╠" + ("═" * CELL_W + "╬") * (self.grid_size - 1) + "═" * CELL_W + "╣"
        bottom_border = "╚" + ("═" * CELL_W + "╩") * (self.grid_size - 1) + "═" * CELL_W + "╝"

        grid_width = len(top_border)
        padding = max(0, (terminal_width - grid_width) // 2)

        print(" " * padding + top_border)

        for row in range(self.grid_size):
            for subrow in range(CELL_H):
                row_str = " " * padding + "║"
                for col in range(self.grid_size):
                    if (row, col) == position and subrow == 1:
                        dot = f"{ANSI_COLORS[color]}{SYMBOLS['DOT']}{ANSI_RESET}"
                        left_pad = (CELL_W - 1) // 2
                        right_pad = CELL_W - 1 - left_pad
                        cell_content = " " * left_pad + dot + " " * right_pad
                    else:
                        cell_content = " " * CELL_W
                    row_str += cell_content + "║"
                print(row_str)
            if row < self.grid_size - 1:
                print(" " * padding + mid_border)

        print(" " * padding + bottom_border)

        # Controls
        print()
        self.print_centered(f"{THEME['ACCENT']}┌───────────────────────────────────────────────┐{THEME['RESET']}")
        self.print_centered(
            f"{THEME['ACCENT']}│{THEME['RESET']}  "
            f"{THEME['INFO']}L{THEME['RESET']} Location   "
            f"{THEME['INFO']}A{THEME['RESET']} Color   "
            f"{THEME['INFO']}SPACE{THEME['RESET']} Both  "
            f"{THEME['DIM']}[H]elp [Q]uit [S]cores{THEME['RESET']}"
            f"  {THEME['ACCENT']}│{THEME['RESET']}"
        )
        self.print_centered(f"{THEME['ACCENT']}└───────────────────────────────────────────────┘{THEME['RESET']}")

    def _create_progress_bar(self, current: int, total: int, width: int = 20) -> str:
        """
        Create a visual progress bar.

        Args:
            current: Current progress value
            total: Total/maximum value
            width: Width of the progress bar

        Returns:
            Formatted progress bar string
        """
        filled = int((current / total) * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"

    def show_high_scores(self) -> None:
        """Display high scores in a formatted table."""
        self.clear_screen()
        terminal_width = os.get_terminal_size().columns

        self.print_header(f"{SYMBOLS['TROPHY']} HIGH SCORES {SYMBOLS['TROPHY']}")

        if not self.high_scores:
            self.print_centered(f"{THEME['DIM']}No high scores yet!{THEME['RESET']}")
            self.print_centered(f"{THEME['DIM']}Play some games to set records.{THEME['RESET']}")
        else:
            # Table header
            self.print_centered(f"{THEME['BOLD']}{'#':<4} {'Level':<12} {'Accuracy':<12} {'Score':<15} {'Date':<12}{THEME['RESET']}")
            self.print_centered(f"{THEME['DIM']}{'─' * 60}{THEME['RESET']}")

            # Sorted scores
            sorted_scores = sorted(
                self.high_scores.items(),
                key=lambda x: x[1]['accuracy'],
                reverse=True
            )[:10]

            for i, (key, score) in enumerate(sorted_scores, 1):
                config = key.replace("DN", "N-").replace("_G", " Grid:")
                accuracy = f"{score['accuracy']:.1f}%"
                score_text = f"{score['score']}/{score['total']}"
                date = score['date'][:10]

                # Color code by rank
                if i == 1:
                    color = THEME['SUCCESS']
                elif i <= 3:
                    color = THEME['INFO']
                else:
                    color = THEME['RESET']

                record = f"{color}{i:<4} {config:<12} {accuracy:<12} {score_text:<15} {date:<12}{THEME['RESET']}"
                self.print_centered(record)

        print()
        self.print_centered(f"{THEME['DIM']}Press any key to continue...{THEME['RESET']}")
        self.wait_for_key()

    def show_help(self) -> None:
        """Display help information."""
        self.clear_screen()

        self.print_header("HELP GUIDE")

        self.print_centered(f"{THEME['BOLD']}What is Dual N-Back?{THEME['RESET']}")
        print()
        self.print_centered("A cognitive training task that improves working memory")
        self.print_centered("by tracking both position and color sequences.")
        print()
        print()

        self.print_centered(f"{THEME['BOLD']}How to Play:{THEME['RESET']}")
        print()
        self.print_centered(f"{THEME['SUCCESS']}{SYMBOLS['ARROW']}{THEME['RESET']} Watch the colored dot appear on the grid")
        self.print_centered(f"{THEME['SUCCESS']}{SYMBOLS['ARROW']}{THEME['RESET']} Remember positions and colors from N steps back")
        self.print_centered(f"{THEME['SUCCESS']}{SYMBOLS['ARROW']}{THEME['RESET']} Press keys when you detect a match")
        print()
        print()

        self.print_centered(f"{THEME['BOLD']}Controls:{THEME['RESET']}")
        print()
        self.print_centered(f"{THEME['INFO']}L{THEME['RESET']}          Match in location/position")
        self.print_centered(f"{THEME['INFO']}A{THEME['RESET']}          Match in color")
        self.print_centered(f"{THEME['INFO']}SPACE{THEME['RESET']}      Both location AND color match")
        self.print_centered(f"{THEME['INFO']}H{THEME['RESET']}          Show this help")
        self.print_centered(f"{THEME['INFO']}Q{THEME['RESET']}          Quit to menu")
        self.print_centered(f"{THEME['INFO']}S{THEME['RESET']}          View high scores")
        print()

        self.print_centered(f"{THEME['DIM']}Press any key to continue...{THEME['RESET']}")
        self.wait_for_key()

    def show_menu(self) -> bool:
        """
        Display the main menu.

        Returns:
            True if user wants to play, False to exit
        """
        while True:
            self.clear_screen()
            terminal_width = os.get_terminal_size().columns

            print("\n" * 2)

            # Title
            self.print_centered(f"{THEME['HEADER']}╔═══════════════════════════════════════════════╗{THEME['RESET']}")
            self.print_centered(f"{THEME['HEADER']}║                                               ║{THEME['RESET']}")
            self.print_centered(f"{THEME['HEADER']}║        {SYMBOLS['BRAIN']} DUAL N-BACK TRAINER {SYMBOLS['BRAIN']}        ║{THEME['RESET']}")
            self.print_centered(f"{THEME['HEADER']}║      Cognitive Enhancement Training          ║{THEME['RESET']}")
            self.print_centered(f"{THEME['HEADER']}║                                               ║{THEME['RESET']}")
            self.print_centered(f"{THEME['HEADER']}╚═══════════════════════════════════════════════╝{THEME['RESET']}")

            print("\n" * 2)

            # Menu options
            self.print_centered(f"{THEME['SUCCESS']}1{THEME['RESET']} {SYMBOLS['ARROW']} Start New Game")
            print()
            self.print_centered(f"{THEME['INFO']}2{THEME['RESET']} {SYMBOLS['ARROW']} View High Scores")
            print()
            self.print_centered(f"{THEME['WARNING']}3{THEME['RESET']} {SYMBOLS['ARROW']} Help & Instructions")
            print()
            self.print_centered(f"{THEME['ERROR']}4{THEME['RESET']} {SYMBOLS['ARROW']} Exit")

            print("\n" * 2)
            self.print_centered(f"{THEME['DIM']}Select an option (1-4):{THEME['RESET']}")

            choice = self.wait_for_key()
            if choice == '1':
                self.show_game_settings()
                return True
            elif choice == '2':
                self.show_high_scores()
            elif choice == '3':
                self.show_help()
            elif choice == '4':
                self.clear_screen()
                self.print_centered(f"{THEME['SUCCESS']}Thanks for training! Keep improving! {SYMBOLS['BRAIN']}{THEME['RESET']}")
                print()
                return False

    def show_game_settings(self) -> None:
        """Display game settings menu with interactive configuration."""
        terminal_width = os.get_terminal_size().columns

        # N value selection
        self.clear_screen()
        self.print_header("GAME CONFIGURATION")
        self.print_centered(f"{THEME['ACCENT']}Step 1 of 4: Select N-Back Level{THEME['RESET']}")
        print()

        levels = [
            ("1", "N=1", "Beginner"),
            ("2", "N=2", "Easy"),
            ("3", "N=3", "Normal"),
            ("4", "N=4", "Challenging"),
            ("5", "N=5", "Hard"),
            ("6", "N=6", "Very Hard"),
            ("7", "N=7", "Expert"),
            ("8", "N=8", "Master"),
        ]

        for num, level, difficulty in levels:
            if int(num) == 2:
                marker = f"{THEME['SUCCESS']} (Recommended){THEME['RESET']}"
            else:
                marker = ""
            self.print_centered(f"{THEME['INFO']}{num}{THEME['RESET']} {SYMBOLS['ARROW']} {level:<8} {THEME['DIM']}{difficulty}{THEME['RESET']}{marker}")

        while True:
            char = self.wait_for_key()
            if char in '12345678':
                self.n = int(char)
                break

        # Grid size selection
        self.clear_screen()
        self.print_header("GAME CONFIGURATION")
        self.print_centered(f"{THEME['ACCENT']}Step 2 of 4: Select Grid Size{THEME['RESET']}")
        print()

        for size in range(3, 10):
            if size == 8:
                marker = f"{THEME['SUCCESS']} (Recommended){THEME['RESET']}"
            else:
                marker = ""
            self.print_centered(f"{THEME['INFO']}{size}{THEME['RESET']} {SYMBOLS['ARROW']} {size}×{size} Grid{marker}")

        while True:
            char = self.wait_for_key()
            if char in '3456789':
                self.grid_size = int(char)
                break

        # Trial count selection
        self.clear_screen()
        self.print_header("GAME CONFIGURATION")
        self.print_centered(f"{THEME['ACCENT']}Step 3 of 4: Select Trial Count{THEME['RESET']}")
        print()

        trial_options = [20, 30, 40, 50, 60, 80]
        for i, trials in enumerate(trial_options, 1):
            if trials == 20:
                marker = f"{THEME['SUCCESS']} (Recommended){THEME['RESET']}"
            else:
                marker = ""
            self.print_centered(f"{THEME['INFO']}{i}{THEME['RESET']} {SYMBOLS['ARROW']} {trials} Trials{marker}")

        while True:
            char = self.wait_for_key()
            if char in '123456':
                self.trials = trial_options[int(char) - 1]
                break

        # Display time selection
        self.clear_screen()
        self.print_header("GAME CONFIGURATION")
        self.print_centered(f"{THEME['ACCENT']}Step 4 of 4: Select Response Time{THEME['RESET']}")
        print()

        times = [1.0, 1.5, 2.0, 2.5, 3.0]
        for i, t in enumerate(times, 1):
            if t == 2.0:
                marker = f"{THEME['SUCCESS']} (Recommended){THEME['RESET']}"
            else:
                marker = ""
            self.print_centered(f"{THEME['INFO']}{i}{THEME['RESET']} {SYMBOLS['ARROW']} {t:.1f}s per trial{marker}")

        while True:
            char = self.wait_for_key()
            if char in '12345':
                self.display_time = times[int(char) - 1]
                break

    def run_game(self) -> None:
        """Run a single game session."""
        self.clear_screen()

        # Configuration summary
        self.print_header("GAME READY")

        self.print_centered(f"{THEME['INFO']}N-Back Level:{THEME['RESET']} {THEME['BOLD']}{self.n}{THEME['RESET']}")
        self.print_centered(f"{THEME['INFO']}Grid Size:{THEME['RESET']} {THEME['BOLD']}{self.grid_size}×{self.grid_size}{THEME['RESET']}")
        self.print_centered(f"{THEME['INFO']}Trials:{THEME['RESET']} {THEME['BOLD']}{self.trials}{THEME['RESET']}")
        self.print_centered(f"{THEME['INFO']}Response Time:{THEME['RESET']} {THEME['BOLD']}{self.display_time:.1f}s{THEME['RESET']}")
        print()
        print()
        self.print_centered(f"{THEME['WARNING']}First, memorize {self.n} position/color pairs{THEME['RESET']}")
        self.print_centered(f"{THEME['DIM']}Then respond to matches during the game{THEME['RESET']}")

        print("\n" * 2)
        self.print_centered(f"{THEME['SUCCESS']}Press any key to begin training...{THEME['RESET']}")
        self.wait_for_key()

        # Reset game state
        self.sequence = []
        self.color_sequence = []
        self.score = 0
        self.total_matches = 0
        self.current_trial = 0
        self.is_running = True

        # Memory phase
        for i in range(self.n):
            position = self.generate_position()
            color = self.generate_color()
            self.sequence.append(position)
            self.color_sequence.append(color)
            self.display_grid(position, color)
            self.print_centered(f"{THEME['WARNING']}Memorize item {i+1} of {self.n}{THEME['RESET']}")
            time.sleep(self.display_time)

        self.clear_screen()
        self.print_centered(f"\n\n{THEME['SUCCESS']}Memory phase complete! {SYMBOLS['CHECK']}{THEME['RESET']}")
        self.print_centered(f"{THEME['INFO']}Game starting...{THEME['RESET']}")
        time.sleep(1.5)

        # Main game loop
        for trial in range(self.trials):
            self.current_trial = trial + 1
            position = self.generate_position()
            color = self.generate_color()
            self.sequence.append(position)
            self.color_sequence.append(color)

            self.display_grid(position, color, self.current_trial)

            if len(self.sequence) > self.n:
                is_visual_match = (position == self.sequence[-(self.n + 1)])
                is_color_match = (color == self.color_sequence[-(self.n + 1)])

                if is_visual_match:
                    self.total_matches += 1
                if is_color_match:
                    self.total_matches += 1

                # Wait for user input with timeout
                start_time = time.time()
                response = None
                while time.time() - start_time < self.display_time:
                    char = self.get_char()
                    if char:
                        if char == 'h':
                            self.show_help()
                            self.display_grid(position, color, self.current_trial)
                            continue
                        elif char == 's':
                            self.show_high_scores()
                            self.display_grid(position, color, self.current_trial)
                            continue
                        elif char == 'q':
                            self.is_running = False
                            break
                        elif char in 'al ':
                            if char == ' ':
                                response = 'both'
                            else:
                                response = char
                            break

                if not self.is_running:
                    break

                # Feedback
                print()
                if response is None:
                    self.print_centered(f"{THEME['DIM']}⏱ Time's up!{THEME['RESET']}")
                else:
                    correct = False
                    points_earned = 0

                    if response == 'l' and is_visual_match and not is_color_match:
                        points_earned = 1
                        correct = True
                    elif response == 'a' and is_color_match and not is_visual_match:
                        points_earned = 1
                        correct = True
                    elif response == 'both' and is_visual_match and is_color_match:
                        points_earned = 2
                        correct = True
                    elif response == 'l' and not is_visual_match:
                        correct = False
                    elif response == 'a' and not is_color_match:
                        correct = False
                    elif response == 'both' and not (is_visual_match and is_color_match):
                        correct = False
                    else:
                        correct = False

                    self.score += points_earned

                    if correct:
                        self.print_centered(
                            f"{THEME['SUCCESS']}{SYMBOLS['CHECK']} Correct! "
                            f"+{points_earned} point{'s' if points_earned > 1 else ''}{THEME['RESET']}"
                        )
                    else:
                        self.print_centered(f"{THEME['ERROR']}{SYMBOLS['CROSS']} Incorrect!{THEME['RESET']}")

                time.sleep(0.6)

        # Game over screen
        if self.is_running:
            self.clear_screen()

            self.print_header(f"{SYMBOLS['TROPHY']} TRAINING COMPLETE {SYMBOLS['TROPHY']}")

            if self.total_matches > 0:
                accuracy = (self.score / self.total_matches) * 100

                # Performance rating
                if accuracy >= 90:
                    rating = f"{THEME['SUCCESS']}OUTSTANDING!{THEME['RESET']}"
                    stars = f"{THEME['SUCCESS']}{SYMBOLS['STAR'] * 5}{THEME['RESET']}"
                elif accuracy >= 75:
                    rating = f"{THEME['SUCCESS']}EXCELLENT!{THEME['RESET']}"
                    stars = f"{THEME['SUCCESS']}{SYMBOLS['STAR'] * 4}{THEME['RESET']}"
                elif accuracy >= 60:
                    rating = f"{THEME['INFO']}GOOD JOB!{THEME['RESET']}"
                    stars = f"{THEME['INFO']}{SYMBOLS['STAR'] * 3}{THEME['RESET']}"
                elif accuracy >= 40:
                    rating = f"{THEME['WARNING']}KEEP PRACTICING!{THEME['RESET']}"
                    stars = f"{THEME['WARNING']}{SYMBOLS['STAR'] * 2}{THEME['RESET']}"
                else:
                    rating = f"{THEME['ERROR']}TRY AGAIN!{THEME['RESET']}"
                    stars = f"{THEME['ERROR']}{SYMBOLS['STAR']}{THEME['RESET']}"

                self.print_centered(rating)
                self.print_centered(stars)
                print()
                self.print_centered(f"{THEME['BOLD']}Final Score:{THEME['RESET']} {THEME['SUCCESS']}{self.score}{THEME['RESET']}/{self.total_matches}")
                self.print_centered(f"{THEME['BOLD']}Accuracy:{THEME['RESET']} {THEME['INFO']}{accuracy:.1f}%{THEME['RESET']}")

                # Check for high score
                key = f"DN{self.n}_G{self.grid_size}"
                is_new_record = (
                    key not in self.high_scores or
                    accuracy > self.high_scores[key]['accuracy']
                )

                if is_new_record:
                    print()
                    self.print_centered(f"{THEME['SUCCESS']}{SYMBOLS['TROPHY']} NEW HIGH SCORE! {SYMBOLS['TROPHY']}{THEME['RESET']}")

                self.save_high_score()
            else:
                self.print_centered(f"{THEME['DIM']}No scoring opportunities in this session{THEME['RESET']}")

            print("\n" * 2)
            self.print_centered(f"{THEME['DIM']}Press any key to return to menu...{THEME['RESET']}")
            self.wait_for_key()

    def play(self) -> None:
        """Main game loop."""
        try:
            while True:
                if self.show_menu():
                    self.run_game()
                else:
                    break
        except KeyboardInterrupt:
            self.clear_screen()
            self.print_centered(f"\n{THEME['INFO']}Game interrupted. Goodbye!{THEME['RESET']}\n")
            sys.exit(0)
        except Exception as e:
            self.clear_screen()
            print(f"{THEME['ERROR']}An error occurred: {e}{THEME['RESET']}")
            sys.exit(1)


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Dual N-Back Trainer - Professional cognitive enhancement training",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '-n', '--n-value',
        type=int,
        choices=range(1, 9),
        default=None,
        metavar='N',
        help='Set the N value (1-8, default: 2)'
    )
    parser.add_argument(
        '-g', '--grid-size',
        type=int,
        choices=range(3, 10),
        default=None,
        metavar='SIZE',
        help='Set the grid size (3-9, default: 8)'
    )
    parser.add_argument(
        '-t', '--trials',
        type=int,
        choices=[20, 30, 40, 50, 60, 80],
        default=None,
        metavar='N',
        help='Set number of trials (20, 30, 40, 50, 60, or 80)'
    )
    parser.add_argument(
        '-d', '--display-time',
        type=float,
        default=2.0,
        metavar='SECONDS',
        help='Set display time in seconds (default: 2.0)'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    return parser.parse_args()


def main() -> None:
    """Main entry point for the game."""
    try:
        args = parse_args()

        # Check if any game parameters were provided via command line
        game_args_provided = any([
            args.n_value is not None,
            args.grid_size is not None,
            args.trials is not None,
            args.display_time != 2.0
        ])

        game = NBackGame(
            n=args.n_value if args.n_value is not None else 2,
            grid_size=args.grid_size if args.grid_size is not None else 8,
            trials=args.trials if args.trials is not None else 20,
            display_time=args.display_time
        )

        if game_args_provided:
            # Skip menu and go directly to game
            game.run_game()
        else:
            # Show menu system
            game.play()

    except KeyboardInterrupt:
        print(f"\n{THEME['INFO']}Game interrupted. Goodbye!{THEME['RESET']}")
        sys.exit(0)
    except Exception as e:
        print(f"{THEME['ERROR']}Fatal error: {e}{THEME['RESET']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
