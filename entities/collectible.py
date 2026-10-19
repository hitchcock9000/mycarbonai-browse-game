# entities/collectible.py
"""
Diagnostic Collectibles. Represent carbon nodes, biodiversity seeds,
audit ledgers, and carbon relics.
"""

import pygame
import math
import random
from config import PRIMARY_TEAL, SECONDARY_TEAL, COOL_GREEN, WHITE
from asset_loader import asset_loader

class CollectibleItem:
    def __init__(self, x, y, img_name, label, value):
        self.x = x
        self.y = y
        self.w = 54
        self.h = 54
        self.img_name = img_name
        self.label = label
        self.value = value
        self.done = False
        
        # Floating animations
        self.float_offset = random.uniform(0, 100)
        self.float_speed = 0.05
        self.float_range = 6.0
        self.pulse = 0.0

    def get_rect(self):
        return pygame.Rect(self.x - self.w // 2, self.y - self.h // 2, self.w, self.h)

    def update(self, dt):
        """Hover and cycle pulse frequencies."""
        self.float_offset += self.float_speed * dt
        self.pulse = (self.pulse + 0.06 * dt) % (2 * math.pi)

    def draw_telemetry(self, surface, camera, scan_intensity):
        """Draw holographic projection lines from above in scan mode."""
        if self.done or scan_intensity < 0.05:
            return
            
        screen_x, screen_y = camera.apply((self.x, self.y))
        alpha = int(scan_intensity * 255)
        
        color = SECONDARY_TEAL if "seed" in self.img_name else (PRIMARY_TEAL if "carbon" in self.img_name else WHITE)
        font = asset_loader.get_font("terminal")
        
        # Telemetry labels
        lbl = font.render(f"[DATA_FRAG: {self.label.upper()}]", True, (*color, alpha))
        
        # Anchor point vertical projection lines
        pygame.draw.line(surface, (*color, int(scan_intensity * 100)), 
                         (screen_x, screen_y - 30), (screen_x, screen_y - 70), 1)
        surface.blit(lbl, (screen_x - lbl.get_width()//2, screen_y - 84))

    def draw(self, surface, camera):
        """Draw floating collectible item."""
        if self.done:
            return
            
        # Add float offset
        fy = self.y + math.sin(self.float_offset) * self.float_range
        screen_x, screen_y = camera.apply((self.x - self.w // 2, fy - self.h // 2))
        
        img = asset_loader.get_image(self.img_name, (self.w, self.h))
        surface.blit(img, (screen_x, screen_y))
        
        # Subtle glowing back-orbit ring
        alpha = int(70 + math.sin(self.pulse * 2.5) * 30)
        color = SECONDARY_TEAL if "seed" in self.img_name else PRIMARY_TEAL
        ring_surf = pygame.Surface((self.w + 12, self.h + 12), pygame.SRCALPHA)
        pygame.draw.circle(ring_surf, (*color, alpha), (self.w//2 + 6, self.h//2 + 6), self.w//2 + 4, 1)
        surface.blit(ring_surf, (screen_x - 6, screen_y - 6))
