# systems/particle_system.py
"""
High-fidelity atmospheric particle engine handling rain, carbon smoke, leaves, and holographic overlays.
"""

import random
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COOL_GREEN, PRIMARY_TEAL, WARNING_RED, WHITE, MIST_GRAY

class Particle:
    def __init__(self, x, y, vx, vy, radius, color, life, decay, type_name="generic"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.color = color
        self.life = life          # Float: 1.0 down to 0.0
        self.decay = decay        # Rate of reduction
        self.type_name = type_name
        self.angle = random.uniform(0, 360)
        self.spin = random.uniform(-4, 4)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= self.decay * dt
        self.angle += self.spin * dt
        
        # Behavior tweaks by particle type
        if self.type_name == "steam":
            self.radius += 0.2 * dt  # Expanding fog
            self.vx += random.uniform(-0.1, 0.1) * dt
        elif self.type_name == "rain":
            # Fast downwards pull
            self.vy += 0.15 * dt

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def update(self, dt):
        """Update and filter out dead particles."""
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]

    def draw(self, surface, camera):
        """Render all particles with appropriate blending."""
        for p in self.particles:
            screen_x, screen_y = camera.apply((p.x, p.y))
            
            # Skip drawing if offscreen
            if not (-50 < screen_x < SCREEN_WIDTH + 50 and -50 < screen_y < SCREEN_HEIGHT + 50):
                continue
                
            alpha = int(max(0, min(255, p.life * 255)))
            
            if p.type_name == "rain":
                # Draw sharp diagonal lines
                end_x = screen_x - p.vx * 1.5
                end_y = screen_y - p.vy * 1.5
                
                # Fast draw line
                color = (p.color[0], p.color[1], p.color[2])
                line_surf = pygame.Surface((abs(end_x - screen_x) + 1, abs(end_y - screen_y) + 1), pygame.SRCALPHA)
                pygame.draw.line(line_surf, (*color, alpha), (0, 0), (abs(end_x - screen_x), abs(end_y - screen_y)), 1)
                surface.blit(line_surf, (min(screen_x, end_x), min(screen_y, end_y)))
                
            elif p.type_name == "leaf":
                # Draw rotating organic pixel shapes
                leaf_surf = pygame.Surface((int(p.radius * 2) + 2, int(p.radius * 2) + 2), pygame.SRCALPHA)
                # Draw diamond-leaf structure
                pygame.draw.polygon(leaf_surf, (*p.color, alpha), [
                    (p.radius, 0),
                    (p.radius * 2, p.radius),
                    (p.radius, p.radius * 2),
                    (0, p.radius)
                ])
                # Rotate leaf
                rotated = pygame.transform.rotate(leaf_surf, p.angle)
                rect = rotated.get_rect(center=(screen_x, screen_y))
                surface.blit(rotated, rect.topleft)
                
            else:
                # Standard soft glow circles
                circle_surf = pygame.Surface((int(p.radius * 2) + 2, int(p.radius * 2) + 2), pygame.SRCALPHA)
                pygame.draw.circle(circle_surf, (*p.color, alpha), (p.radius, p.radius), p.radius)
                surface.blit(circle_surf, (screen_x - p.radius, screen_y - p.radius))

    def emit_burst(self, x, y, color, count, type_name="generic"):
        """Spawn a cluster of explosive particles."""
        for _ in range(count):
            angle = random.uniform(0, 2 * 3.14159)
            speed = random.uniform(2, 6)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 1.5 # Slight upward bias
            radius = random.randint(2, 6) if type_name != "leaf" else random.randint(4, 8)
            life = random.uniform(0.6, 1.0)
            decay = random.uniform(0.015, 0.035)
            
            self.particles.append(Particle(x, y, vx, vy, radius, color, life, decay, type_name))

    def emit_rain(self, camera_x, count=2):
        """Continually populate background precipitation."""
        for _ in range(count):
            # Spawn slightly wider than viewport to cover panning
            x = random.uniform(camera_x - 100, camera_x + SCREEN_WIDTH + 300)
            y = -50
            vx = -3.5 - random.uniform(0, 1.5) # Diagonal wind
            vy = 12 + random.uniform(0, 4)      # Fast downward
            radius = random.uniform(1.5, 3)
            life = 1.0
            decay = 0.01
            color = PRIMARY_TEAL
            self.particles.append(Particle(x, y, vx, vy, radius, color, life, decay, "rain"))

    def emit_steam(self, x, y, count=1):
        """Populate drifting steam vent graphics."""
        for _ in range(count):
            vx = random.uniform(-0.6, 0.6)
            vy = -random.uniform(1.2, 2.5)
            radius = random.randint(4, 9)
            life = random.uniform(0.7, 1.0)
            decay = random.uniform(0.01, 0.02)
            # Translucent grey/blue
            color = MIST_GRAY
            self.particles.append(Particle(x, y, vx, vy, radius, color, life, decay, "steam"))

    def emit_smoke(self, x, y, count=1):
        """Populate toxic carbon clouds rising from unresolved leak nodes."""
        for _ in range(count):
            vx = random.uniform(-1.0, 1.0)
            vy = -random.uniform(1.0, 3.0)
            radius = random.randint(5, 12)
            life = random.uniform(0.6, 0.9)
            decay = random.uniform(0.01, 0.02)
            # Toxic red-orange smoke
            color = WARNING_RED
            self.particles.append(Particle(x, y, vx, vy, radius, color, life, decay, "steam"))

import math
