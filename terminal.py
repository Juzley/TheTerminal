"""Module containing the terminal class, the main gameplay logic."""

import pygame
import string
import itertools
from collections import deque
import util
import timer
import random


class Terminal:

    """The main terminal class."""

    _ACCEPTED_CHARS = (string.ascii_letters + string.digits +
                       string.punctuation + " ")
    _BUF_SIZE = 100

    # Constants related to drawing the terminal text.
    _TEXT_SIZE = 16
    _TEXT_FONT = 'media/whitrabt.ttf'
    _TEXT_COLOUR = (20, 200, 20)

    # Constants related to cursor
    _CURSOR_WEIGHT = 1
    _CURSOR_WIDTH = 6
    _CURSOR_ON_FRAMES = 80
    _CURSOR_OFF_FRAMES = 40

    # Constants related to drawing the bezel.
    _BEZEL_IMAGE = 'media/bezel.png'
    _BEZEL_TEXT_SIZE = 30
    _BEZEL_TEXT_LOCATION = (680, 576)

    # The coordinates to start drawing text.
    _TEXT_START = (45, 525)

    def __init__(self, programs, prompt='$ ', time=300):
        """Initialize the class."""
        self._buf = deque(maxlen=Terminal._BUF_SIZE)
        self._prompt = prompt
        self._current_line = self._prompt
        self._font = pygame.font.Font(Terminal._TEXT_FONT, Terminal._TEXT_SIZE)
        self._current_program = None
        self._timer = timer.Timer()
        self._timeleft = time * 1000
        self._cursor_counter = 0
        self.locked = False

        self._bezel = util.load_image(Terminal._BEZEL_IMAGE)
        bezel_font = pygame.font.Font(None, Terminal._BEZEL_TEXT_SIZE)
        bezel_label = ''.join(
            random.choice(string.ascii_uppercase + string.digits)
            for i in range(5))
        self._bezel_text = bezel_font.render(bezel_label, True, (255, 255, 255))

        # Create instances of the programs that have been registered.
        self._programs = {c: programs[c](self) for c in programs}

    def _process_command(self, cmd):
        """Process a completed command."""
        if cmd in self._programs:
            # Create a new instance of the program
            self._current_program = self._programs[cmd]

            # Don't run the program if it is already completed
            # TODO: Some kind of message here.
            if not self._current_program.completed():
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
            self._current_program.text_input(self._current_line)
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

    def on_keypress(self, key, key_unicode):
        """Handle a user keypress."""
        # If we're displaying a graphical program, ignore keyboard input
        if self._current_program and self._current_program.is_graphical():
            return

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

    def on_mouseclick(self, button, pos):
        """Handle a user mouse click."""
        if self._current_program:
            self._current_program.on_mouseclick(button, pos)

    def output(self, output):
        """Add a list of lines to the displayed output."""
        # NB Output is expected to be a list of lines.
        self._add_to_buf(output)

    def draw(self):
        """Draw the terminal."""
        # Draw the buffer.
        y_coord = Terminal._TEXT_START[1]

        for line in itertools.chain([self._current_line], self._buf):
            text = self._font.render(line, True, Terminal._TEXT_COLOUR)
            pygame.display.get_surface().blit(
                text, (Terminal._TEXT_START[0], y_coord))
            y_coord -= Terminal._TEXT_SIZE

        # Increment cursor counter and draw if it is 'on'
        self._cursor_counter += 1
        if self._cursor_counter <= Terminal._CURSOR_ON_FRAMES:
            curr_line_size = self._font.size(self._current_line)
            pygame.draw.rect(pygame.display.get_surface(),
                             Terminal._TEXT_COLOUR,
                             (Terminal._TEXT_START[0] + curr_line_size[0] + 1,
                              Terminal._TEXT_START[1] - 1,
                              Terminal._CURSOR_WIDTH, curr_line_size[1]),
                             Terminal._CURSOR_WEIGHT)
        elif self._cursor_counter > Terminal._CURSOR_ON_FRAMES + Terminal._CURSOR_OFF_FRAMES:
            self._cursor_counter = 0

        # If the current program is a graphical one, draw it now.
        if self._current_program and self._current_program.is_graphical():
            self._current_program.draw()

        # Draw the bezel.
        pygame.display.get_surface().blit(self._bezel, self._bezel.get_rect())
        pygame.display.get_surface().blit(self._bezel_text,
                                          Terminal._BEZEL_TEXT_LOCATION)

        # Draw the countdown text.
        minutes, seconds = divmod(self._timeleft // 1000, 60)
        text = self._font.render('{}:{:02}'.format(minutes, seconds),
                                 True, (255, 255, 255))
        pygame.display.get_surface().blit(text, (0, 0))

    def run(self):
        """Run terminal logic."""
        # Check whether the current program (if there is one) has exited.
        if self._current_program and self._current_program.exited():
            self._current_program = None

            # Display the prompt again.
            self._current_line = self._prompt

        # Check if the player ran out of time.
        self._timer.update()
        self._timeleft -= self._timer.frametime
        if self._timeleft <= 0:
            self.locked = True

    def completed(self):
        """Indicate whether the player has been successful."""
        return len([p for p in self._programs.values()
                    if not p.completed()]) == 0
