# Fichier : gui/app.py
# Point d'entrée principal de l'application GUI

import pygame
import sys

from gui.screens import SetupScreen


class App:
    # Initializes the application with given width and height
    def __init__(self, w=1000, h=700):
        pygame.init()
        self.w, self.h = w, h
        self.screen = pygame.display.set_mode((w, h))
        pygame.display.set_caption("Loup-Garou IA")
        self.clock = pygame.time.Clock()
        self.current_screen = SetupScreen(self)

    # Sets the current screen
    def set_screen(self, screen):
        self.current_screen = screen

    # Main application loop
    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.current_screen.handle_event(event)

            self.current_screen.update(dt)
            self.current_screen.draw(self.screen)
            pygame.display.flip()