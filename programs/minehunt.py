
import itertools
import pygame
from enum import Enum, unique

import mouse
from . import program
from resource import load_font


class MineHunt(program.TerminalProgram):

    """Minehunt program."""

    """The properties of this program."""
    PROPERTIES = program.ProgramProperties(is_graphical=True,
                                           suppress_success=True)

    def __init__(self, terminal):
        """Initialize the class."""
        super().__init__(terminal)

        self._completed = False
        self._exited = False

        self._board = Board(BOARD1)

    @property
    def help(self):
        """Get the help string for the program."""
        return "Play minehunt!"

    @property
    def security_type(self):
        """Get the security type for the program."""
        return "user permissions"

    @property
    def success_syslog(self):
        return "{} user has been promoted to admin".format(
            self.SUCCESS_PREFIX)

    def start(self):
        # Reset board
        self._exited = False

    def completed(self):
        """Indicate whether the program was completed."""
        return self._completed

    def exited(self):
        """Indicate whether the program has exited."""
        return self.completed() or self._exited

    def on_keypress(self, key, key_unicode):
        """Handle a user keypress."""
        pass

    def on_mousemove(self, pos):
        pass

    def on_mouseclick(self, button, pos):
        """Detect whether the user clicked the program."""
        self._board.on_mouseclick(button, pos)

    def draw(self):
        """Draw the program."""
        self._board.draw(pygame.display.get_surface())


BOARD1 = """
.....x
x.....
......
......
......
xx....
"""


class Board:
    _WIDTH = 390
    _HEIGHT = 390
    _BOARD_Y = 50

    def __init__(self, board_str):
        # Board is a 2D array of Squares, indexed by row then col
        self._board = []

        # Number of rows and cols
        self._rows = 0
        self._cols = 0

        # Square size
        self._square_size = 0

        # Create the board
        self._surface = pygame.Surface((self._WIDTH, self._HEIGHT))
        self._surface.fill((255, 255, 255))

        screen_rect = pygame.display.get_surface().get_rect()
        board_rect = self._surface.get_rect()
        self._pos = (int((screen_rect[2] / 2)
                         - (board_rect[2] / 2)), self._BOARD_Y)

        # Surface for the next draw
        self._draw_surface = None

        # Create the board
        self._create_board(board_str)

        self._setup_draw()

    def draw(self, surface):
        surface.blit(self._draw_surface, self._pos)

    def on_mouseclick(self, button, screen_pos):
        square = self._hit_square(self._screen_to_board_pos(screen_pos))
        if square is not None:
            if (button == mouse.Button.LEFT and
                    square.state == Square.State.HIDDEN):
                self._reveal_square(square)
                self._setup_draw()
            elif (button == mouse.Button.RIGHT and
                    square.state == Square.State.HIDDEN):
                square.state = Square.State.FLAGGED
                self._setup_draw()
            elif (button == mouse.Button.RIGHT and
                    square.state == Square.State.FLAGGED):
                square.state = Square.State.HIDDEN
                self._setup_draw()

    def _reveal_square(self, square):
        # Set for this square, and if it doesn't have any bomb neighbours,
        # reveal them!
        if square.state == Square.State.HIDDEN:
            square.state = Square.State.REVEALED
            if square.bombs_nearby == 0:
                for neighbour in square.neighbours:
                    self._reveal_square(neighbour)

    def _create_board(self, board_str):
        lines = [l for l in board_str.split("\n") if len(l) > 0]
        self._rows = len(lines)
        self._cols = len(lines[0])

        # Work out square size
        self._square_size = int(min(self._WIDTH / self._cols,
                                    self._HEIGHT / self._rows))

        def get_type(c):
            return Square.Type.MINE if c == "x" else Square.Type.EMPTY

        def get_rect(r, c):
            return (c * self._square_size,
                    r * self._square_size,
                    self._square_size, self._square_size)

        for row, line in enumerate(lines):
            self._board.append([Square(get_type(c), get_rect(row, col))
                                for col, c in enumerate(line)])

        # Now calculate neighbours
        for row in range(self._rows):
            for col in range(self._cols):
                neighbours = []
                for offset in itertools.product((-1, 0, 1), repeat=2):
                    neighbour = (row + offset[0], col + offset[1])
                    if (neighbour != (row, col) and
                            0 <= neighbour[0] < self._rows and
                            0 <= neighbour[1] < self._cols):
                        neighbours.append(
                            self._board[neighbour[0]][neighbour[1]])

                self._board[row][col].set_neighbours(neighbours)

    def _hit_square(self, pos):
        for square in itertools.chain.from_iterable(self._board):
            if square.collidepoint(pos):
                return square

        return None

    def _setup_draw(self):
        self._draw_surface = self._surface.copy()

        for row in self._board:
            for square in row:
                self._draw_surface.blit(square.get_surface(),
                                        square.rect[:2])

    def _screen_to_board_pos(self, screen_pos):
        return screen_pos[0] - self._pos[0], screen_pos[1] - self._pos[1]


class Square:

    """Class representing a square on the board."""

    @unique
    class Type(Enum):
        EMPTY = 1
        MINE = 2

    @unique
    class State(Enum):
        HIDDEN = 1
        FLAGGED = 2
        REVEALED = 3

    def __init__(self, square_type, rect):
        # Square type
        self.type = square_type

        # Current state
        self.state = self.State.HIDDEN

        # Rectange representing the square's position on the board.
        self.rect = rect

        # List of neighbour squares
        self.neighbours = None

        # Count of neighbours who are bombs
        self.bombs_nearby = 0

        # Create our surfaces
        self._surfaces = {
            Square.State.HIDDEN: pygame.Surface(self.rect[2:]),
            Square.State.FLAGGED: pygame.Surface(self.rect[2:]),
            Square.State.REVEALED: pygame.Surface(self.rect[2:]),
        }

        self._surfaces[Square.State.HIDDEN].fill((180, 180, 180))
        self._surfaces[Square.State.FLAGGED].fill((20, 200, 20))
        self._surfaces[Square.State.REVEALED].fill((255, 255, 255))

        for surface in self._surfaces.values():
            pygame.draw.rect(surface, (0, 0, 0),
                             (0, 0, self.rect[2], self.rect[3]), 1)

        # If we are a mine, then add mine
        if self.type == Square.Type.MINE:
            center = (int(self.rect[2] / 2), int(self.rect[3] / 2))
            pygame.draw.circle(self._surfaces[Square.State.REVEALED],
                               (0, 0, 0),
                               center,
                               center[0] - 2,
                               0)

    def get_surface(self):
        return self._surfaces[self.state]

    def collidepoint(self, board_pos):
        return pygame.Rect(self.rect).collidepoint(board_pos)

    def set_neighbours(self, neighbours):
        self.neighbours = neighbours

        # Count bombs!
        self.bombs_nearby = len([n for n in neighbours
                                 if n.type == Square.Type.MINE])

        # Draw the number on our revealed surface
        if self.bombs_nearby > 0:
            font = load_font(None, self.rect[2] - 3)
            text = font.render(str(self.bombs_nearby), True, (0, 0, 0))

            surface = self._surfaces[Square.State.REVEALED]
            surface_rect = surface.get_rect()
            text_rect = text.get_rect()
            surface.blit(text,
                         (int(surface_rect[2] / 2 - text_rect[2] / 2),
                          int(surface_rect[3] / 2 - text_rect[3] / 2)))



