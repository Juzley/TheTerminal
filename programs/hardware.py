"""Hardware program classes."""

import pygame

import mouse
import util
from . import program


class Component:

    """Base class representing a hardware component on a motherboard."""

    def __init__(self, filename, pos, correct):
        self.disabled = False
        self.correct = correct
        self._surface = util.load_image(filename)
        self._pos = pos

    def draw(self):
        screen = pygame.display.get_surface()
        screen.blit(self._surface, self._pos)
        if self.disabled:
            rect = self._surface.get_rect()
            overlay = pygame.Surface((rect[2], rect[3]))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(100)
            screen.blit(overlay, self._pos)

    def toggle(self):
        self.disabled = not self.disabled

    def contains(self, pos):
        x, y, width, height = self._surface.get_rect()
        return (self._pos[0] <= pos[0] <= self._pos[0] + width and
                self._pos[1] <= pos[1] <= self._pos[1] + height)


class Resistor1(Component):

    """Resister component."""

    def __init__(self, *args):
        super().__init__('media/resistor1.png', *args)


class Resistor2(Component):

    """Resister component."""

    def __init__(self, *args):
        super().__init__('media/resistor2.png', *args)


class Chip(Component):

    """Chip component."""

    def __init__(self, *args):
        super().__init__('media/chip.png', *args)


_MOTHERBOARD1 = [
    (Resistor1, 20, 20, True),
    (Resistor2, 200, 20, False),
    (Chip, 300, 200, False),
]


class Motherboard(program.TerminalProgram):

    """Motherboard inspection program."""

    _BOARD_IMAGE = "media/motherboard.png"
    _BOARD_POS = (80, 50)

    _BUTTON_POS = (500, 510)
    _BUTTON_TEXT = "Reboot system"
    _BUTTON_COLOUR = (255, 255, 255)

    def __init__(self, terminal):
        """Initialize the class."""
        super().__init__(terminal)

        # Get board
        self._board = util.load_image(self._BOARD_IMAGE)

        # Background
        self._background = pygame.Surface((800, 600))
        self._background.fill((0, 0, 0))

        # Add button to background
        font = pygame.font.Font(None, 40)
        button_text = font.render(self._BUTTON_TEXT, True, self._BUTTON_COLOUR)
        self._background.blit(button_text, self._BUTTON_POS)
        self._button_rect = button_text.get_rect().move(self._BUTTON_POS)
        pygame.draw.rect(self._background,
                         self._BUTTON_COLOUR,
                         self._button_rect,
                         1)

        # Create components, positioning them relative to board
        self._components = [
            el((x + self._BOARD_POS[0], y + self._BOARD_POS[1]), c)
            for el, x, y, c in _MOTHERBOARD1
        ]

        self._completed = False
        self._exited = False

    @classmethod
    def is_graphical(cls):
        """Indicate that this is a graphical program."""
        return True

    @property
    def help(self):
        return "Inspect hardware."

    @property
    def security_type(self):
        return "hardware security"

    def start(self):
        # Reset board
        self._reset_board()
        self._exited = False

    def draw(self):
        """Draw the program."""

        screen = pygame.display.get_surface()
        screen.blit(self._background, (0, 0))
        screen.blit(self._board, self._BOARD_POS)

        # Draw components
        for component in self._components:
            component.draw()

    def on_mouseclick(self, button, pos):
        """Detect whether the user clicked the program."""
        if button == mouse.Button.LEFT:
            # Find the component clicked
            component = self._get_component(pos)
            if component is not None:
                component.toggle()
            elif self._is_in_button(pos):
                # If all the correct components have been correctly disabled,
                # and no incorrect ones have, then we are done!
                #
                # If nothing has been disabled, then just reboot
                if len([c for c in self._components
                        if c.disabled]) == 0:
                    self._terminal.reboot()
                    self._exited = True
                elif len([c for c in self._components
                          if c.disabled != c.correct]) == 0:
                    self._completed = True
                    self._terminal.reboot()
                else:
                    self._exited = True
                    self._terminal.reboot(self.failure_prefix +
                                          "Hardware error: clock skew "
                                          "detected. Recovering")
                    self._terminal.reduce_time(10)

    def on_mousemove(self, pos):
        if self._get_component(pos) is not None or self._is_in_button(pos):
            mouse.current.set_cursor(mouse.Cursor.HAND)
        else:
            mouse.current.set_cursor(mouse.Cursor.ARROW)

    def completed(self):
        """Indicate whether the program was completed."""
        return self._completed

    def exited(self):
        """Indicate whether the program has exited."""
        return self.completed() or self._exited

    def _get_component(self, pos):
        match = [c for c in self._components if c.contains(pos)]
        if len(match) > 0:
            return match[0]
        else:
            return None

    def _is_in_button(self, pos):
        return (self._button_rect[0] <= pos[0] <=
                self._button_rect[0] + self._button_rect[2] and
                self._button_rect[1] <= pos[1] <=
                self._button_rect[1] + self._button_rect[3])

    def _reset_board(self):
        for component in self._components:
            component.disabled = False


