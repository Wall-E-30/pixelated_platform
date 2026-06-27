# Chronicles of the Forest

*Chronicles of the Forest* is a 2D retro, story-based pixel platformer game built in Python using the **Pygame** library. The game features scrolling parallax backgrounds, hazard traps, enemy slimes with basic AI, and a fluid double-jump physics engine.

---

## 📖 The Prophecy (Story)

Deep within the digital woods, the legendary **Chronicles of the Forest** has been shattered by corrupt, slime-like entities. Physics is beginning to collapse, tiles are floating, and the Forest Realm is in peril. 

As a brave adventurer, you must venture through the perilous terrain, leap across deadly spikes, defeat the guard slimes, and reach the Golden Gates on the far right to recover the Code and restore balance.

---

## 🎮 Controls

| Action | Keyboard Input |
|---|---|
| **Move Left** | Left Arrow key `←` or `A` |
| **Move Right** | Right Arrow key `→` or `D` |
| **Jump / Double Jump** | `Spacebar` |
| **Attack (Melee)** | `X` or `J` |
| **Restart Game** | `R` (only on Game Over / Victory screen) |
| **Return to Menu** | `M` (only on Game Over / Victory screen) |

---

## ✨ Features

- **Fluid Platforming Physics:** Realistic gravity, acceleration, and double-jump capabilities.
- **Parallax Backgrounds:** Deep parallax scrolling backgrounds that move at different rates to create a pseudo-3D depth effect.
- **Combat & Enemies:** Dynamic sword attack mechanics with customized bounding boxes to hit enemies. Enemies have pathing logic and basic attack contact.
- **Hazard Traps:** Floor spikes and fall-off pits that damage the player.
- **Retro HUD (Heads-Up Display):**
  - Glowing pixelated life hearts showing health.
  - Level progress bar calculating the distance to the Golden Gates.
- **State Machine UI Screens:**
  - **Main Menu:** Title screen with visual instructions.
  - **The Prophecy:** Immersive story introduction screen.
  - **Game Over:** Defeat screen with restart controls.
  - **Quest Complete:** Victory screen upon reaching the portal.

---

## 📁 Repository Structure

- `main.py`: Entry point of the game. Initializes Pygame, the screen, and launches the game loop.
- `game.py`: Core game engine that manages game states, processes events, updates camera scroll positioning, resolves collisions, and draws overlay screen boxes and HUDs.
- `level.py`: Level designer setting up coordinates, platform layouts, enemy spawns, and environment decorations.
- `entities.py`: Animating character entities. Houses base `Entity`, `Player`, and `Enemy` (slime) classes containing sheet-slicing logic and state controllers (idle, running, jumping, attacking, taking hit).
- `physics.py`: Physics resolution handler for gravity, vertical fall caps, and horizontal/vertical collision checking against platforms.
- `environment.py`: Renders sprite elements in the world, including solid blocks (grass/dirt tiles) and visual decorations (trees, stumps).
- `assets_manager.py`: Centralized asset loader that reads raw spritesheets, extracts sprites, flips direction frames, and caches textures.
- `scratch/`: Contains utility scripts:
  - `rename_assets.py`: Standardizes cryptic asset filenames.
  - `generate_gallery.py`: Compiles an asset gallery to view all assets in a grid layout (`gallery.html`).

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.8 or higher installed on your system.
- `pip` (Python package manager).

### Running Locally

1. **Navigate to the project root:**
   ```bash
   cd pixelated_platform
   ```

2. **Activate the virtual environment:**
   - **Windows (PowerShell):**
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **Windows (CMD):**
     ```cmd
     .\venv\Scripts\activate.bat
     ```
   - **macOS / Linux:**
     ```bash
     source venv/bin/activate
     ```

3. **Install the dependencies:**
   ```bash
   pip install pygame
   ```

4. **Launch the game:**
   ```bash
   python main.py
   ```