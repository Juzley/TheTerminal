"""Hardware program classes."""

import pygame
import random

import mouse
from . import program
from resources import load_image, load_font


class BoardDefinition:

    boards = []

    """Defines a board layout. """
    def __init__(self, filename, assets, *pair_positions):
        """

        Initialize the board.

        Arguments:
            filename:
            the image to use for the board

            assets:
            List of image, position pairs for additional static assets to add to
            board.

            pair_positions:
            A pair_position is a tuple of (chip position, resistor position).
            This argument can be repeated multiple times for multiple groups.

        """

        self.filename = filename
        self.positions = pair_positions
        self.assets = assets

        BoardDefinition.boards.append(self)


"""Define boards."""
BoardDefinition("media/motherboard4.png",
                [("media/cpu.png", (420, 240))],
                ((10, 10), (10, 100)),
                ((10, 210), (10, 300)),
                ((210, 10), (210, 100)),
                ((210, 210), (210, 300)))

BoardDefinition("media/motherboard3.png",
                [("media/cpu.png", (420, 240))],
                ((10, 10), (10, 100)),
                ((110, 210), (110, 300)),
                ((210, 10), (210, 100)))


"""Chip codes parameters"""
CHIP_CODE_LENGTHS = (4, 5, 5, 5, 6, 7, 7, 7)
CHIP_CODE_CHARS = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")
CHIP_CODE_END_CHARS = ("0", "0", "1", "2", "3", "4", "A", "B")


"""Resistor codes"""
RESISTOR_CODES = {
    "rryg": 10,
    "rByg": 20,
    "ybbr": 30,
    "rbby": 40,
    "grbg": 50,
    "gBbg": 60,
}


# Rows are: ohms
# Columns are: chip code last char - Odd, even, zero, letter
RULES_TABLE1 = {
    10: ["N", "C", "R", "B"],
    20: ["C", "C", "B", "R"],
    30: ["R", "R", "C", "C"],
    40: ["B", "N", "R", "C"],
    50: [1,    4,  "N",   3],
    60: [5,   "C",   2,   6],
}


# Rows are: row numbers referred to from table1
# Columns are: terminal name last char - Odd, even, zero, letter
RULES_TABLE2 = {
    1: ["C", "N", "R", "C"],
    2: ["R", "C", "R", "C"],
    3: ["R", "B", "C", "R"],
    4: ["C", "R", "C", "R"],
    5: ["N", "C", "R", "B"],
    6: ["C", "C", "C", "R"],
}


# Get column in rules table based on chip/terminal code
def col_from_code(code):
    # Look at last character, return:
    #   0 if odd
    #   1 if even
    #   2 if zero
    #   3 if letter
    try:
        num = int(code[-1], 10)
    except ValueError:
        num = None

    if num is None:
        return 3
    elif num == 0:
        return 2
    elif num % 2 == 0:
        return 1
    else:
        return 0


class ComponentPair:

    """Pair of chip and resister components that are validated together."""

    def __init__(self, terminal_id,
                 chip_code, resistor_code, chip_pos, resistor_pos):
        self._chip = Chip(chip_code, chip_pos)
        self._resistor = Resistor(resistor_code, resistor_pos)
        self._terminal_id = terminal_id

    def setup_draw(self, surface):
        self._chip.setup_draw(surface)
        self._resistor.setup_draw(surface)

    def hit_component(self, pos):
        if self._chip.collidepoint(pos):
            return self._chip
        elif self._resistor.collidepoint(pos):
            return self._resistor
        else:
            return None

    @property
    def has_disabled(self):
        """Does this component group have any disabled elements?"""
        return self._chip.disabled or self._resistor.disabled

    @property
    def is_correct(self):
        """
        Is this component group in a correct state?

        """
        actions = {
            "N": (lambda: not self._chip.disabled and
                  not self._resistor.disabled),
            "C": (lambda: self._chip.disabled and
                  not self._resistor.disabled),
            "R": (lambda: not self._chip.disabled and
                  self._resistor.disabled),
            "B": (lambda: self._chip.disabled and
                  self._resistor.disabled),
        }

        # First get the action based on resister value and chip code
        action = self._action_from_table(RULES_TABLE1,
                                         RESISTOR_CODES[self._resistor.code],
                                         self._chip.code)
        if action in actions:
            return actions[action]()
        else:
            # Action is table2 row, so get action based on this and terminal id
            action = self._action_from_table(RULES_TABLE2,
                                             action,
                                             self._terminal_id)
            return actions[action]()

    @staticmethod
    def _action_from_table(table, key, code):
        return table[key][col_from_code(code)]


