# Fichier : gui/screen.py
# Gestion des écrans et de l'interface utilisateur (menus, affichage, etc.)
# Note : Commentaires en anglais redigé par IA pour uniformité du code.
# Note : Certaines parties du code ont été générées par une IA (Copilot). Le code est fait à la
# main par l'humain, mais l'IA ajoute des optimisations et des suggestions.

import pygame
import threading
import queue
import time


from gui.widgets import Button, Stepper, ChatBox, PlayerListPanel, Tooltip, TextInput
from game.engine_with_ai import GameEngine as GeminiEngine
from game.engine_openrouter import GameEngine as OpenRouterEngine
from game.engine import GameEngine as OllamaOrTemplateEngine
import game.constants
import google.generativeai as genai
from gui.settings_screen import SettingsScreen
from ai.ollama_client import check_ollama_availability
import audio_config
from game import tts_helper

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

        audio_config.TTS_ENABLED = False
        tts_helper.disable_and_stop()

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
            self.app.set_screen(ModeSelectScreen(self.app, self.num_players.value, previous_screen=self))

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


# Screen to select the game mode (API or local)
class ModeSelectScreen(Screen):
    def __init__(self, app, num_players: int, previous_screen=None):
        super().__init__(app)
        self.previous_screen = previous_screen
        self.num_players = num_players

        audio_config.TTS_ENABLED = False
        tts_helper.disable_and_stop()

        self.title_font = pygame.font.SysFont(None, 54)
        self.font = pygame.font.SysFont(None, 28)

        cx = app.w // 2

        self.back_btn = Button((20, 20, 140, 44), "Retour", self.font, tooltip="Retour à l'accueil")

        self.btn_openrouter = Button(
            (cx - 220, 180, 440, 70),
            "Mode API 1 (OpenRouter)",
            self.font,
            tooltip="IA en ligne (clé OpenRouter requise)"
        )
        self.btn_gemini = Button(
            (cx - 220, 270, 440, 70),
            "Mode API 2 (Gemini)",
            self.font,
            tooltip="IA en ligne (clé Gemini requise)"
        )
        self.btn_ollama = Button(
            (cx - 220, 360, 440, 70),
            "Mode local (Ollama)",
            self.font,
            tooltip="IA locale (Ollama + modèle installé requis)"
        )

        self.error = ""

    # Handles events for the mode selection screen
    def handle_event(self, event):
        if self.back_btn.handle_event(event):
            self.app.set_screen(self.previous_screen or SetupScreen(self.app))
            return

        # Handle mode selection buttons, checking API keys or availability before proceeding to TTS setup or error screens
        if self.btn_openrouter.handle_event(event):
            # check OpenRouter key
            if not game.constants.OPENROUTER_API_KEY or "TON_API_KEY" in game.constants.OPENROUTER_API_KEY:
                self.app.set_screen(ApiKeyScreen(self.app, mode="openrouter", num_players=self.num_players, previous_screen=self))
                return
            # go to TTS check
            self.app.set_screen(TTSKeyScreen(self.app, engine_cls=OpenRouterEngine, num_players=self.num_players, previous_screen=self))
            return

        # Gemini requires API key but no real test possible before TTS setup, so we just check if the key is set and if not, go to API key screen. If key is set, we go directly to TTS setup (no real way to validate the key beforehand since Gemini doesn't have a simple ping API, but we'll validate it properly in the TTSKeyScreen when trying to use it).
        if self.btn_gemini.handle_event(event):
            if not game.constants.API_GEMINI or "TON_API_KEY" in game.constants.API_GEMINI:
                self.app.set_screen(ApiKeyScreen(self.app, mode="gemini", num_players=self.num_players, previous_screen=self))
                return
            self.app.set_screen(TTSKeyScreen(self.app, engine_cls=GeminiEngine, num_players=self.num_players, previous_screen=self))
            return

        # Ollama : no API key, but check if Ollama is available before proceeding to TTS setup (since if Ollama isn't available, the game won't work at all)
        if self.btn_ollama.handle_event(event):
            is_available, message = check_ollama_availability()
            if not is_available:
                self.app.set_screen(OllamaErrorScreen(self.app, message, previous_screen=self))
                return
            self.app.set_screen(TTSKeyScreen(self.app, engine_cls=OllamaOrTemplateEngine, num_players=self.num_players, previous_screen=self))
            return

    # Draws the mode selection screen
    def draw(self, surface):
        surface.fill((20, 20, 25))
        title = self.title_font.render("Choisir le mode", True, (240, 240, 240))
        surface.blit(title, title.get_rect(center=(self.app.w // 2, 110)))

        sub = self.font.render(f"Joueurs : {self.num_players}", True, (180, 180, 180))
        surface.blit(sub, sub.get_rect(center=(self.app.w // 2, 145)))

        # Draw buttons for mode selection and back button
        self.back_btn.draw(surface)
        self.btn_openrouter.draw(surface)
        self.btn_gemini.draw(surface)
        self.btn_ollama.draw(surface)



# Screen to input API keys for Gemini or OpenRouter modes
class ApiKeyScreen(Screen):
    def __init__(self, app, mode: str, num_players: int, previous_screen=None):
        super().__init__(app)
        self.mode = mode  # "openrouter" | "gemini"
        self.num_players = num_players
        self.previous_screen = previous_screen

        audio_config.TTS_ENABLED = False
        tts_helper.disable_and_stop()

        self.title_font = pygame.font.SysFont(None, 48)
        self.font = pygame.font.SysFont(None, 28)

        cx = app.w // 2

        # Determine label based on mode
        label = "Clé OpenRouter" if mode == "openrouter" else "Clé Gemini"
        self.title = label

        # Input field for API key and buttons to validate or go back
        self.back_btn = Button((20, 20, 140, 44), "Retour", self.font)
        self.play_btn = Button((cx - 120, 360, 240, 52), "Valider & Continuer", self.font)
        self.input = TextInput((cx - 260, 260, 520, 56), self.font, placeholder=f"Entrer {label}…", mask=True)

        self.msg = ""

    # Updates the API key input field (handles cursor blinking)
    def update(self, dt: float):
        self.input.update(dt)

    # Validates the provided API key by attempting to create a client and perform a simple API call (listing models) to ensure the key works before proceeding to the TTS setup screen. Shows an error message if validation fails.
    def _validate(self, key: str) -> bool:
        key = key.strip()
        if len(key) < 10:
            return False

        # Gemini : no simple ping API available, so we just try to create a client and list models to validate the key (if it works, we should get a non-empty list of models)
        if self.mode == "gemini":
            try:
                genai.configure(api_key=key)
                models = list(genai.list_models())
                return len(models) > 0
            except Exception:
                return False

        # openrouter: vrai test API (liste des modèles)
        try:
            from ai.client import OpenRouterClient, OpenRouterClientConfig
            c = OpenRouterClient(OpenRouterClientConfig(api_key=key))
            _ = c.client.models.list()  # ✅ ping réel
            return True
        except Exception:
            return False

    # Handles events for the API key screen, including validating the key and navigating to the TTS setup screen if valid, or showing an error message if invalid. Also handles going back to the previous screen.
    def handle_event(self, event):
        if self.back_btn.handle_event(event):
            self.app.set_screen(self.previous_screen)
            return

        # Handle API key validation and navigation to TTS setup screen based on the selected mode (OpenRouter or Gemini). Shows an error message if the key is invalid.
        r = self.input.handle_event(event)
        if r == "enter" or self.play_btn.handle_event(event):
            key = self.input.text.strip()
            if self._validate(key):
                if self.mode == "openrouter":
                    game.constants.OPENROUTER_API_KEY = key
                    self.app.set_screen(TTSKeyScreen(self.app, engine_cls=OpenRouterEngine, num_players=self.num_players, previous_screen=self.previous_screen))
                else:
                    game.constants.API_GEMINI = key
                    self.app.set_screen(TTSKeyScreen(self.app, engine_cls=GeminiEngine, num_players=self.num_players, previous_screen=self.previous_screen))
            else:
                self.msg = "Clé invalide. Réessaie."
            return

    # Draws the API key input screen, including the title, input field, buttons, and any error messages
    def draw(self, surface):
        surface.fill((20, 20, 25))
        cx = self.app.w // 2

        title = self.title_font.render(self.title, True, (240, 240, 240))
        surface.blit(title, title.get_rect(center=(cx, 120)))

        help1 = self.font.render("Cette clé est nécessaire pour ce mode.", True, (180, 180, 180))
        surface.blit(help1, help1.get_rect(center=(cx, 175)))

        self.back_btn.draw(surface)
        self.input.draw(surface)
        self.play_btn.draw(surface)

        if self.msg:
            msg = self.font.render(self.msg, True, (255, 120, 120))
            surface.blit(msg, msg.get_rect(center=(cx, 430)))



# Screen to set up TTS (Text-to-Speech) options, including input for ElevenLabs API key if the user wants to enable TTS. Allows users to skip TTS setup and play without voice if they choose.
class TTSKeyScreen(Screen):
    def __init__(self, app, engine_cls, num_players: int, previous_screen=None):
        super().__init__(app)
        self.engine_cls = engine_cls
        self.num_players = num_players
        self.previous_screen = previous_screen

        # Fonts for the screen
        self.title_font = pygame.font.SysFont(None, 46)
        self.font = pygame.font.SysFont(None, 28)

        # Center X coordinate for layout
        cx = app.w // 2

        # Buttons for going back, enabling TTS, or skipping TTS setup
        self.back_btn = Button((20, 20, 140, 44), "Retour", self.font)
        self.enable_btn = Button((cx - 220, 360, 210, 52), "Activer la voix", self.font)
        self.skip_btn = Button((cx + 10, 360, 210, 52), "Continuer sans", self.font)

        # Input field for ElevenLabs API key, with masking for privacy. This allows users to enter their API key if they want to enable TTS, or skip it if they prefer to play without voice.
        self.input = TextInput((cx - 260, 260, 520, 56), self.font, placeholder="Clé ElevenLabs (optionnel)…", mask=True)
        self.msg = ""

        # prefill if key already set in constants (but only if it looks like a real key, to avoid pre-filling with the placeholder or an invalid key) to make it easier for users who have already set their key in the config file to just continue without having to copy-paste it again
        if game.constants.ELEVENLABS_API_KEY and "TON_API_KEY" not in game.constants.ELEVENLABS_API_KEY:
            self.input.text = game.constants.ELEVENLABS_API_KEY

    # Updates the TTS key input field (handles cursor blinking)
    def update(self, dt: float):
        self.input.update(dt)

    # Validates the provided ElevenLabs API key by attempting to create a client and perform a simple API call (listing voices) to ensure the key works before proceeding to the game screen. Shows an error message if validation fails.
    def handle_event(self, event):
        if self.back_btn.handle_event(event):
            self.app.set_screen(self.previous_screen)
            return

        self.input.handle_event(event)

        # Handle enabling TTS with the provided API key, validating it, and navigating to the game screen if valid. If the key is invalid, shows an error message. Also handles skipping TTS setup and going directly to the game screen without voice.
        if self.skip_btn.handle_event(event):
            # désactiver TTS et lancer
            tts_helper.set_enabled(False)
            tts_helper.disable_and_stop()
            self.app.set_screen(GameScreen(self.app, self.num_players, self.engine_cls))
            return

        # Activer TTS : valider la clé et si elle est valide, l'enregistrer et lancer le jeu avec TTS activé. Si la clé est invalide, afficher un message d'erreur.
        if self.enable_btn.handle_event(event):
            key = self.input.text.strip()
            if tts_helper.validate_api_key(key):
                tts_helper.set_api_key(key)
                tts_helper.set_enabled(True)
                self.app.set_screen(GameScreen(self.app, self.num_players, self.engine_cls))
                audio_config.TTS_ENABLED = True
            else:
                self.msg = "Clé TTS invalide (ou ElevenLabs indisponible)."
            return

    # Draws the TTS setup screen, including the title, input field for the ElevenLabs API key, buttons to enable TTS or skip it, and any error messages. This screen allows users to set up voice features for the game or choose to play without them.
    def draw(self, surface):
        surface.fill((20, 20, 25))
        cx = self.app.w // 2

        # Title and instructions for TTS setup, along with input field and buttons for enabling TTS or skipping it. Also displays any error messages related to TTS key validation.
        title = self.title_font.render("Lecture des messages (TTS)", True, (240, 240, 240))
        surface.blit(title, title.get_rect(center=(cx, 120)))

        # Instructions for TTS setup, indicating that it's optional and users can play without voice if they choose.
        help1 = self.font.render("Optionnel : tu peux jouer sans la voix.", True, (180, 180, 180))
        surface.blit(help1, help1.get_rect(center=(cx, 175)))

        # Draw buttons for enabling TTS, skipping it, and going back, along with the input field for the ElevenLabs API key. Display any error messages if the provided key is invalid.
        self.back_btn.draw(surface)
        self.input.draw(surface)
        self.enable_btn.draw(surface)
        self.skip_btn.draw(surface)

        if self.msg:
            msg = self.font.render(self.msg, True, (255, 120, 120))
            surface.blit(msg, msg.get_rect(center=(cx, 430)))



# Main game screen
class GameScreen(Screen):
    def __init__(self, app, num_players: int, engine_cls):
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
        self.engine = engine_cls(num_players)

        # Map player names to voice IDs for TTS (if needed)
        self.voice_map = {p.name: getattr(p, "voice_id", None) for p in self.engine.players}

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

        # Quit confirmation state
        self.show_quit_confirm = False

        # Quit confirmation modal setup
        w, h = 420, 180
        self.quit_modal_rect = pygame.Rect(
            self.app.w // 2 - w // 2,
            self.app.h // 2 - h // 2,
            w, h
        )

        # Fonts and buttons for the quit confirmation modal
        self.quit_title_font = pygame.font.SysFont(None, 34)

        # Calculate button positions for the quit confirmation modal, with "Annuler" on the left and "Quitter" on the right, both aligned at the bottom of the modal with some padding. This allows users to confirm if they really want to quit the current game, preventing accidental exits.
        btn_w, btn_h = 150, 44
        y_btn = self.quit_modal_rect.bottom - 22 - btn_h

        # Quit confirmation buttons: "Annuler" to go back to the game, and "Quitter" to return to the main menu. This allows users to confirm if they really want to quit the current game, preventing accidental exits.
        self.quit_btn_cancel = Button(
            rect=(self.quit_modal_rect.left + 30, y_btn, btn_w, btn_h),
            text="Annuler",
            font=self.font,
            tooltip="Revenir au jeu"
        )

        # Quit confirmation button to return to the main menu, allowing users to confirm if they really want to quit the current game and lose their progress, preventing accidental exits.
        self.quit_btn_confirm = Button(
            rect=(self.quit_modal_rect.right - 30 - btn_w, y_btn, btn_w, btn_h),
            text="Quitter",
            font=self.font,
            tooltip="Retourner à l'accueil"
        )

        # Currently selected vote index
        self.selected_vote_idx = None

        # Store engine class for end screen display
        self.engine_cls = engine_cls

        # Store number of players for end screen
        self.num_players = num_players

        self.pending_events = [] # events to display
        self.msg_delay = 0.55 # seconds between messages
        self._msg_timer = 0.0  # timer for message display

        # Background generation state for API-based engines (like Ollama) to avoid blocking the UI while waiting for responses, especially during the initial start_day call which can take a long time. We use a queue to get results from the background thread when it finishes.
        self._bg_queue = queue.Queue()
        self._bg_loading = False
        
        # Generator for streaming message generation (one at a time from Ollama)
        self._message_generator = None
        
        # Discussion phase timer (max 45 seconds for fluent discussion)
        self._discussion_phase_timer = 0.0
        self._max_discussion_duration = 45.0  # seconds
        self._discussion_end_message_shown = False  # avoid showing it multiple times

        # Background thread for API generation (to avoid blocking the UI while waiting for responses from the engine, especially for API-based engines which can have longer response times)
        self._bg_queue = queue.Queue()
        self._bg_thread = None
        self._bg_loading = False

        # Start the game by calling start_day on the engine, which will return the initial events to display. For engines that support streaming discussion, we can call start_day directly and get a generator for events. For API-based engines that don't support streaming, we need to call start_day in a background thread to avoid blocking the UI while waiting for the response.
        if getattr(self.engine, "supports_streaming_discussion", False):
            # For engines that support streaming discussion (like Ollama), we can call start_day directly to get the initial events and a generator for subsequent messages. We also show a "Generating..." message in the chat while waiting for the first messages to be generated, which will be replaced by the actual messages as they come in from the generator.
            self.chat.add_message("Système", "Génération…", True, is_system=True)

            # Ollama / engines : thread
            if getattr(self.engine, "use_background_generation", False):
                self._start_background_generation(self.engine.start_day)
            else:
                events = self.engine.start_day()
                self._enqueue_events(events)

            self._message_generator = self._create_message_generator() if getattr(self.engine, "supports_streaming_discussion", False) else None
        # API-based engine: start_day can take a long time, so we run it in a background thread and show a loading message in the meantime. Once the thread finishes, it will put the resulting events in the queue, which we will check in the update() method to display them and transition to the discussion phase.
        else:
            self._bg_loading = True
            self.chat.add_message("Système", "Chargement des messages…", True, is_system=True)
            self._update_controls()
            self._start_background_generation_start_day()

        # For engines that support streaming discussion, we can create a message generator right away to start displaying messages one by one as they are generated. For API-based engines that don't support streaming, we will get all the messages at once when the background thread finishes, so we don't need a generator in that case.
        self._message_generator = self._create_message_generator() if getattr(self.engine, "supports_streaming_discussion", False) else None

        self._refresh_ui_players_from_engine()  # Update dead players in UI
        
        # Flag to automatically advance to the next phase after displaying all messages (used for both discussion->vote transition and night phase advancement). This allows us to wait until all messages have been displayed before automatically transitioning, without needing to hardcode delays or rely on the engine's response time.
        self._auto_advance_armed = False

        self._update_vote_buttons_visibility()
        self._update_controls()

        # Backgrounds
        self.bg_day = pygame.image.load("assets/jour_background.png").convert()
        self.bg_night = pygame.image.load("assets/nuit_background.png").convert()

        # Scale to screen size once (important for perf)
        self.bg_day = pygame.transform.scale(self.bg_day, (self.app.w, self.app.h))
        self.bg_night = pygame.transform.scale(self.bg_night, (self.app.w, self.app.h))

    # Helper method to get the appropriate background image based on the current phase of the game (day or night). This allows us to visually differentiate between day and night phases in the game by showing different backgrounds.
    def _get_background(self):
        if self.engine.phase == "Nuit":
            return self.bg_night
        return self.bg_day

    # Starts a background thread to call a given function (like advance) on the engine for API-based engines, putting the resulting events in a queue when done. This is used for advancing the night phase or other phases that require waiting for the engine to generate messages, allowing us to keep the UI responsive and show a loading message in the meantime.
    def _start_background_generation(self, fn):
        self._bg_loading = True
        def worker():
            try:
                events = fn()
                self._bg_queue.put(("events", events))
            except Exception as e:
                self._bg_queue.put(("error", str(e)))
        threading.Thread(target=worker, daemon=True).start()

    # Starts a background thread to call start_day on the engine for API-based engines, putting the resulting events in a queue when done. This allows us to show a loading message and keep the UI responsive while waiting for the engine to generate the initial messages for the day phase.
    def _start_background_generation_start_day(self):
        def worker():
            try:
                events = self.engine.start_day()
                self._bg_queue.put(("events", events))
            except Exception as e:
                self._bg_queue.put(("error", str(e)))

        self._bg_thread = threading.Thread(target=worker, daemon=True)
        self._bg_thread.start()

    # Starts a background thread to call a given function (like advance) on the engine for API-based engines, putting the resulting events in a queue when done. This is used for advancing the night phase or other phases that require waiting for the engine to generate messages, allowing us to keep the UI responsive and show a loading message in the meantime.
    def _start_background_generation(self, fn):
        self._bg_loading = True
        self._update_controls()
        def worker():
            try:
                events = fn()
                self._bg_queue.put(("events", events))
            except Exception as e:
                self._bg_queue.put(("error", str(e)))
        threading.Thread(target=worker, daemon=True).start()

    # Updates the game screen
    def update(self, dt: float):
        # Check if we are waiting for background generation to finish (for API-based engines) and if so, check the queue for results to display when ready. This allows us to keep the UI responsive and show loading messages while waiting for the engine to generate responses, especially during longer operations like start_day or advance for API-based engines.
        if self._bg_loading:
            try:
                kind, payload = self._bg_queue.get_nowait()
                self._bg_loading = False

                if kind == "events":
                    self._enqueue_events(payload)
                    self._refresh_ui_players_from_engine()
                    self._update_vote_buttons_visibility()
                    self._update_controls()
                else:
                    self.chat.add_message("Système", f"Erreur Ollama: {payload}", True, is_system=True)

                self._update_controls()
            except queue.Empty:
                pass

        if self._bg_loading:
            try:
                # Check if the background thread has finished and put something in the queue
                kind, payload = self._bg_queue.get_nowait()
                # When background generation finishes, we get the resulting events from the queue and display them, then transition to the discussion phase. If there was an error during generation, we display an error message in the chat.
                if kind == "events":
                    self._bg_loading = False
                    self._update_controls()
                    self._enqueue_events(payload)
                    self._refresh_ui_players_from_engine()
                    self._update_vote_buttons_visibility()
                    self._update_controls()
                elif kind == "error":
                    self._bg_loading = False
                    self._update_controls()
                    self.chat.add_message("Système", f"Erreur génération API: {payload}", True, is_system=True)
            except queue.Empty:
                pass

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
                is_system = ev.name_ia == "Système"
                self.chat.add_message(ev.name_ia, ev.text, ev.show_name_ia, is_system=is_system)
                self._speak_event(ev)
        
        # After finishing displaying all messages for the current phase, automatically advance to the next phase if applicable (e.g. from discussion to vote, or advancing the night phase). This allows for a smoother flow without needing the player to click "Continue" after every single message, while still giving them time to read the messages before transitioning.
        elif self._auto_advance_armed and not self.pending_events and not self._message_generator:
            self._auto_advance_armed = False
            self._msg_timer = 0.0  # reset for next batch of messages

            # end of discussion phase -> transition to vote phase
            if self.engine.phase == "JourDiscussion":
                try:
                    events = self.engine.start_vote()
                except Exception as e:
                    self.chat.add_message("Système", f"⚠ Erreur moteur (vote): {e}", True, is_system=True)
                    return

                # Enqueue resulting events and update UI for vote phase
                self._enqueue_events(events)
                self._update_vote_buttons_visibility()
                self._update_controls()
                return

            # Auto-advance night phase: only for local engines that support streaming discussion, since for API-based engines we will have already called advance() in the background and enqueued the resulting messages, so we don't want to call advance() again here (which would cause duplicate messages and potentially break the flow). For local engines with streaming support, we can call advance() directly here to get the next batch of messages for the night phase without blocking the UI.
            if self.engine.phase == "Nuit":
                if getattr(self.engine, "supports_streaming_discussion", False):
                    try:
                        events = self.engine.advance()
                    except Exception as e:
                        self.chat.add_message("Système", f"⚠ Erreur moteur (nuit): {e}", True, is_system=True)
                        return

                    self._enqueue_events(events)
                    self._refresh_ui_players_from_engine()
                    self._update_vote_buttons_visibility()
                    self._update_controls()
                    return

                # Engines API: thread (no need to call advance() here since we already called it in the background when we finished displaying the messages for the discussion phase, so we just need to wait for those messages to finish displaying and then the update() method will handle the transition to the next phase and display the resulting messages when they come in from the background thread)
                self.chat.add_message("Système", "Génération…", True, is_system=True)
                self._start_background_generation(self.engine.advance)
                return


        # Generate next message from Ollama if queue is empty AND we haven't exceeded time limit
        elif self._message_generator and self.engine.phase == "JourDiscussion":
            if self._discussion_phase_timer < self._max_discussion_duration:
                self._msg_timer += dt
                if self._msg_timer >= self.msg_delay:
                    self._msg_timer = 0.0
                    try:
                        ev = next(self._message_generator)
                        is_system = ev.name_ia == "Système"
                        self.chat.add_message(ev.name_ia, ev.text, ev.show_name_ia, is_system=is_system)
                        self._speak_event(ev)

                    except StopIteration:
                        self._message_generator = None
            else:
                # Time's up - stop generating and transition to vote phase
                if not self._discussion_end_message_shown:
                    self._discussion_end_message_shown = True
                    self._message_generator = None
                    # Transition to vote phase and get resulting events
                    events = self.engine.start_vote()
                    self._enqueue_events(events)
                    self._update_vote_buttons_visibility()
                    self._update_controls()

    # Enqueue a list of events to be displayed in the chat, and arm the auto-advance flag to transition to the next phase after all messages have been displayed. This allows us to add messages to the queue and automatically transition when they're all done, without needing to hardcode delays or rely on the engine's response time.
    def _enqueue_events(self, events):
        if not events:
            return
        self.pending_events.extend(events)
        self._auto_advance_armed = True

    # Create a generator that yields messages one by one from the engine for streaming discussion. This allows us to display messages progressively as they are generated by the engine, especially for local engines that support streaming, without needing to wait for the entire batch of messages to be generated before displaying anything.
    def _create_message_generator(self):
        while True:
            # 1) Récupérer une liste d'événements depuis l'engine
            if hasattr(self.engine, "generate_day_discussion"):
                events = self.engine.generate_day_discussion()

            elif hasattr(self.engine, "_generate_day_discussion"):
                events = self.engine._generate_day_discussion()

            else:
                events = []

            # Secure check in case the engine doesn't implement the expected method or returns None
            if not events:
                return

            # Yield each event one by one to be displayed in the chat
            for ev in events:
                yield ev

    # Updates the game state
    def _check_game_over(self):
        winner = self.engine.get_winner()
        if winner is None:
            return False

        # Retrieve wolves information
        wolves = self.engine.all_wolves_names()
        found = self.engine.found_wolves_list()

        if winner == "village":
            self.app.set_screen(VictoryScreen(self.app, self.num_players, wolves, found, self.engine_cls))
            return True

        if winner == "loups":
            self.app.set_screen(DefeatScreen(self.app, self.num_players, wolves, found, self.engine_cls))
            return True

        return False


    # Handles vote selection from the player list
    def _on_vote_selected(self, idx: int):
        self.selected_vote_idx = idx
        self._update_controls()


    # Updates control states based on game phase
    def _update_controls(self):
        self.player_list.show_vote_buttons = (self.engine.phase == "JourVote")

        # Disable continue button if we're currently waiting for background generation to finish (for API-based engines), to prevent the player from trying to advance while we're still waiting for the engine to generate responses, which could cause confusion or issues with the flow. We will re-enable the continue button once the background generation finishes and we have the resulting events to display.
        if self.engine.phase != "JourVote":
            if getattr(self, "_bg_loading", False):
                self.continue_btn.enabled = False
                self.continue_btn.tooltip = "Génération en cours…"
            else:
                self.continue_btn.enabled = True
                self.continue_btn.tooltip = "Continuer\nAvance la phase du jeu"

        # Vote phase controls update
        if self.engine.phase == "JourVote":
            # Disable continue button if we're currently waiting for background generation to finish (for API-based engines), to prevent the player from trying to advance while we're still waiting for the engine to generate responses, which could cause confusion or issues with the flow. We will re-enable the continue button once the background generation finishes and we have the resulting events to display.
            if getattr(self, "_bg_loading", False):
                self.continue_btn.enabled = False
                self.continue_btn.tooltip = "Génération en cours…"
            else:
                self.continue_btn.enabled = True
                self.continue_btn.tooltip = "Continuer\nAvance la phase du jeu"

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
        # Quit confirmation modal
        if self.show_quit_confirm:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.show_quit_confirm = False
                return

            if self.quit_btn_cancel.handle_event(event):
                self.show_quit_confirm = False
                return

            if self.quit_btn_confirm.handle_event(event):
                tts_helper.disable_and_stop()
                from gui.screens import SetupScreen
                self.app.set_screen(SetupScreen(self.app))
                return

            # block all other events while the quit confirmation modal is shown
            return

        # Escape to return to setup screen
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.show_quit_confirm = True
            return
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            self.app.set_screen(SettingsScreen(self.app, previous_screen=self))
            return

        if self.engine.phase != "JourVote":
            if getattr(self, "_bg_loading", False):
                return

            if self.continue_btn.handle_event(event):
                if self.pending_events:
                    while self.pending_events:
                        ev = self.pending_events.pop(0)
                        is_system = ev.name_ia == "Système"
                        self.chat.add_message(ev.name_ia, ev.text, ev.show_name_ia, is_system=is_system)
                        self._speak_event(ev)

                    return
                # Stop any ongoing TTS playback to avoid overlapping messages when we advance to the next phase and start displaying new messages, especially if the player clicks "Continue" before all messages have finished playing. This ensures a cleaner audio experience without multiple messages playing at the same time.
                if audio_config.voice_channel:
                    audio_config.voice_channel.stop()

                # Clear any pending messages in the TTS helper to avoid playing outdated messages that were generated for the previous phase if the player clicks "Continue" multiple times quickly or if there are still messages being generated while we're trying to advance. This ensures that we only play the relevant messages for the current phase and avoid confusion from hearing old messages after we've already moved on.
                with tts_helper.generation_lock:
                    tts_helper.audio_ready_list.clear()

                # Show all pending messages immediately without waiting for the timer, since the player has explicitly clicked "Continue" to advance and likely wants to see all messages at once. This allows for a faster transition if there are many messages queued up, while still giving the option to display them one by one over time if the player prefers to wait.
                while self.pending_events:
                    ev = self.pending_events.pop(0)
                    self.chat.add_message(ev.name_ia, ev.text, ev.show_name_ia)

                # Advance the game phase and get resulting events. For engines that support streaming discussion, we can call advance() directly to get the next batch of messages for the new phase. For API-based engines that don't support streaming, we need to call advance() in a background thread to avoid blocking the UI while waiting for the engine to generate the messages for the new phase.
                if getattr(self.engine, "supports_streaming_discussion", False):
                    self._enqueue_events(self.engine.advance())
                else:
                    self.chat.add_message("Système", "Génération…", True, is_system=True)
                    self._start_background_generation(self.engine.advance)

                
                # Recreate generator if we just started a new day
                if self.engine.phase == "JourDiscussion" and getattr(self.engine, "supports_streaming_discussion", False):
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

    # Handle speaking messages with TTS when they are added to the chat, using the voice mapping for each player. This allows us to have different voices for different players if the TTS engine supports it, and to speak messages as they are displayed in the chat for a more immersive experience.
    def _speak_event(self, ev):
        if ev.name_ia.lower() in ("système", "system"):
            return

        voice_id = self.voice_map.get(ev.name_ia)
        if not voice_id:
            return
        
        # Speak the message text using the TTS helper, specifying the voice ID for the player. This will play the message aloud using the appropriate voice if TTS is enabled and configured correctly.
        tts_helper.speak_text(ev.text, voice_id=voice_id)

    # Helper method to draw a semi-transparent panel with rounded corners and an optional border, used for the info panel and quit confirmation modal. This allows us to have a consistent style for panels in the UI, with a nice background and border to make them stand out against the game background.
    def _draw_panel(self, surface, rect, color=(30, 30, 35, 200), radius=14, border=True):
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, color, panel.get_rect(), border_radius=radius)

        if border:
            pygame.draw.rect(
                panel,
                (180, 180, 180, 220),
                panel.get_rect(),
                2,
                border_radius=radius
            )

        surface.blit(panel, rect.topleft)

    # Updates the game screen
    def draw(self, surface):
        surface.blit(self._get_background(), (0, 0))

        if self.engine.phase == "Nuit":
            overlay = pygame.Surface((self.app.w, self.app.h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 60))
            surface.blit(overlay, (0, 0))

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
        dbg = self.small_font.render("Debug : ESC=menu  |  Tab=paramètres", True, (140, 140, 140))
        surface.blit(dbg, (self.chat_rect.x + 10, self.chat_rect.bottom - 24))

        # Bouton du moment
        if self.engine.phase == "JourVote":
            self.confirm_btn.draw(surface)
        else:
            self.continue_btn.draw(surface)

        # Tooltips
        mx, my = pygame.mouse.get_pos()
        hover_text = ""

        # Tooltip for continue/confirm button based on the current phase and whether the button is enabled, providing contextual information to the player about what the button does and whether they can click it. This helps guide the player through the game flow and informs them of any conditions that need to be met before they can proceed.
        hover_text = hover_text or (self.confirm_btn.get_hover_text((mx, my)) if self.engine.phase == "JourVote" else "")
        hover_text = hover_text or (self.continue_btn.get_hover_text((mx, my)) if self.engine.phase != "JourVote" else "")

        # Player list items (name, note, vote buttons)
        hover_text = hover_text or self.player_list.get_hover_text((mx, my))

        # Show tooltip if hovering over something with hover text (buttons, player list items, etc.)
        self.tooltip.draw(surface, hover_text, (mx, my))

        # Quit confirmation modal
        if self.show_quit_confirm:
            # Overlay semi-transparent to dim the background and focus attention on the quit confirmation modal, which asks the player to confirm if they really want to quit the current game and return to the main menu, preventing accidental exits. The modal includes "Annuler" and "Quitter" buttons for the player's choice.
            overlay = pygame.Surface((self.app.w, self.app.h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            surface.blit(overlay, (0, 0))

            # Draw the quit confirmation modal with a title, message, and buttons for confirming or canceling the quit action. This modal appears when the player presses ESC, asking them to confirm if they really want to quit the current game and return to the main menu, which helps prevent accidental exits.
            pygame.draw.rect(surface, (30, 30, 34), self.quit_modal_rect, border_radius=16)
            pygame.draw.rect(surface, (200, 200, 200), self.quit_modal_rect, 2, border_radius=16)

            cx = self.quit_modal_rect.centerx

            # Title and message for the quit confirmation modal, asking the player if they want to quit the current game and return to the main menu, which helps prevent accidental exits. The title is more prominent, while the message provides additional context.
            title = self.quit_title_font.render("Quitter la partie ?", True, (240, 240, 240))
            surface.blit(title, title.get_rect(center=(cx, self.quit_modal_rect.y + 45)))

            # Message for the quit confirmation modal, asking the player if they want to quit the current game and return to the main menu, which helps prevent accidental exits. This message provides additional context below the title.
            msg = self.font.render("Retourner à l'accueil", True, (200, 200, 200))
            surface.blit(msg, msg.get_rect(center=(cx, self.quit_modal_rect.y + 85)))

            self.quit_btn_cancel.draw(surface)
            self.quit_btn_confirm.draw(surface)


# Base class for end screens (victory/defeat)
class EndScreen(Screen):
    # Initializes the end screen with title, subtitle, and buttons
    def __init__(self, app, title: str, subtitle: str, num_players: int, wolves: list[str], found_wolves: list[str], engine_cls):
        super().__init__(app)
        self.title_font = pygame.font.SysFont(None, 72)
        self.font = pygame.font.SysFont(None, 28)

        audio_config.TTS_ENABLED = False
        tts_helper.disable_and_stop()

        # Store number of players
        self.num_players = num_players
        self.title = title
        self.subtitle = subtitle

        self.engine_cls = engine_cls

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
            tts_helper.disable_and_stop()
            self.app.set_screen(SetupScreen(self.app))
            return

        if self.btn_replay.handle_event(event):
            tts_helper.disable_and_stop()
            self.app.set_screen(ModeSelectScreen(self.app, self.num_players))
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            tts_helper.disable_and_stop()
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
    def __init__(self, app, num_players: int, wolves: list[str], found_wolves: list[str], engine_cls):
        super().__init__(
            app,
            title = "VICTOIRE !",
            subtitle = "Tous les loups ont été éliminés.",
            num_players = num_players,
            wolves = wolves,
            found_wolves = found_wolves,
            engine_cls=engine_cls
        )


# Defeat screen subclass
class DefeatScreen(EndScreen):
    def __init__(self, app, num_players: int, wolves: list[str], found_wolves: list[str], engine_cls):
        super().__init__(
            app,
            title = "DÉFAITE…",
            subtitle = "Les loups ont pris le contrôle du village.",
            num_players = num_players,
            wolves = wolves,
            found_wolves = found_wolves,
            engine_cls=engine_cls
        )


# Ollama error screen
class OllamaErrorScreen(Screen):
    def __init__(self, app, error_message: str, previous_screen):
        super().__init__(app)
        self.error_message = error_message
        self.previous_screen = previous_screen

        audio_config.TTS_ENABLED = False
        tts_helper.disable_and_stop()

        # Fonts
        self.title_font = pygame.font.SysFont(None, 48)
        self.font = pygame.font.SysFont(None, 32)
        self.small_font = pygame.font.SysFont(None, 24)

        # Functions from ollama_installer module (injected for easier testing/mocking)
        from game.ollama_installer import (
            is_ollama_running,
            has_model,
            open_ollama_download,
            pull_model_async,
        )
        self._is_ollama_running = is_ollama_running
        self._has_model = has_model
        self._open_ollama_download = open_ollama_download
        self._pull_model_async = pull_model_async

        # State
        self.status_text = ""
        self.model_name = "mistral"
        self.is_downloading = False

        # Checker thread state
        self._ollama_ok = False
        self._model_ok = False
        self._stop_checker = False
        self._checker_thread = None
        self._start_checker_thread()

        # Dots animation for download status
        self._dots_t = 0.0
        self._dots = ""

        # Lock to prevent status text updates during critical operations (like starting a download), to avoid overwriting important messages with automatic status updates from the checker thread. When locked, the checker thread will not update the status text, allowing us to show specific messages related to the current operation without them being overwritten by the periodic checks.
        self._status_lock = False
        self._status_lock_timer = 0.0

        # Progress tracking for model download (if needed in the future, currently we just show an indeterminate "Downloading..." status without progress percentage, but this can be extended to show actual progress if the pull_model_async function provides that information through callbacks or a progress object). For now, we just have a placeholder for progress tracking in case we want to implement it later.
        self.progress = None
        self.last_status_line = ""

        # Flag to block quitting the screen while a critical operation is in progress (like downloading the model), to prevent the user from accidentally leaving the screen and interrupting the operation. When True, we can ignore quit events or show a confirmation dialog if the user tries to leave while an important operation is still ongoing.
        self.block_quit = False

        # Buttons (anchored near bottom)
        cx = app.w // 2
        btn_w, btn_h = 360, 50
        base_y = app.h - 280
        gap = 16

        self.install_btn = Button(
            rect=(cx - btn_w // 2, base_y, btn_w, btn_h),
            text="Installer Ollama",
            font=self.font,
            tooltip="Ouvre la page officielle de téléchargement d'Ollama"
        )

        self.pull_model_btn = Button(
            rect=(cx - btn_w // 2, base_y + (btn_h + gap), btn_w, btn_h),
            text="Télécharger Mistral (~4 Go)",
            font=self.font,
            tooltip="Télécharge le modèle requis (ollama pull mistral)"
        )

        self.retry_btn = Button(
            rect=(cx - btn_w // 2, base_y + 2 * (btn_h + gap), btn_w, btn_h),
            text="Réessayer",
            font=self.font,
            tooltip="Vérifie Ollama + modèle, puis relance"
        )

        self.return_btn = Button(
            rect=(cx - btn_w // 2, base_y + 3 * (btn_h + gap), btn_w, btn_h),
            text="Retour",
            font=self.font,
            tooltip="Retour à la sélection"
        )

        # Initial refresh (so pull button can be disabled immediately)
        self._refresh_availability()

    # Helper to set status text with optional lock to prevent overwriting by checker thread. This allows us to show specific messages related to the current operation (like "Downloading...") without them being overwritten by the periodic status updates from the checker thread, which could cause confusion if they overwrite important messages with more generic status updates.
    def _set_status(self, text: str, lock_seconds: float = 0.0):
        self.status_text = text
        if lock_seconds > 0:
            self._status_lock = True
            self._status_lock_timer = lock_seconds

    # Starts a background thread that periodically checks if Ollama is running and if the required model is available, updating the internal state accordingly. This allows us to keep the UI responsive and automatically update the availability status without blocking the main thread, especially since checking for Ollama and the model might involve some I/O or take a bit of time.
    def _start_checker_thread(self):
        def loop():
            while not self._stop_checker:
                try:
                    ollama_ok = self._is_ollama_running()
                    model_ok = self._has_model("mistral") if ollama_ok else False

                    self._ollama_ok = ollama_ok
                    self._model_ok = model_ok
                except Exception:
                    self._ollama_ok = False
                    self._model_ok = False

                time.sleep(0.6)

        import time
        self._checker_thread = threading.Thread(target=loop, daemon=True)
        self._checker_thread.start()

    # Helper to refresh the availability status of Ollama and the model, enabling/disabling buttons accordingly. This is called periodically by the checker thread to update the UI based on the current availability of Ollama and the model, allowing us to enable or disable the "Download Model" button depending on whether Ollama is running and whether the model is already installed, and to show appropriate status messages to guide the user on what they need to do.
    def _refresh_availability(self):
        ollama_ok = self._is_ollama_running()
        model_ok = self._has_model("mistral") if ollama_ok else False

        # Enable/disable pull button depending on availability
        self.pull_model_btn.enabled = (ollama_ok and not model_ok and not self.is_downloading)

        # Optional: small status helper
        if not ollama_ok:
            # keep existing error_message visible; status is just a helper
            if not self.status_text:
                self.status_text = "Ollama n'est pas lancé."
        else:
            if model_ok and not self.is_downloading:
                self.status_text = "Ollama est prêt. Cliquez sur Réessayer."

    # Cleanup when quitting the screen, including stopping the checker thread and optionally removing the model if a download was in progress, to ensure we don't leave a broken state if the user tries to quit while we're still downloading the model. This allows us to clean up any background threads and potentially remove partially downloaded models to avoid leaving the user's system in a broken state if they exit during a critical operation.
    def on_quit(self):
        if getattr(self, "is_downloading", False):
            try:
                from game.ollama_installer import rm_model_async
                print("[QUIT] Download in progress -> removing model to cleanup...")
                rm_model_async(self.model_name)
            except Exception as e:
                print(f"[QUIT] Cleanup failed: {e}")

    # Updates the screen, including handling status lock timing and updating button states based on current availability and downloading status. This is called every frame to update the UI, allowing us to manage the timing of status messages (like showing "Downloading..." for a certain duration without it being overwritten by the checker thread), and to enable or disable buttons based on whether Ollama is running, whether the model is available, and whether a download is currently in progress.
    def update(self, dt: float):
        # Update status lock timer
        if self._status_lock:
            self._status_lock_timer -= dt
            if self._status_lock_timer <= 0:
                self._status_lock = False

        # Update availability status from checker thread
        disabled = self.is_downloading
        self.install_btn.enabled = not disabled
        self.pull_model_btn.enabled = not disabled and self._ollama_ok and not self._model_ok
        self.retry_btn.enabled = not disabled
        self.return_btn.enabled = not disabled

        # Animate dots for downloading status
        if self.is_downloading:
            self._dots_t += dt
            if self._dots_t >= 0.35:
                self._dots_t = 0.0
                self._dots = "." if self._dots == "" else self._dots + "."
                if len(self._dots) > 3:
                    self._dots = ""

        # Update status text based on current availability and downloading status, but only if not locked by a critical operation (like starting a download), to avoid overwriting important messages with automatic status updates from the checker thread. This allows us to show specific messages related to the current operation without them being overwritten by the periodic checks, while still providing helpful status updates when not in the middle of an important operation.
        if not self._ollama_ok:
            if "téléchargement" not in self.status_text.lower():
                self.status_text = "Ollama n'est pas lancé."
        elif self._model_ok:
            self.status_text = "Ollama est prêt. Cliquez sur Réessayer."
            if self.is_downloading or self._status_lock:
                return
        else:
            self.status_text = "Ollama OK. Téléchargez le modèle Mistral."
            if self.is_downloading or self._status_lock:
                return

    # Handles events for the Ollama error screen, including button clicks and key presses, while also blocking certain events during critical operations like downloading to prevent interruptions. This allows us to manage user interactions with the screen, providing appropriate responses to button clicks (like opening the download page, starting the model download, retrying the check, or returning to the previous screen), while also preventing the user from accidentally interrupting important operations by blocking certain events (like quitting or starting another operation) while a critical operation is in progress.
    def handle_event(self, event):
        # Block certain events while downloading to prevent interruptions
        if self.is_downloading:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                return

        # Handle button events
        if self.install_btn.handle_event(event):
            self._open_ollama_download()
            self.status_text = "Page de téléchargement ouverte."
            return

        # Start model download if button clicked, with appropriate checks and status updates. This initiates the model download process when the user clicks the "Download Model" button, but only if Ollama is running and the model is not already available, and it provides status updates to inform the user about the progress of the download, while also blocking certain interactions during the download to prevent interruptions.
        if self.pull_model_btn.handle_event(event):
            if not self._is_ollama_running():
                self.status_text = "Ollama n'est pas lancé."
                return

            if self.is_downloading:
                return

            self.is_downloading = True
            self.block_quit = True
            self.pull_model_btn.text = "Téléchargement… (patientez)"

            # Call the asynchronous pull function with callbacks for completion, error handling, progress updates, and status updates. This allows us to start the model download in the background without blocking the UI, and to update the UI based on the progress and status of the download through the provided callbacks, giving the user feedback on what's happening during the download process.
            def done():
                self.is_downloading = False
                self.block_quit = False
                self.pull_model_btn.text = "Télécharger Mistral (~4 Go)"
                self.status_text = "Modèle téléchargé. Cliquez sur Réessayer."

            # Handle errors during the download process, updating the status text and resetting the downloading state to allow the user to try again or take other actions. This ensures that if something goes wrong during the download (like a network error, insufficient disk space, or an issue with Ollama), we can inform the user about the error and allow them to recover without leaving them stuck in a broken state.
            def error(msg):
                self.is_downloading = False
                self.block_quit = False
                self.pull_model_btn.text = "Télécharger Mistral (~4 Go)"
                self.status_text = f"Erreur téléchargement : {msg}"

            # Handle progress updates if the pull_model_async function provides that information through callbacks, allowing us to show actual progress percentage in the UI instead of just an indeterminate "Downloading..." status. This can give the user a better sense of how long the download will take and how it's progressing, especially for large models where the download time might be significant.
            def on_progress(pct: int):
                self.progress = pct

            # Handle status updates from the pull_model_async function, allowing us to show specific status messages related to the download process (like "Connecting to server...", "Downloading files...", "Finalizing installation...", etc.) if that information is available through callbacks, giving the user more detailed feedback on what's happening during the download process. For now, we just capture the last status line and display it above the progress bar, but this can be extended to show a history of status messages if desired.
            def on_status(line: str):
                self.last_status_line = line[:60]

            # Start the asynchronous model download process with the defined callbacks for completion, error handling, progress updates, and status updates. This initiates the download in the background and allows us to update the UI based on the progress and status of the download through the provided callbacks, giving the user feedback on what's happening during the download process.
            self._pull_model_async("mistral", on_done=done, on_error=error, on_progress=on_progress, on_status=on_status)
            return

        # Handle retry button click, checking if Ollama and the model are now available, and transitioning back to the previous screen if they are, or showing an updated status message if they're still not available. This allows the user to easily check if they've resolved the issues (like starting Ollama or completing the model download) and to proceed once everything is ready, while also providing feedback if they still need to take action.
        if self.retry_btn.handle_event(event):
            if self._ollama_ok and self._model_ok:
                self._stop_checker = True
                self.app.set_screen(self.previous_screen)
            else:
                self.status_text = "Toujours indisponible : lance Ollama et/ou installe Mistral."
            return

        if self.return_btn.handle_event(event):
            self._stop_checker = True
            from gui.screens import SetupScreen
            self.app.set_screen(SetupScreen(self.app))
            return


        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            from gui.screens import SetupScreen
            self.app.set_screen(SetupScreen(self.app))

    # Draws the Ollama error screen, showing the error message, instructions for resolving the issue, status updates, and buttons for actions like installing Ollama, downloading the model, retrying the check, or returning to the previous screen. This provides a user-friendly interface to help users understand what went wrong with Ollama, how to fix it, and to take appropriate actions to resolve the issue and proceed with the game.
    def draw(self, surface):
        surface.fill((25, 15, 15))  # Dark red background

        cx = self.app.w // 2

        # Title
        title = self.title_font.render("Erreur Ollama", True, (255, 100, 100))
        surface.blit(title, title.get_rect(center=(cx, 120)))

        # Error message (top)
        y = 170
        for line in self.error_message.split("\n"):
            line = line.strip()
            if not line:
                continue
            t = self.small_font.render(line, True, (255, 200, 200))
            surface.blit(t, t.get_rect(center=(cx, y)))
            y += 26

        # Instructions
        instructions = [
            "Assurez-vous que :",
            "• Ollama est lancé (ollama serve)",
            "• Un modèle est installé (ollama pull mistral)",
            "• Le port 11434 est accessible",
        ]
        y = 200
        for instruction in instructions:
            inst_text = self.small_font.render(instruction, True, (200, 200, 200))
            surface.blit(inst_text, inst_text.get_rect(center=(cx, y)))
            y += 24

        # Status text (just above buttons)
        if self.status_text:
            st = self.small_font.render(self.status_text, True, (235, 235, 235))
            surface.blit(st, st.get_rect(center=(cx, 430)))

        # Progress bar area
        bar_w = 520
        bar_h = 18
        bar_x = cx - bar_w // 2
        bar_y = self.install_btn.rect.y - 70


        if self.is_downloading:
            # background
            pygame.draw.rect(surface, (40, 40, 45), (bar_x, bar_y, bar_w, bar_h), border_radius=8)
            pygame.draw.rect(surface, (160, 160, 160), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=8)

            if self.progress is not None:
                fill = int(bar_w * (self.progress / 100.0))
                pygame.draw.rect(surface, (220, 120, 80), (bar_x, bar_y, fill, bar_h), border_radius=8)

                pct_text = self.small_font.render(f"{self.progress}%", True, (235, 235, 235))
                surface.blit(pct_text, pct_text.get_rect(center=(cx, bar_y - 18)))
            else:
                # fallback indeterminate animation
                t = (pygame.time.get_ticks() % 1200) / 1200.0
                block_w = 90
                bx = bar_x + int((bar_w - block_w) * t)
                pygame.draw.rect(surface, (220, 120, 80), (bx, bar_y, block_w, bar_h), border_radius=8)

            if self.last_status_line:
                st = self.small_font.render(self.last_status_line, True, (210, 210, 210))
                surface.blit(st, st.get_rect(center=(cx, bar_y + 32)))

        # Buttons
        self.install_btn.draw(surface)
        self.pull_model_btn.draw(surface)
        self.retry_btn.draw(surface)
        self.return_btn.draw(surface)