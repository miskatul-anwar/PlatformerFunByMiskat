import pygame
from src.platformer.config import (
    WIDTH, HEIGHT, COLOR_WHITE, COLOR_ACCENT, COLOR_GREEN,
    COLOR_RED, COLOR_CYAN, COLOR_TEXT, COLOR_TEXT_MUTED,
    CHARACTERS, CHARACTER_NAMES
)
from src.platformer.graphics import sprites
from src.platformer.levels import levels
from .button import get_font

def draw_pause_overlay(surface, buttons):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((10, 12, 20, 200))
    surface.blit(overlay, (0, 0))

    panel_rect = pygame.Rect(WIDTH // 2 - 220, HEIGHT // 2 - 190, 440, 380)
    pygame.draw.rect(surface, (30, 35, 52), panel_rect, border_radius=18)
    pygame.draw.rect(surface, COLOR_ACCENT, panel_rect, width=3, border_radius=18)

    title_font = get_font(38, bold=True)
    title_surf = title_font.render("GAME PAUSED", True, COLOR_ACCENT)
    title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 130))
    surface.blit(title_surf, title_rect)

    for btn in buttons:
        btn.draw(surface)

def draw_level_clear_overlay(surface, level_name, fruits_collected, total_fruits, score, elapsed_seconds, stars, buttons):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((10, 12, 20, 200))
    surface.blit(overlay, (0, 0))

    panel_rect = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 - 220, 500, 440)
    pygame.draw.rect(surface, (30, 35, 52), panel_rect, border_radius=20)
    pygame.draw.rect(surface, COLOR_GREEN, panel_rect, width=3, border_radius=20)

    title_font = get_font(36, bold=True)
    title_surf = title_font.render("LEVEL COMPLETE!", True, COLOR_GREEN)
    title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 170))
    surface.blit(title_surf, title_rect)

    info_font = get_font(22, bold=False)
    mins = int(elapsed_seconds) // 60
    secs = int(elapsed_seconds) % 60
    lines = [
        f"Stage: {level_name}",
        f"Fruits: {fruits_collected} / {total_fruits}",
        f"Time: {mins:02d}:{secs:02d}",
        f"Level Score: +{score}",
    ]
    for i, line in enumerate(lines):
        line_surf = info_font.render(line, True, COLOR_TEXT)
        surface.blit(line_surf, (WIDTH // 2 - 180, HEIGHT // 2 - 110 + i * 32))

    star_str = "★ " * stars + "☆ " * (3 - stars)
    star_font = get_font(36, bold=True)
    star_surf = star_font.render(star_str.strip(), True, COLOR_ACCENT)
    star_rect = star_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 35))
    surface.blit(star_surf, star_rect)

    for btn in buttons:
        btn.draw(surface)

def draw_game_over_overlay(surface, final_score, buttons):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((20, 5, 5, 215))
    surface.blit(overlay, (0, 0))

    panel_rect = pygame.Rect(WIDTH // 2 - 220, HEIGHT // 2 - 170, 440, 340)
    pygame.draw.rect(surface, (45, 20, 25), panel_rect, border_radius=18)
    pygame.draw.rect(surface, COLOR_RED, panel_rect, width=3, border_radius=18)

    title_font = get_font(42, bold=True)
    title_surf = title_font.render("GAME OVER", True, COLOR_RED)
    title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 110))
    surface.blit(title_surf, title_rect)

    score_font = get_font(24, bold=False)
    score_surf = score_font.render(f"Final Score: {final_score}", True, COLOR_WHITE)
    score_rect = score_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    surface.blit(score_surf, score_rect)

    for btn in buttons:
        btn.draw(surface)

def draw_victory_screen(surface, total_score, total_time, buttons):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((15, 20, 35, 230))
    surface.blit(overlay, (0, 0))

    panel_rect = pygame.Rect(WIDTH // 2 - 300, HEIGHT // 2 - 240, 600, 480)
    pygame.draw.rect(surface, (30, 36, 56), panel_rect, border_radius=22)
    pygame.draw.rect(surface, COLOR_ACCENT, panel_rect, width=4, border_radius=22)

    title_font = get_font(42, bold=True)
    title_surf = title_font.render("YOU BEAT THE GAME!", True, COLOR_ACCENT)
    title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 180))
    surface.blit(title_surf, title_rect)

    sub_font = get_font(20, bold=False)
    sub_surf = sub_font.render("Platformer Fun by Miskatul Anwar - Dept of CSE, CU", True, COLOR_CYAN)
    sub_rect = sub_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 135))
    surface.blit(sub_surf, sub_rect)

    mins = int(total_time) // 60
    secs = int(total_time) % 60
    stats = [
        "Congratulations! You completed all 5 adventure stages!",
        f"Total Final Score: {total_score}",
        f"Total Journey Time: {mins:02d}:{secs:02d}",
        "Thank you for playing!"
    ]
    stat_font = get_font(22, bold=False)
    for i, st in enumerate(stats):
        col = COLOR_ACCENT if "Score" in st else COLOR_TEXT
        s_surf = stat_font.render(st, True, col)
        s_rect = s_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 75 + i * 34))
        surface.blit(s_surf, s_rect)

    for btn in buttons:
        btn.draw(surface)

