
import itertools
import pygame
import random
from enum import Enum, unique

import mouse
from . import program
from resource import load_font


class MineHunt(program.TerminalProgram):

    """Minehunt program."""

    """The properties of this program."""
    PROPERTIES = program.ProgramProperties(is_graphical=True,
                                           suppress_success=True)

    _BOARD_Y = 50
    _FONT_SIZE = 40

    def __init__(self, terminal):
        """Initialize the class."""
        super().__init__(terminal)

        self._completed = False
        self._exited = False
        self._board = Board(random.choice(BOARDS))

        screen_rect = pygame.display.get_surface().get_rect()
        self._board_pos = (int((screen_rect[2] / 2) - (self._board.width / 2)),
                           self._BOARD_Y)

        self._font = load_font(None, self._FONT_SIZE)
        self._game_over_texts = [
            self._font.render("Game over!!", True, (255, 255, 255)),
            self._font.render("Press R to retry, or Q to quit",
                              True, (255, 255, 255)),
        ]
        self._game_won_texts = [
            self._font.render("Game completed!!", True, (255, 255, 255)),
            self._font.render("Press R to retry, or Q to quit",
                              True, (255, 255, 255)),
        ]

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
        self._board.reset()
        self._exited = False

    def completed(self):
        """Indicate whether the program was completed."""
        return self._completed

    def exited(self):
        """Indicate whether the program has exited."""
        return self.completed() or self._exited

    def on_keypress(self, key, key_unicode):
        """Handle a user keypress."""
        if self._board.state != Board.State.PLAYING:
            print(key)
            if key == pygame.K_r:
                self._board.reset()
            elif key == pygame.K_q:
                self._exited = True

    def on_mousemove(self, pos):
        pass

    def on_mouseclick(self, button, pos):
        """Detect whether the user clicked the program."""
        board_pos = (pos[0] - self._board_pos[0], pos[1] - self._board_pos[1])
        self._board.on_mouseclick(button, board_pos)

    def draw(self):
        """Draw the program."""
        screen = pygame.display.get_surface()
        screen.blit(self._board.draw_surface,
                    self._board_pos)
        screen_rect = screen.get_rect()

        # Have we hit a mine? Draw game over text
        # TODO: have a game surface and draw this on
        if self._board.state != Board.State.PLAYING:
            texts = (self._game_over_texts
                     if self._board.state == Board.State.MINE_HIT else
                     self._game_won_texts)
            text_y = self._board_pos[1] + self._board.height + 5
            for text in texts:
                text_rect = text.get_rect()
                text_x = int(screen_rect[2] / 2 - text_rect[2] / 2)
                screen.blit(text, (text_x, text_y))

                text_y += text_rect[3]
        else:
            # Draw mines found text
            text = self._font.render("Mines flagged: {} / {}"
                                     .format(self._board.flag_count,
                                             self._board.mine_count),
                                     True, (255, 255, 255))
            text_x = int(screen_rect[2] / 2 - text.get_rect()[2] / 2)
            text_y = self._board_pos[1] + self._board.height + 5
            screen.blit(text, (text_x, text_y))


