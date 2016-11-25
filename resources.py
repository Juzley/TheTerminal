"""Media management - only load each asset once."""

import os
import sys
import pygame

# A dict mapping filenames to the in-memory representation for each asset.
_media = {}


def make_path(filename):
    """Create the correct path for a given file."""
    # If we're running in a pyinstaller one-file bundle, we need to look in
    # the temporary directory.
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    else:
        return filename


def load_font(filename, size):
    """Load a font from disk, return a pygame Font object."""
    if (filename, size) not in _media:
        _media[(filename, size)] = pygame.font.Font(make_path(filename), size)
    return _media[(filename, size)]


def load_image(filename):
    """Load an image from disk, return a pygame Surface."""
    if filename not in _media:
        _media[filename] = pygame.image.load(
            make_path(filename)).convert_alpha()
    return _media[filename]
