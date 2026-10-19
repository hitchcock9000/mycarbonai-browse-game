# scenes/game_scene.py
"""
Core gameplay scene. Supports Level 1 (Disconnected District) and Level 2 (Industrial Basin).
Implements parallax layers, scanning visor states, terrain transformations, anomalies, and diagnostic overlays.
"""

import pygame
import math
import random
from scenes.base_scene import BaseScene
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH,
    BG_DARK, PRIMARY_TEAL, SECONDARY_TEAL, COOL_GREEN, WARNING_RED, WHITE, GLOW_TEAL, GLOW_RED, MIST_GRAY,
    DIALOGUE_MESSAGES
)
from asset_loader import asset_loader
from audio import audio_system
from entities.player import Player
from entities.drone import CompanionDrone
from entities.anomaly import EnvironmentalAnomaly
from entities.node import RestorationNode
from entities.collectible import CollectibleItem
from systems.camera import Camera
from systems.particle_system import ParticleSystem

class GameScene(BaseScene):
    def __init__(self, manager, level_num=1):
        super().__init__(manager)
        
        self.current_level = level_num
        self.paused = False
        self.game_over = False
        self.victory = False
        self.pause_selection = 0
        
        # Diagnostics
        self.visibility = 0.0      # Goal: Reach 65% visibility to open exit
        self.ecosystem = 42.0 if level_num == 1 else 30.0
        self.energy = 18.0 if level_num == 1 else 10.0
        self.emissions = 88.0 if level_num == 1 else 72.0
        
        # Systems
        self.player = Player(110, 430)
        self.drone = CompanionDrone(110, 350)
        self.camera = Camera()
        self.particles = ParticleSystem()
        
        # Dialogue system
        self.dialogue_text = ""
        self.dialogue_target = ""
        self.dialogue_timer = 0
        self.dialogue_char_idx = 0
        
        self.load_level(self.current_level)
        audio_system.start_ambient()

    def load_level(self, level_num):
        """Build entities, platforms, anomalies, and triggers for Level 1 or 2."""
        self.current_level = level_num
        self.player.x = 110
        self.player.y = 430
        self.player.vx = 0
        self.player.vy = 0
        self.player.grounded = False
        
        # Level Dialogue Trigger
        msg_key = "intro_level_1" if level_num == 1 else "intro_level_2"
        self.trigger_dialogue(DIALOGUE_MESSAGES[msg_key])

        # Platforms configuration
        if level_num == 1:
            self.platforms = [
                {'x': 0, 'y': 612, 'w': 480, 'h': 94, 'img': 'terrain_regen_grass', 'clean': True},
                {'x': 480, 'y': 612, 'w': 420, 'h': 94, 'img': 'terrain_industrial_cracked', 'clean': False},
                {'x': 900, 'y': 612, 'w': 420, 'h': 94, 'img': 'terrain_industrial_pipe', 'clean': False},
                {'x': 1320, 'y': 612, 'w': 460, 'h': 94, 'img': 'terrain_regen_solar', 'clean': True},
                {'x': 1780, 'y': 612, 'w': 420, 'h': 94, 'img': 'terrain_industrial_block', 'clean': False},
                {'x': 2200, 'y': 612, 'w': 430, 'h': 94, 'img': 'terrain_industrial_leak', 'clean': False},
                {'x': 2630, 'y': 612, 'w': 480, 'h': 94, 'img': 'terrain_regen_water', 'clean': True},
                {'x': 3110, 'y': 612, 'w': 790, 'h': 94, 'img': 'terrain_regen_tree', 'clean': True},
                # High solar ledge
                {'x': 760, 'y': 456, 'w': 170, 'h': 44, 'img': 'terrain_regen_solar', 'clean': True},
                {'x': 1510, 'y': 405, 'w': 160, 'h': 44, 'img': 'terrain_industrial_cracked', 'clean': False},
                {'x': 1685, 'y': 350, 'w': 160, 'h': 44, 'img': 'terrain_industrial_pipe', 'clean': False},
                {'x': 2455, 'y': 430, 'w': 160, 'h': 44, 'img': 'terrain_regen_water', 'clean': True}
            ]
            
            # Restoration nodes
            self.nodes = [
                RestorationNode(410, 612, 'transport', 'Transport Node', 14, 5, 7, -8, 'object_repair_terminal'),
                RestorationNode(1245, 612, 'grid', 'Renewable Grid Tower', 18, 7, 22, -14, 'object_energy_tower'),
                RestorationNode(2105, 612, 'water', 'Water Purification Relay', 16, 14, 6, -12, 'object_repair_terminal'),
                RestorationNode(2970, 612, 'biodiversity', 'Biodiversity Network', 17, 18, 5, -10, 'object_energy_tower')
            ]
            
            # Collectibles
            self.collectibles = [
                CollectibleItem(670, 510, 'collect_audit_fragment', 'Audit Ledger v04', 5),
                CollectibleItem(860, 350, 'collect_scope3_relic', 'Scope 3 Certificate', 8),
                CollectibleItem(1430, 515, 'collect_carbon_node', 'Carbon Sink Ledger', 7),
                CollectibleItem(1725, 255, 'collect_biodiversity_seed', 'Oak Spore Seed', 7),
                CollectibleItem(2495, 330, 'collect_scope3_relic', 'Scope 3 Certificate', 8),
                CollectibleItem(2825, 510, 'collect_biodiversity_seed', 'Fern Follicle Seed', 7),
                CollectibleItem(3275, 510, 'collect_carbon_node', 'Carbon Sink Ledger', 7)
            ]
            
            # Anomalies (Perception hazards)
            self.anomalies = [
                EnvironmentalAnomaly(610, 520, 72, 92, 'enemy_carbon_slime', 1.0, 560, 790, 'untracked emissions'),
                EnvironmentalAnomaly(1020, 520, 72, 92, 'enemy_data_parasite', 1.3, 950, 1180, 'disconnected system'),
                EnvironmentalAnomaly(1910, 520, 72, 92, 'enemy_leak_node', 0.8, 1840, 2110, 'methane leak'),
                EnvironmentalAnomaly(2360, 520, 72, 92, 'enemy_carbon_slime', 1.4, 2280, 2540, 'emissions bloom'),
                EnvironmentalAnomaly(2860, 520, 72, 92, 'enemy_data_parasite', 1.1, 2780, 3020, 'data parasite')
            ]
            
            self.emission_flows = []
            self.unstable_zones = []

        else: # Level 2: Industrial Basin
            self.platforms = [
                {'x': 0, 'y': 612, 'w': 480, 'h': 94, 'img': 'terrain_industrial_block', 'clean': False},
                {'x': 480, 'y': 612, 'w': 420, 'h': 94, 'img': 'terrain_industrial_cracked', 'clean': False},
                {'x': 900, 'y': 612, 'w': 420, 'h': 94, 'img': 'terrain_industrial_pipe', 'clean': False},
                {'x': 1320, 'y': 612, 'w': 460, 'h': 94, 'img': 'terrain_industrial_block', 'clean': False},
                {'x': 1780, 'y': 612, 'w': 420, 'h': 94, 'img': 'terrain_industrial_leak', 'clean': False},
                {'x': 2200, 'y': 612, 'w': 430, 'h': 94, 'img': 'terrain_industrial_pipe', 'clean': False},
                {'x': 2630, 'y': 612, 'w': 480, 'h': 94, 'img': 'terrain_industrial_cracked', 'clean': False},
                {'x': 3110, 'y': 612, 'w': 790, 'h': 94, 'img': 'terrain_industrial_block', 'clean': False},
                # High ledges
                {'x': 760, 'y': 456, 'w': 170, 'h': 44, 'img': 'terrain_industrial_cracked', 'clean': False},
                {'x': 1510, 'y': 405, 'w': 160, 'h': 44, 'img': 'terrain_industrial_pipe', 'clean': False},
                {'x': 1685, 'y': 350, 'w': 160, 'h': 44, 'img': 'terrain_industrial_leak', 'clean': False},
                {'x': 2455, 'y': 430, 'w': 160, 'h': 44, 'img': 'terrain_industrial_cracked', 'clean': False}
            ]
            
            self.nodes = [
                RestorationNode(410, 612, 'relay', 'Carbon Relay Tower', 16, 5, 10, -15, 'object_energy_tower'),
                RestorationNode(1245, 612, 'filter', 'Emissions Filter Relay', 15, 8, 5, -20, 'object_repair_terminal'),
                RestorationNode(2105, 612, 'grid', 'Industrial Grid Node', 18, 5, 15, -12, 'object_energy_tower'),
                RestorationNode(2970, 612, 'core', 'Purification Core Tower', 16, 12, 10, -15, 'object_repair_terminal')
            ]
            
            self.collectibles = [
                CollectibleItem(670, 510, 'collect_audit_fragment', 'Audit Ledger v08', 5),
                CollectibleItem(860, 350, 'collect_scope3_relic', 'Scope 3 Certificate', 8),
                CollectibleItem(1430, 515, 'collect_carbon_node', 'Carbon Sink Ledger', 7),
                CollectibleItem(1725, 255, 'collect_audit_fragment', 'Scope 2 Log', 7),
                CollectibleItem(2495, 330, 'collect_scope3_relic', 'Scope 3 Certificate', 8),
                CollectibleItem(2825, 510, 'collect_audit_fragment', 'Scope 1 Log', 7),
                CollectibleItem(3275, 510, 'collect_carbon_node', 'Carbon Sink Ledger', 7)
            ]
            
            self.anomalies = [
                EnvironmentalAnomaly(610, 520, 72, 92, 'enemy_data_parasite', 1.4, 560, 790, 'data parasite'),
                EnvironmentalAnomaly(1020, 520, 72, 92, 'enemy_leak_node', 0.9, 950, 1180, 'methane leak'),
                EnvironmentalAnomaly(1910, 520, 72, 92, 'enemy_data_parasite', 1.5, 1840, 2110, 'data parasite'),
                EnvironmentalAnomaly(2360, 520, 72, 92, 'enemy_leak_node', 1.0, 2280, 2540, 'methane leak'),
                EnvironmentalAnomaly(2860, 520, 72, 92, 'enemy_data_parasite', 1.2, 2780, 3020, 'data parasite')
            ]
            
            # Level 2 organic flow lines revealed under scan
            self.emission_flows = [
                {'x1': 410, 'y1': 560, 'x2': 1245, 'y2': 560},
                {'x1': 1245, 'y1': 560, 'x2': 2105, 'y2': 560},
                {'x1': 2105, 'y1': 560, 'x2': 2970, 'y2': 560},
                {'x1': 900, 'y1': 400, 'x2': 1245, 'y2': 560},
                {'x1': 1780, 'y1': 300, 'x2': 2105, 'y2': 560},
                {'x1': 2630, 'y1': 450, 'x2': 2970, 'y2': 560}
            ]
            
            # Unstable Visor Overload Areas
            self.unstable_zones = [
                {'x': 800, 'y': 480, 'r': 200},
                {'x': 1600, 'y': 480, 'r': 250},
                {'x': 2800, 'y': 480, 'r': 200}
            ]

    def trigger_dialogue(self, message):
        """Start a typing narrative message."""
        self.dialogue_target = message
        self.dialogue_text = ""
        self.dialogue_char_idx = 0
        self.dialogue_timer = 280 # dialogue duration

    def update(self, dt):
        if self.paused or self.game_over or self.victory:
            return

        # 01 - Update Systems
        self.camera.update(self.player.get_rect(), self.player.scan_intensity)
        self.particles.update(dt)
        
        # Continuous atmospheric steam and rain
        self.particles.emit_rain(self.camera.x, 1)
        
        # Steam vent nodes
        for plat in self.platforms:
            if "leak" in plat['img'] and not plat['clean'] and random.random() < 0.08 * dt:
                self.particles.emit_smoke(plat['x'] + plat['w']//2, plat['y'] - 10, 1)

        # 02 - Update Entities
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys, self.current_level == 2)
        
        # Scanning Overload mechanics (Level 2 thermal vents)
        if self.current_level == 2 and self.player.is_scanning:
            px = self.player.x + self.player.w // 2
            py = self.player.y + self.player.h // 2
            in_hotzone = False
            for zone in self.unstable_zones:
                if math.hypot(px - zone['x'], py - zone['y']) < zone['r']:
                    in_hotzone = True
                    break
            if in_hotzone:
                self.player.scan_overload = min(1.0, self.player.scan_overload + 0.02 * dt)
                if self.player.scan_overload >= 0.95:
                    self.player.is_scanning = False
                    self.player.scan_intensity = 0.0
                    self.trigger_dialogue(DIALOGUE_MESSAGES["scan_overload"])
                    self.camera.trigger_shake(12.0)
                    audio_system.play("damage")
            else:
                self.player.scan_overload = max(0.0, self.player.scan_overload - 0.015 * dt)
        else:
            self.player.scan_overload = max(0.0, self.player.scan_overload - 0.025 * dt)

        # Update Player physics
        self.player.update(dt, self.platforms, self.current_level == 2, self.particles)
        
        # Update Drone
        self.drone.update(self.player, dt, self.particles)

        # Check death from pitfall
        if self.player.y > SCREEN_HEIGHT + 80:
            dmg = self.player.damage(15, self.particles, fall=True)
            self.emissions = min(100.0, self.emissions + dmg)
            self.ecosystem = max(0.0, self.ecosystem - dmg * 0.4)
            self.camera.trigger_shake(10.0)

        # 03 - Update Nodes and interaction progress
        restored_count = sum(1 for n in self.nodes if n.restored)
        
        for node in self.nodes:
            node.update(dt)
            dist = math.hypot((self.player.x + self.player.w//2) - node.x, (self.player.y + self.player.h//2) - (node.y - node.h//2))
            
            if dist < 120 and self.player.is_connecting and not node.restored:
                node.connection_progress = min(1.0, node.connection_progress + 0.02 * dt)
                
                # Active scan loop sound hum
                if int(self.player.anim_tick) % 15 == 0:
                    audio_system.play("scan_active")
                
                # Restoration threshold complete
                if node.connection_progress >= 0.99:
                    node.restored = True
                    self.drone.trigger_emotion("happy")
                    audio_system.play("sync_connect")
                    self.camera.trigger_shake(15.0)
                    
                    # Update parameters
                    self.visibility = min(100.0, self.visibility + node.val_visibility)
                    self.ecosystem = min(100.0, self.ecosystem + node.val_ecosystem)
                    self.energy = min(100.0, self.energy + node.val_energy)
                    self.emissions = max(0.0, self.emissions + node.val_emissions)
                    
                    # Spawn lush restored visual leaves
                    self.particles.emit_burst(node.x, node.y - 40, COOL_GREEN, 24, "leaf")
                    self.trigger_dialogue(DIALOGUE_MESSAGES["node_restored"])
                    
                    # Transform surrounding tiles
                    self.restore_nearby_terrain(node.x)
            elif not self.player.is_connecting and not node.restored:
                node.connection_progress = max(0.0, node.connection_progress - 0.04 * dt)

        # 04 - Update Collectibles
        for item in self.collectibles:
            if not item.done:
                item.update(dt)
                player_rect = self.player.get_rect()
                item_rect = item.get_rect()
                
                if player_rect.colliderect(item_rect):
                    item.done = True
                    audio_system.play("collect")
                    self.particles.emit_burst(item.x, item.y, SECONDARY_TEAL, 12, "leaf")
                    
                    # Metric additions
                    self.visibility = min(100.0, self.visibility + item.value)
                    self.ecosystem = min(100.0, self.ecosystem + (4.0 if "seed" in item.img_name else 1.5))
                    self.emissions = max(0.0, self.emissions - (3.5 if "carbon" in item.img_name else 1.0))
                    
                    self.trigger_dialogue(DIALOGUE_MESSAGES["frag_collected"])

        # 05 - Update Patrol Anomalies
        for anomaly in self.anomalies:
            if anomaly.resolved:
                continue
                
            anomaly.update(dt)
            player_rect = self.player.get_rect()
            anomaly_rect = anomaly.get_rect()
            
            if player_rect.colliderect(anomaly_rect):
                # If Walker is actively scanning AND scanner intensity is high, resolve/vaporize it!
                if self.player.is_scanning and self.player.scan_intensity > 0.65:
                    anomaly.resolved = True
                    audio_system.play("collect")
                    self.particles.emit_burst(anomaly.x + anomaly.w//2, anomaly.y + anomaly.h//2, PRIMARY_TEAL, 18, "leaf")
                    
                    # Restore metrics
                    self.visibility = min(100.0, self.visibility + 4.5)
                    self.emissions = max(0.0, self.emissions - 7.0)
                    self.trigger_dialogue(DIALOGUE_MESSAGES["anomaly_cleared"])
                else:
                    # Damage player
                    dmg = self.player.damage(8, self.particles)
                    self.emissions = min(100.0, self.emissions + dmg)
                    self.ecosystem = max(0.0, self.ecosystem - dmg * 0.5)
                    self.camera.trigger_shake(8.0)
                    
        self.anomalies = [a for a in self.anomalies if not a.resolved]

        # 06 - Dialogue ticker
        if self.dialogue_timer > 0:
            self.dialogue_timer -= 1 * dt
            if self.dialogue_char_idx < len(self.dialogue_target):
                self.dialogue_char_idx = min(len(self.dialogue_target), self.dialogue_char_idx + 1)
                self.dialogue_text = self.dialogue_target[:int(self.dialogue_char_idx)]

        # 07 - Core metric decays & Game states
        # Emissions rise slightly based on unresolved anomalies
        self.emissions = min(100.0, self.emissions + 0.003 * len(self.anomalies) * dt)
        self.ecosystem = max(0.0, self.ecosystem - 0.002 * len(self.anomalies) * dt)
        
        if self.emissions >= 99.9 or self.ecosystem <= 0.1:
            self.game_over = True
            audio_system.stop_ambient()
            audio_system.play("damage")
            
        # Check level completion bridge (exit gate at 3500px)
        if self.player.x > 3500:
            if self.visibility >= 65.0:
                if self.current_level == 1:
                    # Proceed to Level 2
                    self.current_level = 2
                    self.load_level(2)
                    audio_system.play("sync_connect")
                else:
                    # Final Victory
                    self.victory = True
                    audio_system.stop_ambient()
                    audio_system.play("sync_connect")
            else:
                self.player.x = 3480
                self.player.vx = -3.0
                self.trigger_dialogue(DIALOGUE_MESSAGES["insufficient_visibility"])
                audio_system.play("damage")

    def restore_nearby_terrain(self, center_x):
        """Heal surrounding platform blocks within 460 pixels."""
        for plat in self.platforms:
            plat_center = plat['x'] + plat['w'] // 2
            if abs(plat_center - center_x) < 460:
                plat['clean'] = True
                if "industrial" in plat['img']:
                    # Transform graphics style
                    if self.current_level == 2:
                        plat['img'] = "terrain_regen_water"
                    else:
                        plat['img'] = "terrain_regen_water" if center_x > 2000 else "terrain_regen_grass"

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.paused:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.pause_selection = (self.pause_selection - 1) % 4
                    audio_system.play("collect")
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.pause_selection = (self.pause_selection + 1) % 4
                    audio_system.play("collect")
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    self.trigger_pause_action()
                elif event.key == pygame.K_ESCAPE:
                    self.paused = False
                    audio_system.play("collect")
            elif self.game_over or self.victory:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    # Restart Game Scene
                    audio_system.play("sync_connect")
                    self.manager.transition_to(GameScene(self.manager, self.current_level))
                elif event.key == pygame.K_ESCAPE:
                    audio_system.play("collect")
                    from scenes.title_scene import TitleScene
                    self.manager.transition_to(TitleScene(self.manager))
            else:
                if event.key == pygame.K_ESCAPE:
                    self.paused = True
                    self.pause_selection = 0
                    audio_system.play("collect")
                elif event.key == pygame.K_SPACE or event.key == pygame.K_UP or event.key == pygame.K_w:
                    # Jump triggers
                    self.player.jump(self.particles)
                elif event.key == pygame.K_r:
                    # Quick Reload level
                    audio_system.play("sync_connect")
                    self.manager.transition_to(GameScene(self.manager, self.current_level))

    def trigger_pause_action(self):
        audio_system.play("sync_connect")
        if self.pause_selection == 0:
            self.paused = False
        elif self.pause_selection == 1:
            self.manager.transition_to(GameScene(self.manager, self.current_level))
        elif self.pause_selection == 2:
            audio_system.stop_ambient()
            from scenes.title_scene import TitleScene
            self.manager.transition_to(TitleScene(self.manager))
        elif self.pause_selection == 3:
            audio_system.enabled = not audio_system.enabled
            if not audio_system.enabled:
                pygame.mixer.quit()
            else:
                audio_system.init_mixer()
                audio_system.start_ambient()

    def draw(self, surface):
        # Draw sky gradient (darker and orange tinted in Level 2)
        sky_grad = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.current_level == 2:
            c1, c2 = (3, 10, 15), (6, 13, 24)
        else:
            c1, c2 = (7, 17, 31), (3, 16, 25)
            
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(c1[0] + (c2[0] - c1[0]) * ratio)
            g = int(c1[1] + (c2[1] - c1[1]) * ratio)
            b = int(c1[2] + (c2[2] - c1[2]) * ratio)
            pygame.draw.line(sky_grad, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        surface.blit(sky_grad, (0, 0))

        # 01 - Parallax Backdrops Silhouette Layers (3 Layers)
        # Far layer (Mountains / mega building towers) - moves at 15% speed
        for i in range(-2, 10):
            bx = int(i * 320 - self.camera.x * 0.15)
            by = SCREEN_HEIGHT - 380
            # Draw simple tech tower polygon
            pygame.draw.rect(surface, (14, 25, 42, 60), (bx, by, 120, 380))
            pygame.draw.rect(surface, PRIMARY_TEAL if self.current_level == 1 else WARNING_RED, (bx + 40, by - 6, 40, 6))

        # Mid layer (Wind turbines / power hubs) - moves at 32% speed
        for i in range(-2, 12):
            bx = int(i * 240 - self.camera.x * 0.32)
            by = SCREEN_HEIGHT - 290
            pygame.draw.rect(surface, (18, 30, 48, 100), (bx, by, 70, 290))
            if i % 3 == 0:
                # Wind turbines blade loops
                center = (bx + 35, by)
                angle = (pygame.time.get_ticks() * 0.001) + i
                pygame.draw.line(surface, MIST_GRAY, center, (center[0] - 8, center[1] + 160), 2) # tower shaft
                for a in [0, 2 * math.pi / 3, 4 * math.pi / 3]:
                    bx2 = center[0] + math.cos(angle + a) * 36
                    by2 = center[1] + math.sin(angle + a) * 36
                    pygame.draw.line(surface, WHITE, center, (bx2, by2), 2)

        # 02 - Grid Observer Overlay (pulses brightly when scanning)
        grid_alpha = int(12 + self.player.scan_intensity * 32)
        grid_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        camera_offset_x = -int(self.camera.x) % 80
        for x in range(camera_offset_x, SCREEN_WIDTH, 80):
            pygame.draw.line(grid_surf, (*PRIMARY_TEAL, grid_alpha), (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 80):
            pygame.draw.line(grid_surf, (*PRIMARY_TEAL, grid_alpha), (0, y), (SCREEN_WIDTH, y), 1)
        surface.blit(grid_surf, (0, 0))

        # Draw volumetric lighting shadows
        # Dim/desaturate the baseline world when scanning
        if self.player.scan_intensity > 0.02:
            dim_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            dim_surf.fill((3, 7, 12, int(self.player.scan_intensity * 120)))
            surface.blit(dim_surf, (0, 0))

        # 03 - Game Entities rendering
        # Terrain blocks
        for plat in self.platforms:
            screen_x, screen_y = self.camera.apply((plat['x'], plat['y']))
            # Draw repeats to bridge large widths
            repeats = plat['w'] // 110
            img = asset_loader.get_image(plat['img'], (110, 138))
            for i in range(repeats):
                surface.blit(img, (screen_x + i * 110, screen_y - 26))

        # Draw objective nodes
        for node in self.nodes:
            node.draw(surface, self.camera, self.player)

        # Draw Collectibles
        for item in self.collectibles:
            item.draw(surface, self.camera)

        # Draw Anomaly Shadows
        for anomaly in self.anomalies:
            anomaly.draw(surface, self.camera, self.player.scan_intensity)

        # Draw Exit Gate (Bridge)
        gate_x, gate_y = self.camera.apply((3560, 500))
        gate_img = asset_loader.get_image("object_checkpoint_flag", (112, 96))
        surface.blit(gate_img, (gate_x, gate_y))
        
        # Color bar indicator at exit
        color = COOL_GREEN if self.visibility >= 65.0 else WARNING_RED
        bar_surf = pygame.Surface((260, 10), pygame.SRCALPHA)
        bar_surf.fill((*color, 140))
        surface.blit(bar_surf, (gate_x - 70, gate_y + 102))

        # Draw companion NORA
        self.drone.draw(surface, self.camera, self.player)

        # Draw Player Walker
        self.player.draw(surface, self.camera)

        # Render particles
        self.particles.draw(surface, self.camera)

        # 04 - Draw Spectral Overlay features (Hidden pipelines and diagnostics)
        if self.player.scan_intensity > 0.05:
            self.draw_spectral_overlay(surface)

        # 05 - Draw Climate OS HUD
        self.draw_hud(surface)

        # 06 - Game Screens Overlay (Pause, Game Over, Ending)
        if self.paused:
            self.draw_pause_screen(surface)
        elif self.game_over:
            self.draw_end_screen(surface, "SYSTEM COLLAPSE", "Visibility failed before restoration could stabilize the ecosystem.")
        elif self.victory:
            self.draw_end_screen(surface, "PLANETARY SYNC STABLE", "Visibility reached standard thresholds. The planetary intelligence can now govern the biome.")

    def draw_spectral_overlay(self, surface):
        """Highlight hidden energy grid connections, leaks, and locked coordinates."""
        scan_alpha = int(self.player.scan_intensity * 120)
        overlay_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Render connecting grid lines for Level 2 leaks
        if self.current_level == 2:
            for flow in self.emission_flows:
                p1 = self.camera.apply((flow['x1'], flow['y1']))
                p2 = self.camera.apply((flow['x2'], flow['y2']))
                # Draw thick red dashboard flow
                pygame.draw.line(overlay_surf, (*WARNING_RED, scan_alpha), p1, p2, 3)
                # Render marching dashes to indicate flow velocity
                flow_offset = int((pygame.time.get_ticks() * 0.1) % 40)
                dx = p2[0] - p1[0]
                dy = p2[1] - p1[1]
                length = math.hypot(dx, dy)
                if length > 0:
                    ux = dx / length
                    uy = dy / length
                    for d in range(flow_offset, int(length), 40):
                        cx = p1[0] + ux * d
                        cy = p1[1] + uy * d
                        pygame.draw.circle(overlay_surf, WHITE, (int(cx), int(cy)), 3)

            # Draw unstable perception areas
            for zone in self.unstable_zones:
                zx, zy = self.camera.apply((zone['x'], zone['y']))
                r = zone['r']
                # Alert zone red rings
                pygame.draw.circle(overlay_surf, (*WARNING_RED, scan_alpha // 2), (zx, zy), r, 2)
                lbl_font = asset_loader.get_font("terminal")
                alert_lbl = lbl_font.render("!!! CRITICAL ANOMALY STRESS PLUME !!!", True, WARNING_RED)
                overlay_surf.blit(alert_lbl, (zx - alert_lbl.get_width()//2, zy - 10))

        # Reconnect tethers from NORA during sync E
        if self.player.connect_pulse > 0.05:
            cx, cy = self.camera.apply((self.player.x + self.player.w//2, self.player.y + self.player.h//2))
            conn_alpha = int(self.player.connect_pulse * 180)
            for node in self.nodes:
                if not node.restored and abs((self.player.x + self.player.w//2) - node.x) < 160:
                    np = self.camera.apply((node.x, node.y - node.h//2))
                    pygame.draw.line(overlay_surf, (*COOL_GREEN, conn_alpha), (cx, cy), np, 3)
                    # Connection beam energy rings
                    pygame.draw.circle(overlay_surf, WHITE, ((cx + np[0])//2, (cy + np[1])//2), 8, 1)

        surface.blit(overlay_surf, (0, 0))

        # Invoke individual entity overlays
        for node in self.nodes:
            node.draw_telemetry(surface, self.camera, self.player.scan_intensity)
        for item in self.collectibles:
            item.draw_telemetry(surface, self.camera, self.player.scan_intensity)
        for anomaly in self.anomalies:
            anomaly.draw_telemetry(surface, self.camera, self.player.scan_intensity)

    def draw_hud(self, surface):
        """Draw diagnostic observer borders and climate OS panels."""
        hud_color = PRIMARY_TEAL
        hud_font = asset_loader.get_font("hud")
        term_font = asset_loader.get_font("terminal")
        
        # Draw tech frame borders
        pygame.draw.rect(surface, hud_color, (15, 15, SCREEN_WIDTH - 30, SCREEN_HEIGHT - 30), 1)
        # Tech crosshairs
        pygame.draw.line(surface, hud_color, (10, 15), (20, 15), 3)
        pygame.draw.line(surface, hud_color, (15, 10), (15, 20), 3)
        pygame.draw.line(surface, hud_color, (SCREEN_WIDTH - 20, 15), (SCREEN_WIDTH - 10, 15), 3)
        pygame.draw.line(surface, hud_color, (SCREEN_WIDTH - 15, 10), (SCREEN_WIDTH - 15, 20), 3)

        # 01 - Header Statistics Info
        lvl_name = "LEVEL 01 : THE DISCONNECTED DISTRICT" if self.current_level == 1 else "LEVEL 02 : INDUSTRIAL BASIN REFRACTORY"
        lbl_level = term_font.render(f"SYS_LOG // {lvl_name}", True, hud_color)
        surface.blit(lbl_level, (30, 25))

        # Restored nodes percentage
        restored = sum(1 for n in self.nodes if n.restored)
        lbl_nodes = term_font.render(f"[NODES_SYNCED]: {restored} / {len(self.nodes)}", True, MIST_GRAY)
        surface.blit(lbl_nodes, (30, 42))

        # 02 - Diagonal Observability bars
        # Visibility Sync bar (must be >65% to complete)
        bar_w = 200
        vis_color = COOL_GREEN if self.visibility >= 65.0 else WHITE
        pygame.draw.rect(surface, (20, 30, 45, 120), (30, 64, bar_w, 14))
        pygame.draw.rect(surface, vis_color, (30, 64, int(bar_w * (self.visibility / 100)), 14))
        pygame.draw.rect(surface, hud_color, (30, 64, bar_w, 14), 1)
        lbl_vis = term_font.render(f"[VISIBILITY_COVERAGE]: {int(self.visibility)}% / 65%", True, vis_color)
        surface.blit(lbl_vis, (30, 82))

        # Ecosystem integrity
        eco_x = 300
        pygame.draw.rect(surface, (20, 30, 45, 120), (eco_x, 64, bar_w, 14))
        pygame.draw.rect(surface, COOL_GREEN, (eco_x, 64, int(bar_w * (self.ecosystem / 100)), 14))
        pygame.draw.rect(surface, hud_color, (eco_x, 64, bar_w, 14), 1)
        lbl_eco = term_font.render(f"[ECOSYSTEM_INTEGRITY]: {int(self.ecosystem)}%", True, COOL_GREEN)
        surface.blit(lbl_eco, (eco_x, 82))

        # Greenhouse emissions
        ems_x = 570
        pygame.draw.rect(surface, (20, 30, 45, 120), (ems_x, 64, bar_w, 14))
        pygame.draw.rect(surface, WARNING_RED, (ems_x, 64, int(bar_w * (self.emissions / 100)), 14))
        pygame.draw.rect(surface, hud_color, (ems_x, 64, bar_w, 14), 1)
        lbl_ems = term_font.render(f"[GREENHOUSE_EMISSIONS]: {int(self.emissions)}%", True, WARNING_RED)
        surface.blit(lbl_ems, (ems_x, 82))

        # Draw scan visor overload gauge (Level 2 thermal vents)
        if self.current_level == 2:
            ovr_x = 840
            pygame.draw.rect(surface, (20, 30, 45, 120), (ovr_x, 64, bar_w, 14))
            pygame.draw.rect(surface, WARNING_RED if self.player.scan_overload > 0.6 else SECONDARY_TEAL, (ovr_x, 64, int(bar_w * self.player.scan_overload), 14))
            pygame.draw.rect(surface, hud_color, (ovr_x, 64, bar_w, 14), 1)
            lbl_ovr = term_font.render(f"[VISOR_OVERLOAD]: {int(self.player.scan_overload * 100)}%", True, WARNING_RED if self.player.scan_overload > 0.6 else SECONDARY_TEAL)
            surface.blit(lbl_ovr, (ovr_x, 82))

        # 03 - NORA dialogue ticker (Center bottom screen)
        if self.dialogue_timer > 0:
            panel_w, panel_h = 600, 60
            px = SCREEN_WIDTH // 2 - panel_w // 2
            py = SCREEN_HEIGHT - 95
            
            # Obsidian tech frame
            pygame.draw.rect(surface, (3, 10, 17, 210), (px, py, panel_w, panel_h), border_radius=6)
            pygame.draw.rect(surface, PRIMARY_TEAL, (px, py, panel_w, panel_h), 1, border_radius=6)
            
            # Print typewritten characters
            txt_surf = term_font.render(self.dialogue_text, True, WHITE)
            surface.blit(txt_surf, (px + 20, py + panel_h // 2 - txt_surf.get_height() // 2))

    def draw_pause_screen(self, surface):
        """Draw translucent pause dialog menu."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((7, 17, 31, 200))
        surface.blit(overlay, (0, 0))

        font_t = asset_loader.get_font("title")
        font_s = asset_loader.get_font("subtitle")

        hdr = font_t.render("WALK SYSTEM SUSPENDED", True, PRIMARY_TEAL)
        surface.blit(hdr, (SCREEN_WIDTH//2 - hdr.get_width()//2, SCREEN_HEIGHT//2 - 120))

        options = [
            "Resume Protocol",
            "Restart Level",
            "Abort to Title Screen",
            f"Sound System: {'ENABLED' if audio_system.enabled else 'DISABLED'}"
        ]

        for idx, opt in enumerate(options):
            color = COOL_GREEN if idx == self.pause_selection else WHITE
            opt_lbl = font_s.render(opt, True, color)
            x = SCREEN_WIDTH//2 - opt_lbl.get_width()//2
            y = SCREEN_HEIGHT//2 - 30 + idx * 45
            surface.blit(opt_lbl, (x, y))
            
            # Draw selector arrow
            if idx == self.pause_selection:
                pygame.draw.polygon(surface, COOL_GREEN, [(x - 20, y + 8), (x - 10, y + 14), (x - 20, y + 20)])

    def draw_end_screen(self, surface, title, description):
        """Draw final death or victory overlays."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        # Warning red overlay for death, cool green for victory
        color = WARNING_RED if self.game_over else COOL_GREEN
        overlay.fill((7, 17, 31, 230))
        surface.blit(overlay, (0, 0))

        font_t = asset_loader.get_font("title")
        font_s = asset_loader.get_font("subtitle")
        font_h = asset_loader.get_font("hud")

        hdr = font_t.render(title, True, color)
        desc = font_s.render(description, True, WHITE)
        
        surface.blit(hdr, (SCREEN_WIDTH//2 - hdr.get_width()//2, SCREEN_HEIGHT//2 - 90))
        surface.blit(desc, (SCREEN_WIDTH//2 - desc.get_width()//2, SCREEN_HEIGHT//2 - 30))

        prompt_txt = "PRESS SPACEBAR TO COMMENCE BIOME RESTORATION" if self.game_over else "CONGRATULATIONS. BIOME SYNCHRONIZATION ACHIEVED."
        prompt = font_h.render(prompt_txt, True, PRIMARY_TEAL)
        surface.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, SCREEN_HEIGHT//2 + 40))
        
        quit_txt = "Press ESC to return to main diagnostic panel."
        quit_lbl = font_h.render(quit_txt, True, MIST_GRAY)
        surface.blit(quit_lbl, (SCREEN_WIDTH//2 - quit_lbl.get_width()//2, SCREEN_HEIGHT//2 + 80))
