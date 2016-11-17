"""Media management - only load each asset once."""

import pygame

# A dict mapping filenames to the in-memory representation for each asset.
_media = {}


def load_font(filename, size):
    """Load a font from disk, return a pygame Font object."""
    if (filename, size) not in _media:
        _media[(filename, size)] = pygame.font.Font(filename, size)
    return _media[(filename, size)]


def load_image(filename):
    """Load an image from disk, return a pygame Surface."""
    if filename not in _media:
        _media[filename] = pygame.image.load(filename).convert_alpha()
    return _media[filename]
