"""Produce the manual image for the decryption game."""
import string
import pygame
from pygame import Surface
from pygame.font import Font
from programs import Decrypt

_TEXT_HEIGHT = 60
_VERTICAL_SPACING = 5
_VERTICAL_PADDING = 5
_HORIZONTAL_SPACING = 20
_HORIZONTAL_PADDING = 10


def render_font(font, charmap):
    """Render all chars for a given font in a column."""
    renders = [font.render(c, True, (0, 0, 0)) for _, c in
               sorted(charmap.items())]
    surf = Surface((max([r.get_rect().w for r in renders]),
                    _TEXT_HEIGHT * len(renders)))
    surf.fill((255, 255, 255))

    y = _VERTICAL_PADDING
    for r in renders:
        surf.blit(r, (0, y))
        y += _TEXT_HEIGHT + _VERTICAL_SPACING

    return surf

pygame.font.init()

# Load the fonts from disk, and group them with their charmaps
fonts = [(Font(f, _TEXT_HEIGHT), m) for f, m in
         [(None, {c: c for c in string.ascii_lowercase})] + Decrypt._FONTS]

# Render columns for each font.
surfs = [render_font(font, charmap) for font, charmap in fonts]

# Work out the size of the image we need
img_height = (_TEXT_HEIGHT * len(string.ascii_lowercase) +
              _VERTICAL_SPACING * (len(string.ascii_lowercase) - 1) +
              _VERTICAL_PADDING * 2)
img_width = (sum([s.get_rect().w for s in surfs]) +
             _HORIZONTAL_SPACING * (len(surfs) - 1) +
             _HORIZONTAL_PADDING * 2)

# Blit each font's column into the final image.
output = Surface((img_width, img_height))
output.fill((255, 255, 255))

x = _HORIZONTAL_PADDING
for surf in surfs:
    output.blit(surf, (x, 0))
    x += surf.get_rect().w + _HORIZONTAL_SPACING

pygame.image.save(output, 'manual/decrypt.png')
