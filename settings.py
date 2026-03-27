import pygame as pg

WIDTH = 800
HEIGHT = 600
TITLE = "Shadow Heist"
FPS = 60
TILESIZE = 32

# player values
PLAYER_SPEED = 280
PLAYER_HIT_RECT = pg.Rect(0, 0, TILESIZE-5, TILESIZE-5)

# --- color palette (all colors chosen to mesh together) ---
DARK_BG      = (18,  18,  30)   # very dark navy — background
WALL_COLOR   = (52,  58,  94)   # muted indigo — walls
FLOOR_COLOR  = (18,  18,  30)   # same as bg so floor is invisible
PLAYER_COLOR = (100, 220, 180)  # soft teal — player
COIN_COLOR   = (255, 210,  60)  # warm gold — coins
GUARD_COLOR  = (220,  80,  80)  # muted red — guards
TEXT_COLOR   = (220, 220, 240)  # soft white — general text
ACCENT_COLOR = (100, 220, 180)  # teal — highlights/win text
DANGER_COLOR = (220,  80,  80)  # red — game over text

# keep these for legacy references in state files
WHITE  = TEXT_COLOR
RED    = DANGER_COLOR
GREEN  = (80, 200, 120)
YELLOW = COIN_COLOR
BLACK  = (0, 0, 0)
BLUE   = DARK_BG

# guard values
GUARD_SPEED = 80
GUARD_VISION_RANGE = 180
GUARD_FOV_ANGLE = 90
GUARD_HIT_RECT = pg.Rect(0, 0, TILESIZE - 5, TILESIZE - 5)

ORANGE = (255, 140, 0)