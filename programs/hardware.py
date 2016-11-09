"""Hardware program classes."""

import pygame

from util import MouseButton
from . import program


class TestGraphical(program.TerminalProgram):

    """Program to test the graphical program handling."""

    # Chip code used to indicate no chip.
    _NO_CHIP = 255

    def __init__(self, terminal):
        """Initialize the class."""
        super().__init__(terminal)

        self._mask_surface = pygame.Surface((600, 450))
        self._mask_surface.fill((255, 255, 255))
        self._mask_surface.fill((0, 0, 0), pygame.Rect(100, 100, 180, 120))
        self._clicked = False

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

    def _get_chip_code(self, pos):
        # Translate the click position to coordinates relative to the mask.
        translated_pos = (pos[0] - 100, pos[1] - 75)

        # The chip code is encoded in the R value of the mask.
        try:
            colour = self._mask_surface.get_at(translated_pos)
        except IndexError:
            # IndexError is raised if the position is outside the surface -
            # return a 0 to indicate no chip was clicked,
            return TestGraphical._NO_CHIP

        return colour.r

    def draw(self):
        """Draw the program."""
        screen = pygame.display.get_surface()
        screen.blit(self._mask_surface, (100, 75))

    def on_mouseclick(self, button, pos):
        """Detect whether the user clicked the program."""
        if (button == MouseButton.LEFT and
                self._get_chip_code(pos) != TestGraphical._NO_CHIP):
            self._clicked = True
            self._terminal.output(["SYSTEM ALERT: Hardware security module "
                                   "disabled."])

    def completed(self):
        """Indicate whether the program was completed."""
        return self._clicked

    def exited(self):
        """Indicate whether the program has exited."""
        return self._clicked
