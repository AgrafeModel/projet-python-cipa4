# Fichier : gui/widgets.py
# Gestion des widgets de l'interface utilisateur (boutons, champs de texte, etc.)
# Note : Commentaires en anglais redigé par IA pour uniformité du code.
# Note : Certaines parties du code ont été générées par une IA (Copilot). Le code est fait à la
# main par l'humain, mais l'IA ajoute des optimisations et des suggestions.

import pygame
import hashlib


# Generate distinctive colors for player names
def generate_player_color(player_name: str) -> tuple[int, int, int]:
    """Generate a consistent, readable color for each player based on their name."""
    # Use hash of player name to get consistent color
    hash_value = int(hashlib.md5(player_name.encode()).hexdigest()[:6], 16)
    
    # Extract RGB components and adjust for readability
    r = (hash_value >> 16) & 0xFF
    g = (hash_value >> 8) & 0xFF
    b = hash_value & 0xFF
    
    # Ensure colors are bright enough to read on dark background
    # Minimum brightness threshold
    min_brightness = 120
    
    # Boost colors if too dark
    if r + g + b < min_brightness * 3:
        r = min(255, r + 80)
        g = min(255, g + 80)
        b = min(255, b + 80)
    
    # Avoid colors too similar to system color (orange)
    # If color is too orange-ish, shift it
    if r > 200 and g > 100 and g < 180 and b < 100:
        g = min(255, g + 60)  # Make more yellow or red
    
    return (r, g, b)

# Loads and scales an icon from the given path to the specified size
def load_icon(path, size):
    icon = pygame.image.load(path).convert_alpha()
    icon = pygame.transform.smoothscale(icon, size)
    return icon

# System message color (red for system messages)
SYSTEM_COLOR = (255, 100, 100)


# Button widget with hover effect and optional tooltip
class Button:
    def __init__(self, rect, text, font, tooltip: str = ""):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.tooltip = tooltip
        self.hover = False
        self.enabled = True # Button enabled state

    # Handles events for the button, returns True if clicked
    def handle_event(self, event) -> bool:
        if not self.enabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True

        return False

    # Returns the tooltip text if hovered
    def get_hover_text(self, mouse_pos) -> str:
        if self.rect.collidepoint(mouse_pos):
            return self.tooltip
        return ""

    # Draws the button on the surface
    def draw(self, surface):
        if not self.enabled:
            color = (60, 60, 60) # grisé
            border = (120, 120, 120)
            text_color = (140, 140, 140)
        else:
            color = (80, 80, 80) if not self.hover else (110, 110, 110)
            border = (180, 180, 180)
            text_color = (240, 240, 240)

        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=10)

        label = self.font.render(self.text, True, text_color)
        surface.blit(label, label.get_rect(center=self.rect.center))


# Stepper widget for selecting numeric values
class Stepper:
    # Initializes a stepper widget with plus and minus buttons
    def __init__(self, x, y, w, h, value, min_value, max_value, font):
        self.value = value
        self.min_value = min_value
        self.max_value = max_value
        self.font = font

        btn_w = h
        self.minus_btn = Button((x, y, btn_w, h), "-", font)
        self.plus_btn = Button((x + w - btn_w, y, btn_w, h), "+", font)
        self.value_rect = pygame.Rect(x + btn_w + 10, y, w - (2 * btn_w) - 20, h)

    # Handles events for the stepper, returns True if value changed
    def handle_event(self, event) -> bool:
        changed = False

        if self.minus_btn.handle_event(event):
            self.value = max(self.min_value, self.value - 1)
            changed = True

        if self.plus_btn.handle_event(event):
            self.value = min(self.max_value, self.value + 1)
            changed = True

        return changed

    # Draws the stepper on the surface
    def draw(self, surface):
        self.minus_btn.draw(surface)
        self.plus_btn.draw(surface)

        pygame.draw.rect(surface, (50, 50, 50), self.value_rect, border_radius=10)
        pygame.draw.rect(surface, (180, 180, 180), self.value_rect, 2, border_radius=10)

        label = self.font.render(str(self.value), True, (240, 240, 240))
        surface.blit(label, label.get_rect(center=self.value_rect.center))


