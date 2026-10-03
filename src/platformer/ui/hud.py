import pygame
from src.platformer.config import (
    WIDTH, COLOR_ACCENT, COLOR_WHITE, COLOR_TEXT, COLOR_TEXT_MUTED
)
from src.platformer.graphics import sprites
from .button import get_font, draw_heart

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
