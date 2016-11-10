"""Base class definitions for use by programs."""


class BadInput(Exception):

    """Exception raised by a program receiving bad input."""

    pass


class TerminalProgram:

    """Base class for terminal programs."""

    def __init__(self, terminal):
        """Initialize the class."""
        self._terminal = terminal

    @classmethod
    def is_graphical(cls):
        """Indicate whether the program is graphical or not."""
        return False

    @property
    def prompt(self):
        """Return the prompt for this program. None if it doesn't have one."""
        return None

    @property
    def help(self):
        """Return help string for this program."""
        return "<empty>"

    @property
    def security_type(self):
        """Return string indicating what security this program can bypass."""
        return "<empty>"

    def draw(self):
        """Draw the program, if it is graphical."""
        pass

    def start(self):
        """Called when the program is started, or restarted."""
        pass

    def text_input(self, line):
        """
        Handle a line of input from the terminal.

        Raises BadInput error on bad input.

        """
        pass

    def on_mouseclick(self, button, pos):
        """Handle a mouse click from the user."""
        pass

    def on_mousemove(self, pos):
        """Handle a mouse move from the user."""
        pass

    def on_abort(self):
        """Handle a ctrl+c from user."""
        pass

    def exited(self):
        """Whether the current instance of the program has exited."""
        return False

    def completed(self):
        """Whether the task associated with this program has been completed."""
        return False