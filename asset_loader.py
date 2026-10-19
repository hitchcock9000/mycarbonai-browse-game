# asset_loader.py
"""
Central Asset Manager for loading, caching, scaling, and managing fallback artwork.
"""

import pygame
import os
import math
from config import ASSET_DIR, PRIMARY_TEAL, SECONDARY_TEAL, COOL_GREEN, WARNING_RED, MIST_GRAY, WHITE, GLOW_TEAL

class AssetLoader:
    def __init__(self):
        self.images = {}
        self.fonts = {}
        
        # Mappings from generic gameplay names to actual filenames in assets/
        self.asset_mapping = {
            'terrain_regen_grass': 'terrain_grass_block',
            'terrain_regen_solar': 'terrain_solar_block',
            'terrain_regen_tree': 'terrain_sprout_block',
            'terrain_regen_water': 'terrain_waterfall_block',
            'terrain_industrial_block': 'terrain_concrete_block',
            'terrain_industrial_cracked': 'terrain_factory_block',
            'terrain_industrial_pipe': 'terrain_pipe_block',
            'terrain_industrial_leak': 'terrain_hazard_pipe',
            
            'object_repair_terminal': 'checkpoint_terminal',
            'object_energy_tower': 'checkpoint_terminal',
            'object_checkpoint_flag': 'checkpoint_flag',
            
            'collect_carbon_node': 'collectible_molecule',
            'collect_biodiversity_seed': 'collectible_heart',
            'collect_audit_fragment': 'collectible_coin',
            'collect_scope3_relic': 'collectible_coin',
            
            'enemy_carbon_slime': 'enemy_slime_small',
            'enemy_data_parasite': 'enemy_slime_mid',
            'enemy_leak_node': 'enemy_slime_smoke'
        }

    def make_opaque(self, surface):
        """Ensure all semi-transparent pixels of the character are fully opaque using standard Pygame PixelArray."""
        surf = surface.copy().convert_alpha()
        # Use PixelArray to lock and modify pixels synchronously
        px = pygame.PixelArray(surf)
        for x in range(surf.get_width()):
            for y in range(surf.get_height()):
                color_int = px[x, y]
                r, g, b, a = surf.unmap_rgb(color_int)
                if a > 8:
                    px[x, y] = surf.map_rgb((r, g, b, 255))
        del px # Safely unlock and force hardware cache synchronization
        return surf

    def load_all(self):
        """Load all assets or generate procedural fallbacks if files are not found."""
        pygame.font.init()
        
        # Load fonts
        font_choices = ["monaco", "menlo", "courier", "consolas", "monospace"]
        available = pygame.font.get_fonts()
        font_name = None
        for choice in font_choices:
            if choice in available:
                font_name = choice
                break
        
        # Font caching
        self.fonts['hud'] = pygame.font.SysFont(font_name, 18, bold=True)
        self.fonts['dialogue'] = pygame.font.SysFont(font_name, 20)
        self.fonts['title'] = pygame.font.SysFont(font_name, 38, bold=True)
        self.fonts['subtitle'] = pygame.font.SysFont(font_name, 22)
        self.fonts['terminal'] = pygame.font.SysFont(font_name, 14)

        # 1. Load correct human Signal Walker assets from assets/visibility/ (and make them opaque!)
        for action in ['signal_idle', 'signal_run', 'signal_jump', 'signal_scan', 'signal_connect']:
            path = os.path.join("assets/visibility", f"{action}.png")
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    img = self.make_opaque(img)
                    self.images[action] = img
                except Exception as e:
                    print(f"Error loading {path}: {e}")
                    self.images[action] = self.generate_fallback(action)
            else:
                self.images[action] = self.generate_fallback(action)

        # 2. Load standard static mapped environment assets from assets/ parent folder
        for game_name, file_name in self.asset_mapping.items():
            path = os.path.join("assets", f"{file_name}.png")
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    self.images[game_name] = img
                except Exception as e:
                    print(f"Error loading {path}: {e}")
                    self.images[game_name] = self.generate_fallback(game_name)
            else:
                self.images[game_name] = self.generate_fallback(game_name)

        # 3. Load other independent sheets (like nora)
        nora_path = os.path.join("assets", "nora_orb.png")
        if os.path.exists(nora_path):
            try:
                self.images["nora_orb"] = pygame.image.load(nora_path).convert_alpha()
            except:
                self.images["nora_orb"] = self.generate_fallback("nora_orb")
        else:
            nora_path_alt = os.path.join("assets/visibility", "nora_orb.png")
            if os.path.exists(nora_path_alt):
                try:
                    self.images["nora_orb"] = pygame.image.load(nora_path_alt).convert_alpha()
                except:
                    self.images["nora_orb"] = self.generate_fallback("nora_orb")
            else:
                self.images["nora_orb"] = self.generate_fallback("nora_orb")

    def get_image(self, name, size=None, flip_x=False, frame=0):
        """Retrieve a cached image, scale it optionally, and flip if requested."""
        if name not in self.images:
            self.images[name] = self.generate_fallback(name)
            
        img = self.images[name]
        
        if size:
            img = pygame.transform.smoothscale(img, size)
            
        if flip_x:
            img = pygame.transform.flip(img, True, False)
            
        return img

    def get_font(self, font_type):
        return self.fonts.get(font_type, pygame.font.SysFont(None, 20))

    def generate_fallback(self, name):
        """Generate high-quality atmospheric fallback graphics procedurally."""
        w, h = 64, 64
        if "terrain" in name:
            w, h = 110, 138
        elif "object" in name:
            w, h = 104, 136
        elif "signal" in name:
            w, h = 72, 122
        elif "nora" in name:
            w, h = 54, 60
        elif "enemy" in name:
            w, h = 72, 92
        elif "collect" in name:
            w, h = 70, 70

        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        
        if "signal" in name:
            pygame.draw.ellipse(surf, (30, 48, 76), (10, 20, 52, 102))  # Suit
            pygame.draw.circle(surf, (20, 32, 50), (36, 18), 16)      # Hood
            pygame.draw.ellipse(surf, PRIMARY_TEAL, (26, 25, 20, 20)) # Visor
            pygame.draw.rect(surf, SECONDARY_TEAL, (32, 50, 8, 30))  # lining
        
        elif "nora_orb" in name:
            center = (w // 2, h // 2)
            pygame.draw.circle(surf, (15, 25, 35), center, 20)
            pygame.draw.circle(surf, PRIMARY_TEAL, center, 14, 2)
            pygame.draw.circle(surf, SECONDARY_TEAL, center, 6)
            pygame.draw.rect(surf, MIST_GRAY, (2, h//2 - 4, 8, 8), border_radius=2)
            pygame.draw.rect(surf, MIST_GRAY, (w - 10, h//2 - 4, 8, 8), border_radius=2)

        elif "enemy" in name:
            color = WARNING_RED if "leak" in name or "slime" in name else MIST_GRAY
            center = (w // 2, h // 2)
            if "slime" in name:
                pygame.draw.ellipse(surf, color, (8, 24, 56, 48))
                pygame.draw.circle(surf, WHITE, (center[0] - 10, center[1] + 2), 4)
                pygame.draw.circle(surf, WHITE, (center[0] + 10, center[1] + 2), 4)
            elif "parasite" in name:
                pygame.draw.rect(surf, color, (12, 12, 48, 68), border_radius=8)
                pygame.draw.line(surf, PRIMARY_TEAL, (16, 24), (56, 56), 3)
            elif "leak_node" in name:
                pygame.draw.circle(surf, (30, 20, 20), center, 28)
                pygame.draw.circle(surf, WARNING_RED, center, 18, 3)
                pygame.draw.circle(surf, WHITE, center, 6)

        elif "terrain_regen" in name:
            color = COOL_GREEN if "grass" in name else (SECONDARY_TEAL if "water" in name else PRIMARY_TEAL)
            pygame.draw.rect(surf, (18, 32, 50), (4, 26, w - 8, h - 26), border_radius=6)
            pygame.draw.rect(surf, color, (4, 26, w - 8, 12))
            if "grass" in name:
                pygame.draw.polygon(surf, COOL_GREEN, [(15, 26), (20, 10), (25, 26)])
                pygame.draw.polygon(surf, COOL_GREEN, [(45, 26), (52, 6), (58, 26)])
            elif "tree" in name:
                pygame.draw.rect(surf, (80, 50, 30), (w//2 - 6, 26, 12, 40))
                pygame.draw.circle(surf, COOL_GREEN, (w//2, 26), 28)
            elif "solar" in name:
                pygame.draw.polygon(surf, PRIMARY_TEAL, [(10, 26), (w//2, 2), (w - 10, 26)])
                pygame.draw.line(surf, WHITE, (w//2, 2), (w//2, 26), 2)
            elif "water" in name:
                pygame.draw.ellipse(surf, WHITE, (10, 20, w - 20, 10), 2)

        elif "terrain_industrial" in name:
            color = WARNING_RED if "leak" in name else (110, 105, 100)
            pygame.draw.rect(surf, (30, 25, 20), (4, 26, w - 8, h - 26), border_radius=4)
            pygame.draw.rect(surf, color, (4, 26, w - 8, 10))
            for i in range(12, w, 24):
                pygame.draw.circle(surf, (60, 50, 45), (i, 40), 3)
            if "pipe" in name:
                pygame.draw.rect(surf, MIST_GRAY, (0, 50, w, 24))
                pygame.draw.rect(surf, (40, 45, 50), (0, 56, w, 12))
            elif "leak" in name:
                pygame.draw.circle(surf, WARNING_RED, (w//2, 50), 10)

        elif "object" in name:
            center_x = w // 2
            pygame.draw.rect(surf, (15, 20, 30), (20, h - 30, w - 40, 30), border_radius=4)
            pygame.draw.rect(surf, MIST_GRAY, (center_x - 6, 40, 12, h - 70))
            if "terminal" in name or "tower" in name:
                color = COOL_GREEN if "terminal" in name else PRIMARY_TEAL
                pygame.draw.rect(surf, (20, 30, 45), (center_x - 30, 10, 60, 36), border_radius=6)
                pygame.draw.rect(surf, color, (center_x - 22, 16, 44, 24))
                pygame.draw.circle(surf, WHITE, (center_x, 0), 8)
            elif "flag" in name:
                pygame.draw.polygon(surf, COOL_GREEN, [(center_x, 10), (w - 10, 25), (center_x, 40)])

        elif "collect" in name:
            color = PRIMARY_TEAL if "carbon" in name else (COOL_GREEN if "biodiversity" in name else SECONDARY_TEAL)
            center = (w // 2, h // 2)
            pygame.draw.circle(surf, color, center, 20, 2)
            pygame.draw.circle(surf, WHITE, center, 10)
            if "seed" in name:
                pygame.draw.polygon(surf, COOL_GREEN, [(center[0], center[1] - 8), (center[0] - 6, center[1] + 4), (center[0] + 6, center[1] + 4)])
            elif "carbon" in name:
                pygame.draw.rect(surf, PRIMARY_TEAL, (center[0] - 6, center[1] - 6, 12, 12), border_radius=2)
            else:
                pygame.draw.line(surf, WHITE, (center[0] - 8, center[1]), (center[0] + 8, center[1]), 2)
                pygame.draw.line(surf, WHITE, (center[0], center[1] - 8), (center[0], center[1] + 8), 2)

        return surf

# Global static instance
asset_loader = AssetLoader()
