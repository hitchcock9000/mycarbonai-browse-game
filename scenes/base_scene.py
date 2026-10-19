# scenes/base_scene.py
"""
Base Scene interface.
"""

class BaseScene:
    def __init__(self, manager):
        self.manager = manager

    def update(self, dt):
        pass

    def handle_event(self, event):
        pass

    def draw(self, surface):
        pass
