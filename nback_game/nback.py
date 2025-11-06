#!/usr/bin/env python3
"""
Dual N-Back Trainer

A command-line implementation of the dual N-Back working memory task.
Players must track both visual positions and colors from N steps back in sequences.

Usage:
    python nback.py [options]

Options:
    -n, --n-value N       Set the N value (1-5, default: 2)
    -g, --grid-size N     Set the grid size (3-9, default: 8)
    -t, --trials N        Set number of trials (default: 20)
    -d, --display-time N  Set display time in seconds (default: 2)
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
from typing import List, Tuple, Optional, Dict
import termios
import tty
import select

# ANSI color codes for color stream (dual N-Back)
ANSI_COLORS = {
    "RED": "\033[91m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "MAGENTA": "\033[95m",
    "CYAN": "\033[96m",
}
ANSI_RESET = "\033[0m"

class NBackGame:
    def __init__(self, n: int = 2, grid_size: int = 8, trials: int = 20, display_time: float = 2.0):
        """
        Initialize the N-Back game.
        
        Args:
            n: Number of steps back to remember
            grid_size: Size of the grid (grid_size x grid_size)
            trials: Number of trials to play
            display_time: Time to display each position in seconds
        """
        self.n = n
        self.grid_size = grid_size
        self.trials = trials
        self.display_time = display_time
        # Sequences for both modalities (position + color)
        self.sequence: List[Tuple[int, int]] = []  # visual positions
        self.color_sequence: List[str] = []        # color names
        self.score = 0
        self.total_matches = 0
        self.current_trial = 0
        self.is_running = True
        self.high_scores: Dict = self.load_high_scores()
        # No audio engine needed for color modality

    def load_high_scores(self) -> Dict:
        """Load high scores from file."""
        scores_file = Path.home() / '.nback_scores.json'
        if scores_file.exists():
            try:
                with open(scores_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_high_score(self):
        """Save high score if it's a new record."""
        if self.total_matches == 0:
            return

        accuracy = (self.score/self.total_matches)*100
        key = f"DN{self.n}_G{self.grid_size}"
        
        if key not in self.high_scores or accuracy > self.high_scores[key]['accuracy']:
            self.high_scores[key] = {
                'accuracy': accuracy,
                'score': self.score,
                'total': self.total_matches,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            scores_file = Path.home() / '.nback_scores.json'
            with open(scores_file, 'w') as f:
                json.dump(self.high_scores, f, indent=2)

    def get_char(self) -> Optional[str]:
        """Get a single character from stdin without requiring Enter."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            if select.select([sys.stdin], [], [], 0.1)[0]:
                char = sys.stdin.read(1)
                return char
            return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def wait_for_key(self) -> str:
        """Wait for a single key press and return it."""
        # Flush input buffer to ensure clean state
        sys.stdin.flush()
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            char = sys.stdin.read(1)
            return char
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')

    def generate_position(self) -> Tuple[int, int]:
        """Generate a random position within the grid."""
        return (random.randint(0, self.grid_size-1), 
                random.randint(0, self.grid_size-1))

    def generate_color(self) -> str:
        """Randomly pick a color name for the color stream."""
        return random.choice(list(ANSI_COLORS.keys()))

    def display_grid(self, position: Tuple[int, int], color: str, trial_num: int = None):
        """Display the current game state with the grid and position."""
        self.clear_screen()

        terminal_width = os.get_terminal_size().columns

        # ===== HEADER =====
        print(f"Dual N-Back Trainer (N={self.n})".center(terminal_width))
        if trial_num is not None:
            print(f"Trial {trial_num}/{self.trials} | Score: {self.score}/{self.total_matches}".center(terminal_width))
        print()

        # ===== GRID =====
        CELL_W = 7  # inner cell width (characters) ‑- bigger than before
        CELL_H = 3  # number of lines per cell
        # Pre-build repetitive pieces so the grid construction is quick
        top_border    = "╔" + ("═"*CELL_W + "╦")*(self.grid_size-1) + "═"*CELL_W + "╗"
        mid_border    = "╠" + ("═"*CELL_W + "╬")*(self.grid_size-1) + "═"*CELL_W + "╣"
        bottom_border = "╚" + ("═"*CELL_W + "╩")*(self.grid_size-1) + "═"*CELL_W + "╝"

        grid_width = len(top_border)
        padding = max(0, (terminal_width - grid_width) // 2)

        # print top border
        print(" "*padding + top_border)

        # Render each cell as 3 lines for vertical centering
        for row in range(self.grid_size):
            for subrow in range(CELL_H):
                row_str = " "*padding + "║"
                for col in range(self.grid_size):
                    if (row, col) == position and subrow == 1:
                        # Manually center the colored dot to avoid ANSI code issues
                        dot = f"{ANSI_COLORS[color]}●{ANSI_RESET}"
                        # Calculate padding to center the visible dot (1 character)
                        left_pad = (CELL_W - 1) // 2
                        right_pad = CELL_W - 1 - left_pad
                        cell_content = " " * left_pad + dot + " " * right_pad
                    else:
                        cell_content = " "*CELL_W
                    row_str += cell_content + "║"
                print(row_str)
            if row < self.grid_size - 1:
                print(" "*padding + mid_border)

        # bottom border
        print(" "*padding + bottom_border)

        # ===== CONTROL HINTS =====
        print()
        print("L = Location   |   A = Color   |   SPACE = Both".center(terminal_width))
        print("H = Help       |   Q = Quit    |   S = Scores".center(terminal_width))

    def show_high_scores(self):
        """Display high scores."""
        self.clear_screen()
        terminal_width = os.get_terminal_size().columns
        
        print("\n" * 2)
        print("HIGH SCORES".center(terminal_width))
        print()
        
        if not self.high_scores:
            print("No high scores yet!".center(terminal_width))
        else:
            for i, (key, score) in enumerate(sorted(self.high_scores.items(), 
                                  key=lambda x: x[1]['accuracy'], 
                                          reverse=True)[:5], 1):
                config = key.replace("DN", "N").replace("_G", " Grid:")
                accuracy = f"{score['accuracy']:.1f}%"
                record = f"{i}. {config} | {accuracy} | {score['score']}/{score['total']} | {score['date'][:10]}"
                print(record.center(terminal_width))
        
        print(f"\n{'Press any key to continue...'.center(terminal_width)}")
        self.wait_for_key()

    def show_help(self):
        """Display help information."""
        self.clear_screen()
        terminal_width = os.get_terminal_size().columns
        
        print("\n" * 2)
        print("HELP GUIDE".center(terminal_width))
        print()
        print("Dual N-Back Training:".center(terminal_width))
        print("• Track position and color streams".center(terminal_width))
        print("• Identify matches from N steps back".center(terminal_width))
        print("• Improves working memory and cognition".center(terminal_width))
        print()
        print("Controls:".center(terminal_width))
        print("L     = Location/Position match".center(terminal_width))
        print("A     = Color match".center(terminal_width))
        print("SPACE = Both location AND color match".center(terminal_width))
        print("H     = Show this help".center(terminal_width))
        print("Q     = Quit to menu".center(terminal_width))
        print("S     = View high scores".center(terminal_width))
        
        print(f"\n{'Press any key to continue...'.center(terminal_width)}")
        self.wait_for_key()

    def show_menu(self) -> bool:
        """Display the main menu."""
        while True:
            self.clear_screen()
            terminal_width = os.get_terminal_size().columns
            
            print("\n" * 3)
            
            print("DUAL N-BACK TRAINER".center(terminal_width))
            print("Cognitive Enhancement Training".center(terminal_width))
            
            print("\n" * 2)
            
            print("1 - Start New Game".center(terminal_width))
            print("2 - View High Scores".center(terminal_width))
            print("3 - Help & Instructions".center(terminal_width))
            print("4 - Exit".center(terminal_width))
            
            print(f"\n{'Select an option (1-4):'.center(terminal_width)}")
            
            choice = self.wait_for_key()
            if choice == '1':
                self.show_game_settings()
                return True
            elif choice == '2':
                self.show_high_scores()
            elif choice == '3':
                self.show_help()
            elif choice == '4':
                return False

    def show_game_settings(self):
        """Display game settings menu."""
        terminal_width = os.get_terminal_size().columns
        
        # N value selection
        self.clear_screen()
        print("\n" * 2)
        print("GAME CONFIGURATION".center(terminal_width))
        print("Step 1: Select N-Back Level".center(terminal_width))
        print()
        print("1 - N=1 (Easy)".center(terminal_width))
        print("2 - N=2".center(terminal_width))
        print("3 - N=3 (Normal)".center(terminal_width))
        print("4 - N=4".center(terminal_width))
        print("5 - N=5 (Hard)".center(terminal_width))
        print("6 - N=6".center(terminal_width))
        print("7 - N=7 (Limit)".center(terminal_width))
        print("8 - N=8".center(terminal_width))
        while True:
            char = self.wait_for_key()
            if char in '12345678':
                self.n = int(char)
                break
        
        # Grid size selection
        self.clear_screen()
        print("\n" * 2)
        print("GAME CONFIGURATION".center(terminal_width))
        print("Step 2: Select Grid Size".center(terminal_width))
        print()
        print("3 - 3×3 Grid".center(terminal_width))
        print("4 - 4×4 Grid".center(terminal_width))
        print("5 - 5×5 Grid".center(terminal_width))
        print("6 - 6×6 Grid".center(terminal_width))
        print("7 - 7×7 Grid".center(terminal_width))
        print("8 - 8×8 Grid".center(terminal_width))
        print("9 - 9×9 Grid".center(terminal_width))
        while True:
            char = self.wait_for_key()
            if char in '3456789':
                self.grid_size = int(char)
                break
        
        # Trial count selection
        self.clear_screen()
        print("\n" * 2)
        print("GAME CONFIGURATION".center(terminal_width))
        print("Step 3: Select Trial Count".center(terminal_width))
        print()
        trial_options = [20, 30, 40, 50, 60, 80]
        for i, trials in enumerate(trial_options, 1):
            print(f"{i} - {trials} Trials".center(terminal_width))
        while True:
            char = self.wait_for_key()
            if char in '123456':
                self.trials = trial_options[int(char) - 1]
                break
        
        # Display time selection
        self.clear_screen()
        print("\n" * 2)
        print("GAME CONFIGURATION".center(terminal_width))
        print("Step 4: Select Response Time".center(terminal_width))
        print()
        times = [1.0, 1.5, 2.0, 2.5, 3.0]
        for i, t in enumerate(times, 1):
            print(f"{i} - {t:.1f}s".center(terminal_width))
        while True:
            char = self.wait_for_key()
            if char in '12345':
                self.display_time = times[int(char) - 1]
                break

    def run_game(self):
        """Run a single game session."""
        self.clear_screen()
        terminal_width = os.get_terminal_size().columns
        
        print("\n" * 2)
        
        # Configuration summary
        print("GAME READY".center(terminal_width))
        print()
        print(f"N-Back Level: {self.n}".center(terminal_width))
        print(f"Grid Size: {self.grid_size}x{self.grid_size}".center(terminal_width))
        print(f"Trials: {self.trials}".center(terminal_width))
        print(f"Response Time: {self.display_time:.1f}s".center(terminal_width))
        print()
        print(f"First, memorize {self.n} position/color pairs".center(terminal_width))
        print("Then respond to matches in the game".center(terminal_width))
        
        print(f"\n{'Press any key to begin training...'.center(terminal_width)}")
        self.wait_for_key()

        # Reset game state
        self.sequence = []
        self.color_sequence = []
        self.score = 0
        self.total_matches = 0
        self.current_trial = 0
        self.is_running = True

        # Memory phase - show first n position/color pairs
        for i in range(self.n):
            position = self.generate_position()
            color = self.generate_color()
            self.sequence.append(position)
            self.color_sequence.append(color)
            self.display_grid(position, color)
            print(f"\nMemorize item {i+1} of {self.n}")
            time.sleep(self.display_time)

        print("\nMemory phase complete! Game starting...")
        time.sleep(1)

        for trial in range(self.trials):
            self.current_trial = trial + 1
            position = self.generate_position()
            color = self.generate_color()
            self.sequence.append(position)
            self.color_sequence.append(color)
            
            self.display_grid(position, color, self.current_trial)
            
            if len(self.sequence) > self.n:
                is_visual_match = (position == self.sequence[-(self.n+1)])
                is_color_match = (color == self.color_sequence[-(self.n+1)])

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
                        elif char in 'al ':  # Added space for spacebar
                            if char == ' ':  # Spacebar = both
                                response = 'both'
                            elif char in 'al':
                                response = char
                            break
                
                if not self.is_running:
                    break
                
                print()  # Add newline before feedback
                
                if response is None:
                    print("Time's up!")
                else:
                    correct = False
                    if response == 'l' and is_visual_match:
                        self.score += 1
                        correct = True
                    elif response == 'a' and is_color_match:
                        self.score += 1
                        correct = True
                    elif response == 'both' and is_visual_match and is_color_match:
                        self.score += 2
                        correct = True
                    print("Correct!" if correct else "Incorrect!")
                
                time.sleep(0.5)  # Brief pause to show feedback

        # Game over screen with results
        self.clear_screen()
        terminal_width = os.get_terminal_size().columns
        
        print("\n" * 2)
        print("TRAINING COMPLETE".center(terminal_width))
        print()
        if self.total_matches > 0:
            accuracy = (self.score/self.total_matches)*100
            print(f"Final Score: {self.score} / {self.total_matches}".center(terminal_width))
            print(f"Accuracy: {accuracy:.1f}%".center(terminal_width))
            self.save_high_score()
        else:
            print("No scoring opportunities yet".center(terminal_width))
        
        print(f"\n{'Press any key to return to menu...'.center(terminal_width)}")
        self.wait_for_key()

    def play(self):
        """Main game loop."""
        while True:
            if self.show_menu():
                self.run_game()
            else:
                sys.exit(0)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Dual N-Back Trainer - Professional cognitive enhancement training",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('-n', '--n-value', type=int, choices=range(1, 9), default=None,
                      help='Set the N value (1-8, default: 2)')
    parser.add_argument('-g', '--grid-size', type=int, choices=range(3, 10), default=None,
                      help='Set the grid size (3-9, default: 8)')
    parser.add_argument('-t', '--trials', type=int, choices=[20, 30, 40, 50, 60, 80], default=None,
                      help='Set number of trials (default: 20)')
    parser.add_argument('-d', '--display-time', type=float, default=2.0,
                      help='Set display time in seconds (default: 2.0)')
    
    return parser.parse_args()

def main():
    """Main entry point for the game."""
    args = parse_args()
    
    # Check if any game parameters were provided via command line
    game_args_provided = any([
        args.n_value is not None,
        args.grid_size is not None, 
        args.trials is not None,
        args.display_time != 2.0  # Check if display_time was changed from default
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

if __name__ == "__main__":
    main() 