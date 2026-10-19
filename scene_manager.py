# scene_manager.py
"""
Central Scene Routing and Transition Engine.
"""

import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT

class SceneManager:
    def __init__(self):
        self.current_scene = None
        self.fade_alpha = 0
        self.target_scene = None
        self.fade_speed = 8
        self.transitioning = False

    def set_scene(self, scene):
        """Immediately transition to a new scene."""
        self.current_scene = scene

    def transition_to(self, new_scene):
        """Trigger a cinematic dark fade transition to a new scene."""
        if self.transitioning:
            return
        self.target_scene = new_scene
        self.transitioning = True
        self.fade_alpha = 0

    def update(self, dt):
        """Update active scene and coordinate transitions."""
        if self.current_scene:
            self.current_scene.update(dt)

        if self.transitioning:
            # Fade out
            if self.target_scene:
                self.fade_alpha = min(255, self.fade_alpha + self.fade_speed * dt)
                if self.fade_alpha >= 255:
                    self.current_scene = self.target_scene
                    self.target_scene = None
            # Fade in
            else:
                self.fade_alpha = max(0, self.fade_alpha - self.fade_speed * dt)
                if self.fade_alpha <= 0:
                    self.transitioning = False

    def handle_event(self, event):
        """Pass system events to the active scene."""
        if self.current_scene and not self.transitioning:
            self.current_scene.handle_event(event)

    def draw(self, surface):
        """Draw active scene and transition screen overlays."""
        if self.current_scene:
            self.current_scene.draw(surface)

        if self.transitioning or self.fade_alpha > 0:
            fade_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            fade_surf.fill((7, 17, 31, int(self.fade_alpha)))
            surface.blit(fade_surf, (0, 0))
