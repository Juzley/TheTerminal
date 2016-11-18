
import pygame
import random

from . import program

PUZZLE1 = ("""
S . . . x x
x . . . x x
x x G x x x
. . . . G .
G . . . . .
x x x x x D
""",
"192.168.1.15",
"255.255.255.0",
"10.0.0.1")

PUZZLE2 = ("""
S . . G x x
. . . . x x
. x . . x x
. . x . G .
G . . x . .
x x . . . D
""",
"192.168.1.15",
"255.255.255.0",
"11.0.0.1")

PUZZLE3 = ("""
S . . G x x
. . . . . x
. x . . G x
. . x . x .
G . . . . .
x x . . . D
""",
"192.168.1.15",
"255.255.0.0",
"11.0.0.1")


"""List of available puzzles, to be chosen at random."""
PUZZLES = (PUZZLE1, PUZZLE2, PUZZLE3)


class NetworkManager(program.TerminalProgram):

    """The network manager program."""

    _GRID_WIDTH = 10
    _GRID_HEIGHT = 10

    _START_NODE = "S"
    _END_NODE = "D"

    _NODE = "o"
    _NODE_OFF = "."

    _LINK_H = ".."
    _LINK_V = ":"

    _SPACE_H = "  "
    _SPACE_V = " "

    _ON_MS = 800
    _OFF_MS = 600

    _REVERT_LINK_TIME = 200
    _ERROR_INITIAL_WAIT = 2000

    """The properties of this program."""
    PROPERTIES = program.ProgramProperties(intercept_keypress=True,
                                           alternate_buf=True,
                                           hide_cursor=True)

    def __init__(self, terminal):
        """Initialize the class."""
        super().__init__(terminal)

        self._completed = False
        self._exited = False

        # Select the puzzle
        puzzle = random.choice(PUZZLES)

        # Track the nodes the user has visited, and which node it was visited
        # from. This allows us to build up the set of links the user has
        # entered.
        self._visited_from = {}

        # IP details
        self._source_ip = puzzle[1]
        self._subnet_mask = puzzle[2]
        self._dest_ip = puzzle[3]

        # Current location (set to start location in start)
        self._curr = (0, 0)

        # Has an error occurred?
        self._error_mode = False

        # When was error mode started?
        self._error_mode_start = None

        # Time that last link was removed on error
        self._last_revert_time = None

        # Reason for being in error mode
        self._error_msg = None

        # Parser the puzzle and solution
        self._puzzle = PuzzleParser(puzzle[0])

    @property
    def allow_ctrl_c(self):
        return not self._error_mode

    @property
    def help(self):
        """Get the help string for the program."""
        return "Manage network connectivity."

    @property
    def security_type(self):
        """Get the security type for the program."""
        return "network access"

    @property
    def success_syslog(self):
        return "{} network connectivity to server established".format(
            self.SUCCESS_PREFIX)

    @property
    def buf(self):
        lines = ["-------------------------------",
                 "Simple Network Manager",
                 "   Networking made easy!",
                 "-------------------------------",
                 "",
                 "Source IP: {}".format(self._source_ip),
                 "Subnet mask: {}".format(self._subnet_mask),
                 "Destination IP: {}".format(self._dest_ip),
                 "",
                 "",
                 "Network map:",
                 ""]

        # If error mode, start reversing the path
        if self._error_mode:
            if self._last_revert_time is None:
                last_time, delay = self._error_mode_start, \
                                   self._ERROR_INITIAL_WAIT
            else:
                last_time, delay = self._last_revert_time, \
                                   self._REVERT_LINK_TIME
            if last_time + delay < self._terminal.time:
                # Find where we came from
                from_node = self._visited_from[self._curr]

                # Remove link
                del self._visited_from[self._curr]

                # Update position. If we have reached None, then start again
                if from_node is None:
                    self.start()
                else:
                    self._curr = from_node
                    self._last_revert_time = self._terminal.time

        is_on = (self._error_mode or
                 self._terminal.time % (self._ON_MS + self._OFF_MS) <
                 self._ON_MS)

        # Draw the grid
        for r in range(self._puzzle.rows):
            line = ""
            for c in range(self._puzzle.cols):
                # See whether we need to draw a link to previous node
                if c > 0:
                    if self._has_connection((r, c), (r, c - 1)):
                        line += self._LINK_H
                    else:
                        line += self._SPACE_H

                # Add character - remembering to make current location flash
                if (r, c) == self._curr and not is_on:
                    line += self._NODE_OFF
                elif (r, c) == self._puzzle.start:
                    line += self._START_NODE
                elif (r, c) == self._puzzle.end:
                    line += self._END_NODE
                else:
                    line += self._NODE
            if self._error_mode:
                lines.append("<c r>" + line)
            else:
                lines.append("<c w>" + line)

            # Now create gap between the row, drawing links to next row
            if r < self._puzzle.rows - 1:
                line = ""
                for c in range(self._puzzle.cols):
                    if c > 0:
                        line += self._SPACE_H

                    if self._has_connection((r, c), (r + 1, c)):
                        line += self._LINK_V
                    else:
                        line += self._SPACE_V

                if self._error_mode:
                    lines.append("<c r>" + line)
                else:
                    lines.append("<c w>" + line)

        lines.append("")
        if self._error_mode:
            lines.append("<c r>Invalid route detected: {}"
                         .format(self._error_msg))
        else:
            lines.append("Use arrow keys to create a static route from source "
                         "to dest.")

        return reversed(lines)

    def start(self):
        # Reset board
        self._visited_from = {}
        self._exited = False
        self._curr = self._puzzle.start

        # Mark the start node as visited
        self._visited_from[self._curr] = None

        # Make sure error mode is turned off
        self._error_mode = False
        self._last_revert_time = None

    def completed(self):
        """Indicate whether the program was completed."""
        return self._completed

    def exited(self):
        """Indicate whether the program has exited."""
        return self.completed() or self._exited

    def on_keypress(self, key, key_unicode):
        """Handle a user keypress (used for INTERACTIVE and GRAPHICAL)."""
        # Ignore if in error mode
        if self._error_mode:
            return

        new_curr = None
        if key == pygame.K_UP:
            new_curr = (self._curr[0] - 1, self._curr[1])
        elif key == pygame.K_DOWN:
            new_curr = (self._curr[0] + 1, self._curr[1])
        elif key == pygame.K_RIGHT:
            new_curr = (self._curr[0], self._curr[1] + 1)
        elif key == pygame.K_LEFT:
            new_curr = (self._curr[0], self._curr[1] - 1)

        # Move to this location if we can
        if (new_curr is not None and
                0 <= new_curr[0] < self._puzzle.rows and
                0 <= new_curr[1] < self._puzzle.cols and
                new_curr not in self._visited_from):
            self._visited_from[new_curr] = self._curr
            self._curr = new_curr

            # Was this a valid node?
            if new_curr in self._puzzle.bad_nodes:
                self._enable_error_mode("attempted to use a down node")

        # If we have reached the destination, check we have used every gateway
        if not self._error_mode and self._curr == self._puzzle.end:
            missing = [g for g in self._puzzle.gateway_nodes
                       if g not in self._visited_from]
            if len(missing) > 0:
                self._enable_error_mode("missing gateway node")
            else:
                self._completed = True

    def _has_connection(self, node1, node2):
        if node1 in self._visited_from and self._visited_from[node1] == node2:
            return True
        elif node2 in self._visited_from and self._visited_from[node2] == node1:
            return True
        else:
            return False

    def _enable_error_mode(self, msg):
        self._error_mode = True
        self._error_msg = msg
        self._error_mode_start = self._terminal.time


