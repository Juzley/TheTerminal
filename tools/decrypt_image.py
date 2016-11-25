"""Produce the manual image for the decryption game."""
import string
import pygame
from pygame import Surface
from pygame.font import Font
from programs import Decrypt
import constants

_TEXT_HEIGHT = 34
_VERTICAL_SPACING = 20
_VERTICAL_PADDING = 5
_HORIZONTAL_SPACING = 20
_HORIZONTAL_PADDING = 10
_CENTRAL_SPACING = 50
_BACKGROUND_COLOUR = (50, 50, 50)


def render_font(font, charmap):
    """Render all chars for a given font in a column."""
    renders = [font.render(c, True, constants.TEXT_COLOUR) for _, c in charmap]
    surf = Surface((max([r.get_rect().w for r in renders]),
                    (_TEXT_HEIGHT + _VERTICAL_SPACING) * len(renders)))
    surf.fill(_BACKGROUND_COLOUR)

    y = _VERTICAL_PADDING
    for r in renders:
        surf.blit(r, (0, y))
        y += _TEXT_HEIGHT + _VERTICAL_SPACING

    return surf


def render_half(fonts):
    """Render one half of the final image."""
    # Render columns for each font.
    surfs = [render_font(font, charmap) for font, charmap in fonts]

    # Work out the size of the image we need
    img_height = max([s.get_rect().h for s in surfs])
    img_width = (sum([s.get_rect().w for s in surfs]) +
                 _HORIZONTAL_SPACING * (len(surfs) - 1) +
                 _HORIZONTAL_PADDING * 2)

    # Blit each font's column into the final image.
    output = Surface((img_width, img_height))
    output.fill(_BACKGROUND_COLOUR)

    x = _HORIZONTAL_PADDING
    for surf in surfs:
        output.blit(surf, (x, 0))
        x += surf.get_rect().w + _HORIZONTAL_SPACING

    return output


if __name__ == '__main__':
    pygame.font.init()

    # Load the fonts from disk, and group them with their charmaps
    fonts = [(Font(f, _TEXT_HEIGHT), sorted(m.items())) for f, m in
             [(None, {c: c for c in string.ascii_lowercase})] + Decrypt._FONTS]

    # Split the fonts in half, so that we can render them in two columns, giving
    # a squarer final image.
    fonts_left = [(f, m[:len(m) // 2]) for f, m in fonts]
    fonts_right = [(f, m[len(m) // 2:]) for f, m in fonts]

    # Render the two halfs of the image.
    surf_left = render_half(fonts_left)
    surf_right = render_half(fonts_right)

    # Combine the two halfs into the final image.
    final_height = max(surf_left.get_rect().h, surf_right.get_rect().h)
    final_width = (surf_left.get_rect().w + surf_right.get_rect().w +
                   _CENTRAL_SPACING)
    output = Surface((final_width, final_height))
    output.fill(_BACKGROUND_COLOUR)
    output.blit(surf_left, (0, 0))
    output.blit(surf_right, (surf_left.get_rect().w + _CENTRAL_SPACING, 0))
    pygame.image.save(output, 'manual/decrypt.png')
