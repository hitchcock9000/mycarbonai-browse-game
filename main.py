# main.py
"""
MyCarbonAI - Visibility Protocol
Game Entry Point. Initialises system resources, bootloaders, and starts the gameplay clock.
"""

import sys
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, DEEP_NAVY
from asset_loader import asset_loader
from audio import audio_system
from scene_manager import SceneManager
from scenes.title_scene import TitleScene

def main():
    # Initialize Core Pygame modules
    pygame.init()
    pygame.mixer.init()
    
    # Establish window framework
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("MyCarbonAI — Visibility Protocol")

    # Load procedural sound systems
    # Synthesises sine and square waveforms on startup
    audio_system.init_mixer()

    # Load asset pipelines
    # Auto-extracts details and caches fallbacks for missing structures
    asset_loader.load_all()

    # Create Scene Router
    # Pushes Walker title menu to start
    manager = SceneManager()
    title_scene = TitleScene(manager)
    manager.set_scene(title_scene)

    # Frame clock
    clock = pygame.time.Clock()
    running = True

    while running:
        # System event listener
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                # Delegate events to active scenes
                manager.handle_event(event)

        # Update Scene Manager (Frame step updates)
        # Dynamic Delta-Time calculations
        dt = clock.tick(FPS) / 16.666 # Normalized dt (1.0 = 60 FPS baseline)
        
        # Upper clamp to prevent massive leaps on hiccups
        dt = min(2.5, dt)
        
        manager.update(dt)

        # Draw framework
        screen.fill(DEEP_NAVY)
        manager.draw(screen)
        
        pygame.display.flip()

    # Graceful shutdown
    audio_system.stop_ambient()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted by user, shutting down...")
    finally:
        try:
            pygame.quit()
        except Exception:
            pass
        sys.exit(0)
