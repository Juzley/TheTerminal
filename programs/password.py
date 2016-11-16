"""Password program classes."""

import random
from . import program


class PasswordGuess(program.TerminalProgram):

    """Class for a password-guessing program."""

    _MAX_GUESSES = 5
    _PASSWORDS = {
        'root':  ['flask', 'great', 'asked', 'tarts', 'force', 'gleam', 'think',
                  'brick', 'flute', 'brisk', 'freak', 'blast', 'feast', 'flick',
                  'flank'],
        'ro0t': ['tusks', 'blush', 'askew', 'train', 'asset', 'burns', 'tries',
                 'turns', 'basks', 'busks'],
        'rewt': ['maple', 'pearl', 'lapel', 'myths', 'cycle', 'apple', 'ladle',
                 'ample', 'maize', 'capel'],
        '00142331': ['trice', 'racer', 'tours', 'glaze', 'trail', 'raise',
                     'slick', 'track', 'grace', 'trace'],
        '00143231': ['court', 'truce', 'fords', 'flirt', 'cruel', 'craft',
                     'tours', 'chart', 'fours', 'count'],
        '01043231': ['eagle', 'ariel', 'glare', 'gains', 'earns', 'gauge',
                     'angle', 'early', 'agile', 'engle']
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
