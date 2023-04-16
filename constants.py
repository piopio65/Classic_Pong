import pygame as pg
import math
from enum import Enum

class GameState(Enum):

    pause       = 0
    run         = 1
    gameover    = 2


class Level(Enum):
    '''
                    p0: la vitesse de la balle  (ratio)
                    p1: la hauteur des raquettes (ratio)
                    p2: la vitesse des raquettes (ratio)
    '''
    novice      = (0.7,1.5,0.85)
    easy        = (0.8,1.25,0.9)
    normal      = (1,1,1)
    hard        = (1.3,0.9,1.2)
    impossible  = (1.5,0.7,1.4)


# CONFIG FILE
CFG_FILE        = 'pong.cfg'
REMARKS         = ('#','--',"'","//")
SEP             = '='

# SCREEN
FPS = 60
SCR_W = 1024
SCR_H = 768
SPC_Y = 10
# Default Title
TITLE = 'Classic Pong'


# KEYS 
P1_UP           = pg.K_a
P1_DOWN         = pg.K_q
P2_UP           = pg.K_UP
P2_DOWN         = pg.K_DOWN
PAUSE           = pg.K_SPACE


# DEFAULT KEYS
DEFAULT_P1_UP   = 'K_a'
DEFAULT_P1_DOWN = 'K_q'
DEFAULT_P2_UP   = 'K_UP'
DEFAULT_P2_DOWN = 'K_DOWN'

# DEFAULT LEVEL
DEFAULT_LEVEL = Level.normal

# Default With Borders
BORDERLESS  = False
# COLORS
C_BLACK     = (0x00,0x00,0x00,0xFF)
C_WHITE     = (0xFF,0xFF,0xFF,0xFF)
C_GREY      = (0x89,0x89,0x89,0xFF)
C_DARKGREY  = (0x62,0x62,0x62,0xFF)
C_LIGHTGREY = (0xAD,0xAD,0xAD,0xFF)

# BALL
BALL_W          = 8
BALL_H          = 8
BALL_X          = (SCR_W - BALL_W) / 2
BALL_Y          = (SCR_H - BALL_H) / 2
BALL_MAX_ANGLE  = 46

# ANGLES
MIN_ANGLE_RAD = math.pi/180
TRIG_ANGLE_START = math.sqrt(2)/2 # 45 degrés
ANGLE_RANDOM_RANGE = 10.0


# RAQUETTES
BAT_W = 10
BAT_H = 52
BATL_X = round(SCR_W / 5)
BATL_Y = round((SCR_H - BAT_H) / 2)

BATR_X = SCR_W - BATL_X - BAT_W
BATR_Y = round((SCR_H - BAT_H) / 2)

TWEEN_MIN = 0.0001
TWEEN_MAX = 0.9999

# SPEEDS
SPD_BALL = 560
SPD_BAT  = 740

# VLINE
VLINE_NB_SEGMENTS = 60
LINE_WIDTH = 4
LINE_HEIGHT = 13 
NB_LINES = round(SCR_H / LINE_HEIGHT) 
LINE_MIN = 20
THICKNESS = 1

# MOUSE
MOUSE_VISIBLE   = False

# EXIT
EXIT_PRG        = pg.K_ESCAPE

# SOUNDS
BALL_HIT_BAT    = 'assets/sounds/ball_hit_bat.wav'
BALL_HIT_WALL   = 'assets/sounds/ball_hit_wall.wav'
BALL_LOST       = 'assets/sounds/ball_lost.wav'

# FONTS
FONT1            = 'assets/fonts/pong-score.ttf'
FONT2            = 'assets/fonts/bit5x3.ttf'
FONT_SIZE        = 72
FONT_SIZE2       = 56


# ICONE         
ICON            = 'assets/images/pong.png'

# SCORE         Score max de la plupart des machines de l'epoque  
MAX_SCORE       = 15

# PAUSE
TXT_PAUSE        = 'GAME PAUSED'
TXT_PLAY         = 'PRESS SPACE TO PLAY'
TXT_RESTART      = 'PRESS SPACE TO RESTART'
TXT_L_PLAYER_WIN = 'LEFT PLAYER WIN'
TXT_R_PLAYER_WIN = 'RIGHT PLAYER WIN'

RATIO_START_V    = 20
