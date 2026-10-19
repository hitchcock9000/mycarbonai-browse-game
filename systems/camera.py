# systems/camera.py
"""
Cinematic Camera Controller with smooth easing and procedural screenshake.
"""

import random
from config import SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.shake_intensity = 0
        self.shake_decay = 0.9  # Decay factor per frame

    def update(self, player_rect, scan_intensity):
        """Smoothly track the player and incorporate screenshake."""
        # Focus on player center
        px = player_rect.x + player_rect.width / 2
        py = player_rect.y + player_rect.height / 2

        # Dynamic target based on screen position
        self.target_x = px - SCREEN_WIDTH / 2
        self.target_y = py - SCREEN_HEIGHT / 2 - 80 # Offset upwards for readability of subterranean tunnels

        # Easing interpolation (Lag)
        # Slow down camera tracking slightly during scanning for a heavy, cinematic feel
        lerp_speed = 0.08 if scan_intensity < 0.1 else 0.04
        self.x += (self.target_x - self.x) * lerp_speed
        self.y += (self.target_y - self.y) * lerp_speed

        # Bound constraints
        self.x = max(0, min(self.x, WORLD_WIDTH - SCREEN_WIDTH))
        self.y = max(-100, min(self.y, SCREEN_HEIGHT)) # Small vertical buffer for vertical sectors

        # Apply screen shake
        if self.shake_intensity > 0.1:
            self.x += random.uniform(-self.shake_intensity, self.shake_intensity)
            self.y += random.uniform(-self.shake_intensity, self.shake_intensity)
            self.shake_intensity *= self.shake_decay

    def trigger_shake(self, amount):
        """Trigger camera trauma."""
        self.shake_intensity = max(self.shake_intensity, amount)

    def apply(self, pos_tuple):
        """Translate a world coordinate into screen coordinate."""
        wx, wy = pos_tuple
        return (int(wx - self.x), int(wy - self.y))
