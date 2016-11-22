"""Base classes for the menu system."""


import pygame
import util
import mouse
import constants
from gamestate import GameState
from resource import load_font


class MenuItem:

    """A single item in a menu."""

    def __init__(self, item_id, pos, text, text_size,
                 colour=(255, 255, 255), align=util.Align.CENTER):
        """Initialize the class."""
        self.item_id = item_id
        self._pos = pos

        font = load_font(None, text_size)
        self._text = font.render(text, True, colour)

        # Handle alignment
        text_width = self._text.get_rect()[2]
        surface_width = pygame.display.get_surface().get_rect()[2]
        if align == util.Align.LEFT:
            self._pos = (0, self._pos[1])
        elif align == util.Align.CENTER:
            self._pos = (int((surface_width / 2) - (text_width / 2)),
                         self._pos[1])
        else:
            self._pos = (surface_width - text_width, self._pos[1])

    def collidepoint(self, pos):
        """Determine whether a given point is within this menu item."""
        return self._text.get_rect().move(self._pos).collidepoint(pos)

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

    def __init__(self, items):
        """Initialize the class."""
        self._items = items
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
            if self._selected_index < len(self._items) - 1:
                self._selected_index += 1
        elif event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
            mouse.current.set_cursor(mouse.Cursor.ARROW)
            self._on_choose(self._items[self._selected_index])

    def _on_mouseclick(self, event):
        """Handle a mouse click."""
        if event.button == mouse.Button.LEFT:
            for item in [i for i in self._items if i.collidepoint(event.pos)]:
                mouse.current.set_cursor(mouse.Cursor.ARROW)
                self._on_choose(item)

    def _on_mousemove(self, event):
        """Handle mousemove event."""
        over_item = False
        for idx, item in enumerate(self._items):
            if item.collidepoint(event.pos):
                self._selected_index = idx
                over_item = True
        if over_item:
            mouse.current.set_cursor(mouse.Cursor.HAND)
        else:
            mouse.current.set_cursor(mouse.Cursor.ARROW)

    def _on_choose(self, item):
        """Handle activation of a menu item."""
        pass


class CLIMenuItem:

    """Class representing an item in a CLI Menu."""

    def __init__(self, text, cmd="", item=None, disabled=False, selected=False):
        """Initialize the class."""
        self.text = text
        self.cmd = cmd
        self.item = item
        self.disabled = disabled
        self.selected = selected


class CLIMenu(GameState):

    """A menu designed to look like a CLI."""

    _TEXT_SIZE = constants.TERMINAL_TEXT_SIZE
    _TEXT_FONT = constants.TERMINAL_FONT
    _TEXT_COLOUR = constants.TEXT_COLOUR
    _DISABLED_COLOUR = (100, 100, 100)
    _TEXT_START = (45, 50)
    _CMD_TEXT_POS = (45, 525)

    def __init__(self, mgr, entries):
        """Initialize the class."""
        super().__init__()
        self._mgr = mgr

        self._bezel = util.render_bezel(constants.VERSION_STRING)
        self._font = load_font(CLIMenu._TEXT_FONT, CLIMenu._TEXT_SIZE)
        self._selected_index = 0
        self._items = []
        self._cmds = {}

        # Create a '<' image to mark the selected item.
        self._select_marker = self._font.render(' <', True,
                                                CLIMenu._TEXT_COLOUR)
        self._buf = []
        y_coord = CLIMenu._TEXT_START[1]
        for entry in entries:
            # Render all the text up front, so that we can use the resulting
            # surfaces for hit-detection - we store a tuple containing:
            #   - The surface,
            #   - Its coordinates,
            #   - The menu item it represents, if any
            colour = CLIMenu._TEXT_COLOUR
            disabled = False
            if isinstance(entry, CLIMenuItem):
                line = entry.text
                item = entry.item

                if entry.disabled:
                    colour = CLIMenu._DISABLED_COLOUR
                    disabled = True
                else:
                    self._items.append(item)

                    # If this entry should start selected, set the
                    # selected-index appropriately.
                    if entry.selected:
                        self._selected_index = len(self._items) - 1

                    # If there's a command string associated with this item,
                    # render the text and store it in a dictionary mapping the
                    # item ID to the cmd text
                    if entry.cmd:
                        self._cmds[item] = self._font.render(
                            entry.cmd, True, CLIMenu._TEXT_COLOUR)
            else:
                line = entry
                item = None

            text = self._font.render(line, True, colour)
            self._buf.append((text, (CLIMenu._TEXT_START[0], y_coord), item,
                              disabled))
            y_coord += CLIMenu._TEXT_SIZE

    def run(self, events):
        """Handle events."""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._on_mouseclick(event)
            elif event.type == pygame.MOUSEMOTION:
                self._on_mousemove(event)
            elif event.type == pygame.KEYDOWN:
                self._on_keypress(event)

    def draw(self):
        """Draw the menu."""
        selected_item = self._items[self._selected_index]

        # Draw the text
        for line, coords, item, disabled in self._buf:
            if line:
                pygame.display.get_surface().blit(line, coords)

            if item == selected_item:
                pygame.display.get_surface().blit(
                    self._select_marker,
                    (coords[0] + line.get_rect().w, coords[1]))

        # Draw the command string
        if selected_item in self._cmds:
            pygame.display.get_surface().blit(self._cmds[selected_item],
                                              CLIMenu._CMD_TEXT_POS)

        # Draw the bezel
        pygame.display.get_surface().blit(self._bezel, self._bezel.get_rect())

    def _hit_item(self, pos):
        """Determine whether a given point hits a menu item."""
        # Only consider the lines associated with menu items.
        for line, coords, item, disabled in [l for l in self._buf
                                             if l[2] is not None]:
            if not disabled and line.get_rect().move(coords).collidepoint(pos):
                return item

        return None

    def _on_keypress(self, event):
        if event.key in [pygame.K_UP, pygame.K_LEFT]:
            if self._selected_index > 0:
                self._selected_index -= 1
        elif event.key in [pygame.K_DOWN, pygame.K_RIGHT]:
            if self._selected_index < len(self._items) - 1:
                self._selected_index += 1
        elif event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
            mouse.current.set_cursor(mouse.Cursor.ARROW)
            self._on_choose(self._items[self._selected_index])

    def _on_mouseclick(self, event):
        """Determine whether we've clicked on a menu item."""
        item = self._hit_item(event.pos)
        if item is not None:
            mouse.current.set_cursor(mouse.Cursor.ARROW)
            self._on_choose(item)

    def _on_mousemove(self, event):
        """Determine if we've moused over a menu item."""
        item = self._hit_item(event.pos)
        if item is not None:
            self._selected_index = self._items.index(item)
            mouse.current.set_cursor(mouse.Cursor.HAND)
        else:
            mouse.current.set_cursor(mouse.Cursor.ARROW)

    def _on_choose(self, item):
        """Handle activation of a menu item."""
        pass
