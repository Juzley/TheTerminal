"""Classes for programs that run on the terminal."""


import pygame
import random
from util import MouseButton


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

    def on_abort(self):
        """Handle a ctrl+c from user."""
        pass

    def exited(self):
        """Whether the current instance of the program has exited."""
        return False

    def completed(self):
        """Whether the task associated with this program has been completed."""
        return False


class PasswordGuess(TerminalProgram):

    """Class for a password-guessing program."""

    _PROMPT = 'Enter password: '

    _MAX_GUESSES = 5

    # TODO: Some more complicated matching of user to passwords, e.g. only have
    # certain characters available in the manual - need to make sure there's
    # no ambiguity though.
    _PASSWORDS = {
        'root':  ['flask', 'great', 'asked', 'tarts', 'force', 'gleam', 'think',
                  'brick', 'flute', 'brisk', 'freak', 'blast', 'feast', 'flick',
                  'flank'],
        'ro0t': ['tusks', 'blush', 'askew', 'train', 'asset', 'burns', 'tries',
                 'turns', 'basks', 'busks'],
        'rewt': ['maple', 'pearl', 'lapel', 'myths', 'cycle', 'apple', 'ladle',
                 'ample', 'maize', 'capel']
    }

    def __init__(self, terminal):
        """Initialize the class."""
        self._guesses = 0
        self._guessed = False
        self._aborted = False

        # Pick a user
        self._user = random.choice(list(PasswordGuess._PASSWORDS.keys()))
        self._password = random.choice(PasswordGuess._PASSWORDS[self._user])

        super().__init__(terminal)

    @property
    def help(self):
        """Return the help string for the program."""
        return "Run main login program."

    @property
    def security_type(self):
        """Return the security type for the program."""
        return "password protection"

    def _get_prompt(self):
        """Get the prompt string."""
        return "Enter password for user '{}' ({} attempts remaining)".format(
            self._user,
            PasswordGuess._MAX_GUESSES - self._guesses)

    def start(self):
        """Start the program."""
        # Don't reset guesses if we are restarting after an abort
        if self._aborted:
            self._aborted = False
        else:
            self._guesses = 0

            # Pick a new password for the current user.
            self._password = random.choice(PasswordGuess._PASSWORDS[self._user])

        self._terminal.output([self._get_prompt()])

    def text_input(self, line):
        """Check a password guess."""
        correct = 0
        for c in zip(line, self._password):
            if c[0] == c[1]:
                correct += 1

        if correct == len(self._password):
            self._terminal.output(['Password accepted'])
            self._guessed = True
        else:
            self._guesses += 1

            if self._guesses == PasswordGuess._MAX_GUESSES:
                self._terminal.output([
                    'Max retries reached - password reset!'])
            else:
                self._terminal.output([
                    'Incorrect password. {} of {} characters correct'.format(
                        correct, len(self._password)),
                    self._get_prompt()])

    def on_abort(self):
        """Handle a ctrl+c from user."""
        self._aborted = True

    def completed(self):
        """Indicate whether the user has guessed the password."""
        return self._guessed

    def exited(self):
        """Indicate whether the current instance has exited."""
        return self.completed() or self._guesses == PasswordGuess._MAX_GUESSES


class TestGraphical(TerminalProgram):

    """Program to test the graphical program handling."""

    # Chip code used to indicate no chip.
    _NO_CHIP = 255

    def __init__(self, terminal):
        """Initialize the class."""
        super().__init__(terminal)

        self._mask_surface = pygame.Surface((600, 450))
        self._mask_surface.fill((255, 255, 255))
        self._mask_surface.fill((0, 0, 0), pygame.Rect(100, 100, 180, 120))
        self._clicked = False

    @classmethod
    def is_graphical(cls):
        """Indicate that this is a graphical program."""
        return True

    @property
    def help(self):
        return "Inspect hardware."

    @property
    def security_type(self):
        return "hardware security"

    def _get_chip_code(self, pos):
        # Translate the click position to coordinates relative to the mask.
        translated_pos = (pos[0] - 100, pos[1] - 75)

        # The chip code is encoded in the R value of the mask.
        try:
            colour = self._mask_surface.get_at(translated_pos)
        except IndexError:
            # IndexError is raised if the position is outside the surface -
            # return a 0 to indicate no chip was clicked,
            return TestGraphical._NO_CHIP

        return colour.r

    def draw(self):
        """Draw the program."""
        screen = pygame.display.get_surface()
        screen.blit(self._mask_surface, (100, 75))

    def on_mouseclick(self, button, pos):
        """Detect whether the user clicked the program."""
        if (button == MouseButton.LEFT and
                self._get_chip_code(pos) != TestGraphical._NO_CHIP):
            self._clicked = True
            self._terminal.output(["SYSTEM ALERT: Hardware security module "
                                   "disabled."])

    def completed(self):
        """Indicate whether the program was completed."""
        return self._clicked

    def exited(self):
        """Indicate whether the program has exited."""
        return self._clicked

