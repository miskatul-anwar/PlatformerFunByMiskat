import math
import pygame
from constants import (
    WIDTH, HEIGHT, COLOR_WHITE, COLOR_BLACK, COLOR_ACCENT,
    COLOR_GREEN, COLOR_RED, COLOR_BLUE, COLOR_CYAN, COLOR_PURPLE,
    COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_PANEL, CHARACTERS, CHARACTER_NAMES
)
from sound import SoundManager
import sprites

def get_font(size, bold=True):
    try:
        return pygame.font.SysFont("arial", size, bold=bold)
    except Exception:
        return pygame.font.Font(None, size)

class Button:
    def __init__(self, x, y, width, height, text, bg_color=COLOR_BLUE, hover_color=COLOR_CYAN, text_color=COLOR_WHITE, font_size=24, border_radius=10, icon=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_radius = border_radius
        self.font = get_font(font_size, bold=True)
        self.icon = icon
        self.hovered = False

    def check_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        return self.hovered

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.check_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                SoundManager.get_instance().play("click")
                return True
        return False

    def draw(self, surface):
        color = self.hover_color if self.hovered else self.bg_color
        # Shadow
        shadow_rect = pygame.Rect(self.rect.x + 3, self.rect.y + 4, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, (15, 18, 28, 160), shadow_rect, border_radius=self.border_radius)
        # Main Button
        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, (255, 255, 255, 60), self.rect, width=2, border_radius=self.border_radius)

        # Content
        text_surf = self.font.render(self.text, True, self.text_color)
        if self.icon:
            total_w = self.icon.get_width() + 8 + text_surf.get_width()
            start_x = self.rect.centerx - total_w // 2
            icon_y = self.rect.centery - self.icon.get_height() // 2
            surface.blit(self.icon, (start_x, icon_y))
            surface.blit(text_surf, (start_x + self.icon.get_width() + 8, self.rect.centery - text_surf.get_height() // 2))
        else:
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

def draw_heart(surface, x, y, size=24, filled=True):
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    color = COLOR_RED if filled else (90, 90, 110)
    r = size // 3
    pygame.draw.circle(s, color, (r, r), r)
    pygame.draw.circle(s, color, (size - r, r), r)
    pygame.draw.polygon(s, color, [(1, r + 2), (size - 1, r + 2), (size // 2, size - 2)])
    if filled:
        # Highlight gloss
        pygame.draw.circle(s, (255, 255, 255, 140), (r - 2, r - 2), max(1, r // 3))
    surface.blit(s, (x, y))

def draw_hud(surface, player, fruits_collected, total_fruits, score, level_name, elapsed_seconds, lives):
    hud_surf = pygame.Surface((WIDTH, 60), pygame.SRCALPHA)
    hud_surf.fill((20, 24, 38, 180))
    surface.blit(hud_surf, (0, 0))

    # Health Hearts
    for i in range(3):
        draw_heart(surface, 20 + i * 32, 16, size=26, filled=(i < player.health))

    # Lives
    font_sm = get_font(18, bold=True)
    lives_surf = font_sm.render(f"Lives: {lives}", True, COLOR_TEXT_MUTED)
    surface.blit(lives_surf, (126, 20))

    # Level Name
    font_md = get_font(22, bold=True)
    lvl_surf = font_md.render(level_name, True, COLOR_ACCENT)
    lvl_rect = lvl_surf.get_rect(center=(WIDTH // 2, 20))
    surface.blit(lvl_surf, lvl_rect)

    # Timer
    mins = int(elapsed_seconds) // 60
    secs = int(elapsed_seconds) % 60
    time_surf = font_sm.render(f"Time: {mins:02d}:{secs:02d}", True, COLOR_TEXT)
    surface.blit(time_surf, (WIDTH // 2 - time_surf.get_width() // 2, 38))

    # Fruits Counter
    apple_img, _ = sprites.load_fruit_sprites("Apple", scale=1)
    if apple_img:
        surface.blit(apple_img[0], (WIDTH - 250, 14))
    fruit_text = font_md.render(f"{fruits_collected}/{total_fruits}", True, COLOR_TEXT)
    surface.blit(fruit_text, (WIDTH - 215, 18))

    # Score
    score_surf = font_md.render(f"Score: {score}", True, COLOR_WHITE)
    surface.blit(score_surf, (WIDTH - 130, 18))

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

    # Star Rating Display
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
        f"Congratulations! You completed all 5 adventure stages!",
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
