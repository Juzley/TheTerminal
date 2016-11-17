import pygame
import random

from . import program


class MineHunt(program.TerminalProgram):

    """Minehunt program."""

    """The properties of this program."""
    PROPERTIES = program.ProgramProperties(is_graphical=True,
                                           suppress_success=True)

    def __init__(self, terminal):
        """Initialize the class."""
        super().__init__(terminal)

        self._completed = False
        self._exited = False

    @property
    def help(self):
        """Get the help string for the program."""
        return "Play minehunt!"

    @property
    def security_type(self):
        """Get the security type for the program."""
        return "user permissions"

    @property
    def success_syslog(self):
        return "{} user has been promoted to admin".format(
            self.SUCCESS_PREFIX)

    def start(self):
        # Reset board
        self._exited = False

    def completed(self):
        """Indicate whether the program was completed."""
        return self._completed

    def exited(self):
        """Indicate whether the program has exited."""
        return self.completed() or self._exited

    def on_keypress(self, key, key_unicode):
        """Handle a user keypress."""
        pass

    def on_mousemove(self, pos):
        pass

    def on_mouseclick(self, button, pos):
        """Detect whether the user clicked the program."""
        pass

    def draw(self):
        """Draw the program."""
        pass
