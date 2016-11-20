
import itertools
import math
import pygame
import random
from enum import Enum, unique

import mouse
from . import program
from resource import load_font


class MineHunt(program.TerminalProgram):

    """Minehunt program."""

    """The properties of this program."""
    PROPERTIES = program.ProgramProperties(is_graphical=True)

    _TIMER_Y = 50
    _BOARD_Y = 80
    _BOARD_MAX_WIDTH = 600
    _BOARD_MAX_HEIGHT = 400
    _STATUS_FONT_SIZE = 30
    _END_FONT_SIZE = 40
    _TIMER_FONT_SIZE = 40
    _TIME_LIMIT = 30 * 1000

    def __init__(self, terminal):
        """Initialize the class."""
        super().__init__(terminal)

        self._puzzle = random.choice(Puzzle.puzzles)

        self._completed = False
        self._exited = False
        self._board = Board(self._puzzle.board_def,
                            self._BOARD_MAX_WIDTH, self._BOARD_MAX_HEIGHT)
        self._start_time = None
        self._secs_left = None

        screen_rect = pygame.display.get_surface().get_rect()
        self._board_pos = (int((screen_rect[2] / 2) - (self._board.width / 2)),
                           self._BOARD_Y)

        self._status_font = load_font(None, self._STATUS_FONT_SIZE)
        self._timer_font = load_font(None, self._TIMER_FONT_SIZE)
        end_font = load_font(None, self._END_FONT_SIZE)
        self._game_over_texts = [
            end_font.render("Game over!!", True, (255, 255, 255)),
            end_font.render("Press R to retry, or Q to quit",
                            True, (255, 255, 255)),
        ]
        self._game_won_texts = [
            end_font.render("Game completed!!", True, (255, 255, 255)),
            end_font.render("Press R to retry, or Q to quit",
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
        self._start_time = self._terminal.time
        self._secs_left = self._TIME_LIMIT / 1000

    def completed(self):
        """Indicate whether the program was completed."""
        return self._completed

    def exited(self):
        """Indicate whether the program has exited."""
        return self.completed() or self._exited

    def on_keypress(self, key, key_unicode):
        """Handle a user keypress."""
        if self._board.state != Board.State.PLAYING:
            if key == pygame.K_r:
                self.start()
            elif key == pygame.K_q:
                self._exited = True

    def on_mousemove(self, pos):
        pass

    def on_mouseclick(self, button, pos):
        """Detect whether the user clicked the program."""
        board_pos = (pos[0] - self._board_pos[0], pos[1] - self._board_pos[1])
        self._board.on_mouseclick(button, board_pos)

    def run(self):
        # Get time left
        if self._board.state == Board.State.PLAYING:
            time_left = (self._TIME_LIMIT - (self._terminal.time -
                         self._start_time))
            if time_left <= 0:
                time_left = 0
                self._board.state = Board.State.TIME_OUT

            self._secs_left = math.ceil(time_left / 1000)
        else:
            # Did the user end with the correct time remaining?
            success = (self._puzzle.timeleft_multiple is None or
                       (self._secs_left % self._puzzle.timeleft_multiple) == 0)

            # Have all mines been flagged, and if there is a mine to be clicked,
            # has it been clicked?
            if success:
                for loc, square in self._board.mines:
                    # Do we have a victory mine, if so this mine should be
                    # clicked and not flagged.
                    #
                    # If not, then the mine should be flagged.
                    victory_mine = (self._puzzle.click_mine is not None and
                                    loc == self._puzzle.click_mine)
                    if victory_mine and square.state != Square.State.REVEALED:
                        success = False
                    elif (not victory_mine and
                          square.state != Square.State.FLAGGED):
                        success = False

            # Have only mines been flagged?
            if success:
                for loc, square in self._board.flags:
                    if square.type != Square.Type.MINE:
                        success = False

            # Display crash message if success
            if success:
                # TODO: Better crash dump message
                self._terminal.output(["CRASH ALERT: minehunt crashed -- "
                                       "segfault at address 0x445d9ee9"])

            self._completed = success

    def draw(self):
        """Draw the program."""
        screen = pygame.display.get_surface()
        screen.blit(self._board.draw_surface,
                    self._board_pos)
        screen_rect = screen.get_rect()

        # Draw timer
        text = self._timer_font.render("Time left: {}s"
                                       .format(self._secs_left),
                                       True, (255, 255, 255))
        screen.blit(text, (self._board_pos[0], self._TIMER_Y))

        # Have we hit a mine? Draw game over text
        # TODO: have a game surface and draw this on
        if self._board.state != Board.State.PLAYING:
            # Dim the board
            dim = pygame.Surface((self._board.width, self._board.height),
                                 flags=pygame.SRCALPHA)
            if self._board.state == Board.State.CLEARED:
                dim.fill((255, 100, 255, 0))
            else:
                dim.fill((100, 255, 255, 0))
            screen.blit(dim, self._board_pos,
                        special_flags=pygame.BLEND_RGBA_SUB)

            # Get the end game texts
            texts = (self._game_won_texts
                     if self._board.state == Board.State.CLEARED else
                     self._game_over_texts)

            total_height = sum(t.get_rect()[3] for t in texts)
            text_y = self._board_pos[1] + self._board.height + 5

            # Draw text
            for text in texts:
                text_rect = text.get_rect()
                text_x = int(screen_rect[2] / 2 - text_rect[2] / 2)
                screen.blit(text, (text_x, text_y))

                text_y += text_rect[3]

        else:
            # Draw mines found text
            text = self._status_font.render("Mines flagged: {} / {}"
                                            .format(self._board.flag_count,
                                                    self._board.mine_count),
                                            True, (255, 255, 255))
            text_x = int(screen_rect[2] / 2 - text.get_rect()[2] / 2)
            text_y = self._board_pos[1] + self._board.height + 5
            screen.blit(text, (text_x, text_y))


class Board:
    @unique
    class State(Enum):
        PLAYING = 1
        MINE_HIT = 2
        TIME_OUT = 3
        CLEARED = 4

    def __init__(self, board_def, max_width, max_height):
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
        self._create_board(board_def, max_width, max_height)

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

    @property
    def mines(self):
        for row in range(self._rows):
            for col in range(self._cols):
                square = self._board[row][col]
                if square.type == Square.Type.MINE:
                    yield ((row, col), square)

    @property
    def flags(self):
        for row in range(self._rows):
            for col in range(self._cols):
                square = self._board[row][col]
                if square.type == Square.State.FLAGGED:
                    yield ((row, col), square)

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

    def _create_board(self, board_def, max_width, max_height):
        self._rows = len(board_def)
        self._cols = len(board_def[0])

        # Work out square size
        self._square_size = int(min(max_width / self._cols,
                                    max_height / self._rows))

        def get_type(c):
            return Square.Type.MINE if c == "x" else Square.Type.EMPTY

        def get_rect(r, c):
            return (c * self._square_size,
                    r * self._square_size,
                    self._square_size, self._square_size)

        for row, line in enumerate(board_def):
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
    _MINE_SCALE_FACTOR = 0.8

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
                               int(self._MINE_SCALE_FACTOR * center[0]),
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


class Puzzle:
    puzzles = []

    def __init__(self, board_str, timeleft_multiple=None, click_mine=None):
        self.timeleft_multiple = timeleft_multiple
        self.click_mine = click_mine
        Puzzle.puzzles.append(self)

        # Parse the board
        lines = [l for l in board_str.split("\n") if len(l) > 0]
        self.board_def = [[c for c in line]
                          for line in lines]

        # Make sure that there is a mine in the mine loc
        if click_mine is not None:
            assert self.board_def[click_mine[0]][click_mine[1]] == "x", \
                   "No mine at location {}".format(click_mine)


Puzzle(
"""
.....x
x.....
......
...x..
......
xx....
""",
timeleft_multiple=3)

Puzzle("""
.....x...
x........
.........
...x.....
........x
xx......x
""",
timeleft_multiple=3,
click_mine=(5, 8))

Puzzle("""
.....x
......
......
...x..
......
xx....
..x...
.x....
""",
timeleft_multiple=4)
