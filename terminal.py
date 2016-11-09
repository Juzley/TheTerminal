"""Module containing the terminal class, the main gameplay logic."""

import itertools
import random
import string
from collections import deque

import pygame

import timer
import util
from programs.program import BadInput


class Terminal:

    """The main terminal class."""

    _ACCEPTED_CHARS = (string.ascii_letters + string.digits +
                       string.punctuation + " ")
    _BUF_SIZE = 100
    _HISTORY_SIZE = 50

    # Constants related to drawing the terminal text.
    _TEXT_SIZE = 16
    _TEXT_FONT = 'media/whitrabt.ttf'
    _TEXT_COLOUR = (20, 200, 20)

    # Constants related to cursor
    _CURSOR_WIDTH = 6
    _CURSOR_ON_MS = 800
    _CURSOR_OFF_MS = 600

    # Constants related to drawing the bezel.
    _BEZEL_IMAGE = 'media/bezel.png'
    _BEZEL_TEXT_SIZE = 30
    _BEZEL_TEXT_LOCATION = (680, 576)

    # The coordinates to start drawing text.
    _TEXT_START = (45, 525)

    # Freeze progress bar size
    _PROGRESS_BAR_SIZE = 30

    def __init__(self, programs, prompt='$ ', time=300, depends=None):
        """Initialize the class."""
        self._buf = deque(maxlen=Terminal._BUF_SIZE)
        self._prompt = prompt
        self._current_line = self._prompt
        self._cmd_history = deque(maxlen=Terminal._HISTORY_SIZE)
        self._history_pos = -1
        self._saved_line = ""
        self._font = pygame.font.Font(Terminal._TEXT_FONT, Terminal._TEXT_SIZE)
        self._current_program = None
        self._timer = timer.Timer()
        self._timeleft = time * 1000
        self._has_focus = True
        self._depends = {} if depends is None else depends
        self._freeze_start = None
        self._freeze_time = None
        self.locked = False

        self._bezel = util.load_image(Terminal._BEZEL_IMAGE)
        bezel_font = pygame.font.Font(None, Terminal._BEZEL_TEXT_SIZE)
        bezel_label = ''.join(
            random.choice(string.ascii_uppercase + string.digits)
            for _ in range(5))
        self._bezel_text = bezel_font.render(bezel_label, True, (255, 255, 255))

        # Create instances of the programs that have been registered.
        self._programs = {c: programs[c](self) for c in programs}

        # Display welcome message
        self.output([
            "-" * 60,
            "Mainframe terminal",
            "",
            "You have {}s to login before terminal is locked down.".format(
                time),
            "",
            "Tip of the day: press ctrl+c to cancel current command.",
            "-" * 60] + [""] * 20 + ["Type 'help' for available commands"])

    def _process_command(self, cmd):
        """Process a completed command."""
        if cmd in self._programs:
            # Check dependencies for this command
            if self._is_cmd_runnable(cmd):
                # Create a new instance of the program
                self._current_program = self._programs[cmd]

                # Don't run the program if it is already completed
                # TODO: Some kind of message here.
                if not self._current_program.completed():
                    self._current_program.start()
        elif cmd in ('help', '?'):
            sorted_cmds = sorted(self._programs.items(),
                                 key=lambda i: i[0])
            self.output(["Available commands:"] +
                        ["  {:10}   {}".format(c, p.help)
                         for c, p in sorted_cmds])
        elif cmd:
            self.output(["Unknown command '{}'.".format(cmd)])

    def _is_cmd_runnable(self, cmd):
        depends_list = self._depends.get(cmd)
        if depends_list is None:
            blocked_on = []
        else:
            # Get blocked-on list
            blocked_on = [self._programs[c] for c in depends_list
                          if not self._programs[c].completed()]

        if len(blocked_on) == 0:
            return True
        else:
            self.output(["{} currently blocked by: {}".format(
                cmd, ", ".join(p.security_type for p in blocked_on)
            )])
            return False

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
            # Skip the prompt
            if self._current_program.prompt is not None:
                line = self._current_line[len(self._current_program.prompt):]
            else:
                line = self._current_line

            # Handle bad input errors
            try:
                self._current_program.text_input(line)
            except BadInput as e:
                self.output(["Error: {}".format(str(e))])
        else:
            # Skip the prompt and any leading/trailing whitespace to get
            # the command.
            cmd = self._current_line[len(self._prompt):].lstrip().rstrip()

            # Add to command history, skipping repeated entries
            if cmd and (len(self._cmd_history) == 0 or
                        self._cmd_history[0] != cmd):
                self._cmd_history.appendleft(cmd)
            self._process_command(cmd)

        # Reset the prompt
        self._reset_prompt()

    def _reset_prompt(self):
        # Use current program's prompt if it has one
        if self._current_program and self._current_program.prompt is not None:
            self._current_line = self._current_program.prompt
        elif self._current_program:
            self._current_line = ""
        else:
            self._current_line = self._prompt

    def on_keypress(self, key, key_unicode):
        """Handle a user keypress."""
        # Ignore all input if in freeze mode
        if self._freeze_time is not None:
            return

        # Detect ctrl+c
        ctrl_c_pressed = (key == pygame.K_c and
                          pygame.key.get_mods() & pygame.KMOD_CTRL)

        # If we're displaying a graphical program, ignore keyboard input
        # (unless it is ctrl+c)
        if (self._current_program and
                self._current_program.is_graphical() and
                not ctrl_c_pressed):
            return

        # Any typing other than arrows reset history navigation
        if key not in (pygame.K_UP, pygame.K_DOWN):
            self._history_pos = -1

        if ctrl_c_pressed:
            # If we are in a program, then abort it
            if self._current_program:
                self._current_program.on_abort()
                self._current_program = None
            self.output([self._current_line + "^C"])
            self._current_line = self._prompt
        elif key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
            if self._current_line:
                self._complete_input()
        elif key == pygame.K_BACKSPACE:
            # Don't allow removing the prompt, just what the user has typed.
            # If a program is running then grab its prompt (which will be None
            # if it doesn't have one)
            if self._current_program:
                prompt = self._current_program.prompt
            else:
                prompt = self._prompt
            if prompt is None or len(self._current_line) > len(prompt):
                self._current_line = self._current_line[:-1]
        elif key == pygame.K_UP:
            if self._history_pos + 1 < len(self._cmd_history):
                # If we are starting a history navigation, then save current
                # line
                if self._history_pos == -1:
                    self._saved_line = self._current_line
                self._history_pos += 1
                self._current_line = self._prompt + \
                    self._cmd_history[self._history_pos]
        elif key == pygame.K_DOWN:
            if self._history_pos > 0:
                self._history_pos -= 1
                self._current_line = self._prompt + \
                    self._cmd_history[self._history_pos]
            elif self._history_pos == 0:
                # Restore saved line
                self._history_pos = -1
                self._current_line = self._saved_line
        elif key_unicode in Terminal._ACCEPTED_CHARS:
            self._current_line += key_unicode

    def on_mouseclick(self, button, pos):
        """Handle a user mouse click."""
        if self._current_program:
            self._current_program.on_mouseclick(button, pos)

    def on_active_event(self, active_event):
        """Handle a window active event."""
        if active_event.input_focus_change:
            self._has_focus = active_event.gained

    def output(self, output):
        """Add a list of lines to the displayed output."""
        # NB Output is expected to be a list of lines.
        self._add_to_buf(output)

    def freeze(self, time):
        """Freeze terminal for 'time' ms, displaying progress bar."""
        self._freeze_start = self._timer.time
        self._freeze_time = time

    def draw(self):
        """Draw the terminal."""

        # If terminal freeze is enabled, then update progress bar to indicate
        # how long there is left to wait.
        if self._freeze_time is not None:
            done = ((self._timer.time -
                     self._freeze_start) * 100) / self._freeze_time
            remain = int((100 - done) * self._PROGRESS_BAR_SIZE / 100)
            self._current_line = ("[" +
                                  "!" * (self._PROGRESS_BAR_SIZE - remain) +
                                  " " * remain + "]")

        # Draw the buffer.
        y_coord = Terminal._TEXT_START[1]
        for line in itertools.chain([self._current_line], self._buf):
            text = self._font.render(line, True, Terminal._TEXT_COLOUR)
            pygame.display.get_surface().blit(
                text, (Terminal._TEXT_START[0], y_coord))
            y_coord -= Terminal._TEXT_SIZE

        # Determine whether the cursor is on
        if (self._timer.time % (Terminal._CURSOR_ON_MS +
                                Terminal._CURSOR_OFF_MS) <
                Terminal._CURSOR_ON_MS):
            curr_line_size = self._font.size(self._current_line)
            pygame.draw.rect(pygame.display.get_surface(),
                             Terminal._TEXT_COLOUR,
                             (Terminal._TEXT_START[0] + curr_line_size[0] + 1,
                              Terminal._TEXT_START[1] - 1,
                              Terminal._CURSOR_WIDTH, curr_line_size[1]),
                             0 if self._has_focus else 1)

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

        # See whether terminal can be unfrozen
        if (self._freeze_time is not None and
                self._timer.time > self._freeze_start + self._freeze_time):
            self._freeze_time = None
            self._freeze_start = None

            # Reset current line to prompt
            self._reset_prompt()

    def completed(self):
        """Indicate whether the player has been successful."""
        return len([p for p in self._programs.values()
                    if not p.completed()]) == 0
