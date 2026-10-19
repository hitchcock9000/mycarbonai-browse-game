# MyCarbonAI — Visibility Protocol
## Complete 2D Cinematic Climate-Tech Prototype

> "See different. Connect deeper. Restore tomorrow."

Welcome to the **Visibility Protocol**, a playable 2D cinematic platform-exploration game prototype built for the **MyCarbonAI Universe**. 

You are a **Signal Walker** exploring the disconnected, subterranean pipelines and industrial zones beneath a towering futuristic megacity. Pair-programmed with your companion AI drone **NORA**, you do not carry weapons — instead, **your perception is your interface for planetary restoration**.

---

## 🎮 CORE GAMEPLAY MECHANICS

01. **Kinematic Platform Movement**: Enjoy smooth acceleration-based controls with horizontal slides, dynamic thruster-climbing thrusters, double jumps, and high-velocity neon dashes.
02. **The Perception Visor (Scan Mode - S)**: Hold `S` to desaturate the environment and dim ambient visibility, activating a custom diagnostic climate overlay. It reveals glowing underground purification pipelines, thermal emission zones, locking frames for anomalies, and node telemetry indices. Activating the Visor also slows down local timeline clocks by up to 50%, enabling precise investigative actions.
03. **Systems Synchronization (Sync Node - E)**: Discover inactive infrastructure nodes (Water relays, Renewable grid towers, and Carbon filters). Stand near them and hold `E` to pull a glowing green connection tether from NORA and yourself to the node. Once connection thresholds reach 100%, the biome dynamically transforms: surrounding industrial blocks within 460 pixels turn into lush grass and clean water canals, neon lights spark to life, leaves burst into the air, and local greenhouse gases vanish!
04. **Invisible Operational Chaos**: Encounter environmental anomalies (Carbon Slimes, Data Parasites, and Leak Nodes). In normal vision, these elements appear as faint, hazardous shadows that trigger system damage and screen trauma upon collision. Holding `S` locking-on to them reveals their diagnostic markers — scanning them directly at high intensity immediately stabilizes and resolutes them into pure light restoration particles.
05. **Diagnostic Climate HUD**: Experience a polished operating system interface modeled after clinical ESG observability frames. Monitor [VISIBILITY_COVERAGE] (Minimum 65% required to proceed past the District Exit Bridge), [ECOSYSTEM_INTEGRITY], [GREENHOUSE_EMISSIONS], and [VISOR_OVERLOAD] (Level 2 thermal hot-zones).
06. **Procedural Synthesizer Audio**: To ensure immediate out-of-the-box immersion without needing external asset files, the game synthesizes custom PCM waveforms (Sine, Triangle, and Square wave buffers) in-memory! It features beautiful low-frequency looping ambient chord backdrops, scan visor hums, thruster jumps, static error damage crunches, and musical C-Major arpeggios when collecting data fragments and synching towers.

---

## 📂 PROJECT DIRECTORY ARCHITECTURE

The prototype uses a modular, professional 2D game structure designed for seamless expansion into future episodes:

```
game-mycarbonai/
├── main.py                 # Game entry bootloader, initializes mixer, display, and ticking clocks
├── config.py               # Central configuration, brand palette, dialogue scripts, and boundaries
├── asset_loader.py         # Caching asset manager with robust high-quality procedural fallbacks
├── audio.py                # Procedural waveform synthesizer & loop channel controller
├── scene_manager.py        # Central scene routing and dark fade transitions
├── ui.py                   # Custom text drawing and hud overlays (integrated into scenes)
├── requirements.txt        # Core engine dependencies (Pygame)
├── README.md               # Systems documentation and manual (this file)
├── entities/
│   ├── __init__.py
│   ├── player.py           # Kinetic player physics, dash states, visor parameters
│   ├── drone.py            # Floating NORA companion with spring follow and hologram beams
│   ├── node.py             # Restoration towers with connection arcs and terrain triggers
│   ├── collectible.py      # Ledger fragment files with hovering floating formulas
│   └── anomaly.py          # Patrol hazards with transparency-blended perception layers
└── systems/
    ├── __init__.py
    ├── camera.py           # Cinematic tracking camera with vertical lags and directional trauma shake
    └── particle_system.py  # Atmospheric engine handling precipitation, steam, flurries, and rings
```

---

## 🚀 INSTALLATION & LAUNCH INSTRUCTIONS

### Prerequisites
- Python 3.8 or higher installed on your system.
- Standard terminal access.

### 01. Install Dependencies
Install the required Pygame framework using pip:
```bash
pip install -r requirements.txt
```

### 02. Launch the Protocol
Execute the main bootloader:
```bash
python main.py
```

---

## ⌨️ KEYBOARD MANUAL

| Key Input | Action | Game Context |
| :--- | :--- | :--- |
| **A / D** or **Left / Right** | Horizontal movement | Smooth kinematic walking |
| **W** or **Spacebar** | Thruster Jump | Launch into air. Press twice for thruster double-jump. |
| **LSHIFT** or **RSHIFT** | Kinetic Dash | Execute a horizontal dash, resetting thruster counters. |
| **S** (Hold) | Perception Visor | Scan the sector, slowing down time and revealing hidden paths. |
| **E** (Hold) | Reconnect Node | Stand near disconnected structures to synchronize network lines. |
| **Escape** | Pause Menu | Suspend current protocol state, adjust sound mixers, or exit. |
| **R** | Quick Restart | Instantly reboot current sector grid. |
| **SPACE** / **ENTER** | Confirm Actions | Proceed through menus, diagnostics, and ending screens. |

---

## 🌎 BRAND VISUAL LANGUAGE CONSISTENCY

This prototype incorporates exact details matching the **MyCarbonAI Universe Spec**:
- **Thin Cyan HUD interfaces**: Border crosshairs, monospace data telemetries, and progress tickers.
- **Speculative Worldbuilding**: Transition from the toxic soot-grey environment of the Disconnected District and Industrial Basin into a glowing, clean-energy solarpunk interface.
- **Narrative Philosophy**: Replaces combat mechanics with exploration, visibility systems mapping, and environmental intelligence calibration.

---
*Visibility is the UI for survival. Restoring systems. Code calibrating.*
