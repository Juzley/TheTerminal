"""Base class definitions for use by programs."""


class BadInput(Exception):

    """Exception raised by a program receiving bad input."""

    pass


class ProgramProperties:

    """Class that indicates the program properties"""

    def __init__(self,
                 intercept_keypress=False,
                 alternate_buf=False,
                 hide_cursor=False,
                 suppress_success=False,
                 is_graphical=False,
                 skip_bezel=False):

        # If graphical, then set correct properties
        if is_graphical:
            intercept_keypress = True
            alternate_buf = False
            hide_cursor = True

        self.intercept_keypress = intercept_keypress
        self.alternate_buf = alternate_buf
        self.hide_cursor = hide_cursor
        self.suppress_success = suppress_success
        self.is_graphical = is_graphical
        self.skip_bezel = skip_bezel


class TerminalProgram:

    """Base class for terminal programs."""

    """The properties of this program."""
    PROPERTIES = ProgramProperties()

    SUCCESS_PREFIX = "SYSTEM INFO:"

    def __init__(self, terminal):
        """Initialize the class."""
        self._terminal = terminal

    @property
    def allow_ctrl_c(self):
        """Indicate whether ctrl-c is allowed to cancel the program."""
        return True

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

    @property
    def success_syslog(self):
        return "{} {} disabled.".format(self.SUCCESS_PREFIX, self.security_type)

    @property
    def failure_prefix(self):
        return "<c r>SYSTEM ALERT: "

    @property
    def buf(self):
        """Terminal buffer contents for this interactive program."""
        return []

    def draw(self):
        """Draw the program, if it is graphical."""
        pass

    def run(self):
        """Run any background program logic that isn't user input driven."""
        pass

    def start(self):
        """Called when the program is started, or restarted."""
        pass

    def text_input(self, line):
        """
        Handle a line of input from the terminal (Used for TERMINAL).

        Raises BadInput error on bad input.

        """
        pass

    def on_keypress(self, key, key_unicode):
        """Handle a user keypress (used for INTERACTIVE and GRAPHICAL)."""
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
