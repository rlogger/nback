"""
Dual N-Back Trainer

A command-line implementation of the dual N-Back working memory task.
Players must track both visual positions and colors from N steps back in sequences.
"""

__version__ = "1.0.0"
__author__ = "N-Back Trainer Team"
__license__ = "MIT"

from .nback import NBackGame, main

__all__ = ["NBackGame", "main"]