# Chat box for displaying messages
# Using _ to indicate private methods
class ChatBox:
    # Initializes the chat box with given rectangle and font
    def __init__(self, rect: pygame.Rect, font: pygame.font.Font):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.padding = 12
        self.line_gap = 6
        self.scroll_px = 0
        self.messages = []  # {"name_ia": str, "text": str, "show_name_ia": bool, "color": tuple}
        self.player_colors = {}  # Cache of player colors

    # Adds a message to the chat box
    def add_message(self, name_ia: str, text: str, show_name_ia: bool = True, is_system: bool = False):
        # Determine color for the message
        if is_system:
            color = SYSTEM_COLOR
        else:
            if name_ia not in self.player_colors:
                self.player_colors[name_ia] = generate_player_color(name_ia)
            color = self.player_colors[name_ia]
        
        self.messages.append({
            "name_ia": name_ia, 
            "text": text, 
            "show_name_ia": show_name_ia,
            "color": color
        })
        self.scroll_to_bottom()

    # Scrolls the chat box to the bottom
    def scroll_to_bottom(self):
        content_h = self._get_content_height()
        viewport_h = self.rect.height - 2 * self.padding
        self.scroll_px = max(0, content_h - viewport_h)

    # Handles scroll events
    # We can only scroll if the mouse is over the chat box
    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            # note : pygame MOUSEWHEEL does not use event.pos for mouse position
            mx, my = pygame.mouse.get_pos()
            if not self.rect.collidepoint(mx, my):
                return
            self.scroll_px = max(0, self.scroll_px - event.y * 40)

    # Wraps text into multiple lines based on max width
    def _wrap_text(self, text: str, max_w: int):
        words = text.split(" ")
        lines = []
        current = ""
        for w in words:
            test = (current + " " + w).strip()
            if self.font.size(test)[0] <= max_w:
                current = test
            else:
                if current:
                    lines.append(current)
                current = w
        if current:
            lines.append(current)
        return lines

    # Calculates the total height of the content
    def _get_content_height(self) -> int:
        max_w = self.rect.width - 2 * self.padding
        total = 0
        for m in self.messages:
            # Prefix the message with the IA name or "???"
            prefix = f"{m['name_ia']}: " if m["show_name_ia"] else "???: "
            # List of lines after wrapping
            lines = self._wrap_text(prefix + m["text"], max_w)
            # total height for this message
            total += len(lines) * self.font.get_linesize() + self.line_gap
        return total

    # Draws the chat box on the surface
    def draw(self, surface):
        pygame.draw.rect(surface, (25, 25, 30), self.rect, border_radius=12)
        pygame.draw.rect(surface, (180, 180, 180), self.rect, 2, border_radius=12)

        # Clip to chat box area for scrolling
        clip = surface.get_clip()
        surface.set_clip(self.rect)

        x = self.rect.x + self.padding
        y = self.rect.y + self.padding - self.scroll_px
        max_w = self.rect.width - 2 * self.padding

        # Draw each message with wrapping and colors
        for m in self.messages:
            message_color = m.get("color", (235, 235, 235))
            is_system_msg = message_color == SYSTEM_COLOR
            prefix = f"{m['name_ia']}: " if m["show_name_ia"] else "???: "
            full_text = prefix + m["text"]
            
            # Wrap the full text
            lines = self._wrap_text(full_text, max_w)
            
            for i, line in enumerate(lines):
                if is_system_msg:
                    # System messages: everything in red
                    label = self.font.render(line, True, message_color)
                    surface.blit(label, (x, y))
                elif i == 0 and m["show_name_ia"]:
                    # First line of player message: render name in color, rest in white
                    if ": " in line:
                        name_part, text_part = line.split(": ", 1)
                        name_part += ": "
                        
                        # Render name part in player color
                        name_surface = self.font.render(name_part, True, message_color)
                        surface.blit(name_surface, (x, y))
                        
                        # Render text part in white
                        name_width = self.font.size(name_part)[0]
                        text_surface = self.font.render(text_part, True, (235, 235, 235))
                        surface.blit(text_surface, (x + name_width, y))
                    else:
                        # Fallback: render entire line in player color
                        label = self.font.render(line, True, message_color)
                        surface.blit(label, (x, y))
                else:
                    # Other lines: render in white (continuation of message)
                    label = self.font.render(line, True, (235, 235, 235))
                    surface.blit(label, (x, y))
                
                y += self.font.get_linesize()
            
            y += self.line_gap

        # Restore previous clip
        surface.set_clip(clip)


