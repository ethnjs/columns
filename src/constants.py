import pygame
import time

INITIAL_SIZE = (800, 800)
FRAME_RATE = 30

BACKGROUND_COLOR = pygame.Color(20, 20, 20)
BOARD_COLOR = pygame.Color(0, 0 , 0)
CELL_BORDER_COLOR = pygame.Color(40, 40, 40)
LANDED_COLOR = pygame.Color(255, 255, 255)

INITIAL_TICK_INTERVAL = 20
MIN_NORMAL_TICK_INTERVAL = 4
FAST_TICK_INTERVAL = 2

MICRO_FONT = 'assets/fonts/Micro5-Regular.ttf'
FONT_COLOR = pygame.Color(255, 255, 255)