
import pygame
import random

from . import program

PUZZLE1 = ("""
o  o  o  o  o  o  o

o  o  o  o  o  o  o

o  o..o..o..o..o  o
   :           :
o  o  o  o  o  o..D
   :
o  o  o  o  o  o  o
   :
S..o  o  o  o  o  o
""",
"192.168.1.15",
"255.255.255.0",
"10.0.0.1")


PUZZLE2 = ("""
o  o  o  o  o  D..o
                  :
o  o  o  o  o  o..o
               :
o  o..o..o..o  o  o
   :        :  :
o  o  o  o  o  o  o
   :        :  :
o  o  o  o  o..o  o
   :
S..o  o  o  o  o  o
""",
"192.168.1.15",
"255.255.0.0",
"10.0.0.1")


PUZZLES = (PUZZLE1, PUZZLE2)


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
        self._hostmask = puzzle[2]
        self._dest_ip = puzzle[3]

        # Current location (set to start location in start)
        self._curr = (0, 0)

        # Has an error occurred?
        self._error_mode = False

        # When was error mode started?
        self._error_mode_start = None

        # Time that last link was removed on error
        self._last_revert_time = None

        # Parser the puzzle and solution
        self._puzzle = PuzzleParser(puzzle[0])

    @property
    def program_type(self):
        """Return the program type."""
        return program.TerminalProgram.Type.INTERACTIVE

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
        return "SYSTEM WARNING: network connectivity to server established"

    @property
    def buf(self):
        lines = ["-------------------------------",
                 "Simple Network Manager",
                 "   Networking made easy!",
                 "-------------------------------",
                 "",
                 "Source IP: {}".format(self._source_ip),
                 "Source hostmask: {}".format(self._hostmask),
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
                    self._error_mode = False
                    self._last_revert_time = None
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
                lines.append("<r>" + line)
            else:
                lines.append("<w>" + line)

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
                    lines.append("<r>" + line)
                else:
                    lines.append("<w>" + line)

        lines.append("")
        if self._error_mode:
            lines.append("<r>Invalid route detected.")
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

            # Was this valid?
            if not self._puzzle.is_connection_correct(new_curr, self._curr):
                self._error_mode = True
                self._error_mode_start = self._terminal.time

            # Update current
            self._curr = new_curr

        # If we have reached the destination then we are done!
        if not self._error_mode and self._curr == self._puzzle.end:
            self._completed = True

    def _has_connection(self, node1, node2):
        if node1 in self._visited_from and self._visited_from[node1] == node2:
            return True
        elif node2 in self._visited_from and self._visited_from[node2] == node1:
            return True
        else:
            return False


class PuzzleParser:

    """Class to parse the puzzle solution from an ascii representation."""

    _SPACE_CHAR = " "
    _NODE_CHAR = "o"
    _START_CHAR = "S"
    _END_CHAR = "D"

    def __init__(self, puzzle_data):
        self.cols = 0
        self.rows = 0
        self.start = (0, 0)
        self.end = (0, 0)

        # Solution is a list of pairs of nodes that have a link. Use a list
        # here, so we don't have to worry about the order the links are added
        # (i.e. so we don't have to try and walk the links in order, we can
        # just add them as each line of the puzzle is parsed).
        self._solution = []

        # Number of spaces between nodes
        self._node_gap = 0

        next_row_nodes = True
        for line in puzzle_data.split("\n"):
            # Ignore initial empty lines
            if self.rows == 0 and not line:
                continue
            if next_row_nodes:
                self.rows += 1
                self._parse_node_row(line)
                next_row_nodes = False
            else:
                self._parse_spacer_row(line)
                next_row_nodes = True

        # Add a connection from None to start
        self._add_solution_link(None, self.start)

    @property
    def correct_link_count(self):
        return len(self._solution)

    def is_connection_correct(self, node1, node2):
        return ((node1, node2) in self._solution
                or (node2, node1) in self._solution)

    def _parse_node_row(self, line):
        cols = 0
        node_gap = 0
        has_link = False
        for idx, char in enumerate(line):
            if char in (self._NODE_CHAR, self._START_CHAR, self._END_CHAR):
                cols += 1

                # See whether this is the start or end
                if char == self._START_CHAR:
                    self.start = (self.rows - 1, cols - 1)
                elif char == self._END_CHAR:
                    self.end = (self.rows - 1, cols - 1)

                # Record the link if there was one
                if has_link:
                    self._add_solution_link((self.rows - 1, cols - 1),
                                            (self.rows - 1, cols - 2))

                # If this isn't first node, then record the node gap
                if idx != 0:
                    if self._node_gap == 0:
                        self._node_gap = node_gap
                    elif node_gap != self._node_gap:
                        raise Exception("Row {} has gap {} != {}"
                                        .format(self.rows - 1,
                                                node_gap, self._node_gap))

                # Reset!
                has_link = False
                node_gap = 0
            elif char != self._SPACE_CHAR:
                has_link = True
                node_gap += 1
            else:
                node_gap += 1

        # Make sure cols agrees with global
        if self.cols == 0:
            self.cols = cols
        elif self.cols != cols:
            raise Exception("Row {} has cols {} != {}"
                            .format(self.rows - 1, cols, self.cols))

    def _parse_spacer_row(self, line):
        chars_since_col = None
        cols = 0
        for char in line:
            # Are we due a node column?
            if (chars_since_col is None or
                        chars_since_col == self._node_gap):
                # Update current col
                cols += 1
                chars_since_col = 0

                # Do we have a connector to the next row?
                if char != self._SPACE_CHAR:
                    self._add_solution_link((self.rows - 1, cols - 1),
                                            (self.rows, cols - 1))
            else:
                chars_since_col += 1

        # Make sure cols is not large than global. It can be less in the case
        # the row wasn't finished off with spaces.
        if self.cols < cols:
            raise Exception("Spacer row {} has cols {} > {}"
                            .format(self.rows - 1, cols, self.cols))

    def _add_solution_link(self, node1, node2):
        # Sanity check - a node can only be involved in 2 links!
        for node in (node1, node2):
            usages = [(n1, n2) for n1, n2 in self._solution
                      if n1 == node or n2 == node]
            if len(usages) > 1:
                raise Exception("{} already used twice: {}"
                                .format(node, usages))

        self._solution.append((node1, node2))
