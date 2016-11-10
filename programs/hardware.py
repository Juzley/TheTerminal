"""Hardware program classes."""

import pygame
import random

import mouse
import util
from . import program


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
BoardDefinition("media/motherboard.png",
                [("media/cpu.png", (420, 240))],
                ((10, 10), (10, 100)),
                ((10, 210), (10, 300)),
                ((210, 10), (210, 100)),
                ((210, 210), (210, 300)))

"""Chip codes"""
# TODO: proper chip codes
CHIP_CODES = ("15835A", "3445", "453463", "3455345", "445BC")


"""Resistor codes"""
# TODO: proper resistor codes
RESISTOR_CODES = ("brrg", "bryb", "yyrr", "rrgr")


class ComponentPair:

    """Pair of chip and resister components that are validated together."""

    def __init__(self, chip_code, resistor_code, chip_pos, resistor_pos):
        self._chip = Chip(chip_code, chip_pos)
        self._resistor = Resistor(resistor_code, resistor_pos)

    def setup_draw(self, surface):
        self._chip.setup_draw(surface)
        self._resistor.setup_draw(surface)

    def get_component(self, pos):
        if self._chip.contains(pos):
            return self._chip
        elif self._resistor.contains(pos):
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
        # TODO: implement code checking logic from manual
        return (("g" in self._resistor.code) == self._resistor.disabled and
                ("A" in self._chip.code) == self._chip.disabled)


class HardwareInspect(program.TerminalProgram):

    """The hardware inspection program."""

    _BOARD_Y = 50

    _BUTTON_TEXT = "Reboot system"
    _BUTTON_COLOUR = (255, 255, 255)

    def __init__(self, terminal):
        """Initialize the class."""
        super().__init__(terminal)

        # The draw surface
        self._draw_surface = None

        # Grab a board definition at random
        board_def = random.choice(BoardDefinition.boards)

        self._component_pairs = self._create_component_pairs(board_def)

        # Create the board
        self._board = util.load_image(board_def.filename)

        # Add the static assets
        for filename, pos in board_def.assets:
            image = util.load_image(filename)
            self._board.blit(image, pos)

        # Set the board position
        screen_rect = pygame.display.get_surface().get_rect()
        board_rect = self._board.get_rect()
        self._board_pos = (int((screen_rect[2] / 2) - (board_rect[2] / 2)),
                           self._BOARD_Y)

        # Create the button
        font = pygame.font.Font(None, 40)
        self._button_text = font.render(self._BUTTON_TEXT, True,
                                        self._BUTTON_COLOUR)
        button_rect = self._button_text.get_rect()
        self._button_pos = (self._board_pos[0] + board_rect[2] - button_rect[2],
                            self._board_pos[1] + board_rect[3] + 10)
        self._button_rect = button_rect.move(self._button_pos)

        self._completed = False
        self._exited = False

    @classmethod
    def is_graphical(cls):
        """Indicate that this is a graphical program."""
        return True

    @property
    def help(self):
        """Get the help string for the program."""
        return "Inspect hardware."

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
        if self._get_component(pos) is not None or self._is_in_button(pos):
            mouse.current.set_cursor(mouse.Cursor.HAND)
        else:
            mouse.current.set_cursor(mouse.Cursor.ARROW)

    def on_mouseclick(self, button, pos):
        """Detect whether the user clicked the program."""
        if button == mouse.Button.LEFT:
            # Find the component clicked
            component = self._get_component(pos)
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

    @staticmethod
    def _create_component_pairs(board_def):
        component_pairs = []

        # Keep generating sets until we get one that has a pair that isn't
        # correct yet
        while len([c for c in component_pairs if not c.is_correct]) == 0:
            component_pairs = [ComponentPair(random.choice(CHIP_CODES),
                                             random.choice(RESISTOR_CODES),
                                             c_pos, r_pos)
                               for c_pos, r_pos in board_def.positions]

        return component_pairs

    def _setup_draw(self):
        self._draw_surface = self._board.copy()

        for pair in self._component_pairs:
            pair.setup_draw(self._draw_surface)

    def _is_in_button(self, pos):
        return (self._button_rect[0] <= pos[0] <=
                self._button_rect[0] + self._button_rect[2] and
                self._button_rect[1] <= pos[1] <=
                self._button_rect[1] + self._button_rect[3])

    def _get_component(self, pos):
        board_pos = self._screen_to_board_pos(pos)
        for pair in self._component_pairs:
            component = pair.get_component(board_pos)
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

    def contains(self, pos):
        x, y, width, height = self._image.get_rect()
        return (self._pos[0] <= pos[0] <= self._pos[0] + width and
                self._pos[1] <= pos[1] <= self._pos[1] + height)


class Resistor(Component):

    """Resister component."""

    _COLOURS = {
        "r": (190, 50, 50),
        "g": (110, 175, 55),
        "b": (70, 70, 230),
        "y": (220, 190, 90),

    }

    _LINE_WIDTH = 5
    _BACKGROUND_COLOUR = (216, 192, 169)
    _AREA_START = 42
    _AREA_WIDTH = 94

    def create_image(self):
        self._image = util.load_image('media/resistor.png')

        # Create a surfance to draw the lines on
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
        self._image = util.load_image('media/chip.png')

        # Add code to the chip
        font = pygame.font.Font(None, 20)
        text = font.render(self.code, True, (0, 0, 0))

        image_rect = self._image.get_rect()
        text_rect = text.get_rect()
        self._image.blit(text,
                         (image_rect[2] - text_rect[2] - 5,
                          image_rect[3] - text_rect[3] - 15))
