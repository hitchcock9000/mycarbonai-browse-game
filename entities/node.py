# entities/node.py
"""
Restoration Nodes. Interactive energy towers, repair terminals, and filters
which heal nearby terrain upon synchronization.
"""

import pygame
import math
import random
from config import PRIMARY_TEAL, SECONDARY_TEAL, COOL_GREEN, WARNING_RED, WHITE
from asset_loader import asset_loader

class RestorationNode:
    def __init__(self, x, y, node_type, label, val_vis, val_eco, val_nrg, val_ems, img_name):
        self.x = x
        self.y = y
        self.w = 104
        self.h = 136
        self.node_type = node_type # transport, grid, water, biodiversity, relay, filter
        self.label = label
        
        # Metrics impact upon restoration
        self.val_visibility = val_vis
        self.val_ecosystem = val_eco
        self.val_energy = val_nrg
        self.val_emissions = val_ems
        
        self.img_name = img_name
        self.restored = False
        
        # Connection state trackers
        self.connection_progress = 0.0 # 0.0 to 1.0
        self.pulse = 0.0

    def get_rect(self):
        # Anchor base boundary
        return pygame.Rect(self.x - self.w // 2, self.y - self.h, self.w, self.h)

    def update(self, dt):
        self.pulse = (self.pulse + 0.05 * dt) % (2 * math.pi)

    def draw_telemetry(self, surface, camera, scan_intensity):
        """Draw neon diagnostic text and diagnostic overlay panels under scan mode."""
        if scan_intensity < 0.05:
            return
            
        screen_x, screen_y = camera.apply((self.x, self.y))
        alpha = int(scan_intensity * 255)
        
        # Select diagnostic color
        color = COOL_GREEN if self.restored else WARNING_RED
        font = asset_loader.get_font("terminal")
        
        # Text fields
        id_lbl = font.render(f"[SYS_ID: {self.node_type.upper()}_NODE]", True, (*color, alpha))
        status_lbl = font.render(f"[STATUS: {'ONLINE' if self.restored else 'DISCONNECTED'}]", True, (*color, alpha))
        label_lbl = font.render(f"NAME: {self.label}", True, (*WHITE, alpha))
        
        # Draw floating diagnostic panel
        panel_y = screen_y - self.h - 40
        surface.blit(label_lbl, (screen_x - label_lbl.get_width()//2, panel_y))
        surface.blit(id_lbl, (screen_x - id_lbl.get_width()//2, panel_y + 16))
        surface.blit(status_lbl, (screen_x - status_lbl.get_width()//2, panel_y + 30))

        if not self.restored:
            # Draw dashed broken emissions lines leaking down to soil
            dash_surf = pygame.Surface((20, 140), pygame.SRCALPHA)
            pygame.draw.line(dash_surf, (*WARNING_RED, int(scan_intensity * 120)), (10, 0), (10, 140), 2)
            # Add line dashes by cutting them out or drawing individual rects
            for offset in range(0, 140, 15):
                pygame.draw.rect(dash_surf, (0,0,0,0), (8, offset, 4, 8))
            surface.blit(dash_surf, (screen_x - 10, screen_y - 20))

    def draw(self, surface, camera, player):
        """Draw the node structure and dynamic connection overlays."""
        screen_x, screen_y = camera.apply((self.x - self.w // 2, self.y - self.h))
        
        # Render main structure sprite
        img = asset_loader.get_image(self.img_name, (self.w, self.h))
        surface.blit(img, (screen_x, screen_y))
        
        # Diagnostic rings
        center_x = screen_x + self.w // 2
        center_y = screen_y + self.h - 58
        
        if not self.restored:
            # Pulsing unstable warning grid ring
            glow_radius = int(72 + math.sin(self.pulse * 2) * 5)
            alpha = int(80 + math.sin(self.pulse * 2) * 40)
            
            ring_surf = pygame.Surface((glow_radius * 2 + 4, glow_radius * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (*WARNING_RED, alpha), (glow_radius, glow_radius), glow_radius, 2)
            surface.blit(ring_surf, (center_x - glow_radius, center_y - glow_radius))

            # Connection progress dial
            if self.connection_progress > 0.02:
                dial_radius = 48
                dial_surf = pygame.Surface((dial_radius * 2 + 4, dial_radius * 2 + 4), pygame.SRCALPHA)
                
                # Draw dynamic progress arc
                arc_rect = pygame.Rect(2, 2, dial_radius * 2, dial_radius * 2)
                end_angle = (self.connection_progress * 2 * math.pi) - (math.pi / 2)
                pygame.draw.arc(dial_surf, COOL_GREEN, arc_rect, -math.pi/2, end_angle, 4)
                
                # Center percentage text
                pct_font = asset_loader.get_font("hud")
                pct_lbl = pct_font.render(f"{int(self.connection_progress * 100)}%", True, COOL_GREEN)
                
                surface.blit(dial_surf, (center_x - dial_radius, center_y - dial_radius))
                surface.blit(pct_lbl, (center_x - pct_lbl.get_width()//2, center_y - pct_lbl.get_height()//2))
        else:
            # Stable circular telemetry bracket
            glow_radius = 64
            ring_surf = pygame.Surface((glow_radius * 2 + 4, glow_radius * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (*COOL_GREEN, 100), (glow_radius, glow_radius), glow_radius, 2)
            
            # Subtle revolving tech brackets
            brk_angle = self.pulse
            x1 = glow_radius + math.cos(brk_angle) * glow_radius
            y1 = glow_radius + math.sin(brk_angle) * glow_radius
            pygame.draw.circle(ring_surf, WHITE, (int(x1), int(y1)), 4)
            
            surface.blit(ring_surf, (center_x - glow_radius, center_y - glow_radius))