class PuzzleParser:

    """Class to parse the puzzle solution from an ascii representation."""

    _SPACE_CHAR = " "
    _NODE_CHAR = "."
    _GATEWAY_CHAR = "G"
    _AVOID_CHAR = "x"
    _START_CHAR = "S"
    _END_CHAR = "D"

    def __init__(self, puzzle_data):
        self.cols = 0
        self.rows = 0
        self.start = (0, 0)
        self.end = (0, 0)

        # Gateway nodes; these must be included in solution
        self.gateway_nodes = []

        # Bad nodes; these must be avoided
        self.bad_nodes = []

        for line in puzzle_data.split("\n"):
            # Ignore empty lines
            if not line:
                continue
            self.rows += 1
            self._parse_node_row(line)

    def _parse_node_row(self, line):
        cols = 0
        for idx, char in enumerate(line):
            if char == self._NODE_CHAR:
                cols += 1
            elif char == self._START_CHAR:
                cols += 1
                self.start = (self.rows - 1, cols - 1)
            elif char == self._END_CHAR:
                cols += 1
                self.end = (self.rows - 1, cols - 1)
            elif char == self._GATEWAY_CHAR:
                cols += 1
                self.gateway_nodes.append((self.rows - 1, cols - 1))
            elif char == self._AVOID_CHAR:
                cols += 1
                self.bad_nodes.append((self.rows - 1, cols - 1))
            elif char != self._SPACE_CHAR:
                raise Exception("Unknown char {} in row {}"
                                .format(char, self.rows - 1))

        # Make sure cols agrees with global
        if self.cols == 0:
            self.cols = cols
        elif self.cols != cols:
            raise Exception("Row {} has cols {} != {}"
                            .format(self.rows - 1, cols, self.cols))
