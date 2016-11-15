"""Miscellaneous utilities for use in the game."""


import pygame


class Align:

    """Class containing the values representing text alignment."""

    LEFT = -1
    CENTER = 0
    RIGHT = 1


class ActiveEvent:

    """
    Class representing an pygame.ACTIVEEVENT.

    This wraps the state mask, providing a cleaner interface.

    """

    MOUSE_FOCUS = 0x1
    APP_INPUT_FOCUS = 0x2
    APP_ACTIVE = 0x4

    def __init__(self, state_mask, gain):
        """Initialize the class from the event parameters."""
        self._state_mask = state_mask
        self._gain = gain

    @property
    def gained(self):
        """Indicate if this event gained or lost the state."""
        return self._gain == 1

    @property
    def mouse_focus_change(self):
        """Indicate if the event is a mouse focus change."""
        return self._has_state(ActiveEvent.MOUSE_FOCUS)

    @property
    def input_focus_change(self):
        """Indicate if this event is an app input focus change."""
        return self._has_state(ActiveEvent.APP_INPUT_FOCUS)

    @property
    def app_active_change(self):
        """Indicate if this event is an app active change."""
        return self._has_state(ActiveEvent.APP_ACTIVE)

    def _has_state(self, state):
        """Determine whether the event has a givenstate."""
        return (self._state_mask & state) == state

def center_align(w, h):
    """Return coords to align an image in the center of the screen."""
    return ((pygame.display.get_surface().get_rect().w - w) / 2,
            (pygame.display.get_surface().get_rect().h - h) / 2)
