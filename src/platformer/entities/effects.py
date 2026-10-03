import pygame
from src.platformer.config import COLOR_ACCENT

class Particle:
    def __init__(self, x, y, vx, vy, image=None, color=None, lifetime=45, size=4, gravity=0.2):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.image = image
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.gravity = gravity

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.lifetime -= 1

    @property
    def alive(self):
        return self.lifetime > 0

    def draw(self, surface, offset_x=0, offset_y=0):
        alpha = max(0, min(255, int(255 * (self.lifetime / self.max_lifetime))))
        px = int(self.x - offset_x)
        py = int(self.y - offset_y)
        if self.image:
            img = self.image.copy()
            img.set_alpha(alpha)
            surface.blit(img, (px, py))
        elif self.color:
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color[:3], alpha), (self.size, self.size), self.size)
            surface.blit(s, (px - self.size, py - self.size))

class FloatingText:
    def __init__(self, x, y, text, color=COLOR_ACCENT, font_size=24, lifetime=45):
        self.x = x
        self.y = y
        self.vy = -1.2
        self.text = text
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        try:
            self.font = pygame.font.SysFont("arial", font_size, bold=True)
        except Exception:
            self.font = pygame.font.Font(None, font_size)

    def update(self):
        self.y += self.vy
        self.lifetime -= 1

    @property
    def alive(self):
        return self.lifetime > 0

    def draw(self, surface, offset_x=0, offset_y=0):
        alpha = max(0, min(255, int(255 * (self.lifetime / self.max_lifetime))))
        text_surf = self.font.render(self.text, True, self.color)
        text_surf.set_alpha(alpha)
        surface.blit(text_surf, (int(self.x - offset_x), int(self.y - offset_y)))
