"""Main Menu Implementation."""


import constants
from .menu import Menu, MenuItem, CLIMenu
from .level import LevelMenu
from enum import Enum, unique


class MainMenu(CLIMenu):

    """The main menu."""

    @unique
    class Items(Enum):
        START_GAME = 1
        QUIT = 2

    def __init__(self, mgr):
        """Initialize the class."""
        buf = [
            ('-' * 60, None, None),
            ('', None, None),
            ('Welcome to {}'.format(constants.GAMENAME), None, None),
            ('', None, None),
            ('-' * 60, None, None),
            ('', None, None),
            ('$ ls', None, None),
            ('  start', MainMenu.Items.START_GAME, '$ start'),
            ('  exit', MainMenu.Items.QUIT, '$ exit')
        ]
        super().__init__(mgr, buf)

    def _on_choose(self, item):
        if item == MainMenu.Items.START_GAME:
            self._mgr.push(LevelMenu(self._mgr))
        elif item == MainMenu.Items.QUIT:
            # The main menu should be the last gamestate on the stack, so
            # popping it should cause the game to exit.
            self._mgr.pop()
