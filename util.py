"""Miscellaneous utilities for use in the game."""


import pygame


class MouseButton:

    """Class representing the different mouse buttons."""

    LEFT = 1
    MIDDLE = 2
    RIGHT = 3
    WHEEL_UP = 4
    WHEEL_DOWN = 5


def load_image(filename):
    """Load an image from disk, return a pygame Surface."""
    image = pygame.image.load(filename).convert_alpha()
    return image

