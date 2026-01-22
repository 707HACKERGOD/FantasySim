import pygame
from config import COLORS, FONTS, TILE_SIZE, LOCATIONS, ROADS, HOUSES, BEDS, LAKE_COL_START, LAKE_COL_END

def get_sky_color(time_of_day):
    """Calculates the color of the sky based on the time of day."""
    if 350 <= time_of_day < 750: return COLORS["sky_day"]
    if 950 <= time_of_day or time_of_day < 150: return COLORS["sky_night"]
    
    prog = 0
    start, end = COLORS["sky_day"], COLORS["sky_night"]
    if 750 <= time_of_day < 950:
        prog = (time_of_day - 750) / 200
    elif 150 <= time_of_day < 350:
        prog = (time_of_day - 150) / 200
        start, end = COLORS["sky_night"], COLORS["sky_day"]

    return (
        int(start[0] + (end[0] - start[0]) * prog),
        int(start[1] + (end[1] - start[1]) * prog),
        int(start[2] + (end[2] - start[2]) * prog)
    )

def draw_viewport(surface, game_world, assets, camera, frame_count, selected_char):
    """Draws the world, structures, and characters."""
    vw, vh = surface.get_size()
    cam_x, cam_y = camera
    
    start_col = int(max(0, cam_x // TILE_SIZE))
    end_col = int(min(game_world.map_w // TILE_SIZE, (cam_x + vw) // TILE_SIZE + 1))
    start_row = int(max(0, cam_y // TILE_SIZE))
    end_row = int(min(game_world.map_h // TILE_SIZE, (cam_y + vh) // TILE_SIZE + 1))

    # --- Draw Terrain ---
    sea_frames = assets.sprites["water_sea"]
    fresh_frames = assets.sprites["water_fresh"]
    grass_frames = assets.sprites["grass"]
    
    # CHANGED: Speed up animations (lower divisor = faster)
    sea_idx = (frame_count // 5) % len(sea_frames)
    fresh_idx = (frame_count // 5) % len(fresh_frames)

    for row in range(start_row, end_row):
        for col in range(start_col, end_col):
            x, y = col * TILE_SIZE - cam_x, row * TILE_SIZE - cam_y
            tile_x, tile_y = col * TILE_SIZE, row * TILE_SIZE
            
            if tile_y > 1200:
                surface.blit(sea_frames[sea_idx], (x, y))
            elif LAKE_COL_START <= col < LAKE_COL_END and 550 < tile_y < 1100:
                surface.blit(fresh_frames[fresh_idx], (x, y))
            elif "FARM" in LOCATIONS and LOCATIONS["FARM"].collidepoint(tile_x, tile_y):
                surface.blit(assets.sprites["dirt"], (x, y))
            else:
                # CHANGED: Speed up grass animation slightly
                grass_idx = (col + row + (frame_count // 8)) % len(grass_frames)
                surface.blit(grass_frames[grass_idx], (x, y))

    # --- Draw Structures ---
    for r in ROADS:
        pygame.draw.rect(surface, COLORS["road"], (r.x - cam_x, r.y - cam_y, r.w, r.h))
    for name, r in LOCATIONS.items():
        pygame.draw.rect(surface, COLORS["building"], (r.x - cam_x, r.y - cam_y, r.w, r.h))
        surface.blit(FONTS["default"].render(name, True, COLORS["text_highlight"]), (r.x - cam_x + 10, r.y - cam_y + 10))
    for h in HOUSES:
        pygame.draw.rect(surface, COLORS["house"], (h.x - cam_x, h.y - cam_y, h.w, h.h))
    for bx, by in BEDS:
        if -50 < bx - cam_x < vw and -50 < by - cam_y < vh:
            pygame.draw.rect(surface, COLORS["bed_sheet"], (bx - cam_x, by - cam_y, 25, 40))
            pygame.draw.rect(surface, COLORS["bed_frame"], (bx - cam_x, by - cam_y + 10, 25, 30))

    # --- Draw Characters ---
    for c in sorted(game_world.chars, key=lambda char: char.y):
        sx, sy = c.x - cam_x, c.y - cam_y
        if -50 < sx < vw + 50 and -50 < sy < vh + 50:
            if c.job_state.get("boat_active"):
                pygame.draw.ellipse(surface, (100, 60, 40), (sx - 15, sy - 5, 30, 20))
            
            if c == selected_char:
                 pygame.draw.circle(surface, COLORS["white"], (int(sx), int(sy)), 14, 2)

            pygame.draw.circle(surface, c.color, (int(sx), int(sy)), 10)
            
            if c.chat_timer > 0 and c.chat_text:
                txt = FONTS["bubble"].render(c.chat_text, True, COLORS["black"])
                bg_rect = pygame.Rect(sx, sy - 40, txt.get_width() + 8, 20)
                pygame.draw.rect(surface, COLORS["white"], bg_rect, border_radius=5)
                surface.blit(txt, (bg_rect.x + 4, bg_rect.y + 2))

def draw_lighting(surface, game_world, assets, camera):
    """Applies darkness and light sources to the final viewport."""
    time_of_day = game_world.time_of_day
    # No lighting effects needed during the day
    if 350 <= time_of_day < 750:
        return

    vw, vh = surface.get_size()
    cam_x, cam_y = camera
    
    # 1. Create the darkness overlay
    sky_color = get_sky_color(time_of_day)
    darkness = pygame.Surface((vw, vh))
    darkness.fill(sky_color)
    
    # 2. Darken the entire drawn scene
    surface.blit(darkness, (0, 0), special_flags=pygame.BLEND_MULT)

    # 3. Add light sources back on top if it's deep night
    if time_of_day > 750 or time_of_day < 350:
        # Create a blank layer for the lights
        light_layer = pygame.Surface((vw, vh), pygame.SRCALPHA)
        
        # Draw building glows onto the light layer
        for r in LOCATIONS.values():
            lx, ly = r.centerx - cam_x, r.centery - cam_y
            light_layer.blit(assets.sprites["light"], (lx - 150, ly - 150))
        
        # Draw fireflies onto the light layer
        for p in game_world.environment.particles:
            px, py = p[0] - cam_x, p[1] - cam_y
            pygame.draw.circle(light_layer, (180, 180, 50), (int(px), int(py)), 3)
            
        # 4. Add the lights to the darkened scene
        surface.blit(light_layer, (0, 0), special_flags=pygame.BLEND_ADD)