class Board:
    _MAX_WIDTH = 400
    _MAX_HEIGHT = 400

    @unique
    class State(Enum):
        PLAYING = 1
        MINE_HIT = 2
        CLEARED = 3

    def __init__(self, board_str):
        # Board is a 2D array of Squares, indexed by row then col
        self._board = []

        # Number of rows and cols
        self._rows = 0
        self._cols = 0

        # Square size
        self._square_size = 0

        # Surface for the next draw
        self.draw_surface = None

        # Board state
        self.state = Board.State.PLAYING

        # Total mine count
        self.mine_count = 0

        # Create the board
        self._create_board(board_str)

        # Set width and height
        self.width = self._cols * self._square_size
        self.height = self._rows * self._square_size

        # Create the board
        self._surface = pygame.Surface((self.width, self.height))
        self._surface.fill((255, 255, 255))

        self._setup_draw()

    @property
    def flag_count(self):
        return len([s for s in itertools.chain.from_iterable(self._board)
                    if s.state == Square.State.FLAGGED])

    def reset(self):
        self.state = Board.State.PLAYING
        for square in itertools.chain.from_iterable(self._board):
            square.state = Square.State.HIDDEN
        self._setup_draw()

    def on_mouseclick(self, button, pos):
        if self.state != Board.State.PLAYING:
            return

        square = self._hit_square(pos)
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

            # Game is over when mines have been flagged and all squares
            # revealed
            if len([
                s for s in itertools.chain.from_iterable(self._board)
                if s.state == Square.State.HIDDEN or
                (s.state == Square.State.FLAGGED and
                 s.type == Square.Type.EMPTY) or
                (s.state != Square.State.FLAGGED and
                 s.type == Square.Type.MINE)]) == 0:
                self.state = Board.State.CLEARED

    def _reveal_square(self, square):
        # Set for this square, and if it doesn't have any mine neighbours,
        # reveal them!
        if (square.state == Square.State.HIDDEN and
                square.type == Square.Type.EMPTY):
            square.state = Square.State.REVEALED
            if square.mines_nearby == 0:
                for neighbour in square.neighbours:
                    self._reveal_square(neighbour)
        elif (square.state == Square.State.HIDDEN and
              square.type == Square.Type.MINE):
            # We have revealed a Mine!
            square.state = Square.State.REVEALED
            self.state = Board.State.MINE_HIT

    def _create_board(self, board_str):
        lines = [l for l in board_str.split("\n") if len(l) > 0]
        self._rows = len(lines)
        self._cols = len(lines[0])

        # Work out square size
        self._square_size = int(min(self._MAX_WIDTH / self._cols,
                                    self._MAX_HEIGHT / self._rows))

        def get_type(c):
            return Square.Type.MINE if c == "x" else Square.Type.EMPTY

        def get_rect(r, c):
            return (c * self._square_size,
                    r * self._square_size,
                    self._square_size, self._square_size)

        for row, line in enumerate(lines):
            self._board.append([Square(get_type(c), get_rect(row, col))
                                for col, c in enumerate(line)])

        # Now calculate neighbours and mines
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
                square = self._board[row][col]
                square.set_neighbours(neighbours)
                if square.type == Square.Type.MINE:
                    self.mine_count += 1

    def _hit_square(self, pos):
        for square in itertools.chain.from_iterable(self._board):
            if square.collidepoint(pos):
                return square

        return None

    def _setup_draw(self):
        self.draw_surface = self._surface.copy()

        for square in itertools.chain.from_iterable(self._board):
            self.draw_surface.blit(square.get_surface(),
                                   square.rect[:2])


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

    _FLAG_HEIGHT_FACTOR = 0.6
    _FLAG_POLE_WIDTH = 3
    _FLAG_SIZE_FACTOR = 0.6

    def __init__(self, square_type, rect):
        # Square type
        self.type = square_type

        # Current state
        self.state = self.State.HIDDEN

        # Rectangle representing the square's position on the board.
        self.rect = rect

        # List of neighbour squares
        self.neighbours = None

        # Count of neighbours who are mines
        self.mines_nearby = 0

        # Create our surfaces
        self._surfaces = {
            Square.State.HIDDEN: pygame.Surface(self.rect[2:]),
            Square.State.FLAGGED: pygame.Surface(self.rect[2:]),
            Square.State.REVEALED: pygame.Surface(self.rect[2:]),
        }

        self._surfaces[Square.State.HIDDEN].fill((180, 180, 180))
        self._surfaces[Square.State.FLAGGED].fill((180, 180, 180))
        self._surfaces[Square.State.REVEALED].fill((255, 255, 255))

        for surface in self._surfaces.values():
            pygame.draw.rect(surface, (0, 0, 0),
                             (0, 0, self.rect[2], self.rect[3]), 1)

        # If we are a mine, then add mine to revealed square
        if self.type == Square.Type.MINE:
            center = (int(self.rect[2] / 2), int(self.rect[3] / 2))
            pygame.draw.circle(self._surfaces[Square.State.REVEALED],
                               (0, 0, 0),
                               center,
                               center[0] - 2,
                               0)

        # Add a flag to the flagged square
        flag = self._surfaces[Square.State.FLAGGED]
        pole_length = int(self.rect[3] * self._FLAG_HEIGHT_FACTOR)
        flag_size = int(pole_length * self._FLAG_SIZE_FACTOR)
        pole_gap = int((self.rect[3] - pole_length) / 2)
        x_coord = int(self.rect[2] / 2 - flag_size / 2 +
                      self._FLAG_POLE_WIDTH / 2)
        pygame.draw.line(flag, (0, 0, 0),
                         (x_coord, pole_gap),
                         (x_coord, self.rect[3] - pole_gap),
                         self._FLAG_POLE_WIDTH)
        pygame.draw.rect(flag, (255, 20, 20),
                         ((x_coord, pole_gap,
                           flag_size, int(flag_size * 0.9))),
                         0)

    def get_surface(self):
        return self._surfaces[self.state]

    def collidepoint(self, board_pos):
        return pygame.Rect(self.rect).collidepoint(board_pos)

    def set_neighbours(self, neighbours):
        self.neighbours = neighbours

        # Count mines!
        self.mines_nearby = len([n for n in neighbours
                                 if n.type == Square.Type.MINE])

        # Draw the number on our revealed surface
        if self.mines_nearby > 0:
            font = load_font(None, self.rect[2] - 3)
            text = font.render(str(self.mines_nearby), True, (0, 0, 0))

            surface = self._surfaces[Square.State.REVEALED]
            surface_rect = surface.get_rect()
            text_rect = text.get_rect()
            surface.blit(text,
                         (int(surface_rect[2] / 2 - text_rect[2] / 2),
                          int(surface_rect[3] / 2 - text_rect[3] / 2)))


BOARDS = (
"""
.....x
x.....
......
...x..
......
xx....
""",
"""
.....x...
x........
.........
...x.....
........x
xx......x
""",
"""
.....x
......
......
...x..
......
xx....
..x...
.x....
""",
)
