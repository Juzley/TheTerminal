"""Implementation of the core gameplay."""


import pygame
import timer
from terminal import Terminal
from program import PasswordGuess
import mainmenu


class LostState:

    """Gamestate implementation for the defeat screen."""

    _WAIT_TIME = 2000

    def __init__(self, mgr):
        """Initialize the class."""
        self._mgr = mgr
        self._timer = timer.Timer()

    def draw(self):
        """Draw the losing screen."""
        # TODO: make this look like the terminal
        font = pygame.font.Font(None, 30)
        text = font.render('You have been locked out', True, (255, 255, 255))
        pygame.display.get_surface().blit(text, (0, 0))

        if self._timer.time >= LostState._WAIT_TIME:
            text = font.render('Press any key to continue...', True,
                               (255, 255, 255))
            pygame.display.get_surface().blit(text, (0, 30))

    def run(self, events):
        """Run the lost-game screen."""
        self._timer.update()
        if self._timer.time >= LostState._WAIT_TIME:
            if len([e for e in events if e.type == pygame.KEYDOWN]) > 0:
                # Return to the main menu.
                self._mgr.pop_until(mainmenu.MainMenuState)


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

        self._terminal.run()

        # The player is locked out, switch to the Lost gamestate.
        if self._terminal.locked:
            # Push so that we can restart the game if required by just popping
            # again.
            self._mgr.push(LostState(self._mgr))

    def draw(self):
        """Draw the game."""
        self._terminal.draw()
