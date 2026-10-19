# scenes/title_scene.py
"""
Interactive climate observatory terminal main title scene.
"""

import pygame
import math
import random
from scenes.base_scene import BaseScene
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BG_DARK, PRIMARY_TEAL, SECONDARY_TEAL, COOL_GREEN, WHITE, WARNING_RED, MIST_GRAY
from asset_loader import asset_loader
from audio import audio_system
from entities.drone import CompanionDrone
from systems.particle_system import ParticleSystem
from systems.camera import Camera

class TitleScene(BaseScene):
    def __init__(self, manager):
        super().__init__(manager)
        
        # Companion AI drone in Title
        self.drone = CompanionDrone(SCREEN_WIDTH // 2 - 27, SCREEN_HEIGHT // 2 - 80)
        self.particles = ParticleSystem()
        self.camera = Camera()
        
        class FakePlayer:
            def __init__(self):
                self.x = SCREEN_WIDTH // 2 - 36
                self.y = SCREEN_HEIGHT // 2 - 60
                self.w = 72
                self.h = 122
                self.dir = 1
                self.is_scanning = True
                self.is_connecting = False
                
        self.fake_player = FakePlayer()
        
        # Title animations
        self.tick = 0
        self.selected_level = 1
        self.show_prompt_flicker = True
        
        # Diagnostic terminal lines
        self.terminal_logs = [
            "SYS_BOOT: MyCarbonAI Perception Visor v1.0",
            "SYS_LOG : Initializing planetary intelligence feeds...",
            "SYS_LOG : Hydrological networks: OFFLINE",
            "SYS_LOG : Carbon ledger fragments: DISCONNECTED",
            "SYS_WARN: ESG greenwashing locks detected in high-rises.",
            "SYS_CMD : Awaiting Signal Walker connection..."
        ]
        self.log_reveal_tick = 0
        self.revealed_logs_count = 1

    def update(self, dt):
        self.tick += 1 * dt
        
        # Hover Prompt flickering
        if int(self.tick / 24) % 2 == 0:
            self.show_prompt_flicker = True
        else:
            self.show_prompt_flicker = False

        # Update logs reveal
        self.log_reveal_tick += 1 * dt
        if self.log_reveal_tick >= 15 and self.revealed_logs_count < len(self.terminal_logs):
            self.revealed_logs_count += 1
            self.log_reveal_tick = 0

        self.drone.update(self.fake_player, dt, self.particles)
        self.particles.update(dt)
        self.particles.emit_rain(0, 1)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                # Trigger game start
                audio_system.play("sync_connect")
                from scenes.game_scene import GameScene
                game_scene = GameScene(self.manager, self.selected_level)
                self.manager.transition_to(game_scene)
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                if self.selected_level > 1:
                    self.selected_level = 1
                    audio_system.play("collect")
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                if self.selected_level < 2:
                    self.selected_level = 2
                    audio_system.play("collect")

    def draw(self, surface):
        # Draw deep dark grid backdrop
        surface.fill(BG_DARK)
        
        # Grid overlays
        grid_alpha = int(24 + math.sin(self.tick * 0.05) * 8)
        grid_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for x in range(0, SCREEN_WIDTH, 60):
            pygame.draw.line(grid_surf, (*PRIMARY_TEAL, grid_alpha), (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 60):
            pygame.draw.line(grid_surf, (*PRIMARY_TEAL, grid_alpha), (0, y), (SCREEN_WIDTH, y), 1)
        surface.blit(grid_surf, (0, 0))

        # Render floating background particles
        self.particles.draw(surface, self.camera)

        # Draw NORA drone in the center
        self.drone.draw(surface, self.camera, self.fake_player)

        # UI Diagnostic Elements
        title_font = asset_loader.get_font("title")
        sub_font = asset_loader.get_font("subtitle")
        term_font = asset_loader.get_font("terminal")
        hud_font = asset_loader.get_font("hud")

        # 01 - Header Brand Logo
        logo_lbl = title_font.render("MyCarbonAI", True, WHITE)
        brand_lbl = hud_font.render("VISIBILITY IS THE UI FOR SURVIVAL", True, PRIMARY_TEAL)
        surface.blit(logo_lbl, (SCREEN_WIDTH // 2 - logo_lbl.get_width() // 2, 80))
        surface.blit(brand_lbl, (SCREEN_WIDTH // 2 - brand_lbl.get_width() // 2, 125))

        # 02 - Diagnostic logs panel (Left side)
        log_panel = pygame.Surface((360, 200), pygame.SRCALPHA)
        pygame.draw.rect(log_panel, (7, 17, 31, 140), (0, 0, 360, 200), border_radius=6)
        pygame.draw.rect(log_panel, PRIMARY_TEAL, (0, 0, 360, 200), 1, border_radius=6)
        # Title of terminal box
        hdr = term_font.render("COGNITIVE TERMINAL FEEDS:", True, PRIMARY_TEAL)
        log_panel.blit(hdr, (15, 12))
        
        for idx in range(self.revealed_logs_count):
            line = self.terminal_logs[idx]
            color = WARNING_RED if "WARN" in line else (COOL_GREEN if "BOOT" in line else WHITE)
            txt = term_font.render(line, True, color)
            log_panel.blit(txt, (15, 36 + idx * 24))
            
        surface.blit(log_panel, (60, SCREEN_HEIGHT // 2 - 100))

        # 03 - Game Instructions panel (Right side)
        instr_panel = pygame.Surface((360, 200), pygame.SRCALPHA)
        pygame.draw.rect(instr_panel, (7, 17, 31, 140), (0, 0, 360, 200), border_radius=6)
        pygame.draw.rect(instr_panel, PRIMARY_TEAL, (0, 0, 360, 200), 1, border_radius=6)
        hdr2 = term_font.render("WALKER OPERATIONAL MANUAL:", True, PRIMARY_TEAL)
        instr_panel.blit(hdr2, (15, 12))
        
        controls = [
            "A / D or Arrow Keys  : Smooth Walk",
            "W or Spacebar        : Thruster Jump",
            "Double Tap Jump      : Fungal Leaf Rise",
            "LSHIFT / RSHIFT      : Kinetic Dash Boost",
            "Hold S (Perception)  : Scan Hidden Systems",
            "Hold E (Interaction) : Reconnect Nodes"
        ]
        for idx, ctrl in enumerate(controls):
            txt = term_font.render(ctrl, True, WHITE)
            instr_panel.blit(txt, (15, 36 + idx * 24))
            
        surface.blit(instr_panel, (SCREEN_WIDTH - 420, SCREEN_HEIGHT // 2 - 100))

        # 04 - Level Selection Interface (Center bottom)
        level_y = SCREEN_HEIGHT - 220
        lbl1_col = COOL_GREEN if self.selected_level == 1 else MIST_GRAY
        lbl2_col = WARNING_RED if self.selected_level == 2 else MIST_GRAY
        
        lvl1_lbl = sub_font.render("LEVEL 1: THE DISCONNECTED CANALS", True, lbl1_col)
        lvl2_lbl = sub_font.render("LEVEL 2: INDUSTRIAL EMISSIONS BASIN", True, lbl2_col)
        
        # Center them in bottom slots
        surface.blit(lvl1_lbl, (SCREEN_WIDTH // 2 - lvl1_lbl.get_width() - 30, level_y))
        surface.blit(lvl2_lbl, (SCREEN_WIDTH // 2 + 30, level_y))
        
        # Selection highlight box
        box_w = lvl1_lbl.get_width() + 20 if self.selected_level == 1 else lvl2_lbl.get_width() + 20
        box_x = SCREEN_WIDTH // 2 - lvl1_lbl.get_width() - 40 if self.selected_level == 1 else SCREEN_WIDTH // 2 + 20
        pygame.draw.rect(surface, PRIMARY_TEAL, (box_x, level_y - 6, box_w, 36), 1, border_radius=4)
        
        nav_lbl = term_font.render("< Press Left/Right Arrow to switch starting biomes >", True, SECONDARY_TEAL)
        surface.blit(nav_lbl, (SCREEN_WIDTH // 2 - nav_lbl.get_width() // 2, level_y + 44))

        # 05 - Press SPACE prompt
        if self.show_prompt_flicker:
            prompt_lbl = sub_font.render("PRESS SPACEBAR TO COMMENCE SIGNAL WALK", True, PRIMARY_TEAL)
            surface.blit(prompt_lbl, (SCREEN_WIDTH // 2 - prompt_lbl.get_width() // 2, SCREEN_HEIGHT - 90))
            
        # Draw soft vignettes
        vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for r in range(400, 900, 50):
            alpha = int((r - 400) / 500 * 120)
            pygame.draw.circle(vignette, (0, 0, 0, alpha), (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), r, 50)
        surface.blit(vignette, (0, 0))
