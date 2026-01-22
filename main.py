import pygame
from config import SCREEN_W, SCREEN_H, FPS, RACES, JOBS_LIST, MBTI_TYPES
from assets import AssetManager
from world import World
from ui import UIManager
from input_handler import InputHandler
from social import process_interaction
from drawing import draw_viewport, draw_lighting

class GameState:
    def __init__(self):
        self.screen_w, self.screen_h = SCREEN_W, SCREEN_H
        self.current = "MENU"
        self.mode = "NORMAL"
        self.speed = 1
        self.saved_speed = 1
        self.zoom = 1.0
        self.camera = [0, 0]
        self.selected_char = None
        self.player_target = None
        
        self.menu_selection = 0
        self.creation_selection = 0
        self.interaction_selection = 0
        
        self.creation_data = {"name": "Player", "race_idx": 0, "job_idx": 3, "mbti_idx": 0}

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
        pygame.display.set_caption("Fantasy Sim: Refactored")
        
        self.assets = AssetManager()
        self.world = World()
        self.state = GameState()
        self.ui = UIManager((self.state.screen_w, self.state.screen_h))
        self.input_handler = InputHandler(self.state)
        
        self.clock = pygame.time.Clock()
        self.frame_count = 0
        self.running = True

    def run(self):
        self.assets.load_all()
        
        while self.running:
            self.clock.tick(FPS)
            self.frame_count += 1
            
            action = self.input_handler.handle_events(pygame.event.get())
            if action:
                self.handle_action(action)
            
            if self.state.current == "GAME":
                self.world.update(self.state.speed, self.state.mode)
                self.assets.update_ambient_sounds(self.world.player_char)
                self.update_camera()

            self.draw()
            
        pygame.quit()

    def handle_action(self, action_data):
        action_type = action_data if isinstance(action_data, str) else action_data[0]
        action_value = None if isinstance(action_data, str) else action_data[1]

        # System
        if action_type == "QUIT": self.running = False
        if action_type == "RESIZE":
            self.screen = pygame.display.set_mode((self.state.screen_w, self.state.screen_h), pygame.RESIZABLE)
            self.ui = UIManager((self.state.screen_w, self.state.screen_h))

        # Game State
        if action_type == "NEW_GAME": self.state.current = "CREATION"
        if action_type == "LOAD_GAME":
            if self.world.load(): self.state.current = "GAME"
        if action_type == "GOTO_MENU": self.state.current = "MENU"
        
        if action_type == "CREATION_CHANGE": self.update_creation_data(action_value)
        if action_type == "START_GAME":
            self.world.create_new(self.state.creation_data)
            self.state.current = "GAME"

        if action_type == "TOGGLE_PAUSE":
            if self.state.current == "PAUSE":
                self.state.current = "GAME"
                self.state.speed = self.state.saved_speed
            else:
                self.state.saved_speed = self.state.speed
                self.state.speed = 0
                self.state.current = "PAUSE"
        
        if action_type == "SAVE_GAME": self.world.save()
        if action_type == "TOGGLE_GOD_MODE":
            self.state.mode = "GOD" if self.state.mode == "NORMAL" else "NORMAL"
        
        if action_type == "PLAYER_MOVE": self.handle_player_movement(action_value)
        if action_type == "CAMERA_MOVE": self.handle_camera_movement(action_value)

        if action_type == "SELECT_CHAR":
            wx = (self.input_handler.mouse_pos[0] / self.state.zoom) + self.state.camera[0]
            wy = (self.input_handler.mouse_pos[1] / self.state.zoom) + self.state.camera[1]
            self.state.selected_char = self.world.get_char_at((wx, wy))

        # God Mode Actions
        if action_type == "GOD_ENTER_EDITOR": self.state.mode = "EDITOR"
        if action_type == "GOD_EXIT_EDITOR": self.state.mode = "GOD"
            
        if self.state.selected_char:
            if action_type == "GOD_REROLL": self.state.selected_char.recalculate_stats()
            if action_type == "GOD_POSSESS":
                if self.world.player_char: self.world.player_char.is_player = False
                self.state.selected_char.is_player = True
                self.world.player_char = self.state.selected_char
                self.state.mode = "NORMAL"

        # Interaction Menu
        if action_type == "INTERACT":
            closest = min(
                (c for c in self.world.chars if c != self.world.player_char),
                key=lambda c: (self.world.player_char.x - c.x)**2 + (self.world.player_char.y - c.y)**2,
                default=None
            )
            if closest and ((self.world.player_char.x - closest.x)**2 + (self.world.player_char.y - closest.y)**2)**0.5 < 60:
                self.state.player_target = closest
                self.state.interaction_selection = 0

        if action_type == "INTERACTION_CANCEL": self.state.player_target = None
        if action_type == "INTERACTION_SELECT":
            choice = action_value + 1
            if choice == 4: # Cancel
                self.state.player_target = None
            elif self.state.player_target:
                actor, target = self.world.player_char, self.state.player_target
                act, line = process_interaction(actor, target, choice)
                actor.say(line)
                self.world.interaction_log.append(f"You ({act}): {line}")
                self.state.player_target = None

    def update_creation_data(self, direction):
        sel = self.state.creation_selection
        data = self.state.creation_data
        if sel == 0: data["race_idx"] = (data["race_idx"] + direction) % len(RACES)
        elif sel == 1: data["job_idx"] = (data["job_idx"] + direction) % len(JOBS_LIST)
        elif sel == 2: data["mbti_idx"] = (data["mbti_idx"] + direction) % len(MBTI_TYPES)

    def handle_player_movement(self, keys):
        if not self.world.player_char: return
        player = self.world.player_char
        
        # Determine base speed
        spd = player.speed * 2 if keys[pygame.K_LSHIFT] else player.speed
        
        # Calculate direction (dx, dy)
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1
        
        # Normalize diagonal speed
        # If moving in both X and Y directions, scale speed down
        if dx != 0 and dy != 0:
            spd *= 0.7071  # Multiplies by ~1/sqrt(2)
            
        # Apply movement
        player.x += dx * spd
        player.y += dy * spd
        
        # Update target coordinates so the AI/Movement logic doesn't override it
        player.target_x, player.target_y = player.x, player.y    
    
    def handle_camera_movement(self, keys):
        cam_speed = 20 / self.state.zoom
        if keys[pygame.K_w] or keys[pygame.K_UP]: self.state.camera[1] -= cam_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: self.state.camera[1] += cam_speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.state.camera[0] -= cam_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.state.camera[0] += cam_speed

    def update_camera(self):
        if self.state.mode == "NORMAL" and self.world.player_char:
            target_x = self.world.player_char.x - (self.state.screen_w / self.state.zoom / 2)
            target_y = self.world.player_char.y - (self.state.screen_h / self.state.zoom / 2)
            self.state.camera[0] += (target_x - self.state.camera[0]) * 0.1
            self.state.camera[1] += (target_y - self.state.camera[1]) * 0.1
        
        vw, vh = self.state.screen_w / self.state.zoom, self.state.screen_h / self.state.zoom
        self.state.camera[0] = max(0, min(self.state.camera[0], self.world.map_w - vw))
        self.state.camera[1] = max(0, min(self.state.camera[1], self.world.map_h - vh))

    def draw(self):
        if self.state.current in ["GAME", "PAUSE", "EDITOR"]:
            viewport_size = (int(self.state.screen_w / self.state.zoom), int(self.state.screen_h / self.state.zoom))
            viewport = pygame.Surface(viewport_size)
            
            draw_viewport(viewport, self.world, self.assets, self.state.camera, self.frame_count, self.state.selected_char)
            draw_lighting(viewport, self.world, self.assets, self.state.camera)
            
            scaled_view = pygame.transform.scale(viewport, (self.state.screen_w, self.state.screen_h))
            self.screen.blit(scaled_view, (0, 0))
            
            self.ui.draw_game_ui(self.screen, self.world, self.state, self.state.selected_char, self.state.player_target)

        elif self.state.current == "CREATION":
            self.ui.draw_creation_menu(self.screen, self.state.creation_data, self.state.creation_selection)
        
        else: # MENU
            self.ui.draw_main_menu(self.screen, self.state.menu_selection)

        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
