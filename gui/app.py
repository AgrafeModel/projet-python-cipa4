# Fichier : gui/app.py
# Point d'entrée principal de l'application GUI
# Note : Commentaires en anglais redigé par IA pour uniformité du code.
# Note : Certaines parties du code ont été générées par une IA (Copilot). Le code est fait à la
# main par l'humain, mais l'IA ajoute des optimisations et des suggestions.

import pygame
import sys
import os

from gui.screens import SetupScreen, GameScreen, VictoryScreen, DefeatScreen
import audio_config

class App:
    """Application with multiple music tracks for different screens"""
    
    def __init__(self, w=1000, h=700):
        pygame.init()
        pygame.mixer.init()
        
        self.w, self.h = w, h
        self.screen = pygame.display.set_mode((w, h))
        pygame.display.set_caption("Loup-Garou IA")
        self.clock = pygame.time.Clock()

        # Initialize pygame scrap for clipboard access (used in some screens)
        from pygame import scrap
        scrap.init()
        try:
            scrap.set_mode(pygame.SCRAP_CLIPBOARD)
        except Exception:
            pass
        
        # Music tracks for different screens
        self.music_tracks = {
            "menu": "music/menu2.mp3",
            "game": "music/LG.mp3",
            "victory": "music/Victory.mp3",
            "defeat": "music/Game_over.mp3"
        }
        
        self.current_track = None
        self.current_screen = SetupScreen(self)
        
        self.music_volume = audio_config.music_volume
        self.sound_volume = audio_config.voice_volume

        # Play menu music
        self.play_music("menu")

        pygame.mixer.music.set_volume(self.music_volume)  # Volume initial correct
        
    def play_music(self, track_name):
        """
        Changes the currently playing music
        
        Args:
            track_name: Name of the track ("menu", "game", "victory", "defeat")
        """
        # Don't reload if already playing
        if track_name == self.current_track:
            return
        
        # Check if track exists in dictionary
        if track_name not in self.music_tracks:
            print(f"⚠ Unknown track: {track_name}")
            return
        
        music_path = self.music_tracks[track_name]
        
        # Check if file exists
        if not os.path.exists(music_path):
            print(f"⚠ Music file not found: {music_path}")
            print(f"  Place a file named '{os.path.basename(music_path)}' in assets/music/")
            return
        
        try:
            # Keep current volume when switching tracks
            current_volume = pygame.mixer.music.get_volume()
            
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(current_volume)
            if music_path in {"music/LG.mp3", "music/menu2.mp3"}:
                pygame.mixer.music.play(-1)  # Loop infinitely
            else:
                pygame.mixer.music.play()
            
            self.current_track = track_name
            print(f"♪ Now playing: {track_name} ({os.path.basename(music_path)})")
            
        except pygame.error as e:
            print(f"⚠ Error loading music: {e}")
    
    def set_screen(self, screen):
        """
        Changes the current screen and adapts the music accordingly
        """
        self.current_screen = screen
        
        # Change music based on screen type
        if isinstance(screen, SetupScreen):
            self.play_music("menu")
        elif isinstance(screen, GameScreen):
            self.play_music("game")
        elif isinstance(screen, VictoryScreen):
            self.play_music("victory")
        elif isinstance(screen, DefeatScreen):
            self.play_music("defeat")
    
    def run(self):
        """Main application loop"""
        while True:
            dt = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # if the current screen has a custom on_quit method, call it to allow for cleanup before quitting
                    if hasattr(self.current_screen, "on_quit"):
                        try:
                            self.current_screen.on_quit()
                        except Exception as e:
                            print(f"[QUIT] on_quit error: {e}")

                    pygame.quit()
                    sys.exit()

                self.current_screen.handle_event(event)

            self.current_screen.update(dt)
            self.current_screen.draw(self.screen)
            pygame.display.flip()