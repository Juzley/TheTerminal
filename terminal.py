"""Module containing the main terminal class."""

import pygame
import string
import itertools
from collections import deque
import timer


class Terminal:

    """The main terminal class."""

    _ACCEPTED_CHARS = (string.ascii_letters + string.digits +
                       string.punctuation + " ")
    _BUF_SIZE = 100
    _TEXT_SIZE = 20

    def __init__(self, prompt='$ ', programs=None, time=300):
        """Initialize the class."""
        self._buf = deque(maxlen=Terminal._BUF_SIZE)
        self._prompt = prompt
        self._current_line = self._prompt
        self._font = pygame.font.Font(None, Terminal._TEXT_SIZE)
        self._current_program = None
        self._timer = timer.Timer()
        self._timeleft = time * 1000
        self._locked = False

        if not programs:
            # Can't have a mutable type as a default argument.
            self._programs = {}
        else:
            self._programs = programs

    def _process_command(self, cmd):
        """Process a completed command."""
        if cmd in self._programs:
            # Create a new instance of the program
            self._current_program = self._programs[cmd](self)
            self._current_program.start()
        elif cmd == 'help':
            # TODO: Output available commands.
            pass

    def _add_to_buf(self, lines):
        """Add lines to the display buffer."""
        for line in lines:
            # The buffer is ordered left to right from newest to oldest.
            # This will push old lines off the end of the buffer if it is full.
            self._buf.appendleft(line)

    def _complete_input(self):
        """Process a line of input from the user."""
        # Add the current line to the buffer
        self._add_to_buf([self._current_line])

        if self._current_program:
            self._current_program.input(self._current_line)

            # Check if the latest input has caused the current program to exit.
            if self._current_program.finished():
                self._current_program = None
        else:
            # Skip the prompt and any leading/trailing whitespace to get
            # the command.
            cmd = self._current_line[len(self._prompt):].lstrip().rstrip()
            self._process_command(cmd)

        # Reset the prompt, unless a program is running in which case there is
        # no prompt.
        if self._current_program:
            self._current_line = ""
        else:
            self._current_line = self._prompt

    def input(self, key, key_unicode):
        """Handle a user keypress."""
        if key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
            if self._current_line:
                self._complete_input()
        elif key == pygame.K_BACKSPACE:
            # Don't allow removing the prompt, just what the user has typed.
            # If a program is running there is no prompt.
            if (self._current_program or
                    len(self._current_line) > len(self._prompt)):
                self._current_line = self._current_line[:-1]
        elif key_unicode in Terminal._ACCEPTED_CHARS:
            self._current_line += key_unicode

    def output(self, output):
        """Add a list of lines to the displayed output."""
        # NB Output is expected to be a list of lines.
        self._add_to_buf(output)

    def draw(self):
        """Draw the terminal."""
        y_coord = pygame.display.Info().current_h - Terminal._TEXT_SIZE

        for line in itertools.chain([self._current_line], self._buf):
            text = self._font.render(line, True, (255, 255, 255))
            pygame.display.get_surface().blit(text, (0, y_coord))
            y_coord -= Terminal._TEXT_SIZE

    def run(self):
        """Run terminal logic."""
        self._timer.update()
        self._timeleft -= self._timer.frametime

        if self._timeleft <= 0:
            self._locked = True
