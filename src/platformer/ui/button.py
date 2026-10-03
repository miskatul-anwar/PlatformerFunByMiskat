import pygame
from src.platformer.config import (
    COLOR_WHITE, COLOR_BLUE, COLOR_CYAN, COLOR_RED
)
from src.platformer.core.sound import SoundManager

def get_font(size, bold=True):
    try:
        return pygame.font.SysFont("arial", size, bold=bold)
    except Exception:
        return pygame.font.Font(None, size)

def draw_heart(surface, x, y, size=24, filled=True):
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    color = COLOR_RED if filled else (90, 90, 110)
    r = size // 3
    pygame.draw.circle(s, color, (r, r), r)
    pygame.draw.circle(s, color, (size - r, r), r)
    pygame.draw.polygon(s, color, [(1, r + 2), (size - 1, r + 2), (size // 2, size - 2)])
    if filled:
        pygame.draw.circle(s, (255, 255, 255, 140), (r - 2, r - 2), max(1, r // 3))
    surface.blit(s, (x, y))

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
        shadow_rect = pygame.Rect(self.rect.x + 3, self.rect.y + 4, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, (15, 18, 28, 160), shadow_rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, (255, 255, 255, 60), self.rect, width=2, border_radius=self.border_radius)

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
