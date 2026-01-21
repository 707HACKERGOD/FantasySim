import random
from config import RACES, MBTI_TYPES, JOBS_PRIMARY_STAT, LOCATIONS, INN_BAR_AREA, PATROL_POINTS, RANCH, FIELDS

class Relationship:
    def __init__(self):
        self.friendship = 0
        self.romance = 0
        self.status = "Strangers"

class Character:
    def __init__(self, name, x, y, color):
        self.name = name
        self.color = color
        self.is_player = False
        
        self.race = random.choice(RACES)
        self.mbti = random.choice(MBTI_TYPES)
        self.job = "Unemployed"
        
        self.stats = {}
        self.relationships = {}
        self.recalculate_stats()
        
        self.job_state = { "task": "Idle", "path": [], "path_index": 0, "boat_active": False }
        self.daily_routine = 0
        self.schedule_offset = random.randint(-40, 40)
        
        self.chat_text = None
        self.chat_timer = 0
        
        self.x, self.y = x, y
        self.target_x, self.target_y = x, y
        self.home_coords = (0, 0)
        self.bed_coords = (0, 0)
        self.work_coords = (0, 0)
        self.speed = 2

    def update(self, world, game_mode, process_interaction):
        if self.chat_timer > 0:
            self.chat_timer -= 1

        if self.is_player and game_mode == "NORMAL":
            return 

        self._update_ai_behavior(world, process_interaction)
        self.move()

    def _update_ai_behavior(self, world, process_interaction):
        self.job_state["boat_active"] = False
        self.job_state["task"] = "Idle"
        
        time = world.time_of_day + self.schedule_offset
        dest = self.home_coords

        if time > 1100 or time < 300:
            dest = self.bed_coords
        elif 300 <= time < 850:
            self.job_state["task"] = "Working"
            dest = self._get_work_destination()
        else:
            dest = INN_BAR_AREA.center if self.stats["social"] > 5 else self.home_coords

        self.target_x = dest[0] + random.randint(-20, 20)
        self.target_y = dest[1] + random.randint(-20, 20)
        
        if random.random() < 0.005:
            for other in world.chars:
                if self != other and ((self.x - other.x)**2 + (self.y - other.y)**2)**0.5 < 40:
                    act, line = process_interaction(self, other)
                    self.say(line)
                    world.interaction_log.append(f"{self.name}: {line}")
                    break

    def _get_work_destination(self):
        if self.job == "Farmer":
            field_idx = 0 if self.daily_routine == 0 else 1
            if self.daily_routine == 2:
                return RANCH.center
            
            if not self.job_state.get("path") or self.job_state.get("field_idx") != field_idx:
                self.job_state["path"] = self._generate_farmer_path(field_idx)
                self.job_state["path_index"] = 0
                self.job_state["field_idx"] = field_idx

            dest = self.job_state["path"][self.job_state["path_index"]]
            if ((self.x - dest[0])**2 + (self.y - dest[1])**2)**0.5 < 10:
                self.job_state["path_index"] = (self.job_state["path_index"] + 1) % len(self.job_state["path"])
            return self.job_state["path"][self.job_state["path_index"]]

        elif self.job == "Guard":
            return PATROL_POINTS[self.daily_routine % len(PATROL_POINTS)]
        elif self.job == "Fisher":
            if self.daily_routine == 0:
                self.job_state["boat_active"] = (self.y > 1150)
                return (random.randint(200, 800), 1400)
            elif self.daily_routine == 1:
                return (LOCATIONS["DOCKS"].x + 50, LOCATIONS["DOCKS"].y + 350)
            else:
                return (LOCATIONS["DOCKS"].x + 50, LOCATIONS["DOCKS"].y + 50)
        elif self.job == "Innkeeper":
            return (LOCATIONS["INN"].x + 250, LOCATIONS["INN"].y + 200) if self.daily_routine == 0 else INN_BAR_AREA.center
        elif self.job == "Unemployed":
            if self.daily_routine == 0: return LOCATIONS["PARK"].center
            if self.daily_routine == 1: return LOCATIONS["MARKET"].center
            return LOCATIONS["DOCKS"].center
        else:
            return self.work_coords

    def _generate_farmer_path(self, field_idx):
        path = []
        field = FIELDS[field_idx % 2]
        for i in range(5):
            y = field.y + 40 + (i * 80)
            start_x, end_x = field.x + 20, field.x + field.w - 20
            path.extend([(start_x, y), (end_x, y)] if i % 2 == 0 else [(end_x, y), (start_x, y)])
        return path

    def assign_work_coords(self):
        job_map = {
            "Innkeeper": "INN", "Blacksmith": "BLACKSMITH", "Farmer": "FARM",
            "Fisher": "DOCKS", "Merchant": "MARKET", "Scholar": "GUILD", "Guard": "GUARD_POST"
        }
        loc_name = job_map.get(self.job)
        if loc_name and loc_name in LOCATIONS:
            self.work_coords = LOCATIONS[loc_name].center

    def roll_daily_routine(self):
        self.daily_routine = random.randint(0, 2)
        if self.job == "Farmer": self.job_state["path"] = []

    def recalculate_stats(self):
        self.stats = {k: random.randint(3, 8) for k in ["social", "intellect", "strength", "joy", "libido", "work_ethic"]}
        if self.race == "Orc": self.stats["strength"] += 3
        elif self.race == "Elf": self.stats["intellect"] += 3
        elif self.race == "Halfling": self.stats["social"] += 3
        elif self.race == "Dwarf": self.stats["work_ethic"] += 3
        
        if "E" in self.mbti: self.stats["social"] += 2
        if "I" in self.mbti: self.stats["social"] -= 1
        if "T" in self.mbti: self.stats["intellect"] += 1
        if "F" in self.mbti: self.stats["joy"] += 1
        for k in self.stats: self.stats[k] = max(1, min(10, self.stats[k]))

    def get_job_suitability(self, job_name):
        primary_stat = JOBS_PRIMARY_STAT.get(job_name, "social")
        score = self.stats.get(primary_stat, 0) * 2
        if job_name == "Guard" and "J" in self.mbti: score += 3
        if job_name == "Innkeeper" and "E" in self.mbti: score += 5
        if job_name == "Fisher" and "P" in self.mbti: score += 4
        return score

    def get_relationship(self, other_name):
        if other_name not in self.relationships:
            self.relationships[other_name] = Relationship()
        return self.relationships[other_name]

    def say(self, text):
        self.chat_text = text
        self.chat_timer = 180

    def move(self):
        dx, dy = self.target_x - self.x, self.target_y - self.y
        dist = (dx**2 + dy**2)**0.5
        
        actual_speed = self.speed * 2 if self.job_state.get("boat_active") else self.speed
        if dist > actual_speed:
            self.x += (dx / dist) * actual_speed
            self.y += (dy / dist) * actual_speed
        else:
            self.x, self.y = self.target_x, self.target_y

    def get_known_info(self, observer):
        if observer == self: return self.get_full_info()
        rel = observer.get_relationship(self.name)
        info = {"name": self.name, "job": "???", "mbti": "???", "race": self.race, "status": rel.status}
        if rel.friendship > 0 or rel.romance > 0 or self.job_state.get("task") == "Working":
            info["job"] = self.job
        if rel.friendship > 30 or rel.romance > 20:
            info["mbti"] = self.mbti
        return info

    def get_full_info(self):
        return {"name": self.name, "job": self.job, "mbti": self.mbti, "race": self.race, "status": "Self"}