# Panel displaying the list of players
class PlayerListPanel:
    # Labels for player notes
    NOTE_LABELS = ["-", "Gentil", "Suspect", "Loup"]

    # Initializes the player list panel
    def __init__(self, rect: pygame.Rect, font: pygame.font.Font, small_font: pygame.font.Font, players: list[dict]):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.small_font = small_font
        self.players = players

        # Layout
        self.padding = 10
        self.title_h = 44
        self.row_h = 44
        self.scroll_px = 0

        # Vote button state
        self.show_vote_buttons = False
        self.on_vote = None  # callable(index:int) -> None
        self.selected_vote_index = None

    # Returns the rectangle for the rows viewport
    def _rows_viewport_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.rect.x,
            self.rect.y + self.title_h,
            self.rect.width,
            self.rect.height - self.title_h
        )

    # Calculates the total content height
    def _content_height(self) -> int:
        return len(self.players) * self.row_h

    # Maximum scroll position
    def _max_scroll(self) -> int:
        vp = self._rows_viewport_rect()
        return max(0, self._content_height() - (vp.height - self.padding))

    # Returns the rectangle for a specific row
    def _row_rect(self, idx: int) -> pygame.Rect:
        vp = self._rows_viewport_rect()
        y = vp.y + self.padding + idx * self.row_h - self.scroll_px
        x = self.rect.x + self.padding
        w = self.rect.width - 2 * self.padding
        h = self.row_h - 6
        return pygame.Rect(x, y, w, h)

    # Note button rectangle for a specific row
    def _note_rect_for_row(self, idx: int) -> pygame.Rect:
        row = self._row_rect(idx)
        w, h = 100, 30
        return pygame.Rect(row.right - 10 - w, row.y + (row.height - h) // 2, w, h)

    # Role badge rectangle for a specific row
    def _role_badge_rect_for_row(self, idx: int) -> pygame.Rect:
        row = self._row_rect(idx)
        w, h = 100, 30
        return pygame.Rect(row.right - 10 - w, row.y + (row.height - h) // 2, w, h)

    # Vote button rectangle for a specific row
    def _vote_rect_for_row(self, idx: int) -> pygame.Rect:
        row = self._row_rect(idx)
        w, h = 76, 30
        x = row.right - 10 - 100 - 12 - w
        y = row.y + (row.height - h) // 2
        return pygame.Rect(x, y, w, h)


    # Handles events for the player list panel
    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if not self.rect.collidepoint(mx, my):
                return
            # Scroll up/down
            self.scroll_px = max(0, min(self._max_scroll(), self.scroll_px - event.y * 40))
            return

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        # Handle clicks on rows
        mx, my = event.pos
        vp = self._rows_viewport_rect()
        if not vp.collidepoint(mx, my):
            return

        # Determine which row was clicked
        local_y = (my - vp.y) + self.scroll_px
        idx = int(local_y // self.row_h)
        if idx < 0 or idx >= len(self.players):
            return

        # Get the player
        p = self.players[idx]
        if not p["alive"]:
            return

        # Vote click
        if self.show_vote_buttons:
            vote_rect = self._vote_rect_for_row(idx)
            if vote_rect.collidepoint(mx, my):
                self.selected_vote_index = idx
                if callable(self.on_vote):
                    self.on_vote(idx)  # Send index of voted player
                return


        # Note click
        note_rect = self._note_rect_for_row(idx)
        if note_rect.collidepoint(mx, my):
            p["note"] = (p["note"] + 1) % 4
    
    # Returns hover text for the given mouse position
    def get_hover_text(self, mouse_pos) -> str:
        mx, my = mouse_pos
        vp = self._rows_viewport_rect()
        if not vp.collidepoint(mx, my):
            return ""

        # Determine which row is hovered
        local_y = (my - vp.y) + self.scroll_px
        idx = int(local_y // self.row_h)
        if idx < 0 or idx >= len(self.players):
            return ""

        p = self.players[idx]
        if not p["alive"]:
            return f"{p['name']} est mort.\nRôle révélé : {p['role'].capitalize()}"

        # vote hover
        if self.show_vote_buttons and self._vote_rect_for_row(idx).collidepoint(mx, my):
            return f"Voter\nSélectionner {p['name']} comme cible"

        # note hover
        note_rect = self._note_rect_for_row(idx)
        if note_rect.collidepoint(mx, my):
            label = self.NOTE_LABELS[p["note"]]
            meaning = "Neutre" if label == "-" else label
            return f"Annotation personnelle : {meaning}\nClique pour changer"

        return ""

    # Determines the color for a player's name based on their note and alive status
    def _name_color_for_note(self, p: dict) -> tuple[int, int, int]:
        if not p.get("alive", True):
            return (120, 120, 120)

        note = p.get("note", 0)

        # Mapping notes to colors: 0=neutre, 1=gentil, 2=suspect, 3=loup
        if note == 3:
            return (220, 70, 70)
        if note == 1:
            return (90, 200, 90)
        if note == 2:
            return (240, 170, 60)

        # Default color based on player name
        return (230, 230, 230)

    # Draws the player list panel
    def draw(self, surface):
        pygame.draw.rect(surface, (35, 35, 40), self.rect, border_radius=12)
        pygame.draw.rect(surface, (180, 180, 180), self.rect, 2, border_radius=12)

        # Title
        title = self.font.render("Joueurs", True, (235, 235, 235))
        surface.blit(title, (self.rect.x + self.padding, self.rect.y + 8))

        # Rows
        vp = self._rows_viewport_rect()
        clip = surface.get_clip()
        surface.set_clip(vp)

        # Draw each player row
        for i, p in enumerate(self.players):
            row_rect = self._row_rect(i)
            if row_rect.bottom < vp.top or row_rect.top > vp.bottom:
                continue

            pygame.draw.rect(surface, (45, 45, 52), row_rect, border_radius=10)

            # Player name with color based on note and alive status
            name_col = self._name_color_for_note(p)
            name_label = self.font.render(p["name"], True, name_col)

            surface.blit(name_label, (row_rect.x + 10, row_rect.y + 8))

            # Draw vote button and note badge if alive
            if p["alive"]:
                if self.show_vote_buttons:
                    vr = self._vote_rect_for_row(i)

                    # Colors for vote button states
                    base = (230, 150, 40)
                    hover = (255, 205, 110)
                    border = (210, 210, 210)
                    hover_border = (255, 245, 220)
                    text_col = (25, 25, 25)
                    selected_bg = (200, 120, 30)

                    mx, my = pygame.mouse.get_pos()
                    is_hover = vr.collidepoint(mx, my) and vp.collidepoint(mx, my)

                    # Draw button background with hover and selection states
                    draw_rect = vr.inflate(4, 2) if is_hover else vr  # +4px, +2px on hover for a "pop" effect
                    if is_hover:
                        bg = hover
                    elif self.selected_vote_index == i:
                        bg = selected_bg
                    else:
                        bg = base


                    pygame.draw.rect(surface, bg, draw_rect, border_radius=10)

                    # Border with stronger highlight if selected, else hover effect, else normal
                    if self.selected_vote_index == i:
                        # selected: strong highlight + inner glow
                        pygame.draw.rect(surface, (255, 240, 210), draw_rect, 3, border_radius=10)
                    elif is_hover:
                        # hover only: subtle highlight
                        pygame.draw.rect(surface, hover_border, draw_rect, 3, border_radius=10)
                        pygame.draw.rect(surface, (120, 90, 40), draw_rect.inflate(4, 4), 2, border_radius=12)
                    else:
                        pygame.draw.rect(surface, border, draw_rect, 2, border_radius=10)

                    # Text centered in the button
                    lab = self.small_font.render("Voter", True, text_col)
                    surface.blit(lab, lab.get_rect(center=draw_rect.center))




                # Note badge
                btn = self._note_rect_for_row(i)
                pygame.draw.rect(surface, (120, 80, 160), btn, border_radius=8)
                pygame.draw.rect(surface, (200, 200, 200), btn, 2, border_radius=8)
                lab = self.small_font.render(self.NOTE_LABELS[p["note"]], True, (240, 240, 240))
                surface.blit(lab, lab.get_rect(center=btn.center))

            # Draw role badge if dead
            else:
                badge = self._role_badge_rect_for_row(i)
                role = p["role"]
                if role == "villageois":
                    outline = (80, 220, 120)
                    text = "Villageois"
                else:
                    outline = (230, 80, 80)
                    text = "Loup"

                pygame.draw.rect(surface, (30, 30, 34), badge, border_radius=8)
                pygame.draw.rect(surface, outline, badge, 2, border_radius=8)
                lab = self.small_font.render(text, True, (230, 230, 230))
                surface.blit(lab, lab.get_rect(center=badge.center))

        # Restore previous clip
        surface.set_clip(clip)

# Tooltip widget for displaying hover text
class Tooltip:
    def __init__(self, font: pygame.font.Font):
        self.font = font
        self.padding = 8

    # Draws the tooltip at the given position
    def draw(self, surface, text: str, pos: tuple[int, int]):
        if not text:
            return

        # Let's support multi-line tooltips
        lines = text.split("\n")
        rendered = [self.font.render(line, True, (240, 240, 240)) for line in lines]

        # Calculate size
        w = max(r.get_width() for r in rendered) + 2 * self.padding
        h = sum(r.get_height() for r in rendered) + 2 * self.padding + (len(lines) - 1) * 2

        x, y = pos
        x += 14
        y += 14

        # keep inside window
        sw, sh = surface.get_size()
        if x + w > sw:
            x = sw - w - 10
        if y + h > sh:
            y = sh - h - 10

        # Tooltip background
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surface, (20, 20, 24), rect, border_radius=8)
        pygame.draw.rect(surface, (180, 180, 180), rect, 1, border_radius=8)

        # Draw each line
        yy = y + self.padding
        for r in rendered:
            surface.blit(r, (x + self.padding, yy))
            yy += r.get_height() + 2



# Text input widget with optional password masking and reveal toggle
class TextInput:
    def __init__(self, rect, font, placeholder="", mask=False):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.placeholder = placeholder
        self.mask = mask

        # Load icons for reveal toggle
        self.icon_eye = load_icon("assets/eye.png", (22, 22))
        self.icon_eye_slash = load_icon("assets/eye_slash.png", (22, 22))

        self.text = ""
        self.active = False

        # cursor / selection
        self.cursor_pos = 0  # position in self.text
        self.cursor_timer = 0.0
        self.show_cursor = True

        # horizontal scroll (pixels)
        self.scroll_x = 0

        # backspace hold repeat
        self._backspace_held = False
        self._backspace_initial_delay = 0.35
        self._backspace_repeat_rate = 0.045
        self._backspace_timer = 0.0
        self._backspace_repeat_timer = 0.0

        # reveal toggle for masked inputs
        self.reveal = False
        self.toggle_rect = pygame.Rect(0, 0, 0, 0)

    # Deletes the character to the left of the cursor   
    def _delete_left(self):
        if self.cursor_pos > 0 and self.text:
            self.text = self.text[: self.cursor_pos - 1] + self.text[self.cursor_pos :]
            self.cursor_pos -= 1

    # Inserts text at the cursor position
    def _insert_text(self, s: str):
        if not s:
            return
        self.text = self.text[: self.cursor_pos] + s + self.text[self.cursor_pos :]
        self.cursor_pos += len(s)

    # Clamps the cursor position to be within the bounds of the text
    def _clamp_cursor(self):
        self.cursor_pos = max(0, min(self.cursor_pos, len(self.text)))

    # Ensures the cursor is visible by adjusting scroll_x based on the cursor position and text width
    def _ensure_cursor_visible(self, display_text: str, text_area_w: int):
        # Calculate the pixel width of the text up to the cursor position
        prefix = display_text[: self.cursor_pos]
        prefix_w = self.font.size(prefix)[0]

        # Adjust scroll_x to ensure the cursor is visible within the text area
        if prefix_w - self.scroll_x < 0:
            self.scroll_x = prefix_w
        elif prefix_w - self.scroll_x > text_area_w:
            self.scroll_x = prefix_w - text_area_w

        # clamp scroll_x to not scroll beyond the text width
        full_w = self.font.size(display_text)[0]
        self.scroll_x = max(0, min(self.scroll_x, max(0, full_w - text_area_w)))

    # Converts a mouse x-coordinate to a cursor position index in the text, accounting for scrolling
    def _pos_from_mouse_x(self, mouse_x: int, display_text: str, text_start_x: int):
        rel_x = (mouse_x - text_start_x) + self.scroll_x
        rel_x = max(0, rel_x)

        # Binary search to find the character index corresponding to the mouse x position
        lo, hi = 0, len(display_text)
        while lo < hi:
            mid = (lo + hi) // 2
            w = self.font.size(display_text[:mid])[0]
            if w < rel_x:
                lo = mid + 1
            else:
                hi = mid
        return lo

    # Handles events for the text input, including mouse clicks, keyboard input, and backspace hold repeat
    def handle_event(self, event):
        if self.mask:
            self.toggle_rect = pygame.Rect(self.rect.right - 46, self.rect.y + 6, 40, self.rect.height - 12)

        # Mouse
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # toggle reveal
            if self.mask and self.toggle_rect.collidepoint(event.pos):
                self.reveal = not self.reveal
                return None

            # click inside input box
            was_active = self.active
            self.active = self.rect.collidepoint(event.pos)

            if self.active:
                # move cursor to click position
                display = self.text
                if self.mask and self.text and not self.reveal:
                    display = "*" * len(self.text)

                text_start_x = self.rect.x + 12
                text_area_w = self.rect.width - 24 - (46 if self.mask else 0)
                self.cursor_pos = self._pos_from_mouse_x(event.pos[0], display, text_start_x)
                self._clamp_cursor()
                self._ensure_cursor_visible(display, text_area_w)

                # reset blinking for better UX
                self.cursor_timer = 0.0
                self.show_cursor = True

            # if we clicked outside and were previously active, stop backspace repeat
            if not self.active and was_active:
                self._backspace_held = False

        # Backspace key up stops repeating
        if event.type == pygame.KEYUP and event.key == pygame.K_BACKSPACE:
            self._backspace_held = False

        # Keyboard input
        if event.type == pygame.KEYDOWN and self.active:
            # Paste (Ctrl+V / Cmd+V)
            if (event.key == pygame.K_v) and (event.mod & pygame.KMOD_CTRL or event.mod & pygame.KMOD_META):
                try:
                    clip = pygame.scrap.get(pygame.SCRAP_TEXT)
                    if clip:
                        pasted = clip.decode("utf-8", errors="ignore")
                        pasted = pasted.replace("\x00", "").replace("\r", "").replace("\n", "").strip()
                        self._insert_text(pasted)
                except Exception:
                    pass

            elif event.key == pygame.K_BACKSPACE:
                # delete once immediately, then repeat in update()
                self._delete_left()
                self._backspace_held = True
                self._backspace_timer = 0.0
                self._backspace_repeat_timer = 0.0

            elif event.key == pygame.K_RETURN:
                return "enter"

            elif event.key == pygame.K_LEFT:
                self.cursor_pos -= 1
                self._clamp_cursor()

            elif event.key == pygame.K_RIGHT:
                self.cursor_pos += 1
                self._clamp_cursor()

            elif event.key == pygame.K_HOME:
                self.cursor_pos = 0

            elif event.key == pygame.K_END:
                self.cursor_pos = len(self.text)

            else:
                if event.unicode and len(event.unicode) == 1:
                    # avoid null chars etc.
                    ch = event.unicode.replace("\x00", "")
                    if ch:
                        self._insert_text(ch)

        return None

    # Updates the text input state, including cursor blinking and backspace hold repeat
    def update(self, dt):
        # cursor blink
        if self.active:
            self.cursor_timer += dt
            if self.cursor_timer >= 0.5:
                self.cursor_timer = 0.0
                self.show_cursor = not self.show_cursor
        else:
            self.show_cursor = False

        # backspace hold repeat
        if self.active and self._backspace_held:
            self._backspace_timer += dt
            if self._backspace_timer >= self._backspace_initial_delay:
                self._backspace_repeat_timer += dt
                while self._backspace_repeat_timer >= self._backspace_repeat_rate:
                    self._backspace_repeat_timer -= self._backspace_repeat_rate
                    self._delete_left()
                    if self.cursor_pos <= 0:
                        self._backspace_held = False
                        break
    
    # Draws the text input on the surface, including background, text (with masking if enabled), cursor, and reveal toggle button
    def draw(self, surface):
        bg = (35, 35, 40) if not self.active else (45, 45, 55)
        pygame.draw.rect(surface, bg, self.rect, border_radius=10)
        pygame.draw.rect(surface, (180, 180, 180), self.rect, 2, border_radius=10)

        # choose display text
        display = self.text
        if self.mask and self.text and not self.reveal:
            display = "*" * len(self.text)

        # area where text is allowed (exclude padding + reveal button)
        pad_left = 12
        pad_right = 12 + (46 if self.mask else 0)
        text_area_w = self.rect.width - pad_left - pad_right

        # placeholder / label rendering
        if not display and not self.active and self.placeholder:
            label_surf = self.font.render(self.placeholder, True, (140, 140, 140))
            label_x = self.rect.x + pad_left
            label_y = self.rect.y + (self.rect.height - label_surf.get_height()) // 2
            surface.blit(label_surf, (label_x, label_y))
        else:
            # make sure cursor is visible
            self._clamp_cursor()
            self._ensure_cursor_visible(display, text_area_w)

            # clip area
            clip_rect = pygame.Rect(self.rect.x + pad_left, self.rect.y, text_area_w, self.rect.height)
            old_clip = surface.get_clip()
            surface.set_clip(clip_rect)

            label_surf = self.font.render(display, True, (240, 240, 240))
            label_x = self.rect.x + pad_left - self.scroll_x
            label_y = self.rect.y + (self.rect.height - label_surf.get_height()) // 2
            surface.blit(label_surf, (label_x, label_y))

            # cursor
            if self.active and self.show_cursor:
                prefix = display[: self.cursor_pos]
                cursor_px = self.font.size(prefix)[0]
                cursor_x = self.rect.x + pad_left + cursor_px - self.scroll_x
                pygame.draw.line(
                    surface,
                    (240, 240, 240),
                    (cursor_x, self.rect.y + 10),
                    (cursor_x, self.rect.bottom - 10),
                    2,
                )

            surface.set_clip(old_clip)

        # reveal toggle button
        if self.mask:
            self.toggle_rect = pygame.Rect(self.rect.right - 46, self.rect.y + 6, 40, self.rect.height - 12)
            pygame.draw.rect(surface, (60, 60, 70), self.toggle_rect, border_radius=10)
            pygame.draw.rect(surface, (160, 160, 160), self.toggle_rect, 2, border_radius=10)

            icon = self.icon_eye if self.reveal else self.icon_eye_slash
            icon_rect = icon.get_rect(center=self.toggle_rect.center)
            surface.blit(icon, icon_rect)
