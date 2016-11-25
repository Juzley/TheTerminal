"""Miscellaneous utilities for use in the game."""


import pygame
from resources import load_image, load_font


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


def text_align(text, coords, align):
    """Align text around given coords."""
    if align == Align.LEFT:
        return coords
    elif align == Align.CENTER:
        return (coords[0] - text.get_rect().w / 2, coords[1])
    else:
        return (coords[0] - text.get_rect().w, coords[1])


def render_bezel(label, power_off=False):
    """Render the bezel and label text."""
    if power_off:
        bezel = load_image('media/bezel_off.png')
    else:
        bezel = load_image('media/bezel.png')
    text = load_font('media/fonts/METRO-DF.TTF', 19).render(
        label, True, (60, 60, 60))

    # Copy the bezel surface so we don't overwrite the stored cached surface in
    # the media manager.
    surf = bezel.copy()
    surf.blit(text, text_align(text, (725, 570), Align.CENTER))

    return surf
