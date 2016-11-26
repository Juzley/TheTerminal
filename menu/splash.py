"""Splash screen with manual information."""

import webbrowser
from enum import Enum, unique
import constants
import timer
from .menu import CLIMenu, CLIMenuItem
from .mainmenu import MainMenu


class SplashScreen(CLIMenu):

    """The splash screen."""

    @unique
    class Items(Enum):
        LAUNCH_MANUAL = 1

    _WAIT_TIME = 1000

    def __init__(self, mgr):
        """Initialize the class."""
        self._timer = timer.Timer()

        buf = [
            '-' * 60,
            '',
            'Welcome to {}'.format(constants.GAMENAME),
            '',
            'Please read this important notice before you begin',
            '',
            '-' * 60,
            '',
            'This is a cooperative local multiplayer game and must be played',
            "with reference to the manual, which can be found in the game's",
            'docs directory, or at: ',
            '',
            CLIMenuItem('{} (click to view)'.format(constants.MANUAL_URL),
                        '',
                        SplashScreen.Items.LAUNCH_MANUAL),
            '',
            'Please ensure you have the correct version of the manual to match',
            'your game; this is {} of the game.'.format(
                constants.VERSION_STRING),
            '',
            'Press any key to continue...'
        ]
        super().__init__(mgr, buf)

    def run(self, events):
        """Handle events."""
        self._timer.update()
        super().run(events)

    @staticmethod
    def _highlight_selection():
        """Don't highlight the URL button."""
        return False

    def _on_keypress(self, event):
        if self._timer.time >= SplashScreen._WAIT_TIME:
            self._mgr.replace(MainMenu(self._mgr))

    def _on_mouseclick(self, event):
        item = self._hit_item(event.pos)
        if item is None:
            if self._timer.time >= SplashScreen._WAIT_TIME:
                self._mgr.replace(MainMenu(self._mgr))
        else:
            super()._on_mouseclick(event)

    def _on_choose(self, item):
        if item == SplashScreen.Items.LAUNCH_MANUAL:
            webbrowser.open(constants.MANUAL_URL)
