"""Level select menu."""


import json
import programs
from . import menu
from enum import Enum, unique
from gameplay import GameplayState


class LevelMenu(menu.CLIMenu):

    """The level select menu."""

    @unique
    class Items(Enum):
        BACK = 1

    _LEVELS_FILE = 'levels.json'

    def __init__(self, mgr):
        """Initialize the class."""
        # Load levels from the level file.
        with open(LevelMenu._LEVELS_FILE) as f:
            self._levels = json.load(f)

            # The program class names are represented in the JSON as strings,
            # we need to convert them to the corresponding class objects.
            for level_info in self._levels.values():
                for cmd, cls_str in level_info['programs'].items():
                    level_info['programs'][cmd] = getattr(programs, cls_str)

        buf = [
            ('$ cd levels', None, None),
            ('$ ls', None, None),
            ('  ..', LevelMenu.Items.BACK, '$ cd ..')
        ]

        # Add each level as a menu item - we create a list of the levle names,
        # so that we can use an index into this list as the menu item id.
        # For now sort the level names alphabetically, assuming that this will
        # give a good ordering in the menu.
        self._level_names = sorted(self._levels.keys())
        buf.extend([('  ' + name, idx, '$ connect {}'.format(name)) for
                    idx, name in enumerate(self._level_names)])

        super().__init__(mgr, buf)

    def _on_choose(self, item):
        if item == LevelMenu.Items.BACK:
            # Return to the main menu.
            self._mgr.pop()
        else:
            # If this isn't an item from enum of items, assume that the user
            # clicked on a level - in this case 'item' contains the index of
            # the level name in the list of names, whch we can use to look up
            # the level info.
            level_info = self._levels[self._level_names[item]]
            self._mgr.replace(GameplayState(self._mgr, level_info))
