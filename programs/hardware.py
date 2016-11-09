"""Hardware program classes."""

import pygame

from util import MouseButton
from . import program


class HardwareInspect(program.TerminalProgram):

    """Program to test the graphical program handling."""

    _NO_CHIP_CODE = 255
    _RESET_CODE = 244

    def __init__(self, terminal):
        """Initialize the class."""
        super().__init__(terminal)

        self._mask_surface = pygame.Surface((600, 450))
        self._mask_surface.fill((255, 255, 255))
        self._mask_surface.fill((0, 0, 0), pygame.Rect(100, 100, 50, 50))
        self._mask_surface.fill((1, 1, 1), pygame.Rect(100, 200, 50, 50))
        self._mask_surface.fill((2, 2, 2), pygame.Rect(100, 300, 50, 50))
        self._mask_surface.fill((244, 244, 244), pygame.Rect(200, 100, 50, 50))
        self._expected_disabled = set([0, 2])
        self._disabled_chips = set()
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

    def start(self):
        """Start the program."""
        self._exited = False

    def _get_chip_code(self, pos):
        """Determine the chip code based on the area the player clicked."""
        # Translate the click position to coordinates relative to the mask.
        translated_pos = (pos[0] - 100, pos[1] - 75)

        # The chip code is encoded in the R value of the mask.
        try:
            colour = self._mask_surface.get_at(translated_pos)
        except IndexError:
            # IndexError is raised if the position is outside the surface -
            # return a 0 to indicate no chip was clicked,
            return HardwareInspect._NO_CHIP

        return colour.r

    def draw(self):
        """Draw the program."""
        screen = pygame.display.get_surface()
        screen.blit(self._mask_surface, (100, 75))

    def on_mouseclick(self, button, pos):
        """Detect whether the user clicked the program."""
        if button == MouseButton.LEFT:
            chip_code = self._get_chip_code(pos)
            if chip_code == HardwareInspect._RESET_CODE:
                self._exited = True
                # See if the user disabled the correct chips.
                if self._disabled_chips == self._expected_disabled:
                    self._completed = True
                    self._terminal.output(["SYSTEM ALERT: Hardware security"
                                           " module disabled."])
                else:
                    # TODO: Reboot.
                    pass
            elif chip_code != HardwareInspect._NO_CHIP_CODE:
                if chip_code in self._disabled_chips:
                    self._disabled_chips.remove(chip_code)
                else:
                    self._disabled_chips.add(chip_code)

    def completed(self):
        """Indicate whether the program was completed."""
        return self._completed

    def exited(self):
        """Indicate whether the program has exited."""
        return self._exited
