"""Module responsible for switching between different gamestates."""


class GameStateManager:

    """Class to manage running and switching between gamestates."""

    def __init__(self):
        """Initialize the class."""
        # _states is a stack of gamestates, implemented as a list where the
        # end of the list is the top of the stack. The current gamestate,
        # therefore, is at the end of the list.
        self._states = []

    def push(self, gamestate):
        """Push a new gamestate onto the stack."""
        self._states.append(gamestate)

    def replace(self, gamestate):
        """Replace the current gamestate with a new gamestate."""
        self.pop()
        self.push(gamestate)

    def pop(self):
        """Pop the current gamestate off the stack, and move to the next one."""
        if self._states:
            self._states.pop()

    def run(self, events):
        """Run the current gamestate."""
        if self._states:
            self._states[-1].run(events)

    def draw(self):
        """Draw the current gamestate."""
        if self._states:
            self._states[-1].draw()
