"""Decryption program classes."""


import random
import string
from media import load_font
from . import program


class Decrypt(program.TerminalProgram):

    """Program class for the decryption puzzle."""

    # For each font, we have a dictionary mapping from the character in the font
    # to what the correct decryption is.
    _FONTS = [
        ('media/fonts/Arrows.ttf',
         {'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd', 'e': 'e', 'f': 'f', 'g': 'g',
          'h': 'h', 'i': 'A', 'j': 'B', 'k': 'C', 'l': 'D', 'm': 'E', 'n': 'F',
          'o': 'G', 'p': 'H', 'q': 'y', 'r': 'z', 's': 'Y', 't': 'Z', 'u': 'm',
          'v': 'n', 'w': 'Q', 'x': 'R', 'y': 'S', 'z': 'y'}),
        ('media/fonts/Gobotronic.otf',
         {'a': 'n', 'b': 'o', 'c': 'p', 'd': 'q', 'e': 'r', 'f': 's', 'g': 't',
          'h': 'u', 'i': 'v', 'j': 'w', 'k': 'x', 'l': 'y', 'm': 'z', 'n': 'N',
          'o': 'O', 'p': 'P', 'q': 'Q', 'r': 'R', 's': 'S', 't': 'T', 'u': 'U',
          'v': 'V', 'w': 'W', 'x': 'X', 'y': 'Y', 'z': 'Z'}),
        ('media/fonts/PigpenCipher.otf',
         {'a': 'n', 'b': 'z', 'c': 'q', 'd': 'o', 'e': 'e', 'f': 'g', 'g': 'm',
          'h': 'u', 'i': 'v', 'j': 'p', 'k': 'x', 'l': 'k', 'm': 'f', 'n': 'b',
          'o': 'y', 'p': 'i', 'q': 'l', 'r': 'r', 's': 'c', 't': 't', 'u': 'w',
          'v': 'h', 'w': 'd', 'x': 's', 'y': 'a', 'z': 'j'}),
        ('media/fonts/MageScript.otf', {c: c for c in string.ascii_lowercase}),
     ]

    _TEXT_SIZE = 40
    _MIN_LENGTH = 4
    _MAX_LENGTH = 12
    _FREEZE_TIME = 2 * 1000

    def __init__(self, terminal):
        """Initialize the class."""
        super().__init__(terminal)
        self._correct = False

        self._fontname = ""
        self._cyper = None

        self._enc_string = ""
        self._dec_string = ""

    def start(self):
        """Start the program."""
        self._fontname, self._cypher = random.choice(Decrypt._FONTS)
        load_font(self._fontname, Decrypt._TEXT_SIZE)
        self._dec_string = ''.join(
            [random.choice(list(self._cypher.keys())) for _ in
             range(random.randrange(Decrypt._MIN_LENGTH,
                                    Decrypt._MAX_LENGTH + 1))])
        self._enc_string = ''.join([self._cypher[e] for e in self._dec_string])
        self._terminal.output(['<s {}><f {}>{}'.format(
            Decrypt._TEXT_SIZE, self._fontname, self._enc_string)])

    @property
    def help(self):
        """Return the help string."""
        return "Decrypt filesystem."

    @property
    def security_type(self):
        """Return the security type."""
        return "filesystem encryption."

    @property
    def prompt(self):
        """Return the prompt."""
        return "Enter decryption key: "

    def exited(self):
        """Indicate whether the program has exited."""
        return self._correct

    def completed(self):
        """Indicate whether the task was completed."""
        return self._correct

    def text_input(self, line):
        """Check whether the correct password was entered."""
        if line == self._dec_string:
            self._correct = True
        else:
            self._terminal.output([self.failure_prefix +
                                   "decryption failed, reversing!"])
            self._terminal.freeze(Decrypt._FREEZE_TIME)
