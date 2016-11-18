"""Main Menu Implementation."""


import constants
from .menu import CLIMenu, CLIMenuItem
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
            '-' * 60,
            '',
            'Welcome to {}'.format(constants.GAMENAME),
            '',
            '-' * 60,
            '',
            '$ ls',
            CLIMenuItem('  start', '$ start', MainMenu.Items.START_GAME),
            CLIMenuItem('  exit', '$ exit', MainMenu.Items.QUIT)
        ]
        super().__init__(mgr, buf)

    def _on_choose(self, item):
        if item == MainMenu.Items.START_GAME:
            self._mgr.push(LevelMenu(self._mgr))
        elif item == MainMenu.Items.QUIT:
            # The main menu should be the last gamestate on the stack, so
            # popping it should cause the game to exit.
            self._mgr.pop()
