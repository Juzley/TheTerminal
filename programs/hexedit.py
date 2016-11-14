"""Hexeditor program classes."""

import random
from enum import Enum, unique
from . import program


class HexEditor(program.TerminalProgram):

    """Program class for the hex-editor puzzle."""

    @unique
    class States(Enum):
        QUERY_ROW = 0
        ENTER_COL = 1
        ENTER_VAL = 2
        FINISHED = 3

    _ALLOWED_LINES = [
        [0x1, 0x2, 0x3, 0x4, 0x5, 0x6],
        [0xa, 0xb, 0xc, 0xd, 0xe, 0xf],
        [0x1, 0xf, 0x2, 0xe, 0x3, 0xd],
        [0xf, 0x1, 0xe, 0x2, 0xd, 0x3],
        [0xb, 0xe, 0xe, 0xf, 0xe, 0xd],
        [0xd, 0xe, 0xa, 0xd, 0x0, 0x0],
        [0x5, 0x4, 0x3, 0x6, 0x7, 0x0],
        [0x9, 0x8, 0x8, 0x7, 0x4, 0x2],
        [0x2, 0x1, 0x9, 0x8, 0x1, 0x2],
        [0x8, 0x9, 0x7, 0x6, 0x2, 0x0]
    ]

    _MIN_FILE_LENGTH = 3
    _MAX_FILE_LENGTH = 5

    # The chance that a line will be randomly-generated, not picked from the
    # set of allowed lines.
    _RAND_LINE_CHANCE = 0.25

    _ROW_PROMPT = 'Edit line {}? (y/n)'
    _COL_PROMPT = 'Edit col num: '
    _VAL_PROMPT = 'Change {:#04x} to (leave empty to cancel): '

    # How long is the freeze time (in ms) when a mistake is made
    _FREEZE_TIME = 5 * 1000

    def __init__(self, terminal):
        """Initialize the class."""
        super().__init__(terminal)
        self._completed = False
        self._row = 0
        self._col = 0
        self._state = HexEditor.States.QUERY_ROW
        self._data = []

    @property
    def help(self):
        """Return the help string."""
        return "Modify raw software data."

    @property
    def security_type(self):
        """Return the security type."""
        return "software lock"

    @property
    def prompt(self):
        """Return the prompt based on the current state."""
        if self._state == HexEditor.States.QUERY_ROW:
            return HexEditor._ROW_PROMPT.format(self._row)
        elif self._state == HexEditor.States.ENTER_COL:
            return HexEditor._COL_PROMPT
        elif self._state == HexEditor.States.ENTER_VAL:
            return HexEditor._VAL_PROMPT.format(
                self._data[self._row][0][self._col])

    def start(self):
        """Start the program."""
        self._row = 0
        self._col = 0
        self._state = HexEditor.States.QUERY_ROW
        self._generate_data()
        self._output_data()

    def completed(self):
        """Indicate whether the user has guessed the password."""
        return self._completed

    def exited(self):
        """Indicate whether the current instance has exited."""
        return self._state == HexEditor.States.FINISHED

    def text_input(self, line):
        """Handle editor commands."""
        # Remove any leading whitespace and convert to lowercase.
        line = line.lstrip().lower()

        if self._state == HexEditor.States.QUERY_ROW:
            if line.startswith('y'):
                self._state = HexEditor.States.ENTER_COL
            else:
                self._row += 1
        elif self._state == HexEditor.States.ENTER_COL:
            try:
                self._col = int(line)
            except ValueError:
                raise program.BadInput('Not a number')

            if self._col < 0 or self._col >= len(self._data[0][0]):
                raise program.BadInput('Column out of range')

            self._state = HexEditor.States.ENTER_VAL
        elif self._state == HexEditor.States.ENTER_VAL:
            # If the user has cancelled, go back to the row query.
            if not line:
                self._state = HexEditor.States.QUERY_ROW
            else:
                try:
                    self._data[self._row][0][self._col] = int(line, 16)
                except ValueError:
                    raise program.BadInput('Not a number')

                # Set the 'expected match' value for the row to True, so that we
                # catch the situation where the player has modified a row that
                # didn't match any of the rows in the manual.
                self._data[self._row][1] = True
                self._row += 1
                self._state = HexEditor.States.QUERY_ROW

        # Check if we've reached the end of the file, and if so see if the edits
        # were correct.
        self._check_finished()

    def _check_finished(self):
        """Determine if edits are finished, and whether they were successful."""
        if self._row == len(self._data):
            self._state = HexEditor.States.FINISHED
            if self._data_correct():
                self._completed = True
            else:
                self._terminal.output([self.failure_prefix +
                                       "corruption detected "
                                       "in system file, repairing!"])
                self._terminal.freeze(HexEditor._FREEZE_TIME)

    @staticmethod
    def _check_line(line):
        for allowed in HexEditor._ALLOWED_LINES:
            if line == allowed:
                return True

    @staticmethod
    def _generate_matching_line():
        line = list(random.choice(HexEditor._ALLOWED_LINES))

        # Peturb one of the entries.
        line[random.randrange(len(line))] = random.randrange(0x10)

        return line

    @staticmethod
    def _generate_random_line():
        return [random.randrange(0x10) for _ in range(6)]

    @staticmethod
    def _expect_match(line):
        for allowed in HexEditor._ALLOWED_LINES:

            matched = 0
            for pair in zip(line, allowed):
                if pair[0] == pair[1]:
                    matched += 1

            if matched >= len(allowed) - 1:
                return True

        return False

    def _generate_data(self):
        """Generate the data for the puzzle."""
        # The data is represented as an array of two-element tuples, where the
        # first element is a tuple containing the data, and the second element
        # is a bool indicating whether we are expecting the line to match an
        # allowed value.
        for _ in range(random.randrange(HexEditor._MIN_FILE_LENGTH,
                                        HexEditor._MAX_FILE_LENGTH)):
            if random.random() < HexEditor._RAND_LINE_CHANCE:
                data = self._generate_random_line()
                # It's possible that we randomly generate a matching line,
                # so check whether this is the case.
                entry = [data, HexEditor._expect_match(data)]
            else:
                entry = [self._generate_matching_line(), True]

            self._data.append(entry)

    def _output_data(self):
        """Output the data on the screen."""
        col_count = len(self._data[0][0])
        self._terminal.output([""] +
                              [" " * 2 + " | " +
                               "  ".join("{:4}".format(i)
                                         for i in range(col_count))] +
                              ["-" * (5 + 6 * col_count)])
        self._terminal.output(
            ["{:2} | ".format(idx) + "  ".join(
                "{:#04x}".format(c) for c in row[0])
             for idx, row in enumerate(self._data)] + [""])

    def _data_correct(self):
        """Determine if the edits made to the data were correct."""
        # Search for lines in the data which we are expecting to match an
        # allowed line, but don't.
        return len([l for l in self._data if l[1] and l[0] not in
                    HexEditor._ALLOWED_LINES]) == 0

    def _validate_filename(self, filename):
        # TODO: come up with clues for what the filename should be and vary it.
        # Could potentially have different sets of hex files for different
        # filenames?
        return filename == "login.dll"