class HardwareInspect(program.TerminalProgram):

    """Program to test the graphical program handling."""

    _NO_CHIP_CODE = 255
    _RESET_CODE = 244

    def __init__(self, terminal):
        """Initialize the class."""
        super().__init__(terminal)

        # TODO: Load this from metadata).
        self._chips = {0: ('S3411', pygame.Rect(100, 100, 50, 50)),
                       1: ('S3412', pygame.Rect(100, 200, 50, 50)),
                       2: ('S3413', pygame.Rect(100, 300, 50, 50)),
                       3: ('S3414', pygame.Rect(100, 400, 50, 50))}
        self._reset_rect = pygame.Rect(200, 100, 50, 50)

        # TODO: Load image from disk.
        self._board = pygame.Surface((600, 450))
        self._board.fill((255, 255, 255))

        self._mask = self._board.copy()
        for code, chip in self._chips.items():
            self._board.fill((0, 0, 0), chip[1])
            self._mask.fill((code, 0, 0), chip[1])
        self._board.fill((100, 100, 100), self._reset_rect)
        self._mask.fill((HardwareInspect._RESET_CODE, 0, 0), self._reset_rect)

        self._chip = pygame.Surface((50, 50))
        self._chip.fill((255, 0, 0))

        self._required_chips = {0, 2}
        self._current_chips = set(list(self._chips))

        # This wlil be set up in the start function, rather than here, which
        # ensures that it will be reset whenever the program is restarted.
        self._draw_surface = None

        self._exited = False
        self._completed = False

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

    def _setup_draw(self):
        self._draw_surface = self._board.copy()

        for chip in self._current_chips:
            self._draw_surface.blit(self._chip, self._chips[chip][1])

    def _get_chip_code(self, pos):
        """Determine the chip code based on the area the player clicked."""
        # Translate the click position to coordinates relative to the mask.
        translated_pos = (pos[0] - 100, pos[1] - 75)

        # The chip code is encoded in the R value of the mask.
        try:
            colour = self._mask.get_at(translated_pos)
        except IndexError:
            # IndexError is raised if the position is outside the surface -
            # return a 0 to indicate no chip was clicked,
            return HardwareInspect._NO_CHIP_CODE

        return colour.r

    def start(self):
        """Start the program."""
        self._exited = False
        self._current_chips = set(list(self._chips))
        self._setup_draw()

    def draw(self):
        """Draw the program."""
        screen = pygame.display.get_surface()
        screen.blit(self._draw_surface, (100, 75))

    def on_mouseclick(self, button, pos):
        """Detect whether the user clicked the program."""
        if button == mouse.Button.LEFT:
            chip_code = self._get_chip_code(pos)
            if chip_code == HardwareInspect._RESET_CODE:
                self._exited = True
                # See if the user disabled the correct chips.
                if self._current_chips == self._required_chips:
                    self._completed = True
                    self._terminal.reboot()
                else:
                    self._terminal.reboot(self.failure_prefix +
                                          "Hardware error: clock skew "
                                          "detected. Recovering")
                    self._terminal.reduce_time(10)

            elif chip_code != HardwareInspect._NO_CHIP_CODE:
                if chip_code in self._current_chips:
                    self._current_chips.remove(chip_code)
                else:
                    self._current_chips.add(chip_code)

                # Might need to change what we're drawing - do that now.
                self._setup_draw()

    def on_mousemove(self, pos):
        """Handle a mouse move event."""
        if self._get_chip_code(pos) != HardwareInspect._NO_CHIP_CODE:
            mouse.current.set_cursor(mouse.Cursor.HAND)
        else:
            mouse.current.set_cursor(mouse.Cursor.ARROW)

    def completed(self):
        """Indicate whether the program was completed."""
        return self._completed

    def exited(self):
        """Indicate whether the program has exited."""
        return self._exited