class HardwareInspect(program.TerminalProgram):

    """The hardware inspection program."""

    _BOARD_Y = 50

    _BUTTON_TEXT = "Reboot system"
    _BUTTON_COLOUR = (255, 255, 255)

    """The properties of this program."""
    PROPERTIES = program.ProgramProperties(is_graphical=True,
                                           suppress_success=True)

    def __init__(self, terminal):
        """Initialize the class."""
        super().__init__(terminal)

        # The draw surface
        self._draw_surface = None

        # Grab a board definition at random
        board_def = random.choice(BoardDefinition.boards)

        self._component_pairs = self._create_component_pairs(board_def)

        # Create the board
        self._board = load_image(board_def.filename)

        # Add the static assets
        for filename, pos in board_def.assets:
            image = load_image(filename)
            self._board.blit(image, pos)

        # Set the board position
        screen_rect = pygame.display.get_surface().get_rect()
        board_rect = self._board.get_rect()
        self._board_pos = (int((screen_rect[2] / 2) - (board_rect[2] / 2)),
                           self._BOARD_Y)

        # Create the button
        font = load_font(None, 40)
        self._button_text = font.render(self._BUTTON_TEXT, True,
                                        self._BUTTON_COLOUR)
        button_rect = self._button_text.get_rect()
        self._button_pos = (self._board_pos[0] + board_rect[2] - button_rect[2],
                            self._board_pos[1] + board_rect[3] + 10)
        self._button_rect = button_rect.move(self._button_pos)

        self._completed = False
        self._exited = False

    @property
    def help(self):
        """Get the help string for the program."""
        return "Suspend system and modify hardware."

    @property
    def security_type(self):
        """Get the scurity type for the program."""
        return "hardware security"

    def start(self):
        # Reset board
        self._setup_draw()
        self._exited = False

    def completed(self):
        """Indicate whether the program was completed."""
        return self._completed

    def exited(self):
        """Indicate whether the program has exited."""
        return self.completed() or self._exited

    def on_mousemove(self, pos):
        if self._hit_component(pos) is not None or self._is_in_button(pos):
            mouse.current.set_cursor(mouse.Cursor.HAND)
        else:
            mouse.current.set_cursor(mouse.Cursor.ARROW)

    def on_mouseclick(self, button, pos):
        """Detect whether the user clicked the program."""
        if button == mouse.Button.LEFT:
            # Find the component clicked
            component = self._hit_component(pos)
            if component is not None:
                component.toggle()
                self._setup_draw()
            elif self._is_in_button(pos):
                # If nothing has been disabled, then just reboot. Else check
                # that there are no incorrect groups.
                if len([p for p in self._component_pairs
                        if p.has_disabled]) == 0:
                    self._terminal.reboot()
                    self._exited = True
                elif len([p for p in self._component_pairs
                          if not p.is_correct]) == 0:
                    self._completed = True
                    self._terminal.reboot(self.success_syslog)
                else:
                    self._exited = True
                    self._terminal.reboot(self.failure_prefix +
                                          "Hardware error: clock skew "
                                          "detected. Recovering")
                    self._terminal.reduce_time(10)

    def draw(self):
        """Draw the program."""
        screen = pygame.display.get_surface()
        screen.blit(self._draw_surface, self._board_pos)

        # Draw button
        screen.blit(self._button_text, self._button_pos)
        pygame.draw.rect(screen,
                         self._BUTTON_COLOUR,
                         self._button_rect,
                         1)

    def _create_component_pairs(self, board_def):
        component_pairs = []

        def chip_code():
            code = ""
            for _ in range(random.choice(CHIP_CODE_LENGTHS) - 1):
                code += random.choice(CHIP_CODE_CHARS)
            code += random.choice(CHIP_CODE_END_CHARS)
            return code

        resistor_codes = list(RESISTOR_CODES.keys())

        # Keep generating sets until we get one that has a pair that isn't
        # correct yet
        while len([c for c in component_pairs if not c.is_correct]) == 0:
            component_pairs = [ComponentPair(self._terminal.id_string,
                                             chip_code(),
                                             random.choice(resistor_codes),
                                             c_pos, r_pos)
                               for c_pos, r_pos in board_def.positions]

        return component_pairs

    def _setup_draw(self):
        self._draw_surface = self._board.copy()

        for pair in self._component_pairs:
            pair.setup_draw(self._draw_surface)

    def _is_in_button(self, pos):
        return self._button_rect.collidepoint(pos)

    def _hit_component(self, pos):
        board_pos = self._screen_to_board_pos(pos)
        for pair in self._component_pairs:
            component = pair.hit_component(board_pos)
            if component is not None:
                return component

        return None

    def _screen_to_board_pos(self, pos):
        return pos[0] - self._board_pos[0], pos[1] - self._board_pos[1]


