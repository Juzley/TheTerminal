"""Main Menu Implementation."""


import pygame
from gameplay import GameplayState


class MainMenuState:

    """Gamestate implementation for the main menu."""

    def __init__(self, mgr):
        """Initialize the class."""
        self._font = pygame.font.Font(None, 40)
        self._mgr = mgr

    def run(self, events):
        """Run the main menu logic."""
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                self._mgr.push(GameplayState(self._mgr))

    def draw(self):
        """Draw the main menu."""
        text = self._font.render('Press enter to start', True, (255, 255, 255))
        pygame.display.get_surface().blit(text, (0, 0))
