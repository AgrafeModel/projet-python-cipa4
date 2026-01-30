# Fichier : gui/screen.py
# Gestion des écrans et de l'interface utilisateur (menus, affichage, etc.)
# Note : Commentaires en anglais redigé par IA pour uniformité du code.
# Note : Certaines parties du code ont été générées par une IA (Copilot). Le code est fait à la
# main par l'humain, mais l'IA ajoute des optimisations et des suggestions.

import pygame

from gui.widgets import Button, Stepper, ChatBox, PlayerListPanel, Tooltip
from game.engine import GameEngine
from gui.settings_screen import SettingsScreen

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
        
        # Settings button
        self.settings_btn = Button(
            rect=(app.w // 2 - 120, app.h // 2 + 150, 240, 50),
            text="Paramètres",
            font=self.font,
            tooltip="Accéder aux paramètres (S)"
        )

    # Handles events for the setup screen
    def handle_event(self, event):
        # Keyboard shortcut for settings
        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            self.app.set_screen(SettingsScreen(self.app, previous_screen=self))
            return
        
        self.num_players.handle_event(event)

        if self.start_btn.handle_event(event):
            self.app.set_screen(GameScreen(self.app, self.num_players.value))
        
        if self.settings_btn.handle_event(event):
            self.app.set_screen(SettingsScreen(self.app, previous_screen=self))

    # Draws the setup screen
    def draw(self, surface):
        surface.fill((20, 20, 25))

        title = self.title_font.render("Loup-Garou IA", True, (240, 240, 240))
        surface.blit(title, title.get_rect(center=(self.app.w // 2, 120)))

        label = self.font.render("Nombre de joueurs (min. 6)", True, (200, 200, 200))
        surface.blit(label, label.get_rect(center=(self.app.w // 2, self.app.h // 2 - 70)))

        self.num_players.draw(surface)
        self.start_btn.draw(surface)
        self.settings_btn.draw(surface)


# Main game screen
class GameScreen(Screen):
    def __init__(self, app, num_players: int):
        super().__init__(app)

        # Fonts
        self.font = pygame.font.SysFont(None, 30)
        self.small_font = pygame.font.SysFont(None, 22)
        self.big_font = pygame.font.SysFont(None, 34)

        # Layout
        margin = 20
        left_w = 320
        gap = 20

        # Rectangles for different UI sections
        self.info_rect = pygame.Rect(margin, margin, left_w, 80)
        self.list_rect = pygame.Rect(margin, margin + 100, left_w, app.h - (margin + 100) - margin)
        self.chat_rect = pygame.Rect(margin + left_w + gap, margin, app.w - (margin + left_w + gap) - margin, app.h - 2 * margin)

        # Engine (game logic)
        self.engine = GameEngine(num_players)

        # Widgets
        self.chat = ChatBox(self.chat_rect, self.font)
        self.player_list = PlayerListPanel(self.list_rect, self.font, self.small_font, self._players_view())

        # Vote button handler
        self.player_list.on_vote = self._on_vote_selected

        self.tooltip = Tooltip(self.small_font)

        self.continue_btn = Button(
            rect=(self.info_rect.right - 140, self.info_rect.y + 44, 120, 28),
            text="Continuer",
            font=self.small_font,
            tooltip="Continuer\nAvance la phase du jeu"
        )

        self.confirm_btn = Button(
            rect=(self.info_rect.right - 140, self.info_rect.y + 44, 120, 28),
            text="Confirmer",
            font=self.small_font,
            tooltip="Confirmer le vote\nÉlimine la cible sélectionnée"
        )

        # Currently selected vote index
        self.selected_vote_idx = None

        # Store number of players for end screen
        self.num_players = num_players

        self.pending_events = [] # events to display
        self.msg_delay = 0.55 # seconds between messages
        self._msg_timer = 0.0  # timer for message display
        
        # Generator for streaming message generation (one at a time from Ollama)
        self._message_generator = None
        
        # Discussion phase timer (max 45 seconds for fluent discussion)
        self._discussion_phase_timer = 0.0
        self._max_discussion_duration = 45.0  # seconds
        self._discussion_end_message_shown = False  # avoid showing it multiple times

        # Start with night phase instead of day discussion (avoid baseless accusations on day 1)
        events = self.engine.resolve_night_and_start_next_day()
        self._enqueue_events(events)
        self._message_generator = self._create_message_generator()
        self._refresh_ui_players_from_engine()  # Update dead players in UI
        
        self._update_vote_buttons_visibility()
        self._update_controls()

    # Updates the game screen
    def update(self, dt: float):
        # Track discussion phase duration
        if self.engine.phase == "JourDiscussion":
            self._discussion_phase_timer += dt
        else:
            self._discussion_phase_timer = 0.0
            self._discussion_end_message_shown = False
        
        # Display pending chat messages over time
        if self.pending_events:
            self._msg_timer += dt

            # Show next message if timer exceeds delay
            if self._msg_timer >= self.msg_delay:
                self._msg_timer = 0.0
                ev = self.pending_events.pop(0)
                self.chat.add_message(ev.name_ia, ev.text, ev.show_name_ia)
        
        # Generate next message from Ollama if queue is empty AND we haven't exceeded time limit
        elif self._message_generator and self.engine.phase == "JourDiscussion":
            if self._discussion_phase_timer < self._max_discussion_duration:
                self._msg_timer += dt
                if self._msg_timer >= self.msg_delay:
                    self._msg_timer = 0.0
                    try:
                        ev = next(self._message_generator)
                        self.chat.add_message(ev.name_ia, ev.text, ev.show_name_ia)
                    except StopIteration:
                        self._message_generator = None
            else:
                # Time's up - stop generating and show system message
                if not self._discussion_end_message_shown:
                    self._discussion_end_message_shown = True
                    self._message_generator = None
                    # Add "discussion time elapsed" message
                    from game.engine import ChatEvent
                    self.chat.add_message(
                        "Système",
                        "Temps de discussion écoulé, passons au vote!",
                        True
                    )

    # Enqueues events to be displayed in the chat
    def _enqueue_events(self, events):
        self.pending_events.extend(events)

    # Generator that creates messages one at a time (streaming from Ollama)
    def _create_message_generator(self):
        """Yields messages one at a time as they're generated from Ollama."""
        alive_names = [p.name for p in self.engine.players if p.alive]
        if not alive_names:
            return
        
        # Build role info for context
        role_map = {p.name: p.role for p in self.engine.players}
        
        # Generate messages continuously (until stopped by time limit)
        message_count = 0
        while True:  # Infinite loop - stopped by time limit in update()
            speaker = self.engine.rng.choice(alive_names)
            agent = self.engine.agents[speaker]
            
            # Create public state with role info
            from ai.rules import PublicState
            state = PublicState(
                alive_names=alive_names,
                chat_history=self.engine.public_chat_history,
                day=self.engine.day_count,
            )
            state.role_map = role_map  # Add role info to state
            
            agent.observe_public(state)
            
            # Generate message (calls Ollama now, not earlier)
            msg = agent.decide_message(state)
            
            # Avoid repeating recently
            for _try in range(3):
                rendered = f"{speaker}:{msg}"
                if rendered not in self.engine.recent_messages:
                    self.engine.recent_messages.append(rendered)
                    break
            else:
                msg = agent.decide_message(state)
            
            # Record in engine
            self.engine.public_chat_history.append((speaker, msg))
            
            message_count += 1
            
            # Yield the message as an event
            from game.engine import ChatEvent
            yield ChatEvent(name_ia=speaker, text=msg, show_name_ia=True)

    # Updates the game state
    def _check_game_over(self):
        winner = self.engine.get_winner()
        if winner is None:
            return False

        # Retrieve wolves information
        wolves = self.engine.all_wolves_names()
        found = self.engine.found_wolves_list()

        if winner == "village":
            self.app.set_screen(VictoryScreen(self.app, self.num_players, wolves, found))
            return True

        if winner == "loups":
            self.app.set_screen(DefeatScreen(self.app, self.num_players, wolves, found))
            return True

        return False


    # Handles vote selection from the player list
    def _on_vote_selected(self, idx: int):
        self.selected_vote_idx = idx
        self._update_controls()


    # Updates control states based on game phase
    def _update_controls(self):
        self.player_list.show_vote_buttons = (self.engine.phase == "JourVote")

        # Vote phase controls update
        if self.engine.phase == "JourVote":
            # Check if a selection has been made
            has_selection = self.selected_vote_idx is not None

            self.confirm_btn.enabled = has_selection
            self.confirm_btn.tooltip = (
                "Confirmer le vote\nÉlimine la cible sélectionnée"
                if has_selection
                else "Sélectionne une cible d'abord"
            )

            # Update selected index in player list
            self.player_list.selected_vote_index = self.selected_vote_idx
        else:
            # Reset the selection outside of vote phase
            self.selected_vote_idx = None
            self.player_list.selected_vote_index = None
            self.confirm_btn.enabled = False

    # Update vote buttons visibility (Day 2+ only)
    def _update_vote_buttons_visibility(self):
        self.player_list.show_vote_buttons = (self.engine.phase == "JourVote")

    # Handles vote button clicks
    def _on_vote_clicked(self, idx: int):
        events = self.engine.cast_vote(idx)

        # Enqueue resulting events
        self._enqueue_events(events)

        # Refresh UI after vote
        self._refresh_ui_players_from_engine()
        self._update_vote_buttons_visibility()

    # Prepares a view of players for the UI
    def _players_view(self):
        view = []
        for p in self.engine.players:
            view.append({
                "name": p.name,
                "alive": p.alive,
                "role": p.role,
                "note": p.note,
            })
        return view

    # Syncs modified notes from UI back to the engine
    def _sync_notes_back_to_engine(self):
        for p, v in zip(self.engine.players, self.player_list.players):
            p.note = v["note"]

    # Refreshes the UI player list from the engine state
    def _refresh_ui_players_from_engine(self):
        self.player_list.players = self._players_view()

    # Handles events for the game screen
    def handle_event(self, event):
        # Escape to return to setup screen
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.set_screen(SetupScreen(self.app))
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            self.app.set_screen(SettingsScreen(self.app, previous_screen=self))
            return

        # Prioritize buttons
        if self.engine.phase != "JourVote":
            if self.continue_btn.handle_event(event):
                if self.pending_events:
                    while self.pending_events:
                        ev = self.pending_events.pop(0)
                        self.chat.add_message(ev.name_ia, ev.text, ev.show_name_ia)
                    return

                events = self.engine.advance()
                self._enqueue_events(events)
                
                # Recreate generator if we just started a new day
                if self.engine.phase == "JourDiscussion":
                    self._message_generator = self._create_message_generator()
                    self._discussion_end_message_shown = False
                else:
                    self._message_generator = None

                self._refresh_ui_players_from_engine()
                self._update_controls()
                if self._check_game_over():
                    return
                return 
        # Vote confirmation
        else:
            if self.confirm_btn.handle_event(event):
                if self.selected_vote_idx is not None:
                    events = self.engine.cast_vote(self.selected_vote_idx)
                    self._enqueue_events(events)

                    self._refresh_ui_players_from_engine()
                    self._update_controls()
                    if self._check_game_over():
                        return
                return 

        # Handle SPACE for phase toggle (debug)
        self.chat.handle_event(event)
        self.player_list.handle_event(event)
        self._sync_notes_back_to_engine()


    # Updates the game screen
    def draw(self, surface):
        surface.fill((15, 15, 18))

        # Info panel
        pygame.draw.rect(surface, (55, 55, 62), self.info_rect, border_radius=12)
        pygame.draw.rect(surface, (180, 180, 180), self.info_rect, 2, border_radius=12)

        # Phase and day title
        title = self.big_font.render(f"{self.engine.phase} {self.engine.day_count}", True, (240, 240, 240))
        surface.blit(title, (self.info_rect.x + 14, self.info_rect.y + 10))

        # Player list
        self.player_list.draw(surface)

        # Chat
        self.chat.draw(surface)

        # Debug info
        dbg = self.small_font.render("Debug : ESC=menu", True, (140, 140, 140))
        surface.blit(dbg, (self.chat_rect.x + 10, self.chat_rect.bottom - 24))

        # Bouton du moment
        if self.engine.phase == "JourVote":
            self.confirm_btn.draw(surface)
        else:
            self.continue_btn.draw(surface)

        # Tooltips
        mx, my = pygame.mouse.get_pos()
        hover_text = ""

        # priorité : boutons
        hover_text = hover_text or (self.confirm_btn.get_hover_text((mx, my)) if self.engine.phase == "JourVote" else "")
        hover_text = hover_text or (self.continue_btn.get_hover_text((mx, my)) if self.engine.phase != "JourVote" else "")

        # puis liste joueurs
        hover_text = hover_text or self.player_list.get_hover_text((mx, my))

        # affiche
        self.tooltip.draw(surface, hover_text, (mx, my))


# Base class for end screens (victory/defeat)
class EndScreen(Screen):
    # Initializes the end screen with title, subtitle, and buttons
    def __init__(self, app, title: str, subtitle: str, num_players: int, wolves: list[str], found_wolves: list[str]):
        super().__init__(app)
        self.title_font = pygame.font.SysFont(None, 72)
        self.font = pygame.font.SysFont(None, 28)

        # Store number of players
        self.num_players = num_players
        self.title = title
        self.subtitle = subtitle

        # Store wolves information
        self.wolves = wolves
        self.found_wolves = set(found_wolves)


        # Buttons
        self.btn_home = Button(
            rect=(app.w // 2 - 170, app.h // 2 + 90, 160, 50),
            text="Accueil",
            font=self.font,
            tooltip="Retour à l'accueil"
        )

        self.btn_replay = Button(
            rect=(app.w // 2 + 10, app.h // 2 + 90, 160, 50),
            text="Rejouer",
            font=self.font,
            tooltip="Rejouer avec le même nombre de joueurs"
        )


    # Handles events for the end screen
    def handle_event(self, event):
        if self.btn_home.handle_event(event):
            self.app.set_screen(SetupScreen(self.app))
            return

        if self.btn_replay.handle_event(event):
            self.app.set_screen(GameScreen(self.app, self.num_players))
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.set_screen(SetupScreen(self.app))

    # Draws the end screen
    def draw(self, surface):
        surface.fill((15, 15, 18))

        cx = self.app.w // 2

        # Title
        t = self.title_font.render(self.title, True, (240, 240, 240))
        surface.blit(t, t.get_rect(center=(cx, self.app.h // 2 - 160)))

        # Subtitle
        s = self.font.render(self.subtitle, True, (200, 200, 200))
        surface.blit(s, s.get_rect(center=(cx, self.app.h // 2 - 120)))

        # Wolves panel
        panel_w = 520
        panel_h = 150
        panel_rect = pygame.Rect(cx - panel_w // 2, self.app.h // 2 - 95, panel_w, panel_h)

        pygame.draw.rect(surface, (25, 25, 30), panel_rect, border_radius=14)
        pygame.draw.rect(surface, (180, 180, 180), panel_rect, 2, border_radius=14)

        # Header in panel
        label = self.font.render("Loups :", True, (230, 230, 230))
        surface.blit(label, (panel_rect.x + 18, panel_rect.y + 14))

        # Found count
        found_count = sum(1 for w in self.wolves if w in self.found_wolves)
        total = len(self.wolves)
        count_text = self.font.render(f"Trouvés : {found_count}/{total}", True, (190, 190, 190))
        surface.blit(count_text, (panel_rect.right - 18 - count_text.get_width(), panel_rect.y + 14))

        # Pills layout
        x = panel_rect.x + 18
        y = panel_rect.y + 54
        max_x = panel_rect.right - 18
        row_gap = 10
        col_gap = 10

        # Draw each wolf name as a pill
        for name in self.wolves:
            text = self.font.render(name, True, (235, 235, 235))
            pad_x, pad_y = 14, 8
            pill_w = text.get_width() + 2 * pad_x
            pill_h = text.get_height() + 2 * pad_y

            # wrap
            if x + pill_w > max_x:
                x = panel_rect.x + 18
                y += pill_h + row_gap

            pill = pygame.Rect(x, y, pill_w, pill_h)

            # Background
            pygame.draw.rect(surface, (30, 30, 34), pill, border_radius=12)

            # Border color
            if name in self.found_wolves:
                border = (230, 80, 80)
                thick = 3
            else:
                border = (130, 130, 130)
                thick = 2

            pygame.draw.rect(surface, border, pill, thick, border_radius=12)

            surface.blit(text, (pill.x + pad_x, pill.y + pad_y))

            x += pill_w + col_gap

        # Buttons draw
        self.btn_home.draw(surface)
        self.btn_replay.draw(surface)


# Victory screen subclass
class VictoryScreen(EndScreen):
    def __init__(self, app, num_players: int, wolves: list[str], found_wolves: list[str]):
        super().__init__(
            app,
            title = "VICTOIRE !",
            subtitle = "Tous les loups ont été éliminés.",
            num_players = num_players,
            wolves = wolves,
            found_wolves = found_wolves
        )


# Defeat screen subclass
class DefeatScreen(EndScreen):
    def __init__(self, app, num_players: int, wolves: list[str], found_wolves: list[str]):
        super().__init__(
            app,
            title = "DÉFAITE…",
            subtitle = "Les loups ont pris le contrôle du village.",
            num_players = num_players,
            wolves = wolves,
            found_wolves = found_wolves
        )