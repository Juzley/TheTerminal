"""Classes for programs that run on the terminal."""


class TerminalProgram:

    """Base class for terminal programs."""

    def __init__(self, terminal):
        """Initialize the class."""
        self._terminal = terminal

    @classmethod
    def is_graphical(cls):
        """Indicate whether the program is graphical or not."""
        return False

    def draw(self):
        """Draw the program, if it is graphical."""
        pass

    def start(self):
        """Called when the program is started, or restarted."""
        pass

    def input(self, line):
        """Handle a line of input from the terminal."""
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

    def __init__(self, terminal):
        """Initialize the class."""
        self._guesses = 0
        self._maxguesses = 5
        self._guessed = False
        self._password = 'Test'

        super().__init__(terminal)

    def start(self):
        """Start the program."""
        self._guesses = 0
        self._terminal.output([PasswordGuess._PROMPT])

    def input(self, line):
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
            if self._guesses == self._maxguesses:
                # TODO: Pick another password, reduce the timer.
                pass
            else:
                self._terminal.output(
                    ['Login failed. {} of {}'.format(
                        correct, len(self._password)),
                     PasswordGuess._PROMPT])

    def completed(self):
        """Indicate whether the user has guessed the password."""
        return self._guessed

    def exited(self):
        """Indicate whether the current instance has exited."""
        return self.completed() or self._guesses == self._maxguesses
