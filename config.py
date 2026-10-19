# config.py
"""
Global configurations, asset mappings, and styling parameters
for MyCarbonAI - Visibility Protocol.
"""

# Screen Dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Physics Parameters
GRAVITY = 0.65
WORLD_WIDTH = 3900

# Color Palette (MyCarbonAI Specification)
DEEP_NAVY = (7, 17, 31)         # #07111F
BG_DARK = (10, 22, 40)          # #0A1628
PRIMARY_TEAL = (0, 217, 255)    # #00D9FF
SECONDARY_TEAL = (0, 229, 216)  # #00E5D8
COOL_GREEN = (61, 220, 151)     # #3DDC97
MIST_GRAY = (143, 163, 173)     # #8FA3AD
WARNING_RED = (255, 94, 91)     # #FF5E5B
WHITE = (223, 252, 255)         # #DFFCFF
BLACK = (2, 5, 8)

# HUD Color Codes
GLOW_TEAL = (0, 217, 255, 100)
GLOW_RED = (255, 94, 91, 100)

# Asset Details
ASSET_DIR = "assets"

# Keyboard Controls
# Movement: Left/Right (A/D or Arrows), Jump (W or Space), Dash (Shift)
# Actions: Scan (Hold S), Sync/Connect (Hold E), Title Reset (R), Pause (Escape)

# Text Messages (NORA AI Companion Dialogue)
DIALOGUE_MESSAGES = {
    "intro_level_1": "NORA: Signal Walker. The Water Purification Grid has collapsed. Connect the visible, restore the hidden.",
    "intro_level_2": "NORA: WARNING. Level 2 - Industrial Basin. Massive greenhouse leaks detected. Scan carefully - hazard overload active.",
    "node_restored": "SYS_SYNC: NETWORK NODE RESTORED. Environmental metrics stabilizing.",
    "insufficient_visibility": "ERR: INSUFFICIENT VISIBILITY. Minimum 65% coverage required to override the district gate.",
    "scan_overload": "SYS_WARN: SPECTRAL VISOR SCAN OVERLOAD. Perception buffers cooling down...",
    "anomaly_cleared": "RESOLVED: Methane leak stabilized. Air toxicity reducing.",
    "frag_collected": "LOG: Scope 3 ledger fragment recovered. Environmental history loaded.",
}
