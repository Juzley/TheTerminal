"""Defines various mouse related classes."""

import pygame

_HAND_STRINGS = (  # sized 24x24
  "     XX                 ",
  "    X..X                ",
  "    X..X                ",
  "    X..X                ",
  "    X..X                ",
  "    X..XXX              ",
  "    X..X..XXX           ",
  "    X..X..X..XX         ",
  "    X..X..X..X.X        ",
  "XXX X..X..X..X..X       ",
  "X..XX........X..X       ",
  "X...X...........X       ",
  " X..X...........X       ",
  "  X.X...........X       ",
  "  X.............X       ",
  "   X............X       ",
  "   X...........X        ",
  "    X..........X        ",
  "    X..........X        ",
  "     X........X         ",
  "     X........X         ",
  "     XXXXXXXXXX         ",
  "                        ",
  "                        ",
)
_HAND_CURSOR = ((24, 24), (5, 0)) + \
               pygame.cursors.compile(_HAND_STRINGS, ".", "X")


class Cursor:
    """Supported cursors."""
    ARROW = 1
    HAND = 2


class Button:

    """Class representing the different mouse buttons."""

    LEFT = 1
    MIDDLE = 2
    RIGHT = 3
    WHEEL_UP = 4
    WHEEL_DOWN = 5


class Mouse:

    """Class for tracking and updating cursor."""

    _CURSORS = {
        Cursor.ARROW: pygame.cursors.arrow,
        Cursor.HAND: _HAND_CURSOR,
    }

    def __init__(self):
        self._current_cursor = None

    def set_cursor(self, cursor_num):
        if self._current_cursor != cursor_num:
            pygame.mouse.set_cursor(*Mouse._CURSORS[cursor_num])
            self._current_cursor = cursor_num


# Current Mouse
current = Mouse()
