"""Image password program classes."""

import pygame
import random
import mouse
from enum import Enum, unique
from . import program
from resource import load_font


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
    ARCHERY = 12
    BOOKS = 13
    WINE = 14
    BEER = 15
    HORSES = 16
    BASKETBALL = 17
    BASEBALL = 18
    SKATEBOARDING = 19


class ImagePassword(program.TerminalProgram):

    """The image password program."""

    _USER_INFO = [
        {Categories.CARS, Categories.PLANES, Categories.FLOWERS,
         Categories.CATS, Categories.DOGS, Categories.MUSIC},
        {Categories.CARS, Categories.BEER, Categories.SOCCER,
         Categories.TENNIS, Categories.FOOD, Categories.COMPUTERS},
        {Categories.SOCCER, Categories.TENNIS, Categories.FLOWERS,
         Categories.CATS, Categories.BOATS, Categories.ARCHERY},
        {Categories.CARS, Categories.BOATS, Categories.ARCHERY,
         Categories.CATS, Categories.COMPUTERS, Categories.BOOKS},
        {Categories.BOOKS, Categories.WINE, Categories.PLANES,
         Categories.COMPUTERS, Categories.MUSIC, Categories.HORSES},
        {Categories.FOOD, Categories.WINE, Categories.BEER,
         Categories.PLANES, Categories.BASKETBALL, Categories.BASEBALL},
        {Categories.SOCCER, Categories.BASKETBALL, Categories.BASEBALL,
         Categories.ARCHERY, Categories.SKATEBOARDING, Categories.TENNIS},
        {Categories.SKATEBOARDING, Categories.HORSES, Categories.MUSIC,
         Categories.DOGS, Categories.FOOD, Categories.WINE}
    ]

    _BUTTON_COORDS = [
        (80, 100),
        (260, 100),
        (440, 100),
        (620, 100),
    ]

    _BUTTON_SIZE = 100
    _LOCK_TIME = 2000

    """The properties of this program."""
    PROPERTIES = program.ProgramProperties(is_graphical=True)

    def __init__(self, terminal):
        """Initialize the class."""
        super().__init__(terminal)
        self._completed = False
        self._user_info = random.choice(ImagePassword._USER_INFO)
        self._buttons = []
        self._lock_time = 0

    @property
    def help(self):
        """Return the help string for the program."""
        return "Run visual login program."

    @property
    def security_type(self):
        """Return the security type for the program."""
        return "visual authentication"

    @property
    def allow_ctrl_c(self):
        """Don't allow ctrl-c if the program is locked."""
        return not self._locked()

    def start(self):
        """Start the program."""
        self._pick_images()
        self._lock_time = 0

    def _pick_images(self):
        """Pick the images to present, and generate buttons from them."""
        # Pick 3 images from the user's images, and a 4th from the remaining
        # images, shuffle together to form the final list of images.
        user_imgs = random.sample(self._user_info, 3)
        other_img = random.sample(
            set(Categories).difference(self._user_info), 1)
        choices = user_imgs + other_img
        random.shuffle(choices)

        # Build the buttons
        self._buttons = []
        font = load_font(None, 30)
        for i, c in enumerate(choices):
            text = font.render(c.name, True, (255, 255, 255))
            surf = pygame.Surface((ImagePassword._BUTTON_SIZE,
                                   ImagePassword._BUTTON_SIZE))
            surf.fill((0, 0, 255))
            surf.blit(text, (0, 0))
            self._buttons.append((surf, ImagePassword._BUTTON_COORDS[i], c))

    def _locked(self):
        """Indicate if the user is temporarily locked out."""
        return (self._lock_time != 0 and
                self._terminal.time <= self._lock_time +
                ImagePassword._LOCK_TIME)

    def draw(self):
        """Draw the program."""
        for surf, coords, _ in self._buttons:
            pygame.display.get_surface().blit(surf, coords)

    def on_mouseclick(self, button, pos):
        """Detect whether the user clicked the correct image."""
        # Ignore clicks if the program is locked.
        if not self._locked() and button == mouse.Button.LEFT:
            item = [item for surf, coords, item in self._buttons if
                    surf.get_rect().move(coords).collidepoint(pos)][0]
            if item not in self._user_info:
                self._completed = True
            else:
                self._lock_time = self._terminal.time
                self._pick_images()

    def completed(self):
        """Indicate whether the program was successfully completed."""
        return self._completed

    def exited(self):
        """Indicate whether the program has exited."""
        return self.completed()
