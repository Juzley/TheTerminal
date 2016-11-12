"""Pause Menu implementation."""

import pygame
from .menu import Menu, MenuItem
from .mainmenu import MainMenu
from enum import Enum, unique


class PauseMenu(Menu):

    """Class defining the pause menu."""

    @unique
    class Items(Enum):
        RESUME = 1
        QUIT = 2

    def __init__(self, mgr):
        """Initialize the class."""
        super().__init__(items=[
            MenuItem(item_id=PauseMenu.Items.RESUME,
                     pos=(0, 200),
                     text='Resume',
                     text_size=40,
                     colour=(20, 200, 20)),
            MenuItem(item_id=PauseMenu.Items.QUIT,
                     pos=(0, 240),
                     text='Quit',
                     text_size=40,
                     colour=(20, 200, 20))
        ])

        self._font = pygame.font.Font(None, 40)
        self._mgr = mgr

    def _on_choose(self, item):
        """Handle activation of a menu item."""
        if item.item_id == PauseMenu.Items.RESUME:
            self._mgr.pop()
        elif item.item_id == MainMenu.Items.QUIT:
            self._mgr.pop_until(MainMenu)
