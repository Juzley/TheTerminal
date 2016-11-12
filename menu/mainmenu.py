"""Main Menu Implementation."""


import pygame
from .menu import Menu, MenuItem
from .level import LevelMenu
from enum import Enum, unique


class MainMenu(Menu):

    """Class defining the main menu."""

    @unique
    class Items(Enum):
        START_GAME = 1
        QUIT = 2

    def __init__(self, mgr):
        """Initialize the class."""
        super().__init__(items=[
            MenuItem(item_id=MainMenu.Items.START_GAME,
                     pos=(0, 200),
                     text='Start Game',
                     text_size=40,
                     colour=(255, 255, 255)),
            MenuItem(item_id=MainMenu.Items.QUIT,
                     pos=(0, 240),
                     text='Quit',
                     text_size=40,
                     colour=(255, 255, 255))
        ])

        self._font = pygame.font.Font(None, 40)
        self._mgr = mgr

    def _on_choose(self, item):
        """Handle activation of a menu item."""
        if item.item_id == MainMenu.Items.START_GAME:
            self._mgr.push(LevelMenu(self._mgr))
        elif item.item_id == MainMenu.Items.QUIT:
            # The main menu should be the last gamestate on the stack, so
            # popping it should cause the game to exit.
            self._mgr.pop()
