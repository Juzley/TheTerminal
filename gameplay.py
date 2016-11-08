"""Implementation of the core gameplay."""


import pygame
import timer
import util
from terminal import Terminal
from gamestate import GameState
from program import PasswordGuess, TestGraphical, HexEditor
import mainmenu


class SuccessState(GameState):

    """Gamestate implementation for the success screen."""

    _WAIT_TIME = 2000

    def __init__(self, mgr):
        """Initialize the class."""
        self._mgr = mgr
        self._timer = timer.Timer()

    def draw(self):
        """Draw the losing screen."""
        # TODO: make this look like the terminal
        font = pygame.font.Font(None, 30)
        text = font.render('You have gained access', True, (255, 255, 255))
        pygame.display.get_surface().blit(text, (0, 0))

        if self._timer.time >= SuccessState._WAIT_TIME:
            text = font.render('Press any key to continue...', True,
                               (255, 255, 255))
            pygame.display.get_surface().blit(text, (0, 30))

    def run(self, events):
        """Run the lost-game screen."""
        self._timer.update()
        if self._timer.time >= SuccessState._WAIT_TIME:
            if len([e for e in events if e.type == pygame.KEYDOWN]) > 0:
                # Return to the main menu.
                self._mgr.pop_until(mainmenu.MainMenu)


class LostState(GameState):

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
                self._mgr.pop_until(mainmenu.MainMenu)


class GameplayState(GameState):

    """Gamestate implementation for the core gameplay."""

    def __init__(self, mgr):
        """Initialize the class."""
        self._terminal = Terminal(programs={
            'login': PasswordGuess,
            'gfx': TestGraphical,
            'hexedit': HexEditor})
        self._mgr = mgr

    def run(self, events):
        """Run the game."""
        for e in events:
            if e.type == pygame.KEYDOWN:
                self._terminal.on_keypress(e.key, e.unicode)
            elif e.type == pygame.MOUSEBUTTONDOWN:
                self._terminal.on_mouseclick(e.button, e.pos)
            elif e.type == pygame.ACTIVEEVENT:
                self._terminal.on_active_event(util.ActiveEvent(e.state,
                                                                e.gain))

        self._terminal.run()

        # The player is locked out, switch to the Lost gamestate.
        if self._terminal.locked:
            # Push so that we can restart the game if required by just popping
            # again.
            self._mgr.push(LostState(self._mgr))

        # The player has succeeded, switch to the success gamestate.
        if self._terminal.completed():
            # Don't need to return to the game, so replace this gamestate with
            # the success screen.
            self._mgr.replace(SuccessState(self._mgr))

    def draw(self):
        """Draw the game."""
        self._terminal.draw()
