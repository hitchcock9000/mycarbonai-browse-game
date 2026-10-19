# entities/drone.py
"""
NORA AI Companion Drone.
Hovers smoothly, highlights objectives, and projects interactive holobeams.
"""

import pygame
import math
import random
from config import PRIMARY_TEAL, SECONDARY_TEAL, COOL_GREEN, WARNING_RED, WHITE
from asset_loader import asset_loader

class CompanionDrone:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 54
        self.h = 60
        
        # Hover parameters (Sine-wave oscillations)
        self.hover_offset = 0.0
        self.hover_speed = 0.06
        self.hover_range = 8.0
        
        # Physics Spring coefficients (elastic follow)
        self.spring_constant = 0.08
        self.damping = 0.76
        self.vx = 0
        self.vy = 0
        
        # Objective tracking
        self.objective_target = None
        self.hologram_pulse = 0.0
        self.emotion = "neutral"  # neutral, happy, warning
        self.emotion_timer = 0

    def update(self, player, dt, particles):
        """Update spring-based positions and emotional triggers."""
        # Calculate target position (hover above shoulder opposite to walking direction)
        target_x = player.x - 55 if player.dir > 0 else player.x + player.w + 10
        target_y = player.y - 68
        
        # Add float sine oscillation
        self.hover_offset += self.hover_speed * dt
        target_y += math.sin(self.hover_offset) * self.hover_range

        # Apply Spring force
        dx = target_x - self.x
        dy = target_y - self.y
        
        force_x = dx * self.spring_constant
        force_y = dy * self.spring_constant
        
        self.vx = (self.vx + force_x) * self.damping
        self.vy = (self.vy + force_y) * self.damping
        
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Drone light pulses
        self.hologram_pulse = (self.hologram_pulse + 0.04 * dt) % (2 * math.pi)

        # Emotional timers
        if self.emotion_timer > 0:
            self.emotion_timer -= 1 * dt
            if self.emotion_timer <= 0:
                self.emotion = "neutral"

        # Emit floating nano-particles from drone engine
        if random.random() < 0.15 * dt:
            color = COOL_GREEN if self.emotion == "happy" else (WARNING_RED if self.emotion == "warning" else PRIMARY_TEAL)
            # Add to systems particles
            particles.emit_burst(self.x + self.w//2, self.y + self.h - 10, color, 1)

    def trigger_emotion(self, emotion_type, duration=120):
        """Affect NORA's expressive reactions."""
        self.emotion = emotion_type
        self.emotion_timer = duration

    def draw(self, surface, camera, player):
        """Draw the NORA sprite with dynamic glow rings and searchlight cones."""
        screen_x, screen_y = camera.apply((self.x, self.y))
        
        # Emotional tint color
        glow_color = COOL_GREEN if self.emotion == "happy" else (WARNING_RED if self.emotion == "warning" else PRIMARY_TEAL)

        # 01 - Draw Translucent Searchlight Cone (Hologram Beam)
        if player.is_scanning or player.is_connecting or self.emotion == "happy":
            beam_surf = pygame.Surface((200, 300), pygame.SRCALPHA)
            beam_width = 80 + math.sin(self.hologram_pulse) * 15
            alpha = int(80 + math.sin(self.hologram_pulse) * 30)
            
            # Triangle polygon for cone representation
            pygame.draw.polygon(beam_surf, (*glow_color, alpha // 3), [
                (100, 0),
                (100 - int(beam_width // 2), 260),
                (100 + int(beam_width // 2), 260)
            ])
            
            # Bottom light circle splash
            pygame.draw.ellipse(beam_surf, (*glow_color, alpha // 2), (100 - int(beam_width // 2), 245, beam_width, 30))
            
            # Draw network grid lines inside the beam
            grid_y = int((self.hologram_pulse * 40) % 240)
            y_ratio = grid_y / 260
            gw = int(beam_width * y_ratio)
            pygame.draw.line(beam_surf, (*glow_color, alpha), (100 - gw//2, grid_y), (100 + gw//2, grid_y), 1)

            # Blit beam centered under the NORA orb
            surface.blit(beam_surf, (screen_x + self.w//2 - 100, screen_y + self.h - 10), special_flags=pygame.BLEND_RGBA_ADD)

        # 02 - Draw dynamic drone sprite
        img = asset_loader.get_image("nora_orb", (self.w, self.h))
        surface.blit(img, (screen_x, screen_y))

        # 03 - Draw digital companion telemetry (thin cyber-bracket above drone)
        if player.is_scanning:
            status_text = "NORA: SYNCING" if self.emotion == "neutral" else (
                "NORA: COMPILATION SUCCESS" if self.emotion == "happy" else "NORA: DETECTING BIOME COLLAPSE"
            )
            font = asset_loader.get_font("terminal")
            lbl = font.render(status_text, True, glow_color)
            surface.blit(lbl, (screen_x - lbl.get_width()//2 + self.w//2, screen_y - 20))
            
            # Diagnostic mini brackets
            pygame.draw.line(surface, glow_color, (screen_x - 10, screen_y - 12), (screen_x - 10, screen_y - 4), 1)
            pygame.draw.line(surface, glow_color, (screen_x + self.w + 10, screen_y - 12), (screen_x + self.w + 10, screen_y - 4), 1)
