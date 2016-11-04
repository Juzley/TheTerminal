"""Classes for programs that run on the terminal."""


class TerminalProgram:
    def __init__(self, terminal):
        """Initialize the class."""
        self._terminal = terminal

    def start(self):
        """Called when the program is started."""
        pass

    def input(self, line):
        """Handle a line of input from the terminal."""
        pass

    def finished(self):
        """Indicate whether the program has finished."""
        return False


class PasswordGuess(TerminalProgram):
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
                # TODO: Pick another password, have a 'strike'.
                pass
            else:
                self._terminal.output(
                    ['Login failed. {} of {}'.format(
                        correct, len(self._password)),
                     PasswordGuess._PROMPT])

    def finished(self):
        return self._guessed or self._guesses == self._maxguesses
