"""Entry point for the game."""


import pygame
import pygame.locals
from gamestate import GameStateManager
from mainmenu import MainMenuState


def setup():
    """Perform initial setup."""
    pygame.init()
    pygame.display.set_mode([800, 600],
                            pygame.DOUBLEBUF | pygame.HWSURFACE,
                            24)


def run():
    """Run the game loop."""
    gamestates = GameStateManager()
    gamestates.push(MainMenuState(gamestates))

    while True:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.locals.QUIT:
                exit()

        gamestates.run(events)

        screen = pygame.display.get_surface()
        screen.fill((0, 0, 0))
        gamestates.draw()
        pygame.display.flip()


if __name__ == '__main__':
    setup()
    run()
