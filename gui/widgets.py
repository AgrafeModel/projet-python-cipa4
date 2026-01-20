# Fichier : gui/widgets.py
# Gestion des widgets de l'interface utilisateur (boutons, champs de texte, etc.)

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