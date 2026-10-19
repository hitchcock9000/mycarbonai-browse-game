# entities/player.py
"""
Signal Walker Player Controller. Handles physics, jump mechanics, dash, scan states,
and interaction links.
"""

import pygame
import math
import random
from config import GRAVITY, WORLD_WIDTH, PRIMARY_TEAL, SECONDARY_TEAL, COOL_GREEN, WARNING_RED, WHITE
from asset_loader import asset_loader
from audio import audio_system

class Player:
    def __init__(self, x, y):
        # Dimensions
        self.w = 72
        self.h = 122
        
        # Position & Velocity
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        
        # Movement specs
        self.speed = 5.2
        self.accel = 0.65
        self.friction = 0.82
        self.jump_force = -14.8
        
        # States
        self.grounded = False
        self.dir = 1                 # 1 = Right, -1 = Left
        self.invuln_timer = 0        # Invulnerability period after damage
        self.action = "idle"         # idle, run, jump, scan, connect, dash
        
        # Dash mechanic
        self.dash_timer = 0
        self.dash_cooldown = 0
        self.dash_duration = 10      # frames of dashing
        self.can_dash = True
        self.double_jump_used = False

        # Scan Visor and Connect values
        self.is_scanning = False
        self.is_connecting = False
        self.scan_intensity = 0.0    # 0.0 to 1.0
        self.connect_pulse = 0.0     # 0.0 to 1.0
        self.scan_overload = 0.0     # 0.0 to 1.0 (Level 2 mechanic)

        # Animation parameters
        self.anim_tick = 0
        self.anim_frame = 0

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def handle_input(self, keys, is_level_2):
        """Translate keyboard states into player impulses and actions."""
        # Force clear inputs and damp velocity if window is not focused
        if not pygame.key.get_focused():
            self.is_scanning = False
            self.is_connecting = False
            self.vx *= self.friction
            if abs(self.vx) < 0.1:
                self.vx = 0
            self.action = "idle"
            return

        # Check primary key mappings
        left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        
        # Dash activator (Shift)
        dash = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        # Special Actions
        self.is_scanning = keys[pygame.K_s]
        self.is_connecting = keys[pygame.K_e]

        # Reset states
        if self.is_connecting:
            self.action = "connect"
        elif self.is_scanning:
            self.action = "scan"
        elif self.dash_timer > 0:
            self.action = "dash"
        elif not self.grounded:
            self.action = "jump"
        elif abs(self.vx) > 0.3:
            self.action = "run"
        else:
            self.action = "idle"

        # Scanning calculations
        if self.is_scanning:
            # Dampen movement speeds during scanning for heavy visor feel
            speed_multiplier = 0.35
            self.scan_intensity = min(1.0, self.scan_intensity + 0.08)
        else:
            speed_multiplier = 1.0
            self.scan_intensity = max(0.0, self.scan_intensity - 0.12)

        # Synchronize connection pulse
        if self.is_connecting:
            self.connect_pulse = min(1.0, self.connect_pulse + 0.06)
        else:
            self.connect_pulse = max(0.0, self.connect_pulse - 0.1)

        # Skip horizontal controls during active dash
        if self.dash_timer > 0:
            return

        # Horizontal Acceleration
        if left:
            self.vx = max(-self.speed * speed_multiplier, self.vx - self.accel)
            self.dir = -1
        elif right:
            self.vx = min(self.speed * speed_multiplier, self.vx + self.accel)
            self.dir = 1
        else:
            self.vx *= self.friction # Slide damping
            if abs(self.vx) < 0.1:
                self.vx = 0

        # Jump control processed inside the game loop scene event listener to prevent multi-triggering
        # Dash control
        if dash and self.can_dash and self.dash_cooldown == 0:
            self.dash_timer = self.dash_duration
            self.dash_cooldown = 45 # Frames cooldown
            self.can_dash = False
            self.vx = self.dir * 14.0 # High velocity boost
            self.vy = 0
            audio_system.play("jump")

    def jump(self, particles):
        """Execute a clean vertical jump pulse."""
        if self.grounded:
            self.vy = self.jump_force
            self.grounded = False
            self.double_jump_used = False
            audio_system.play("jump")
            # Burst dust particles at feet
            particles.emit_burst(self.x + self.w // 2, self.y + self.h, SECONDARY_TEAL, 8)
        elif not self.double_jump_used:
            # Double jump (Climate Thruster Burst)
            self.vy = self.jump_force * 0.85
            self.double_jump_used = True
            audio_system.play("jump")
            particles.emit_burst(self.x + self.w // 2, self.y + self.h, PRIMARY_TEAL, 12, "leaf")

    def update(self, dt, platforms, is_level_2, particles):
        """Resolve movement physics, frame animations, and collisions."""
        # Timers
        if self.invuln_timer > 0:
            self.invuln_timer -= 1 * dt

        if self.dash_timer > 0:
            self.dash_timer -= 1 * dt
            # Spawn dash echo trails
            if random.random() < 0.4:
                from systems.particle_system import Particle
                particles.particles.append(
                    Particle(self.x + self.w // 2, self.y + self.h // 2, -self.dir * 2.0, 0, 10, SECONDARY_TEAL, 0.8, 0.08, "generic")
                )
            if self.dash_timer <= 0:
                self.vx = self.dir * self.speed # Return to normal speed

        if self.dash_cooldown > 0:
            self.dash_cooldown = max(0, self.dash_cooldown - 1 * dt)

        # Time dilation during scanning (up to 55% slowdown)
        time_dilation = 1.0 - (self.scan_intensity * 0.5)
        scaled_dt = dt * time_dilation

        # Apply Gravity
        if not self.grounded and self.dash_timer <= 0:
            self.vy += GRAVITY * scaled_dt

        # Apply Movement
        self.x += self.vx * scaled_dt
        self.y += self.vy * scaled_dt

        # Boundary constraints
        self.x = max(0, min(self.x, WORLD_WIDTH - self.w))

        # Check platform collisions
        self.grounded = False
        player_rect = self.get_rect()
        
        for plat in platforms:
            # Collision boundaries
            plat_rect = pygame.Rect(plat['x'], plat['y'], plat['w'], plat['h'])
            if player_rect.colliderect(plat_rect):
                # Resolve landing from top
                # Require that player bottom is near platform top, and travelling downwards
                if self.vy >= 0 and (self.y + self.h - self.vy * scaled_dt) <= plat['y'] + 15:
                    self.y = plat['y'] - self.h
                    self.vy = 0
                    self.grounded = True
                    self.can_dash = True
                    self.double_jump_used = False

        # Level 2 scan visor overload mechanics
        if is_level_2 and self.is_scanning:
            # Overload rises if walking near thermal leaks / emission flow lines
            # Checked in the level scene manager
            pass
        else:
            self.scan_overload = max(0.0, self.scan_overload - 0.02 * dt)

        # Animation Ticker
        self.anim_tick += 1 * scaled_dt
        if self.anim_tick >= 6:
            self.anim_tick = 0
            self.anim_frame = (self.anim_frame + 1) % 6

    def damage(self, amount, particles, fall=False):
        """Trigger walker damage/disruption feedback."""
        if self.invuln_timer > 0:
            return 0 # Shielded
            
        self.invuln_timer = 90 # 1.5s invulnerable
        self.vy = -7.5          # Knockback jump
        self.vx = -self.dir * 4.5
        audio_system.play("damage")
        
        # Red shock flare
        particles.emit_burst(self.x + self.w // 2, self.y + self.h // 2, WARNING_RED, 20)
        
        if fall:
            # Respawn back up
            self.x = max(100, self.x - 250)
            self.y = 200
            self.vx = 0
            self.vy = 0
            
        return amount

    def draw(self, surface, camera):
        """Render the animated player sprite with glowing climate telemetry details."""
        rect = self.get_rect()
        screen_x, screen_y = camera.apply((rect.x, rect.y))

        # Select sprite frame
        # Frames: signal_idle, signal_run, signal_jump, signal_scan, signal_connect
        sprite_name = f"signal_{self.action}"
        if self.action == "dash":
            sprite_name = "signal_run" # Reuse run sprites for dash with styling
            
        # Get Pygame Surface
        # Use 1-indexed sprites or generic caching
        try:
            img = asset_loader.get_image(sprite_name, (self.w + 32, self.h + 20), flip_x=(self.dir < 0), frame=self.anim_frame)
        except:
            img = asset_loader.get_image("signal_idle", (self.w, self.h), flip_x=(self.dir < 0), frame=self.anim_frame)

        # Calculate bounding box of the non-transparent pixels to center it perfectly!
        bound_rect = img.get_bounding_rect()
        if bound_rect.width > 0 and bound_rect.height > 0:
            # Align the center of the visible pixels with the center of the physics box
            offset_x = (self.w // 2) - (bound_rect.x + bound_rect.width // 2)
            # Align the bottom of the visible pixels with the bottom of the physics box
            offset_y = self.h - (bound_rect.y + bound_rect.height)
            
            # Flash if invulnerable
            if self.invuln_timer > 0 and int(pygame.time.get_ticks() / 80) % 2 == 0:
                pass
            else:
                surface.blit(img, (screen_x + offset_x, screen_y + offset_y))
        else:
            # Flash if invulnerable
            if self.invuln_timer > 0 and int(pygame.time.get_ticks() / 80) % 2 == 0:
                # Skip drawing this frame to simulate flickering shield
                pass
            else:
                # Draw offset slightly for tech bag/cloak visual expansion
                surface.blit(img, (screen_x - 16, screen_y - 12))

        # Draw diagnostic HUD lines attached to player when scanning
        if self.scan_intensity > 0.2:
            alpha = int(self.scan_intensity * 180)
            glow_surf = pygame.Surface((self.w + 40, self.h + 40), pygame.SRCALPHA)
            
            # Telemetry box
            box_color = (*PRIMARY_TEAL, alpha)
            pygame.draw.rect(glow_surf, box_color, (10, 10, self.w + 20, self.h + 20), 1, border_radius=4)
            # Reticle corners
            pygame.draw.line(glow_surf, box_color, (5, 5), (15, 5), 2)
            pygame.draw.line(glow_surf, box_color, (5, 5), (5, 15), 2)
            pygame.draw.line(glow_surf, box_color, (self.w + 35, 5), (self.w + 25, 5), 2)
            pygame.draw.line(glow_surf, box_color, (self.w + 35, 5), (self.w + 35, 15), 2)
            
            surface.blit(glow_surf, (screen_x - 20, screen_y - 20))
