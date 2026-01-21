import pygame

# --- DISPLAY ---
SCREEN_W, SCREEN_H = 1200, 800
FPS = 60
TILE_SIZE = 64

# --- WORLD ---
MAP_W, MAP_H = 2400, 1800
TIME_SPEED = 0.2

# --- COLORS ---
COLORS = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "sky_day": (255, 255, 255),
    "sky_night": (20, 20, 45),
    "building": (60, 50, 40),
    "road": (100, 90, 80),
    "house": (80, 60, 50),
    "bed_frame": (100, 50, 50),
    "bed_sheet": (200, 200, 220),
    "ui_bg": (20, 20, 30),
    "ui_border": (255, 255, 255),
    "text": (220, 220, 220),
    "text_highlight": (255, 215, 0),
    "text_dark": (100, 100, 100),
    "selection": (255, 255, 0),
    "fallback_grass": (34, 59, 34),
    "fallback_sea": (20, 40, 90),
    "fallback_fresh": (40, 100, 140),
    "fallback_dirt": (101, 67, 33),
}

# --- FONTS ---
pygame.font.init()
FONTS = {
    "default": pygame.font.SysFont("Tahoma", 14),
    "bubble": pygame.font.SysFont("Tahoma", 12, bold=True),
    "header": pygame.font.SysFont("Tahoma", 20, bold=True),
    "menu": pygame.font.SysFont("Tahoma", 24),
}

# --- MAP DATA (FIXED AGAIN) ---
LOCATIONS = {
    "INN": pygame.Rect(1000, 600, 300, 250),
    "MARKET": pygame.Rect(950, 900, 400, 300),
    "BLACKSMITH": pygame.Rect(1400, 600, 200, 200),
    "GUILD": pygame.Rect(1400, 850, 200, 200),
    "DOCKS": pygame.Rect(100, 1300, 300, 400),
    "FARM": pygame.Rect(1720, 100, 580, 600),
    "GUARD_POST": pygame.Rect(950, 300, 150, 150),
    "PARK": pygame.Rect(300, 600, 400, 400)
}
INN_BAR_AREA = pygame.Rect(1020, 750, 260, 80)
HOUSES = [pygame.Rect(100 + i * 150, 100, 120, 120) for i in range(5)] + \
         [pygame.Rect(100 + i * 150, 300, 120, 120) for i in range(5)]
ROADS = [
    pygame.Rect(0, 450, 2400, 80),
    pygame.Rect(850, 0, 80, 1800),
    pygame.Rect(0, 1250, 1000, 60),
    pygame.Rect(1650, 0, 60, 800)
]
FIELDS = [pygame.Rect(1750, 150, 200, 500), pygame.Rect(2000, 150, 200, 500)]
RANCH = pygame.Rect(2250, 150, 100, 500)
BEDS = [(h.x + 20, h.y + 20) for h in HOUSES] + \
       [(LOCATIONS["INN"].x + 20 + (i % 3) * 60, LOCATIONS["INN"].y + 20 + (i // 3) * 60) for i in range(6)]
LAKE_COL_START = 400 // TILE_SIZE
LAKE_COL_END = 800 // TILE_SIZE

# --- DYNAMIC PATROL POINTS ---
gp_rect = LOCATIONS["GUARD_POST"]
PATROL_POINTS = [
    (gp_rect.left + 20, gp_rect.top + 20),
    (gp_rect.right - 20, gp_rect.top + 20),
    (gp_rect.right - 20, gp_rect.bottom - 20),
    (gp_rect.left + 20, gp_rect.bottom - 20)
]

# --- GAME DATA ---
MBTI_TYPES = ['INTJ', 'INTP', 'ENTJ', 'ENTP', 'INFJ', 'INFP', 'ENFJ', 'ENFP',
              'ISTJ', 'ISFJ', 'ESTJ', 'ESFJ', 'ISTP', 'ISFP', 'ESTP', 'ESFP']
RACES = ['Human', 'Elf', 'Dwarf', 'Orc', 'Goblin', 'Tiefling', 'Halfling']
JOBS_LIST = ["Innkeeper", "Blacksmith", "Scholar", "Guard", "Merchant", "Fisher", "Farmer", "Unemployed"]
JOBS_PRIMARY_STAT = {
    "Innkeeper": "social", "Blacksmith": "strength", "Scholar": "intellect",
    "Guard": "strength", "Merchant": "social", "Fisher": "joy", "Farmer": "work_ethic"
}
