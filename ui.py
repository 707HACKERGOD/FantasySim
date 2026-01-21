import pygame
from config import COLORS, FONTS

class UIManager:
    def __init__(self, screen_dims):
        self.screen_w, self.screen_h = screen_dims
    
    def draw_main_menu(self, surface, selection_idx):
        surface.fill(COLORS["ui_bg"])
        title = FONTS["header"].render("FANTASY LIFE SIM", True, COLORS["text_highlight"])
        surface.blit(title, (self.screen_w // 2 - title.get_width() // 2, 200))
        
        opts = ["NEW GAME", "LOAD GAME", "QUIT"]
        for i, txt in enumerate(opts):
            col = COLORS["selection"] if i == selection_idx else COLORS["text"]
            t = FONTS["menu"].render(txt, True, col)
            surface.blit(t, (self.screen_w // 2 - t.get_width() // 2, 400 + i * 60))

    def draw_creation_menu(self, surface, creation_data, selection_idx):
        from config import RACES, JOBS_LIST, MBTI_TYPES
        surface.fill((10, 10, 15))
        title = FONTS["header"].render("CREATE CHARACTER", True, COLORS["text_highlight"])
        surface.blit(title, (self.screen_w // 2 - title.get_width() // 2, 100))

        labels = [
            f"RACE: < {RACES[creation_data['race_idx']]} >",
            f"JOB:  < {JOBS_LIST[creation_data['job_idx']]} >",
            f"MBTI: < {MBTI_TYPES[creation_data['mbti_idx']]} >",
            "START GAME"
        ]
        for i, txt in enumerate(labels):
            col = COLORS["selection"] if i == selection_idx else COLORS["text"]
            t = FONTS["menu"].render(txt, True, col)
            surface.blit(t, (self.screen_w // 2 - t.get_width() // 2, 300 + i * 80))

        hint = FONTS["default"].render("[ARROWS] Select/Change | [ENTER] Confirm | [ESC] Back", True, COLORS["text_dark"])
        surface.blit(hint, (self.screen_w // 2 - hint.get_width() // 2, self.screen_h - 100))

    def draw_game_ui(self, surface, game_world, game_state, selected_char, player_target):
        # Bottom Log
        pygame.draw.rect(surface, COLORS["black"], (0, self.screen_h - 100, self.screen_w, 100))
        pygame.draw.line(surface, COLORS["text_highlight"], (0, self.screen_h - 100), (self.screen_w, self.screen_h - 100), 2)
        for i, line in enumerate(reversed(game_world.interaction_log[-3:])):
            surface.blit(FONTS["default"].render(line, True, COLORS["text"]), (30, self.screen_h - 35 - i * 25))

        # Top Info
        info = f"Day {game_world.day} | Time {int(game_world.time_of_day)} | Speed x{game_state.speed} | Zoom {game_state.zoom:.1f}x"
        surface.blit(FONTS["header"].render(info, True, COLORS["white"]), (20, 20))

        if selected_char:
            self._draw_char_panel(surface, selected_char, game_state.mode, game_world.player_char)
        
        if player_target:
            self._draw_interaction_menu(surface, player_target, game_state.interaction_selection)

        if game_state.current == "PAUSE":
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            surface.blit(overlay, (0, 0))
            t = FONTS["header"].render("PAUSED", True, COLORS["white"])
            surface.blit(t, (self.screen_w // 2 - t.get_width() // 2, self.screen_h // 2))

    def _draw_char_panel(self, surface, char, game_mode, player_char):
        panel = pygame.Rect(self.screen_w - 300, 60, 280, 300)
        pygame.draw.rect(surface, COLORS["ui_bg"], panel)
        pygame.draw.rect(surface, COLORS["white"], panel, 2)
        
        if game_mode in ["GOD", "EDITOR"]:
            data = char.get_full_info()
            lines = [f"{data['name']} ({data['job']})", f"{data['race']} {data['mbti']}", "--- GOD TOOLS ---", "[E] Edit  [C] Reroll  [P] Possess"]
        else:
            data = char.get_known_info(player_char)
            lines = [f"{data['name']}", f"Job: {data['job']}", f"Type: {data['mbti']}", f"Status: {data['status']}"]
            
        for i, txt in enumerate(lines):
            surface.blit(FONTS["default"].render(txt, True, COLORS["text"]), (panel.x + 10, panel.y + 10 + i * 25))

    def _draw_interaction_menu(self, surface, target, selection_idx):
        menu_rect = pygame.Rect(self.screen_w // 2 - 100, self.screen_h // 2 - 100, 200, 150)
        pygame.draw.rect(surface, COLORS["ui_bg"], menu_rect)
        pygame.draw.rect(surface, COLORS["white"], menu_rect, 2)
        
        title = FONTS["header"].render(target.name, True, COLORS["text_highlight"])
        surface.blit(title, (menu_rect.x + 20, menu_rect.y + 10))
        
        opts = ["Chat", "Flirt", "Insult", "Cancel"]
        for i, o in enumerate(opts):
            col = COLORS["selection"] if i == selection_idx else COLORS["text"]
            text = FONTS["default"].render(o, True, col)
            surface.blit(text, (menu_rect.x + 20, menu_rect.y + 50 + i * 25))
