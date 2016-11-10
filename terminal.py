"""Module containing the terminal class, the main gameplay logic."""

import itertools
import random
import string
import os
from collections import deque

import pygame

import timer
import util
import mouse
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
    _TEXT_COLOUR_RED = (200, 20, 20)

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

    # Key repeat delay
    _KEY_REPEAT_DELAY = 50
    _KEY_REPEAT_INITIAL_DELAY = 500

    def __init__(self, programs, prompt='$ ', time=300, depends=None):
        """Initialize the class."""
        # Public attributes
        self.locked = False
        self.id_string = ''.join(
            random.choice(string.ascii_uppercase + string.digits)
            for _ in range(5))

        # Current line without prompt. If current line with prompt is required,
        # use get_current_line(True)
        self._current_line = ""
        self._buf = deque(maxlen=Terminal._BUF_SIZE)
        self._prompt = prompt
        self._cmd_history = CommandHistory(self, maxlen=Terminal._HISTORY_SIZE)
        self._font = pygame.font.Font(Terminal._TEXT_FONT, Terminal._TEXT_SIZE)
        self._has_focus = True

        # Timer attributes
        self._timer = timer.Timer()
        self._timeleft = time * 1000

        # Freeze attributes
        self._freeze_start = None
        self._freeze_time = None

        # Repeat key presses when certain keys are held.
        # Held key is a tuple of (key, key_unicode, start time)
        self._held_key = None
        self._key_last_repeat = None

        # Create instances of the programs that have been registered.
        self._programs = {c: p(self) for c, p in programs.items()}
        self._current_program = None
        self._depends = {} if depends is None else depends

        # Draw the monitor bezel
        self._bezel = util.load_image(Terminal._BEZEL_IMAGE)
        bezel_font = pygame.font.Font(None, Terminal._BEZEL_TEXT_SIZE)
        self._bezel_text = bezel_font.render(self.id_string, True,
                                             (255, 255, 255))

        self.reboot(first_boot=True)

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

        # Easter egg!
        elif cmd.startswith("colour "):
            args = cmd.split(" ")[1:]
            if len(args) == 3:
                try:
                    # Get colour and try a render to make sure code correct
                    colour = tuple(int(a) for a in args)
                    self._font.render("test", True, colour)
                    Terminal._TEXT_COLOUR = colour
                except (ValueError, TypeError):
                    self.output(["I am not familiar with that colour code."])
                else:
                    self.output(["Enjoy your new colour!"])

        # Freeze test
        elif cmd.startswith("freeze "):
            try:
                self.freeze(int(cmd.split(" ")[1]))
            except ValueError:
                self.output(["Invalid time"])

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
        self._add_to_buf([self.get_current_line(True)])

        if self._current_program:
            # Handle bad input errors
            try:
                self._current_program.text_input(self.get_current_line())
            except BadInput as e:
                self.output(["Error: {}".format(str(e))])
        else:
            # Skip the prompt and any leading/trailing whitespace to get
            # the command.
            cmd = self.get_current_line().lstrip().rstrip()

            # Add to command history, skipping repeated entries
            if cmd:
                self._cmd_history.add_command(cmd)
            self._process_command(cmd)

        # Reset the prompt
        self._reset_prompt()

    def _reset_prompt(self):
        # Current line doesn't have prompt, so we don't have to worry about
        # adding it.
        self._current_line = ""

    def _tab_complete(self):
        # Only works outside programs for now
        if self._current_program is None:
            partial = self.get_current_line()

            # Find the command being typed
            matches = [c for c in list(self._programs.keys()) + ["help"]
                       if c.startswith(partial)]
            if len(matches) == 1:
                self.set_current_line(matches[0])
            elif len(matches) > 1:
                # Get the common prefix. If this is more than what is typed
                # then complete up till that, else display options
                common_prefix = os.path.commonprefix(matches)
                if common_prefix != partial:
                    self.set_current_line(common_prefix)
                else:
                    self.output([self.get_current_line(True),
                                 "  ".join(matches)])

    def get_current_line(self, include_prompt=False):
        if include_prompt:
            # See if the current program has a prompt. Will be None if it
            # doesn't.
            if self._current_program is not None:
                prompt = self._current_program.prompt
            else:
                prompt = self._prompt

            return (self._current_line if prompt is None
                    else prompt + self._current_line)
        else:
            return self._current_line

    def set_current_line(self, line):
        # Don't need to add prompt - this gets added by get_current_line()
        self._current_line = line

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
            self._cmd_history.reset_navigation()

        repeat_on_hold = False
        if ctrl_c_pressed:
            current_line = self.get_current_line(True)

            # If we are in a program, then abort it
            if self._current_program:
                self._current_program.on_abort()
                self._current_program = None
            self.output([current_line + "^C"])
            self._reset_prompt()
        elif key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
            if self.get_current_line(True):
                self._complete_input()
        elif key == pygame.K_BACKSPACE:
            self._current_line = self._current_line[:-1]
            repeat_on_hold = True
        elif key in (pygame.K_UP, pygame.K_DOWN):
            # Currently not supported in a program
            if self._current_program is None:
                self._cmd_history.navigate(key == pygame.K_UP)
        elif key == pygame.K_TAB:
            self._tab_complete()
        elif key_unicode in Terminal._ACCEPTED_CHARS:
            self._current_line += key_unicode
            repeat_on_hold = True

        # If this is a key that should be repeated when held, then setup the
        # the attributes
        if repeat_on_hold:
            self._held_key = (key, key_unicode, self._timer.time)

    def on_keyrelease(self):
        self._held_key = None
        self._key_last_repeat = None

    def on_mouseclick(self, button, pos):
        """Handle a user mouse click."""
        if self._current_program:
            self._current_program.on_mouseclick(button, pos)

    def on_mousemove(self, pos):
        """Handle a user mouse move."""
        if self._current_program:
            self._current_program.on_mousemove(pos)

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

    def reduce_time(self, time):
        """Reduce the available time by 'time' seconds."""
        self._timeleft -= time * 1000

    def reboot(self, msg="", first_boot=False):
        """Simulate a reboot."""
        # Clear the buffer.
        self._buf.clear()

        # Display welcome message.
        self.output([
            "-" * 60,
            "Mainframe terminal",
            "",
            "You have {}s to login before terminal is locked down.".format(
                round(self._timeleft / 1000)),
            "",
            "Tip of the day: press ctrl+c to cancel current command.",
            "-" * 60])
        if not first_boot:
            self.output(["", "SYSTEM NOTIFICATION: System rebooted!"])
        if msg:
            self.output([msg])

        self.output([""] * (28 - len(self._buf))
                    + ["Type 'help' for available commands"])

    def draw(self):
        """Draw the terminal."""
        # If terminal freeze is enabled, then update progress bar to indicate
        # how long there is left to wait, using this as the current line.
        if self._freeze_time is not None:
            done = ((self._timer.time -
                     self._freeze_start) * 100) / self._freeze_time
            remain = int((100 - done) * self._PROGRESS_BAR_SIZE / 100)
            current_line = ("[" +
                            "!" * (self._PROGRESS_BAR_SIZE - remain) +
                            " " * remain + "]")
        else:
            current_line = self.get_current_line(True)

        # Draw the buffer.
        y_coord = Terminal._TEXT_START[1]
        for line in itertools.chain([current_line], self._buf):
            # If line starts with a colour code, then change colour
            if line.startswith("<r>"):
                colour = Terminal._TEXT_COLOUR_RED
                line = line[3:]
            else:
                colour = Terminal._TEXT_COLOUR
            text = self._font.render(line, True, colour)
            pygame.display.get_surface().blit(
                text, (Terminal._TEXT_START[0], y_coord))
            y_coord -= Terminal._TEXT_SIZE

        # Determine whether the cursor is on
        if (self._timer.time % (Terminal._CURSOR_ON_MS +
                                Terminal._CURSOR_OFF_MS) <
                Terminal._CURSOR_ON_MS):
            curr_line_size = self._font.size(current_line)
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

        # Make sure cursor is an arrow if we are not in a program. This should
        # be a no-op if it is already an arrow.
        if self._current_program is None:
            mouse.current.set_cursor(mouse.Cursor.ARROW)

    def run(self):
        """Run terminal logic."""
        # Check whether the current program (if there is one) has exited.
        if self._current_program and self._current_program.exited():
            self._current_program = None

            # Display the prompt again.
            self._reset_prompt()

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

        # See whether a key is held, and repeat it
        if self._held_key is not None:
            key, key_unicode, start = self._held_key
            if self._key_last_repeat is None:
                last, delay = start, Terminal._KEY_REPEAT_INITIAL_DELAY
            else:
                last, delay = self._key_last_repeat, Terminal._KEY_REPEAT_DELAY

            if (self._timer.time - last) > delay:
                self._key_last_repeat = self._timer.time
                self.on_keypress(key, key_unicode)

    def completed(self):
        """Indicate whether the player has been successful."""
        return len([p for p in self._programs.values()
                    if not p.completed()]) == 0


class CommandHistory:

    """Class for storing and navigating a terminal's command history."""

    def __init__(self, terminal, maxlen):
        self._terminal = terminal
        self._history = deque(maxlen=maxlen)
        self._pos = -1
        self._saved_line = None

    def add_command(self, cmd):
        # Skip repeated commands
        if len(self._history) == 0 or self._history[0] != cmd:
            self._history.appendleft(cmd)

    def reset_navigation(self):
        self._pos = -1

    def navigate(self, up):
        if up:
            if self._pos + 1 < len(self._history):
                # If we are starting a history navigation, then save current
                # line
                if self._pos == -1:
                    self._saved_line = self._terminal.get_current_line()
                self._pos += 1
                self._terminal.set_current_line(self._history[self._pos])
        else:
            if self._pos > 0:
                self._pos -= 1
                self._terminal.set_current_line(self._history[self._pos])
            elif self._pos == 0:
                # Restore saved line
                self._pos = -1
                self._terminal.set_current_line(self._saved_line)
