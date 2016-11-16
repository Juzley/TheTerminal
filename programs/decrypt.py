"""Decryption program classes."""


import random
from media import load_font
from . import program


class Decrypt(program.TerminalProgram):
    # For each font, we have a dictionary mapping from the character in the font
    # to what the correct decryption is.
    _FONTS = [
        ('media/CRUX.ttf', {'a': 'a'})
    ]

    _MIN_LENGTH = 4
    _MAX_LENGTH = 12

    def __init__(self, terminal):
        """Initialize the class."""
        super().__init__(terminal)
        self._correct = False

        self._font, self._cypher = random.choice(Decrypt._FONTS)
        # Preload the font.
        load_font(self._font, self._terminal.TEXT_SIZE)

        self._enc_string = ""
        self._dec_string = ""

    def start(self):
        """Start the program."""
        self._enc_string = ''.join(
            [random.choice(list(self._cypher.keys())) for _ in
             range(random.randrange(Decrypt._MIN_LENGTH,
                                    Decrypt._MAX_LENGTH + 1))])
        self._dec_string = ''.join([self._cypher[e] for e in self._enc_string])

        self._enc_string = self._terminal._ACCEPTED_CHARS
        self._terminal.output(['<f {}>{}'.format(self._font, self._enc_string)])

    def exited(self):
        return self._correct

    def completed(self):
        return self._correct

    def text_input(self, line):
        if line == self._enc_string:
            self._correct = True
