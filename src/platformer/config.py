import os
from pathlib import Path

# Paths
PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
SAVE_FILE = PROJECT_ROOT / "save_data.json"

# Screen & Display
WIDTH = 1080
HEIGHT = 680
FPS = 60
BLOCK_SIZE = 64
TITLE = "Platformer Fun by Miskat"

# Physics Settings
GRAVITY = 0.75
MAX_FALL_SPEED = 14.0
PLAYER_SPEED = 5.5
JUMP_FORCE = 13.0
DOUBLE_JUMP_FORCE = 11.5
TRAMPOLINE_BOUNCE = 19.0
FAN_PUSH = 1.25
COYOTE_TIME = 6
JUMP_BUFFER = 6
INVULN_FRAMES = 90
MAX_HEALTH = 3
INITIAL_LIVES = 3

# Game State Enums
STATE_MENU = "menu"
STATE_CHAR_SELECT = "char_select"
STATE_LEVEL_SELECT = "level_select"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_LEVEL_CLEAR = "level_clear"
STATE_GAME_OVER = "game_over"
STATE_VICTORY = "victory"

# Characters Configuration
CHARACTERS = {
    "VirtualGuy": {
        "name": "Virtual Guy",
        "speed": 5.5,
        "jump": 13.0,
        "desc": "Balanced speed and acrobatic jumps",
        "color": (50, 180, 240)
    },
    "NinjaFrog": {
        "name": "Ninja Frog",
        "speed": 5.7,
        "jump": 13.8,
        "desc": "High leaps and frog agility",
        "color": (80, 220, 80)
    },
    "PinkMan": {
        "name": "Pink Man",
        "speed": 6.2,
        "jump": 12.5,
        "desc": "Swift runner with rapid dashes",
        "color": (255, 105, 180)
    },
    "MaskDude": {
        "name": "Mask Dude",
        "speed": 5.2,
        "jump": 13.0,
        "desc": "Sturdy explorer with longer invulnerability",
        "color": (220, 160, 60)
    }
}

CHARACTER_NAMES = ["VirtualGuy", "NinjaFrog", "PinkMan", "MaskDude"]

# Color Palette
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_BG_DARK = (24, 26, 36)
COLOR_PANEL = (35, 39, 54, 230)
COLOR_ACCENT = (255, 204, 0)
COLOR_GREEN = (76, 209, 55)
COLOR_RED = (235, 77, 75)
COLOR_BLUE = (72, 126, 176)
COLOR_CYAN = (0, 210, 211)
COLOR_PURPLE = (156, 136, 198)
COLOR_TEXT = (245, 246, 250)
COLOR_TEXT_MUTED = (164, 176, 190)
