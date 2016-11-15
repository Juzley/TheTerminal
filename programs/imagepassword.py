"""Image password program classes."""

import pygame
import random
import mouse
from itertools import combinations
from enum import Enum, unique
from . import program


@unique
class Categories(Enum):

    """Categories of image to display."""

    CARS = 1
    PLANES = 2
    FLOWERS = 3
    CATS = 4
    DOGS = 5
    MUSIC = 6
    SOCCER = 7
    TENNIS = 8
    FOOD = 9
    COMPUTERS = 10
    BOATS = 11
    FISHING = 12
    ARCHERY = 13


class ImagePassword(program.TerminalProgram):

    """The image password program."""

    _USER_INFO = [
        ({Categories.SOCCER, Categories.TENNIS},
         {Categories.CARS, Categories.PLANES, Categories.FLOWERS,
          Categories.CATS}),
        ({Categories.FLOWERS, Categories.CATS},
         {Categories.CARS, Categories.PLANES, Categories.DOGS,
          Categories.MUSIC}),
        ({Categories.DOGS, Categories.CATS},
         {Categories.CARS, Categories.FLOWERS, Categories.COMPUTERS,
          Categories.FOOD}),
        ({Categories.DOGS, Categories.CATS},
         {Categories.CARS, Categories.PLANES, Categories.FISHING,
          Categories.BOATS}),
        ({Categories.CARS, Categories.FOOD},
         {Categories.FISHING, Categories.SOCCER, Categories.COMPUTERS,
          Categories.CATS})
    ]

    _BUTTON_COORDS = [
        (80, 100),
        (260, 100),
        (440, 100),
        (620, 100),
    ]

    _BUTTON_SIZE = 100

    """The properties of this program."""
    PROPERTIES = program.ProgramProperties(is_graphical=True)

    def __init__(self, terminal):
        """Initialize the class."""
        super().__init__(terminal)
        self._completed = False

        self._user_index = random.randrange(len(ImagePassword._USER_INFO))
        user_info = ImagePassword._USER_INFO[self._user_index]

        # Pick 3 random wrong choices, and one correct choice, and shuffle them
        # together.
        wrongs = list(random.choice(list(combinations(user_info[1], 3))))
        right = random.sample(user_info[0], 1)
        choices = wrongs + right
        random.shuffle(choices)

        # Build the buttons
        self._buttons = []
        font = pygame.font.Font(None, 30)
        for i, c in enumerate(choices):
            text = font.render(c.name, True, (255, 255, 255))
            surf = pygame.Surface((ImagePassword._BUTTON_SIZE,
                                   ImagePassword._BUTTON_SIZE))
            surf.fill((0, 0, 255))
            surf.blit(text, (0, 0))
            self._buttons.append((surf, ImagePassword._BUTTON_COORDS[i], c))

    @property
    def help(self):
        """Return the help string for the program."""
        return "Run visual login program."

    @property
    def security_type(self):
        """Return the security type for the program."""
        return "visual authentication"

    def draw(self):
        """Draw the program."""
        for surf, coords, _ in self._buttons:
            pygame.display.get_surface().blit(surf, coords)

    def on_mouseclick(self, button, pos):
        """Detect whether the user clicked the correct image."""
        if button == mouse.Button.LEFT:
            item = [item for surf, coords, item in self._buttons if
                    surf.get_rect().move(coords).collidepoint(pos)]
            if item[0] in ImagePassword._USER_INFO[self._user_index][0]:
                self._completed = True
            else:
                # TODO: Do something when things are wrong.
                pass

    def completed(self):
        """Indicate whether the program was successfully completed."""
        return self._completed

    def exited(self):
        """Indicate whether the program has exited."""
        return self.completed()
