import pygame
import os
from config import TILE_SIZE, COLORS, LOCATIONS

class AssetManager:
    def __init__(self):
        self.sprites = {}
        self.sounds = {}
        self.base_path = "assets"

    def _load_animation(self, name, fallback_color):
        frames = []
        path = os.path.join(self.base_path, "sprites", name)
        
        if not os.path.exists(path):
            s = pygame.Surface((TILE_SIZE, TILE_SIZE))
            s.fill(fallback_color)
            return [s]

        start_index = 1 if os.path.exists(os.path.join(path, f"{name}_1.png")) else 0
        i = start_index
        while True:
            file_path = os.path.join(path, f"{name}_{i}.png")
            if os.path.exists(file_path):
                try:
                    img = pygame.image.load(file_path).convert_alpha()
                    frames.append(pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE)))
                    i += 1
                except pygame.error:
                    break
            else:
                break
        
        if not frames:
            s = pygame.Surface((TILE_SIZE, TILE_SIZE))
            s.fill(fallback_color)
            return [s]
            
        return frames

    def _load_image(self, name, fallback_color=None):
        path = os.path.join(self.base_path, "sprites", f"{name}.png")
        try:
            img = pygame.image.load(path).convert_alpha()
            # The light mask is a special case, we don't scale it like a tile
            if name != "light_mask":
                 return pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
            return img
        except (pygame.error, FileNotFoundError): # Correctly catch the error
            if fallback_color:
                s = pygame.Surface((TILE_SIZE, TILE_SIZE))
                s.fill(fallback_color)
                return s
            return None

    def _create_placeholder_light(self):
        s = pygame.Surface((300, 300), pygame.SRCALPHA)
        # Draw a soft yellow glow fading to transparent
        for r in range(150, 0, -5):
            alpha = int(255 * (1 - (r / 150)**0.8)) # Adjusted for a softer falloff
            color = (60, 50, 20, alpha)
            pygame.draw.circle(s, color, (150, 150), r)
        return s

    def load_all(self):
        # Sprites
        self.sprites["grass"] = self._load_animation("grass", COLORS["fallback_grass"])
        self.sprites["water_sea"] = self._load_animation("water_sea", COLORS["fallback_sea"])
        self.sprites["water_fresh"] = self._load_animation("water_fresh", COLORS["fallback_fresh"])
        self.sprites["dirt"] = self._load_image("ground", COLORS["fallback_dirt"])
        
        # This block is now robust and will not crash
        light_img = self._load_image("light_mask")
        self.sprites["light"] = light_img if light_img else self._create_placeholder_light()

        # Sounds
        try:
            pygame.mixer.set_num_channels(16)
            for sound_name in ["nature", "market", "beach"]:
                path = os.path.join(self.base_path, "sounds", f"{sound_name}.wav")
                if os.path.exists(path):
                    self.sounds[sound_name] = pygame.mixer.Sound(path)
                    self.sounds[sound_name].play(-1).set_volume(0)
            
            if "nature" in self.sounds:
                self.sounds["nature"].set_volume(0.2)
        except Exception as e:
            print(f"Could not initialize sounds: {e}")

    def update_ambient_sounds(self, player_pos):
        if not player_pos or not pygame.mixer.get_init(): return

        def dist_vol(rect):
            d = ((player_pos.x - rect.centerx)**2 + (player_pos.y - rect.centery)**2)**0.5
            if d < 100: return 0.6
            if d > 900: return 0.0
            return 0.6 * (1 - (d / 900))

        if "market" in self.sounds and "MARKET" in LOCATIONS:
            self.sounds["market"].set_volume(dist_vol(LOCATIONS["MARKET"]))
        if "beach" in self.sounds and "DOCKS" in LOCATIONS:
            self.sounds["beach"].set_volume(dist_vol(LOCATIONS["DOCKS"]))
