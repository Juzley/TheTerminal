"""Timer module."""

import pygame


class Timer:

    """Timer class."""

    def __init__(self):
        """Initialize the class."""
        self.reset()

    def reset(self):
        """Reset the timer."""
        self._lasttime = pygame.time.get_ticks()
        self.paused = False
        self.time = 0
        self.frametime = 0

    def update(self):
        """Update the time values based on the current tickcount."""
        time = pygame.time.get_ticks()

        if not self.paused:
            self.frametime = time - self._lasttime
            self.time += self.frametime

        self._lasttime = time
