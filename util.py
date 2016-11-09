"""Miscellaneous utilities for use in the game."""


import pygame


class MouseButton:

    """Class representing the different mouse buttons."""

    LEFT = 1
    MIDDLE = 2
    RIGHT = 3
    WHEEL_UP = 4
    WHEEL_DOWN = 5


class ActiveEvent:

    """
    Class representing an pygame.ACTIVEEVENT, wrapping the state mask and
    providing a cleaner interface.

    """

    MOUSE_FOCUS = 0x1
    APP_INPUT_FOCUS = 0x2
    APP_ACTIVE = 0x4

    def __init__(self, state_mask, gain):
        self._state_mask = state_mask
        self._gain = gain

    @property
    def gained(self):
        """Has this event gained or lost the state?"""
        return self._gain == 1

    @property
    def mouse_focus_change(self):
        """Is this event a mouse focus change?"""
        return self._has_state(ActiveEvent.MOUSE_FOCUS)

    @property
    def input_focus_change(self):
        """Is this event an app input focus change?"""
        return self._has_state(ActiveEvent.APP_INPUT_FOCUS)

    @property
    def app_active_change(self):
        """Is this event an app active change?"""
        return self._has_state(ActiveEvent.APP_ACTIVE)

    def _has_state(self, state):
        return (self._state_mask & state) == state


def load_image(filename):
    """Load an image from disk, return a pygame Surface."""
    image = pygame.image.load(filename).convert_alpha()
    return image

