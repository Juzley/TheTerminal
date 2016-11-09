"""Entry point for the game."""


import pygame

import mouse
from gamestate import GameStateManager
from mainmenu import MainMenu


def setup():
    """Perform initial setup."""
    pygame.init()
    pygame.display.set_mode([800, 600],
                            pygame.DOUBLEBUF | pygame.HWSURFACE,
                            24)
    mouse.current.set_cursor(mouse.Cursor.ARROW)


def run():
    """Run the game loop."""
    gamestates = GameStateManager()
    gamestates.push(MainMenu(gamestates))

    running = True
    while running:
        events = pygame.event.get()
        gamestates.run(events)

        if any(e.type == pygame.QUIT for e in events) or gamestates.empty():
            # An empty GameStateManager indicates that the main menu was popped,
            # and we should exit.
            running = False
        else:
            screen = pygame.display.get_surface()
            screen.fill((0, 0, 0))
            gamestates.draw()
            pygame.display.flip()


if __name__ == '__main__':
    setup()
    run()