def draw_main_menu(surface, selected_character, high_score, buttons):
    menu_bg, bg_img = sprites.get_background("Blue.png", WIDTH, HEIGHT)
    for tile in menu_bg:
        surface.blit(bg_img, tile)

    title_font = get_font(52, bold=True)
    sub_font = get_font(22, bold=True)

    t_text = "PLATFORMER FUN BY MISKAT"
    t_shadow = title_font.render(t_text, True, (15, 20, 30))
    t_surf = title_font.render(t_text, True, COLOR_ACCENT)
    cx = WIDTH // 2
    surface.blit(t_shadow, t_shadow.get_rect(center=(cx + 3, 113)))
    surface.blit(t_surf, t_surf.get_rect(center=(cx, 110)))

    s_surf = sub_font.render("Classic Pixel Adventure Platformer Experience", True, COLOR_WHITE)
    surface.blit(s_surf, s_surf.get_rect(center=(cx, 165)))

    hs_surf = get_font(20, bold=True).render(f"HIGH SCORE: {high_score}", True, COLOR_CYAN)
    surface.blit(hs_surf, hs_surf.get_rect(center=(cx, 205)))

    char_info = CHARACTERS.get(selected_character, CHARACTERS["VirtualGuy"])
    char_sprites = sprites.load_character_sprites(selected_character, scale=3)
    run_frames = char_sprites.get("run_right", char_sprites.get("idle_right"))
    frame_idx = int((pygame.time.get_ticks() / 120) % len(run_frames))
    preview_sprite = run_frames[frame_idx]

    box_left = pygame.Rect(cx - 430, 320, 220, 260)
    pygame.draw.rect(surface, (25, 30, 45, 220), box_left, border_radius=16)
    pygame.draw.rect(surface, char_info["color"], box_left, width=3, border_radius=16)

    surface.blit(preview_sprite, (box_left.centerx - preview_sprite.get_width() // 2, box_left.y + 40))
    c_name_surf = get_font(20, bold=True).render(char_info["name"], True, COLOR_WHITE)
    surface.blit(c_name_surf, c_name_surf.get_rect(center=(box_left.centerx, box_left.bottom - 60)))
    click_hint = get_font(14, bold=False).render("(Click 'Select Character' to change)", True, COLOR_TEXT_MUTED)
    surface.blit(click_hint, click_hint.get_rect(center=(box_left.centerx, box_left.bottom - 25)))

    for btn in buttons:
        btn.draw(surface)

    hint_surf = get_font(16, bold=False).render(
        "Controls:  [A/D] or [Arrows] Move  |  [Space/W] Jump / Double Jump  |  [ESC] Pause  |  [R] Restart  |  [M] Audio",
        True, COLOR_TEXT_MUTED
    )
    surface.blit(hint_surf, hint_surf.get_rect(center=(cx, HEIGHT - 25)))

def draw_character_select(surface, selected_character, back_button):
    menu_bg, bg_img = sprites.get_background("Purple.png", WIDTH, HEIGHT)
    for tile in menu_bg:
        surface.blit(bg_img, tile)

    back_button.draw(surface)

    title_font = get_font(42, bold=True)
    title_surf = title_font.render("CHOOSE YOUR HERO", True, COLOR_ACCENT)
    surface.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, 70)))

    sub_font = get_font(20, bold=False)
    sub_surf = sub_font.render("Each hero possesses unique platforming traits and style!", True, COLOR_WHITE)
    surface.blit(sub_surf, sub_surf.get_rect(center=(WIDTH // 2, 115)))

    card_w, card_h = 220, 360
    start_x = WIDTH // 2 - (4 * card_w + 3 * 20) // 2
    for i, c_name in enumerate(CHARACTER_NAMES):
        cx = start_x + i * (card_w + 20)
        cy = 180
        rect = pygame.Rect(cx, cy, card_w, card_h)
        is_selected = (c_name == selected_character)

        bg_col = (35, 40, 60) if not is_selected else (45, 60, 90)
        border_col = COLOR_ACCENT if is_selected else (80, 90, 120)
        border_w = 4 if is_selected else 2

        pygame.draw.rect(surface, bg_col, rect, border_radius=16)
        pygame.draw.rect(surface, border_col, rect, width=border_w, border_radius=16)

        info = CHARACTERS[c_name]
        c_sprites = sprites.load_character_sprites(c_name, scale=3)
        frames = c_sprites.get("run_right", c_sprites.get("idle_right"))
        frame_idx = int((pygame.time.get_ticks() / 120) % len(frames))
        spr = frames[frame_idx]
        surface.blit(spr, (rect.centerx - spr.get_width() // 2, rect.y + 30))

        name_surf = get_font(22, bold=True).render(info["name"], True, COLOR_WHITE)
        surface.blit(name_surf, name_surf.get_rect(center=(rect.centerx, rect.y + 145)))

        stat_font = get_font(16, bold=False)
        s_spd = stat_font.render(f"Speed: {info['speed']}", True, COLOR_CYAN)
        s_jmp = stat_font.render(f"Jump: {info['jump']}", True, COLOR_GREEN)
        surface.blit(s_spd, (rect.x + 24, rect.y + 185))
        surface.blit(s_jmp, (rect.x + 24, rect.y + 215))

        words = info["desc"].split(" ")
        line1 = " ".join(words[:len(words)//2])
        line2 = " ".join(words[len(words)//2:])
        d1_surf = get_font(14, bold=False).render(line1, True, COLOR_TEXT_MUTED)
        d2_surf = get_font(14, bold=False).render(line2, True, COLOR_TEXT_MUTED)
        surface.blit(d1_surf, (rect.x + 16, rect.y + 250))
        surface.blit(d2_surf, (rect.x + 16, rect.y + 270))

        status_text = "✓ SELECTED" if is_selected else "CLICK TO SELECT"
        status_col = COLOR_ACCENT if is_selected else (120, 130, 150)
        st_surf = get_font(16, bold=True).render(status_text, True, status_col)
        surface.blit(st_surf, st_surf.get_rect(center=(rect.centerx, rect.bottom - 30)))

def draw_level_select(surface, unlocked_level, stars_dict, back_button):
    menu_bg, bg_img = sprites.get_background("Gray.png", WIDTH, HEIGHT)
    for tile in menu_bg:
        surface.blit(bg_img, tile)

    back_button.draw(surface)

    title_font = get_font(42, bold=True)
    title_surf = title_font.render("SELECT ADVENTURE LEVEL", True, COLOR_ACCENT)
    surface.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, 70)))

    card_w, card_h = 180, 260
    tot_levels = levels.total_levels()
    total_w = tot_levels * card_w + (tot_levels - 1) * 20
    start_x = WIDTH // 2 - total_w // 2

    for i in range(tot_levels):
        cx = start_x + i * (card_w + 20)
        cy = 220
        rect = pygame.Rect(cx, cy, card_w, card_h)
        is_unlocked = (i < unlocked_level)

        bg_col = (35, 42, 60) if is_unlocked else (25, 26, 32)
        border_col = COLOR_GREEN if is_unlocked else (60, 65, 75)
        pygame.draw.rect(surface, bg_col, rect, border_radius=16)
        pygame.draw.rect(surface, border_col, rect, width=3 if is_unlocked else 2, border_radius=16)

        num_surf = get_font(42, bold=True).render(f"{i + 1}", True, COLOR_WHITE if is_unlocked else (90, 95, 110))
        surface.blit(num_surf, num_surf.get_rect(center=(rect.centerx, rect.y + 60)))

        lvl_meta = levels.get_level(i)
        name_parts = lvl_meta["name"].split(" ")
        p1 = name_parts[0]
        p2 = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        n1_surf = get_font(18, bold=True).render(p1, True, COLOR_ACCENT if is_unlocked else (90, 95, 110))
        n2_surf = get_font(18, bold=True).render(p2, True, COLOR_ACCENT if is_unlocked else (90, 95, 110))
        surface.blit(n1_surf, n1_surf.get_rect(center=(rect.centerx, rect.y + 115)))
        surface.blit(n2_surf, n2_surf.get_rect(center=(rect.centerx, rect.y + 138)))

        stars_earned = stars_dict.get(str(i + 1), 0)
        star_str = "★ " * stars_earned + "☆ " * (3 - stars_earned)
        star_surf = get_font(24, bold=True).render(star_str.strip(), True, COLOR_ACCENT if is_unlocked else (80, 80, 90))
        surface.blit(star_surf, star_surf.get_rect(center=(rect.centerx, rect.y + 185)))

        btn_txt = "PLAY" if is_unlocked else "LOCKED"
        btn_col = COLOR_GREEN if is_unlocked else (100, 100, 110)
        st_surf = get_font(18, bold=True).render(btn_txt, True, btn_col)
        surface.blit(st_surf, st_surf.get_rect(center=(rect.centerx, rect.bottom - 30)))