class Component:
    """"Base class representing active hardware component on a motherboard."""

    def __init__(self, code, pos):
        self.disabled = False
        self.code = code

        self._image = None
        self._pos = pos

    def toggle(self):
        self.disabled = not self.disabled

    def create_image(self):
        pass

    def setup_draw(self, surface):
        # If we don't have an image yet, then create it
        if self._image is None:
            self.create_image()

        # If disabled, grey out
        if self.disabled:
            image = self._image.copy()
            rect = self._image.get_rect()
            dark = pygame.Surface((rect[2], rect[3]),
                                  flags=pygame.SRCALPHA)
            dark.fill((100, 100, 100, 0))
            image.blit(dark, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
            surface.blit(image, self._pos)
        else:
            surface.blit(self._image, self._pos)

    def collidepoint(self, pos):
        return self._image.get_rect().move(self._pos).collidepoint(pos)


class Resistor(Component):

    """Resister component."""

    _COLOURS = {
        "r": (190, 50, 50),
        "g": (110, 175, 55),
        "b": (70, 70, 230),
        "y": (220, 200, 90),
        "B": (0, 0, 0),
    }

    _LINE_WIDTH = 5
    _BACKGROUND_COLOUR = (216, 192, 169)
    _AREA_START = 43
    _AREA_WIDTH = 94

    def create_image(self):
        # Take a copy as we are going to edit it!
        self._image = load_image('media/resistor.png').copy()

        # Create a surface to draw the lines on, so we can blend it with the
        # resistor and have it ignore the portions of the lines outside the
        # resistor
        height = self._image.get_rect()[3]
        surface = pygame.Surface((self._AREA_WIDTH, height))
        surface.fill((255, 255, 255))
        surface.set_alpha(0)

        # Work out the spacing
        gap = (self._AREA_WIDTH - 2 * self._LINE_WIDTH) / (len(self.code) + 1)

        # Add lines
        for idx, colour in enumerate(self.code):
            line_x = self._LINE_WIDTH + idx * gap
            pygame.draw.line(surface,
                             self._COLOURS[colour],
                             (line_x, 0),
                             (line_x, height),
                             self._LINE_WIDTH)

        # Add our surface
        self._image.blit(surface, (self._AREA_START, 0),
                         special_flags=pygame.BLEND_RGBA_MULT)


class Chip(Component):

    """Chip component."""

    def create_image(self):
        # Take a copy as we are going to edit it!
        self._image = load_image('media/chip.png').copy()

        # Add code to the chip
        font = load_font(None, 20)
        text = font.render(self.code, True, (255, 255, 255))

        image_rect = self._image.get_rect()
        text_rect = text.get_rect()
        self._image.blit(text,
                         (image_rect[2] - text_rect[2] - 5,
                          image_rect[3] - text_rect[3] - 15))
