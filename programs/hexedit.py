"""Hexeditor program classes."""

import random

from . import program


class HexFile:

    """Represents a HexEditor file."""

    COL_COUNT = 5

    def __init__(self, rows, row, col, val):
        """Initialize the class."""
        self.row = row
        self.col = col
        self.val = val
        self.rows = rows

    def validate(self, row, col, val):
        """Check whether the file has been correctly edited."""
        return row == self.row and col == self.col and val == self.val


#
# List of hexfiles
#
HEX_FILES = [
    HexFile(((0xa, 0xb, 0xb, 0xb, 0xb),
             (0xa, 0x2, 0x3, 0x4, 0x11),
             (0xa, 0x2, 0x3, 0x1, 0x12),
             (0xa, 0x2, 0x3, 0x4, 0x13),
             (0xa, 0x2, 0x3, 0x4, 0x14)),
            2, 3, 0),
    HexFile(((0xa, 0xb, 0xb, 0xb, 0xb),
             (0xa, 0x2, 0x3, 0x4, 0x11),
             (0xa, 0x2, 0x3, 0x4, 0x12),
             (0xa, 0x1, 0x3, 0x4, 0x13),
             (0xa, 0x2, 0x3, 0x4, 0x14),
             (0xa, 0x2, 0x3, 0x4, 0x14)),
            3, 1, 0),
]


class HexEditor(program.TerminalProgram):
    _FILE_PROMPT = 'Enter filename: '
    _ROW_PROMPT = 'Edit row num: '
    _COL_PROMPT = 'Edit col num: '
    _VAL_PROMPT = 'Change {:#04x} to (leave empty to cancel): '

    # How long is the freeze time (in ms) when a mistake is made
    _FREEZE_TIME = 5 * 1000

    def __init__(self, terminal):
        """Initialize the class."""
        self._guessed = False
        self._file = None
        self._row = None
        self._col = None
        self._filename = None

        super().__init__(terminal)

    @property
    def help(self):
        return "Modify raw software data."

    @property
    def security_type(self):
        return "software lock"

    @property
    def prompt(self):
        if self._file is None:
            return HexEditor._FILE_PROMPT
        elif self._row is None:
            return HexEditor._ROW_PROMPT
        elif self._col is None:
            return HexEditor._COL_PROMPT
        else:
            val = self._file.rows[self._row][self._col]
            return HexEditor._VAL_PROMPT.format(val)

    def start(self):
        """Start the program."""
        self._file = None
        self._row = None
        self._col = None

    def completed(self):
        """Indicate whether the user has guessed the password."""
        return self._guessed

    def exited(self):
        """Indicate whether the current instance has exited."""
        return self.completed()

    def text_input(self, line):
        if self._file is None:
            if not self._validate_filename(line):
                raise program.BadInput("Cannot find file '{}'".format(line))
            self._get_file(line)

        elif self._row is None:
            try:
                row = int(line)
            except:
                raise program.BadInput("Not a number")

            if 0 <= row < len(self._file.rows):
                self._row = row
            else:
                raise program.BadInput("Invalid row")

        elif self._col is None:
            try:
                col = int(line)
            except:
                raise program.BadInput("Not a number")

            if 0 <= col < HexFile.COL_COUNT:
                self._col = col
            else:
                raise program.BadInput("Invalid col")

        elif line:
            try:
                val = int(line)
            except:
                raise program.BadInput("Not a number")

            if self._file.validate(self._row, self._col, val):
                self._guessed = True
            else:
                self._terminal.output([self.failure_prefix +
                                       "corruption detected "
                                       "in file '{}', repairing!"
                                       .format(self._filename)])
                self._row = None
                self._col = None
                self._terminal.freeze(HexEditor._FREEZE_TIME)

        else:
            self._row = None
            self._col = None

    def _validate_filename(self, filename):
        # TODO: come up with clues for what the filename should be and vary it.
        # Could potentially have different sets of hex files for different
        # filenames?
        return filename == "login.dll"

    def _get_file(self, filename):
        self._terminal.output(['Loading {}...'.format(filename)])
        self._filename = filename

        # Select file at random
        self._file = random.choice(HEX_FILES)

        # Draw file
        self._terminal.output([""] +
                              [" " * 2 + " | " +
                               "  ".join("{:4}".format(i)
                                         for i in range(HexFile.COL_COUNT))] +
                              ["-" * (5 + 6 * HexFile.COL_COUNT)])
        self._terminal.output(
            ["{:2} | ".format(idx) + "  ".join("{:#04x}".format(c) for c in row)
             for idx, row in enumerate(self._file.rows)] + [""])
