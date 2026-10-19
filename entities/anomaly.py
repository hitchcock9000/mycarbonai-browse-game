# entities/anomaly.py
"""
Environmental Anomalies. Represent untracked carbon emissions and system glitches.
Walkers resolve them through visual identification and scanning rather than combat.
"""

import pygame
import math
import random
from config import PRIMARY_TEAL, WARNING_RED, WHITE
from asset_loader import asset_loader

class EnvironmentalAnomaly:
    def __init__(self, x, y, width, height, img_name, speed, patrol_min, patrol_max, kind):
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.img_name = img_name
        self.vx = speed
        self.patrol_min = patrol_min
        self.patrol_max = patrol_max
        self.kind = kind
        
        self.resolved = False
        self.pulse = random.uniform(0, 100)

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, dt):
        """Patrol boundaries back and forth."""
        self.x += self.vx * dt
        self.pulse = (self.pulse + 0.08 * dt) % (2 * math.pi)

        # Check boundaries and turn around
        if self.x < self.patrol_min:
            self.x = self.patrol_min
            self.vx *= -1
        elif self.x > self.patrol_max:
            self.x = self.patrol_max
            self.vx *= -1

    def draw_telemetry(self, surface, camera, scan_intensity):
        """Draw diagnostic lock-on brackets and telemetry text in Scan Mode."""
        if scan_intensity < 0.1:
            return
            
        rect = self.get_rect()
        screen_x, screen_y = camera.apply((rect.x + rect.w // 2, rect.y + rect.h // 2))
        alpha = int(scan_intensity * 255)
        
        font = asset_loader.get_font("terminal")
        lbl = font.render(f"[ERR_ENTITY: {self.kind.upper()}]", True, (*WARNING_RED, alpha))
        
        # Revolving lock brackets
        r = int(50 + math.sin(self.pulse * 2) * 5)
        pygame.draw.circle(surface, (*WARNING_RED, alpha), (screen_x, screen_y), r, 1)
        
        # Locking tags
        surface.blit(lbl, (screen_x - lbl.get_width()//2, screen_y - r - 20))

    def draw(self, surface, camera, scan_intensity):
        """Draw the anomaly sprite, blending alpha states to convey perception as gameplay."""
        rect = self.get_rect()
        screen_x, screen_y = camera.apply((rect.x, rect.y))
        
        # State blending: Very shadowy/faint in normal vision, bright/glowing in scan mode
        base_alpha = 40  # Shadowy baseline
        blend_alpha = int(base_alpha + (255 - base_alpha) * scan_intensity)

        # Pygame does not support transparency values natively on images without copying.
        # We can draw it onto a temporary surface to apply transparency
        img = asset_loader.get_image(self.img_name, (self.w + 40, self.h + 40))
        
        temp_surf = pygame.Surface((self.w + 40, self.h + 40), pygame.SRCALPHA)
        temp_surf.blit(img, (0, 0))
        
        # Set final alpha mask
        alpha_surf = pygame.Surface((self.w + 40, self.h + 40), pygame.SRCALPHA)
        alpha_surf.fill((255, 255, 255, blend_alpha))
        temp_surf.blit(alpha_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # Render offset slightly to align with structural collision rect
        surface.blit(temp_surf, (screen_x - 20, screen_y - 28))
