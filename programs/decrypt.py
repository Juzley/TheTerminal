"""Decryption program classes."""


import random
import string
from media import load_font
from . import program


class Decrypt(program.TerminalProgram):
    # For each font, we have a dictionary mapping from the character in the font
    # to what the correct decryption is.
    _FONTS = [
        ('media/Arrows.ttf',
         {'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd', 'e': 'e', 'f': 'f', 'g': 'g',
          'h': 'h', 'A': 'i', 'B': 'j', 'C': 'k', 'D': 'l', 'E': 'm', 'F': 'n',
          'G': 'o', 'H': 'p', 'y': 'q', 'z': 'r', 'Y': 's', 'Z': 't', 'm': 'u',
          'n': 'v', 'Q': 'w', 'R': 'x', 'S': 'y', 'T': 'z'}),
        ('media/MageScript.otf', {c: c for c in string.ascii_lowercase}),
     ]

    _TEXT_SIZE = 40
    _MIN_LENGTH = 4
    _MAX_LENGTH = 12

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
        self._enc_string = ''.join(
            [random.choice(list(self._cypher.keys())) for _ in
             range(random.randrange(Decrypt._MIN_LENGTH,
                                    Decrypt._MAX_LENGTH + 1))])
        self._dec_string = ''.join([self._cypher[e] for e in self._enc_string])
        self._terminal.output(['<s {}><f {}>{}'.format(
            Decrypt._TEXT_SIZE, self._fontname, self._enc_string)])

    def exited(self):
        return self._correct

    def completed(self):
        return self._correct

    def text_input(self, line):
        if line == self._enc_string:
            self._correct = True
