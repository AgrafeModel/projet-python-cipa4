# Fichier : gui/widgets.py
# Gestion des widgets de l'interface utilisateur (boutons, champs de texte, etc.)
# Note : Commentaires en anglais redigé par IA pour uniformité du code.
# Note : Certaines parties du code ont été générées par une IA (Copilot). Le code est fait à la
# main par l'humain, mais l'IA ajoute des optimisations et des suggestions.

import pygame


class Button:
    # Initializes a button with given rectangle, text, and font
    def __init__(self, rect, text, font):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.hover = False

    # Returns True if clicked
    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True

        return False

    # Draws the button on the surface
    def draw(self, surface):
        color = (80, 80, 80) if not self.hover else (110, 110, 110)
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (180, 180, 180), self.rect, 2, border_radius=10)

        label = self.font.render(self.text, True, (240, 240, 240))
        surface.blit(label, label.get_rect(center=self.rect.center))


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
        self.messages = []  # {"name_ia": str, "text": str, "show_name_ia": bool}

    # Adds a message to the chat box
    def add_message(self, name_ia: str, text: str, show_name_ia: bool = True):
        self.messages.append({"name_ia": name_ia, "text": text, "show_name_ia": show_name_ia})
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

        # Draw each message with wrapping
        for m in self.messages:
            prefix = f"{m['name_ia']}: " if m["show_name_ia"] else "???: "
            lines = self._wrap_text(prefix + m["text"], max_w)
            for line in lines:
                label = self.font.render(line, True, (235, 235, 235))
                surface.blit(label, (x, y))
                y += self.font.get_linesize()
            y += self.line_gap

        # Restore previous clip
        surface.set_clip(clip)


# Panel displaying the list of players
class PlayerListPanel:
    # Initializes the player list panel
    """
    players: list of dict
      {
        "name": str,
        "alive": bool,
        "role": "villageois" | "loup",
        "note": int  # 0=none,1=gentil,2=suspect,3=loup
      }
    """
    NOTE_LABELS = ["-", "Gentil", "Suspect", "Loup"]

    # Initializes the player list panel with given rectangle, font, and players
    def __init__(self, rect: pygame.Rect, font: pygame.font.Font, small_font: pygame.font.Font, players: list[dict]):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.small_font = small_font
        self.players = players

        # Layout settings
        self.padding = 10
        self.title_h = 44
        self.row_h = 44

        self.scroll_px = 0  # current scroll position in pixels (vertical)

    # Calculates the viewport rectangle for the rows
    def _rows_viewport_rect(self) -> pygame.Rect:
        # Returns the rectangle area where rows are drawn (excluding title)
        return pygame.Rect(
            self.rect.x,
            self.rect.y + self.title_h,
            self.rect.width,
            self.rect.height - self.title_h
        )

    # Calculates the total content height
    def _content_height(self) -> int:
        return len(self.players) * self.row_h

    # Calculates the maximum scroll position
    def _max_scroll(self) -> int:
        vp = self._rows_viewport_rect()
        # value such that bottom of content aligns with bottom of viewport
        return max(0, self._content_height() - (vp.height - self.padding))

    def handle_event(self, event):
        # Scroll uniquement si la souris est au-dessus du panneau
        if event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if not self.rect.collidepoint(mx, my):
                return
            # scroll up -> event.y > 0
            self.scroll_px = max(0, min(self._max_scroll(), self.scroll_px - event.y * 40))
            return

        # Handle clicks on note buttons
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        # Retrieve mouse position
        mx, my = event.pos
        vp = self._rows_viewport_rect()
        if not vp.collidepoint(mx, my):
            return

        # Convert mouse y to row index considering scroll
        local_y = (my - vp.y) + self.scroll_px
        idx = int(local_y // self.row_h)
        # Safety check on index
        if idx < 0 or idx >= len(self.players):
            return

        # Toggle note for the clicked player
        p = self.players[idx]
        if not p["alive"]:
            return  # mort -> note désactivée

        # Toggle note for the clicked player
        btn_rect = self._note_rect_for_row(idx)
        if btn_rect.collidepoint(mx, my):
            # Cycle through notes 0->1->2->3->0
            p["note"] = (p["note"] + 1) % 4

    # Calculates the rectangle for a specific row
    def _row_rect(self, idx: int) -> pygame.Rect:
        vp = self._rows_viewport_rect()
        # y position considering scroll and padding
        y = vp.y + self.padding + idx * self.row_h - self.scroll_px
        x = self.rect.x + self.padding
        w = self.rect.width - 2 * self.padding
        h = self.row_h - 6
        return pygame.Rect(x, y, w, h)

    # Calculates the rectangle for the note button in a specific row
    def _note_rect_for_row(self, idx: int) -> pygame.Rect:
        row = self._row_rect(idx)
        w, h = 90, 30  # button size
        # Returns rectangle aligned to the right of the row
        return pygame.Rect(
            row.right - 10 - w,
            row.y + (row.height - h) // 2,
            w,
            h
        )

    # Calculates the rectangle for the role badge in a specific row
    def _role_badge_rect_for_row(self, idx: int) -> pygame.Rect:
        row = self._row_rect(idx)
        w, h = 90, 30
        return pygame.Rect(row.right - 10 - w, row.y + (row.height - h) // 2, w, h)

    # Draws the player list panel on the surface
    def draw(self, surface):
        # Panel background and border
        pygame.draw.rect(surface, (35, 35, 40), self.rect, border_radius=12)
        pygame.draw.rect(surface, (180, 180, 180), self.rect, 2, border_radius=12)

        # Title 
        title = self.font.render("Joueurs", True, (235, 235, 235))
        surface.blit(title, (self.rect.x + self.padding, self.rect.y + 8))

        # Content (player rows) with clipping for scrolling
        vp = self._rows_viewport_rect()
        clip = surface.get_clip()
        surface.set_clip(vp)

        # Draw each player row
        for i, p in enumerate(self.players):
            row_rect = self._row_rect(i)

            # Outside viewport -> skip
            if row_rect.bottom < vp.top or row_rect.top > vp.bottom:
                continue

            pygame.draw.rect(surface, (45, 45, 52), row_rect, border_radius=10)

            # Name label
            name_color = (220, 220, 220) if p["alive"] else (140, 140, 140)
            name_label = self.font.render(p["name"], True, name_color)
            surface.blit(name_label, (row_rect.x + 10, row_rect.y + 8))

            # Note button or role badge depending on alive status
            if p["alive"]:
                btn = self._note_rect_for_row(i)
                pygame.draw.rect(surface, (120, 80, 160), btn, border_radius=8)
                pygame.draw.rect(surface, (200, 200, 200), btn, 2, border_radius=8)
                lab = self.small_font.render(self.NOTE_LABELS[p["note"]], True, (240, 240, 240))
                surface.blit(lab, lab.get_rect(center=btn.center))
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

        surface.set_clip(clip)