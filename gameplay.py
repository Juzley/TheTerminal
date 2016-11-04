"""Implementation of the core gameplay."""


import pygame
from terminal import Terminal
from program import PasswordGuess


class GameplayState:

    """Gamestate implementation for the core gameplay."""

    def __init__(self, mgr):
        """Initialize the class."""
        self._terminal = Terminal(programs={'login': PasswordGuess})
        self._mgr = mgr

    def run(self, events):
        """Run the game."""
        for e in events:
            if e.type == pygame.KEYDOWN:
                self._terminal.input(e.key, e.unicode)

    def draw(self):
        """Draw the game."""
        self._terminal.draw()
