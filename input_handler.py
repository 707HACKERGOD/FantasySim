import pygame

class InputHandler:
    def __init__(self, game_state):
        self.game_state = game_state
        self.mouse_pos = (0, 0)

    def handle_events(self, events):
        action = None
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.VIDEORESIZE:
                self.game_state.screen_w, self.game_state.screen_h = event.w, event.h
                return "RESIZE"
            
            self.mouse_pos = pygame.mouse.get_pos()

            if self.game_state.current == "MENU":
                action = self.handle_menu_input(event)
            elif self.game_state.current == "CREATION":
                action = self.handle_creation_input(event)
            elif self.game_state.current in ["GAME", "PAUSE", "EDITOR"]:
                action = self.handle_game_input(event)
            
            if action:
                return action
        
        # Continuous (key-held) input
        if self.game_state.current == "GAME":
            keys = pygame.key.get_pressed()
            if self.game_state.mode == "NORMAL" and not self.game_state.player_target:
                return "PLAYER_MOVE", keys
            elif self.game_state.mode == "GOD":
                return "CAMERA_MOVE", keys

    def handle_menu_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.game_state.menu_selection = (self.game_state.menu_selection - 1) % 3
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.game_state.menu_selection = (self.game_state.menu_selection + 1) % 3
            elif event.key == pygame.K_RETURN or event.key == pygame.K_z:
                if self.game_state.menu_selection == 0: return "NEW_GAME"
                if self.game_state.menu_selection == 1: return "LOAD_GAME"
                if self.game_state.menu_selection == 2: return "QUIT"
            elif event.key == pygame.K_n: return "NEW_GAME"
            elif event.key == pygame.K_l: return "LOAD_GAME"
            elif event.key == pygame.K_q: return "QUIT"
            
    def handle_creation_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: return "GOTO_MENU"
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.game_state.creation_selection = (self.game_state.creation_selection - 1) % 4
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.game_state.creation_selection = (self.game_state.creation_selection + 1) % 4
            elif event.key in [pygame.K_LEFT, pygame.K_a]:
                return "CREATION_CHANGE", -1
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                return "CREATION_CHANGE", 1
            elif event.key == pygame.K_RETURN or event.key == pygame.K_z:
                if self.game_state.creation_selection == 3: return "START_GAME"

    def handle_game_input(self, event):
        if self.game_state.current == "PAUSE":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "TOGGLE_PAUSE"
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.game_state.player_target: return "INTERACTION_CANCEL"
                if self.game_state.mode == "EDITOR": return "GOD_EXIT_EDITOR"
                else: return "TOGGLE_PAUSE"
            
            if self.game_state.player_target:
                return self.handle_interaction_menu_input(event)

            if event.key == pygame.K_F5: return "SAVE_GAME"
            if event.key == pygame.K_F9: return "GOTO_MENU"
            if event.key == pygame.K_TAB: return "TOGGLE_GOD_MODE"
            
            if event.key == pygame.K_F1: self.game_state.speed = 0
            if event.key == pygame.K_F2: self.game_state.speed = 1
            if event.key == pygame.K_F3: self.game_state.speed = 3
            if event.key == pygame.K_F4: self.game_state.speed = 10

            if self.game_state.mode == "GOD" and self.game_state.selected_char:
                if event.key == pygame.K_e: return "GOD_ENTER_EDITOR" # <-- THIS IS THE FIX
                if event.key == pygame.K_c: return "GOD_REROLL"
                if event.key == pygame.K_p: return "GOD_POSSESS"
            
            if self.game_state.mode == "EDITOR" and self.game_state.selected_char:
                 if event.key == pygame.K_RETURN: return "GOD_EXIT_EDITOR"
                 # Add stat-changing logic in main.py based on other key presses

            if self.game_state.mode == "NORMAL" and event.key in [pygame.K_SPACE, pygame.K_z]:
                return "INTERACT"

        if event.type == pygame.MOUSEWHEEL:
            self.game_state.zoom = max(1.0, min(3.0, self.game_state.zoom + event.y * 0.1))
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
             if not (self.mouse_pos[0] > self.game_state.screen_w - 300 and self.game_state.mode != "NORMAL"):
                return "SELECT_CHAR"
    
    def handle_interaction_menu_input(self, event):
        if event.key in [pygame.K_UP, pygame.K_w]:
            self.game_state.interaction_selection = (self.game_state.interaction_selection - 1) % 4
        elif event.key in [pygame.K_DOWN, pygame.K_s]:
            self.game_state.interaction_selection = (self.game_state.interaction_selection + 1) % 4
        elif event.key == pygame.K_RETURN or event.key == pygame.K_z:
            return "INTERACTION_SELECT", self.game_state.interaction_selection
