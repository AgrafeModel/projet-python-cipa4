import pygame
from gui.widgets import Button
import audio_config


# ============================================================================
# SLIDER WIDGET
# ============================================================================
class Slider:    
    def __init__(self, rect, initial_value=0.5, label="", font=None):
        self.rect = pygame.Rect(rect)
        self.value = max(0.0, min(1.0, initial_value))
        self.label = label
        self.font = font or pygame.font.SysFont(None, 24)
        
        self.dragging = False
        self.hover = False

        self.enabled = True
        
        # Couleurs
        self.track_color = (100, 100, 100)
        self.handle_color = (200, 200, 200)
        self.handle_hover_color = (230, 230, 230)
        self.label_color = (240, 240, 240)
        
        self.handle_radius = 10
        
    def handle_event(self, event):
        if not self.enabled:
            self.dragging = False
            self.hover = False
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            handle_pos = self._get_handle_position()
            handle_rect = pygame.Rect(
                handle_pos[0] - self.handle_radius,
                handle_pos[1] - self.handle_radius,
                self.handle_radius * 2,
                self.handle_radius * 2
            )
            
            if handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
                self._update_value_from_mouse(event.pos[0])
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
            
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self._update_value_from_mouse(event.pos[0])
                
            handle_pos = self._get_handle_position()
            handle_rect = pygame.Rect(
                handle_pos[0] - self.handle_radius,
                handle_pos[1] - self.handle_radius,
                self.handle_radius * 2,
                self.handle_radius * 2
            )
            self.hover = handle_rect.collidepoint(event.pos)
    
    def _update_value_from_mouse(self, mouse_x):
        relative_x = max(0, min(mouse_x - self.rect.left, self.rect.width))
        self.value = relative_x / self.rect.width
    
    def _get_handle_position(self):
        x = self.rect.left + int(self.value * self.rect.width)
        y = self.rect.centery
        return (x, y)
    
    def draw(self, surface):
        # Colors depending on enabled
        if not self.enabled:
            track_color = (70, 70, 70)
            handle_color = (120, 120, 120)
            label_color = (150, 150, 150)
        else:
            track_color = self.track_color
            handle_color = self.handle_hover_color if self.hover else self.handle_color
            label_color = self.label_color

        # Label
        if self.label:
            label_surf = self.font.render(self.label, True, label_color)
            label_rect = label_surf.get_rect(
                centerx=self.rect.centerx,
                bottom=self.rect.top - 15
            )
            surface.blit(label_surf, label_rect)

        # Track
        pygame.draw.rect(surface, track_color, self.rect, border_radius=5)

        # Handle
        handle_pos = self._get_handle_position()
        pygame.draw.circle(surface, handle_color, handle_pos, self.handle_radius)

        # % value
        value_text = f"{int(self.value * 100)}%"
        value_surf = self.font.render(value_text, True, label_color)
        value_rect = value_surf.get_rect(
            centerx=self.rect.centerx,
            top=self.rect.bottom + 10
        )
        surface.blit(value_surf, value_rect)



# ============================================================================
# SETTINGS SCREEN
# ============================================================================
class SettingsScreen:
    def __init__(self, app, previous_screen=None):
        self.app = app
        self.previous_screen = previous_screen
        
        self.title_font = pygame.font.SysFont(None, 64)
        self.font = pygame.font.SysFont(None, 32)
        self.small_font = pygame.font.SysFont(None, 24)
        
        # Get actual volume
        current_volume = audio_config.music_volume

        slider_width = min(500, app.w - 200)
        slider_x = (app.w - slider_width) // 2
        slider_y = app.h // 2 + 75

        self.sound_slider = Slider(
            rect=(slider_x, slider_y, slider_width, 10),
            initial_value=audio_config.voice_volume,
            label="Volume de la voix",
            font=self.font
        )
        
        slider_width = min(500, app.w - 200)
        slider_x = (app.w - slider_width) // 2
        slider_y = app.h // 2 - 50
        
        self.volume_slider = Slider(
            rect=(slider_x, slider_y, slider_width, 10),
            initial_value=current_volume,
            label="Volume de la musique",
            font=self.font
        )
        
        self.back_button = Button(
            rect=(app.w // 2 - 100, app.h // 2 + 175, 200, 50),
            text="Retour",
            font=self.font,
            tooltip="Retourner au menu précédent (TAB)"
        )
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            self._go_back()
            return

        # Sliders
        self.volume_slider.handle_event(event)
        self.sound_slider.enabled = getattr(audio_config, "TTS_ENABLED", False)
        self.sound_slider.handle_event(event)

        # Music volume (live)
        try:
            audio_config.music_volume = self.volume_slider.value
            pygame.mixer.music.set_volume(audio_config.music_volume)
        except pygame.error:
            pass

        # Voice volume (live, même son en cours)
        if getattr(audio_config, "TTS_ENABLED", False):
            audio_config.voice_volume = self.sound_slider.value
            if audio_config.voice_channel:
                audio_config.voice_channel.set_volume(audio_config.voice_volume)

        # Back button
        if self.back_button.handle_event(event):
            self._go_back()

    def _go_back(self):
        if self.previous_screen:
            self.app.set_screen(self.previous_screen)
        else:
            from gui.screens import SetupScreen
            self.app.set_screen(SetupScreen(self.app))
    
    def update(self, dt: float):
        pass
    
    def draw(self, surface):
        surface.fill((20, 20, 25))
        
        title = self.title_font.render("Paramètres", True, (240, 240, 240))
        title_rect = title.get_rect(center=(self.app.w // 2, 100))
        surface.blit(title, title_rect)
        
        panel_rect = pygame.Rect(
            self.app.w // 2 - 320,
            self.app.h // 2 - 120,
            640,
            280
        )
        pygame.draw.rect(surface, (35, 35, 40), panel_rect, border_radius=12)
        pygame.draw.rect(surface, (180, 180, 180), panel_rect, 2, border_radius=12)
        
        self.volume_slider.draw(surface)

        self.sound_slider.draw(surface)
        if not getattr(audio_config, "TTS_ENABLED", False):
            msg = self.small_font.render(
                "Désactivé car la lecture vocale (TTS) n’est pas activée",
                True,
                (150, 150, 150)
            )
            msg_rect = msg.get_rect(
                centerx=self.sound_slider.rect.centerx,
                top=self.sound_slider.rect.bottom + 35
            )
            surface.blit(msg, msg_rect)
        
        self.back_button.draw(surface)
        
        hint = self.small_font.render("TAB pour retourner", True, (140, 140, 140))
        hint_rect = hint.get_rect(center=(self.app.w // 2, self.app.h - 40))
        surface.blit(hint, hint_rect)
