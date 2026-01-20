# Fichier : gui/screen.py
# Gestion des écrans et de l'interface utilisateur (menus, affichage, etc.)
# Note : Commentaires en anglais redigé par IA pour uniformité du code.
# Note : Certaines parties du code ont été générées par une IA (Copilot). Le code est fait à la
# main par l'humain, mais l'IA ajoute des optimisations et des suggestions.

import pygame

from gui.widgets import Button, Stepper, ChatBox, PlayerListPanel

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
            rect=(app.w // 2 - 120, app.h // 2 + 70, 240, 60),
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


# Main game screen
class GameScreen(Screen):
    def __init__(self, app, num_players: int):
        super().__init__(app)

        # Fonts
        self.font = pygame.font.SysFont(None, 30)
        self.small_font = pygame.font.SysFont(None, 22)
        self.big_font = pygame.font.SysFont(None, 34)

        # Layout (comme ton dessin)
        margin = 20
        left_w = 320
        gap = 20

        self.info_rect = pygame.Rect(margin, margin, left_w, 80)
        self.list_rect = pygame.Rect(margin, margin + 100, left_w, app.h - (margin + 100) - margin)
        self.chat_rect = pygame.Rect(margin + left_w + gap, margin, app.w - (margin + left_w + gap) - margin, app.h - 2 * margin)

        # Phase mock (on branchera au moteur ensuite)
        self.phase = "Jour"  # "Nuit"
        self.day_count = 1

        # Players mock (roles déjà attribués, mais affichés seulement si mort)
        self.players = []
        for i in range(num_players):
            self.players.append({
                "name": f"IA_{i+1}",
                "alive": True,
                "role": "villageois" if i < max(1, num_players // 4) else "loup",  # juste pour tester
                "note": 0
            })

        # Widgets
        self.chat = ChatBox(self.chat_rect, self.font)
        self.player_list = PlayerListPanel(self.list_rect, self.font, self.small_font, self.players)

        # Seed test messages
        self._seed_test_messages()

    # Adds some initial test messages to the chat
    def _seed_test_messages(self):
        self.chat.add_message("IA_2", "Bon, on doit trouver les loups. Qui te paraît suspect ?", show_name_ia=True)
        self.chat.add_message("IA_5", "Perso j'observe. Je n'ai rien de solide.", show_name_ia=True)
        self.chat.add_message("IA_1", "IA_4 parle peu, ça me gêne.", show_name_ia=True)

    # Toggles between day and night phases
    def toggle_phase(self):
        if self.phase == "Jour":
            self.phase = "Nuit"
            # During night, names are hidden
            self.chat.add_message("IA_?", "…des pas dans l'ombre…", show_name_ia=False)
        else:
            self.phase = "Jour"
            self.day_count += 1
            self.chat.add_message("IA_3", "Nouveau jour. On récapitule ?", show_name_ia=True)

    # Kills a player by index (for testing)
    def kill_player(self, index: int):
        if 0 <= index < len(self.players):
            self.players[index]["alive"] = False

    # Handles events for the game screen
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.app.set_screen(SetupScreen(self.app))

            # TESTS for meaningful interactions
            # SPACE : toggle day/night
            if event.key == pygame.K_SPACE:
                self.toggle_phase()

            # K : kill IA_1 (for testing)
            if event.key == pygame.K_k:
                self.kill_player(0)

        # Pass event to widgets
        self.chat.handle_event(event)
        self.player_list.handle_event(event)

    # Updates the game screen
    def draw(self, surface):
        # Background
        surface.fill((15, 15, 18))

        # Info panel
        pygame.draw.rect(surface, (55, 55, 62), self.info_rect, border_radius=12)
        pygame.draw.rect(surface, (180, 180, 180), self.info_rect, 2, border_radius=12)

        # Title label
        title = self.big_font.render(f"{self.phase} {self.day_count}", True, (240, 240, 240))
        surface.blit(title, (self.info_rect.x + 14, self.info_rect.y + 10))

        # Hint label
        hint = "Les IA discutent (SPACE: toggle jour/nuit)" if self.phase == "Jour" else "Noms masqués dans le chat (SPACE: toggle)"
        hint_label = self.small_font.render(hint, True, (210, 210, 210))
        surface.blit(hint_label, (self.info_rect.x + 14, self.info_rect.y + 48))

        # Player list panel
        self.player_list.draw(surface)

        # Chat box
        self.chat.draw(surface)

        # Debug info
        dbg = self.small_font.render("Debug: SPACE=Jour/Nuit | K=tuer IA_1 | ESC=menu", True, (140, 140, 140))
        surface.blit(dbg, (self.chat_rect.x + 10, self.chat_rect.bottom - 24))
