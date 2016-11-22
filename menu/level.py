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
    _PROGRESS_FILE = 'progress.json'

    def __init__(self, mgr):
        """Initialize the class."""
        # Load levels from the level file.
        with open(LevelMenu._LEVELS_FILE) as f:
            self._levels = json.load(f)

            # The program class names are represented in the JSON as strings,
            # we need to convert them to the corresponding class objects.
            for level in self._levels:
                for group in level['program_groups'].values():
                    for program_info in group['programs']:
                        program_info[1] = getattr(programs, program_info[1])

        # Load progress information.
        progress = LevelMenu._get_progress()
        completed = progress.get('completed', [])

        # Build the menu text
        buf = [
            '$ cd levels',
            '$ ls',
            menu.CLIMenuItem('   ..', '$ cd ..', LevelMenu.Items.BACK)
        ]

        # Add each level as a menu item
        for idx, lvl in enumerate(self._levels):
            # Work out whether this level is accessible.
            disabled = len([r for r in lvl.get('requires', [])
                            if r not in completed]) > 0

            item = menu.CLIMenuItem(text='   ' + lvl['name'],
                                    cmd='$ connect {}'.format(lvl['name']),
                                    item=idx,
                                    disabled=disabled)

            buf.append(item)

        # We want to start with the latest available level selected.
        enabled = [i for i in buf if not item.disabled]
        enabled[-1].selected = True

        super().__init__(mgr, buf)

    @staticmethod
    def _get_progress():
        """Load the current level progress from disk."""
        try:
            with open(LevelMenu._PROGRESS_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, ValueError):
            # The file may not be found if this is the first time the game is
            # played or the user hasn't completed any levels. Also ignore any
            # JSON parsing errors.
            return {}

    @staticmethod
    def completed_level(lvl_id):
        """Mark a level as completed."""
        progress = LevelMenu._get_progress()
        completed = progress.get('completed', [])
        if lvl_id not in completed:
            completed.append(lvl_id)
        progress['completed'] = completed

        with open(LevelMenu._PROGRESS_FILE, 'w') as f:
            json.dump(progress, f)

    def _on_choose(self, item):
        if item == LevelMenu.Items.BACK:
            # Return to the main menu.
            self._mgr.pop()
        else:
            # If this isn't an item from enum of items, assume that the user
            # clicked on a level - in this case 'item' contains the index of
            # the level in the level list.
            self._mgr.replace(GameplayState(self._mgr, self._levels[item]))
