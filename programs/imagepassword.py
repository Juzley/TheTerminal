"""Image password program classes."""

import pygame
import random
import mouse
from enum import Enum, unique
from . import program
from resource import load_font, load_image


@unique
class Categories(Enum):

    """Categories of image to display."""

    CARS = 'media/login/cars.png'
    PLANES = 'media/login/planes.png'
    FLOWERS = 'media/login/flowers.png'
    CATS = 'media/login/cats.png'
    DOGS = 'media/login/dogs.png'
    MUSIC = 'media/login/music.png'
    SOCCER = 'media/login/soccer.png'
    TENNIS = 'media/login/tennis.png'
    FOOD = 'media/login/food.png'
    COMPUTERS = 'media/login/computers.png'
    BOATS = 'media/login/boats.png'
    ARCHERY = 'media/login/archery.png'
    BOOKS = 'media/login/books.png'
    WINE = 'media/login/wine.png'
    BEER = 'media/login/beer.png'
    HORSES = 'media/login/horses.png'
    BASKETBALL = 'media/login/basketball.png'
    BASEBALL = 'media/login/baseball.png'
    SKATEBOARDING = 'media/login/skateboarding.png'


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

    _BACKGROUND_POS = (270, 140)
    _BACKGROUND_SIZE = (260, 290)
    _BACKGROUND_COLOUR = (180, 180, 180)
    _BACKGROUND_FLASH_COLOUR = (255, 0, 0)
    _BACKGROUND_FLASH_TIME = 100

    _HEADER_POS = (2, 2)
    _HEADER_SIZE = (256, 26)
    _HEADER_COLOUR = (160, 160, 160)
    _HEADER_TEXT_SIZE = 22
    _HEADER_TEXT_COLOUR = (0, 0, 0)
    _HEADER_TEXT_POS = (4, 8)

    _BUTTON_COORDS = [
        (280, 180),
        (420, 180),
        (280, 320),
        (420, 320),
    ]

    _BUTTON_SIZE = 100
    _BUTTON_BORDER_WIDTH = 2
    _BUTTON_BORDER_COLOUR = _HEADER_COLOUR

    _GUESSED_OVERLAY_COLOUR = (150, 150, 150)
    _GUESSED_OVERLAY_ALPHA = 180

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
        self._background = pygame.Surface(ImagePassword._BACKGROUND_SIZE)
        self._background.fill(ImagePassword._BACKGROUND_COLOUR)
        header = pygame.Surface(ImagePassword._HEADER_SIZE)
        header.fill(ImagePassword._HEADER_COLOUR)
        self._background.blit(header, ImagePassword._HEADER_POS)

        font = load_font(None, ImagePassword._HEADER_TEXT_SIZE)
        text = font.render("Select three images", True,
                           ImagePassword._HEADER_TEXT_COLOUR)
        self._background.blit(text, ImagePassword._HEADER_TEXT_POS)

        for coords in ImagePassword._BUTTON_COORDS:
            border_coords = (coords[0] - ImagePassword._BUTTON_BORDER_WIDTH -
                             ImagePassword._BACKGROUND_POS[0],
                             coords[1] - ImagePassword._BUTTON_BORDER_WIDTH -
                             ImagePassword._BACKGROUND_POS[1])
            border_size = (ImagePassword._BUTTON_SIZE +
                           ImagePassword._BUTTON_BORDER_WIDTH * 2)

            border = pygame.Surface((border_size, border_size))
            border.fill(ImagePassword._BUTTON_BORDER_COLOUR)
            self._background.blit(border, border_coords)

        self._correct_overlay = pygame.Surface((ImagePassword._BUTTON_SIZE,
                                                ImagePassword._BUTTON_SIZE))
        self._correct_overlay.fill(ImagePassword._GUESSED_OVERLAY_COLOUR)
        self._correct_overlay.set_alpha(ImagePassword._GUESSED_OVERLAY_ALPHA)

        self._flash = pygame.Surface(ImagePassword._BACKGROUND_SIZE)
        self._flash.fill(ImagePassword._BACKGROUND_FLASH_COLOUR)

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
        for i, c in enumerate(choices):
            self._buttons.append([load_image(c.value),
                                  ImagePassword._BUTTON_COORDS[i],
                                  c, False])

    def _locked(self):
        """Indicate if the user is temporarily locked out."""
        return (self._lock_time != 0 and
                self._terminal.time <= self._lock_time +
                ImagePassword._LOCK_TIME)

    def draw(self):
        """Draw the program."""
        # Draw the background.
        pygame.display.get_surface().blit(self._background,
                                          ImagePassword._BACKGROUND_POS)

        # If the user has made a mistake, flash the background.
        if (self._lock_time != 0 and self._terminal.time <= self._lock_time +
                ImagePassword._BACKGROUND_FLASH_TIME):
            pygame.display.get_surface().blit(self._flash,
                                              ImagePassword._BACKGROUND_POS)

        # Draw the buttons.
        if not self._locked():
            for surf, coords, _, correct in self._buttons:
                pygame.display.get_surface().blit(surf, coords)

                if correct:
                    pygame.display.get_surface().blit(self._correct_overlay,
                                                      coords)

    def on_mouseclick(self, button, pos):
        """Detect whether the user clicked the correct image."""
        # Ignore clicks if the program is locked.
        if not self._locked() and button == mouse.Button.LEFT:
            hits = [info for info in self._buttons if
                    info[0].get_rect().move(info[1]).collidepoint(pos)]
            if hits:
                # Mark the image as having been selected.
                hits[0][3] = True

                # Check if we've selected 3 images now.
                guessed = [item for _, _, item, clicked in self._buttons if
                           clicked]
                correct = [item for _, _, item, clicked in self._buttons if
                           clicked and item in self._user_info]
                if len(guessed) is 3:
                    if len(correct) == len(guessed):
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
