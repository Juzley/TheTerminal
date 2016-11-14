
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

    def __init__(self, terminal):
        """Initialize the class."""
        super().__init__(terminal)

        self._completed = False
        self._exited = False

        # Select the puzzle
        puzzle = random.choice(PUZZLES)

        # Grid is indexed by row first, then column, and contains the node
        # grid character.
        self._grid = []

        self._rows = 0
        self._cols = 0

        # Find starting location
        for r in range(self._rows):
            for c in range(self._cols):
                if self._grid[r][c] == self._START_NODE:
                    self._start = (r, c)

        # Track the nodes the user has visited, and which node it was visited
        # from. This allows us to build up the set of links the user has
        # entered.
        self._visited_from = {}

        # Solution is a list of pairs of nodes that have a link. Use a list
        # here, so we don't have to worry about the order the links are added
        # (i.e. so we don't have to try and walk the links in order, we can
        # just add them as each line of the puzzle is parsed).
        self._solution = []

        # IP details
        self._source_ip = puzzle[1]
        self._hostmask = puzzle[2]
        self._dest_ip = puzzle[3]

        # Current location
        self._curr = None

        # Build the grid and solution from the puzzle
        self._parse_puzzle(puzzle[0])

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

        is_on = (self._terminal.time % (self._ON_MS + self._OFF_MS) <
                 self._ON_MS)

        # Draw the grid
        for r in range(self._rows):
            line = ""
            for c in range(self._cols):
                # See whether we need to draw a link to previous node
                if c > 0:
                    if self._has_connection((r, c), (r, c - 1)):
                        line += self._LINK_H
                    else:
                        line += self._SPACE_H

                # Add character - remembering to make current location flash
                if (r, c) == self._curr and not is_on:
                    line += self._NODE_OFF
                else:
                    line += self._grid[r][c]
            lines.append("<w>" + line)

            # Now create gap between the row, drawing links to next row
            if r < self._rows - 1:
                line = ""
                for c in range(self._cols):
                    if c > 0:
                        line += self._SPACE_H

                    if self._has_connection((r, c), (r + 1, c)):
                        line += self._LINK_V
                    else:
                        line += self._SPACE_V

                lines.append("<w>" + line)

        lines.append("")
        lines.append("Use arrow keys to create a static route from source to "
                     "dest.")

        return reversed(lines)

    def start(self):
        # Reset board
        self._visited_from = {}
        self._exited = False
        self._curr = self._start

        # Mark the start node as visited
        self._visited_from[self._start] = None

    def completed(self):
        """Indicate whether the program was completed."""
        return self._completed

    def exited(self):
        """Indicate whether the program has exited."""
        return self.completed() or self._exited

    def on_keypress(self, key, key_unicode):
        """Handle a user keypress (used for INTERACTIVE and GRAPHICAL)."""
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
                0 <= new_curr[0] < self._rows and
                0 <= new_curr[1] < self._cols and
                new_curr not in self._visited_from):
            self._visited_from[new_curr] = self._curr
            self._curr = new_curr

        # If we have reached the destination then check result
        if self._grid[self._curr[0]][self._curr[1]] == self._END_NODE:
            failed = False
            if len(self._visited_from) != len(self._solution):
                failed = True
            else:
                for node1, node2 in self._visited_from.items():
                    if not self._is_correct_connection(node1, node2):
                        failed = True

            if failed:
                self._terminal.output([self.failure_prefix +
                                       "connection to server failed"])
                self._exited = True
            else:
                self._completed = True

    def _parse_puzzle(self, puzzle):
        def add_solution_link(node1, node2):
            # Sanity check - a node can only be involved in 2 links!
            usages = [(n1, n2) for n1, n2 in self._solution
                      if n1 == node1 or n2 == node1]
            if len(usages) > 1:
                raise Exception("{} already used twice: {}"
                                .format(node1, usages))

            usages = [(n1, n2) for n1, n2 in self._solution
                      if n1 == node2 or n2 == node2]
            if len(usages) > 1:
                raise Exception("{} already used twice: {}"
                                .format(node2, usages))
            self._solution.append((node1, node2))

        # Create grid by walking solution, and build up solution dict
        row = 0
        for line in puzzle.split("\n"):
            # Parse a node row
            if self._NODE in line:
                node_row = []
                col = -1
                while len(line) > 0:
                    # Assume start node and end are all the same length
                    if line[:len(self._NODE)] in (self._NODE,
                                                  self._START_NODE,
                                                  self._END_NODE):

                        # Update current col
                        col += 1
                        node_row.append(line[:len(self._NODE)])

                        # Remember starting location
                        if line.startswith(self._START_NODE):
                            self._start = (row, col)
                        line = line[len(self._NODE):]

                    elif line.startswith(self._LINK_H):
                        add_solution_link((row, col + 1), (row, col))
                        line = line[len(self._LINK_H):]
                    elif line.startswith(self._SPACE_H):
                        line = line[len(self._SPACE_H):]
                    else:
                        raise Exception("Unknown line contents: {}"
                                        .format(line))

                self._grid.append(node_row)
                row += 1

            # Parse a spacer row
            else:
                chars_since_col = None
                col = -1
                for char in line:
                    # Are we due a node column?
                    if (chars_since_col is None or
                            chars_since_col == len(self._SPACE_H)):
                        # Update current col
                        col += 1
                        chars_since_col = 0

                        # Do we have a connector?
                        if char == self._LINK_V:
                            add_solution_link((row, col), (row - 1, col))
                    else:
                        chars_since_col += 1

        # Set row and col count
        self._rows = len(self._grid)
        self._cols = len(self._grid[0])

        # The starting location should be visited from None.
        add_solution_link(self._start, None)

    def _has_connection(self, node1, node2):
        if node1 in self._visited_from and self._visited_from[node1] == node2:
            return True
        elif node2 in self._visited_from and self._visited_from[node2] == node1:
            return True
        else:
            return False

    def _is_correct_connection(self, node1, node2):
        return ((node1, node2) in self._solution
                or (node2, node1) in self._solution)
