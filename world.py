import random
import math
import pickle
import os
from character import Character, RACES, MBTI_TYPES
from config import MAP_W, MAP_H, LOCATIONS, BEDS, HOUSES, JOBS_LIST, PATROL_POINTS, INN_BAR_AREA, RANCH, FIELDS, TIME_SPEED

class Environment:
    def __init__(self):
        self.particles = []

    def update(self, time_of_day):
        is_night = time_of_day > 850 or time_of_day < 350
        if is_night and len(self.particles) < 60:
            self.particles.append([random.randint(0, MAP_W), random.randint(0, MAP_H), random.randint(0, 100)])
        elif not is_night:
            self.particles = []

        for p in self.particles:
            p[0] += math.sin(p[2] * 0.05) * 0.5
            p[1] += math.cos(p[2] * 0.05) * 0.5
            p[2] += 1

class World:
    def __init__(self):
        self.chars = []
        self.player_char = None
        self.day = 1
        self.time_of_day = 300
        self.interaction_log = ["Welcome to Fantasy Sim!"]
        self.environment = Environment()
        self.map_w, self.map_h = MAP_W, MAP_H
    
    def get_char_at(self, pos, radius=20):
        for char in self.chars:
            if abs(char.x - pos[0]) < radius and abs(char.y - pos[1]) < radius:
                return char
        return None

    def update(self, game_speed, game_mode):
        from social import process_interaction
        
        # --- TIME UPDATE LOGIC CHANGED HERE ---
        # 1. Check for sleeping (Player near bed)
        is_sleeping = False
        if self.player_char:
            px, py = self.player_char.x, self.player_char.y
            for bx, by in BEDS:
                # Check if player is within 40 pixels of a bed
                if ((px - bx)**2 + (py - by)**2)**0.5 < 40:
                    is_sleeping = True
                    break
        
        # 2. Calculate time increment
        # Use TIME_SPEED from config (0.017)
        increment = TIME_SPEED * game_speed
        
        if is_sleeping:
            increment *= 100  # Speed up time by 100x if sleeping
        
        self.time_of_day += increment
        # -------------------------------------

        if self.time_of_day >= 1200:
            self.time_of_day = 0
            self.day += 1
            for c in self.chars:
                c.roll_daily_routine()
        
        self.environment.update(self.time_of_day)

        for c in self.chars:
            c.update(self, game_mode, process_interaction)

    def create_new(self, player_data):
        self.chars = []
        self.day = 1
        self.time_of_day = 300
        self.interaction_log = ["New World Created."]
        
        names = ["Arin", "Bela", "Cian", "Dora", "Elian", "Fyn", "Gara", "Hux", "Ivy", "Jem", "Kae", "Lorn", "Mika", "Nora", "Odin", "Pia"]
        
        p = Character(player_data["name"], 800, 600, player_data.get("color", (255, 255, 255)))
        p.race = RACES[player_data["race_idx"]]
        p.job = JOBS_LIST[player_data["job_idx"]]
        p.mbti = MBTI_TYPES[player_data["mbti_idx"]]
        p.is_player = True
        p.recalculate_stats()
        p.bed_coords = BEDS[0]
        p.home_coords = HOUSES[0].center
        p.x, p.y = p.bed_coords
        self.chars.append(p)
        self.player_char = p

        for i, name in enumerate(names):
            if len(self.chars) >= 16: break
            c = Character(name, 0, 0, (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200)))
            bed_idx = i + 1
            if bed_idx < len(BEDS):
                c.bed_coords = BEDS[bed_idx]
                c.home_coords = HOUSES[bed_idx].center if bed_idx < len(HOUSES) else LOCATIONS["INN"].center
                c.x, c.y = c.bed_coords
                c.target_x, c.target_y = c.x, c.y
            self.chars.append(c)

        job_openings = {"Innkeeper": 2, "Blacksmith": 2, "Scholar": 2, "Guard": 3, "Merchant": 2, "Fisher": 2, "Farmer": 2}
        for job, slots in job_openings.items():
            for _ in range(slots):
                candidates = [c for c in self.chars if c.job == "Unemployed" and not c.is_player]
                if not candidates: break
                best = max(candidates, key=lambda x: x.get_job_suitability(job))
                best.job = job
        
        for c in self.chars:
            c.assign_work_coords()

    def save(self):
        if not self.player_char: return
        try:
            player_idx = self.chars.index(self.player_char)
            data = {"chars": self.chars, "day": self.day, "time": self.time_of_day, "player_idx": player_idx}
            with open("savegame.pkl", "wb") as f:
                pickle.dump(data, f)
            self.interaction_log.append("Game Saved.")
        except (ValueError, pickle.PicklingError) as e:
            self.interaction_log.append(f"Save failed: {e}")

    def load(self):
        if os.path.exists("savegame.pkl"):
            try:
                with open("savegame.pkl", "rb") as f:
                    data = pickle.load(f)
                self.chars = data["chars"]
                self.day = data["day"]
                self.time_of_day = data["time"]
                self.player_char = self.chars[data["player_idx"]]
                self.interaction_log.append("Game Loaded.")
                return True
            except (IOError, pickle.UnpicklingError, EOFError) as e:
                self.interaction_log.append(f"Load failed: {e}")
                return False
        return False
