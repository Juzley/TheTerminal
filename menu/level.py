"""Level select menu."""


from enum import Enum, unique
from . import menu
from gameplay import GameplayState


class LevelMenu(menu.CLIMenu):

    """The level select menu."""

    @unique
    class Items(Enum):
        TEST = 1
        BACK = 2

    def __init__(self, mgr):
        """Initialize the class."""
        super().__init__(
            mgr,
            buf=[
                ("$ cd levels", None)
                ("$ ls", None),
                ("..", LevelMenu.Items.BACK),
                ("test.lvl", LevelMenu.Items.TEST)
            ])

    def _on_choose(self, item):
        if item == LevelMenu.Items.TEST:
            self._mgr.replace(GameplayState(self._mgr, 'test.lvl'))
        elif item == LevelMenu.Items.BACK:
            self._mgr.pop()
