"""Base classes for the menu system."""


import pygame
from util import MouseButton
from gamestate import GameState


class MenuItem:

    """A single item in a menu."""

    def __init__(self, item_id, pos, text, text_size, colour=(255, 255, 255)):
        """Initialize the class."""
        self.item_id = item_id
        self._pos = pos

        font = pygame.font.Font(None, text_size)
        self._text = font.render(text, True, colour)

    def collidepoint(self, pos):
        """Determine whether a given point is within this menu item."""
        return self._text.get_rect().collidepoint(pos)

    def draw(self, selected):
        """Draw the menu item."""
        screen = pygame.display.get_surface()
        screen.blit(self._text, self._pos)

        if selected:
            pygame.draw.rect(screen, (255, 255, 255),
                             self._text.get_rect().move(self._pos), 1)


class Menu(GameState):

    """
    Base class for a single menu screen.

    Note that this is a subclass of gamestate - the intention is that each
    menu screen is a separate gamestate.
    """

    def __init__(self):
        """Initialize the class."""
        self._items = []
        self._selected_index = 0

    def run(self, events):
        """Handle events."""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._on_mouseclick(event)
            elif event.type == pygame.KEYDOWN:
                self._on_keypress(event)
            elif event.type == pygame.MOUSEMOTION:
                self._on_mousemove(event)

    def draw(self):
        """Draw the menu."""
        for idx, item in enumerate(self._items):
            item.draw(idx == self._selected_index)

    def _on_keypress(self, event):
        """Handle a keypress."""
        if event.key in [pygame.K_UP, pygame.K_LEFT]:
            if self._selected_index > 0:
                self._selected_index -= 1
        elif event.key in [pygame.K_DOWN, pygame.K_RIGHT]:
            if self._selected_index < len(self._items):
                self._selected_index += 1
        elif event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
            self._on_choose(self._items[self._selected_index])

    def _on_mouseclick(self, event):
        """Handle a mouse click."""
        if event.button == MouseButton.LEFT:
            for item in [i for i in self._items if i.collidepoint(event.pos)]:
                self._on_choose(item)

    def _on_mousemove(self, event):
        """Handle mousemove event."""
        for idx, item in enumerate(self._items):
            if item.collidepoint(event.pos):
                self._selected_index = idx

    def _on_choose(self, item):
        """Handle activation of a menu item."""
        pass
