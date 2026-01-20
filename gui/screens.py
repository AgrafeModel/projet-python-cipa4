# Fichier : gui/screen.py
# Gestion des écrans et de l'interface utilisateur (menus, affichage, etc.)

import pygame

from gui.widgets import Button, Stepper

# Base class for all screens
class Screen:
    def __init__(self, app):
        self.app = app

    def handle_event(self, event):
        pass

    def update(self, dt: float):
        pass

    def draw(self, surface):
        pass

# Screen to set up the game
class SetupScreen(Screen):
    # Initializes the setup screen with title, stepper, and start button
    def __init__(self, app):
        super().__init__(app)
        self.title_font = pygame.font.SysFont(None, 64)
        self.font = pygame.font.SysFont(None, 36)

        self.num_players = Stepper(
            x = app.w // 2 - 160,
            y = app.h // 2 - 30,
            w = 320,
            h = 60,
            value = 6,
            min_value = 6,
            max_value = 20,
            font = self.font
        )

        # Start button
        self.start_btn = Button(
            rect=(app.w // 2 - 120, app.h // 72, 240, 60),
            text="START",
            font=self.font
        )

    # Handles events for the setup screen
    def handle_event(self, event):
        self.num_players.handle_event(event)

        if self.start_btn.handle_event(event):
            self.app.set_screen(GameScreen(self.app, self.num_players.value))

    # Draws the setup screen
    def draw(self, surface):
        surface.fill((20, 20, 25))

        title = self.title_font.render("Loup-Garou IA", True, (240, 240, 240))
        surface.blit(title, title.get_rect(center=(self.app.w // 2, 120)))

        label = self.font.render("Nombre de joueurs (min. 6)", True, (200, 200, 200))
        surface.blit(label, label.get_rect(center=(self.app.w // 2, self.app.h // 2 - 70)))

        self.num_players.draw(surface)
        self.start_btn.draw(surface)


# Screen for the main game
class GameScreen(Screen):
    # Initializes the game screen with number of players
    def __init__(self, app, num_players: int):
        super().__init__(app)
        self.font = pygame.font.SysFont(None, 36)
        self.num_players = num_players

    # Handles events for the game screen
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.set_screen(SetupScreen(self.app))

    # Draws the game screen
    def draw(self, surface):
        surface.fill((15, 15, 18))
        txt = self.font.render(f"Game started with {self.num_players} players", True, (240, 240, 240))
        surface.blit(txt, (30, 30))

        hint = self.font.render("ESC = retour au menu", True, (180, 180, 180))
        surface.blit(hint, (30, 70))