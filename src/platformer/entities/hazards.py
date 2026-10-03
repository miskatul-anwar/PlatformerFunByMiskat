import random
import pygame
from src.platformer.graphics import sprites

class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y, size=32):
        super().__init__()
        trap_data = sprites.load_traps(scale=2)
        raw_spike = trap_data["spike"][0]
        self.image = pygame.transform.scale(raw_spike, (size, size))
        self.rect = pygame.Rect(x, y + (size // 2), size, size // 2)
        self.draw_y = y

    def draw(self, win, offset_x=0, offset_y=0):
        win.blit(self.image, (self.rect.x - offset_x, self.draw_y - offset_y))

class Saw(pygame.sprite.Sprite):
    def __init__(self, x, y, move_range=160, speed=2.5, horizontal=True):
        super().__init__()
        self.frames = sprites.load_traps(scale=2)["saw"]
        self.image = self.frames[0]
        self.rect = pygame.Rect(x + 12, y + 12, 52, 52)
        self.start_x = float(x)
        self.start_y = float(y)
        self.pos = float(x if horizontal else y)
        self.move_range = move_range
        self.speed = speed
        self.horizontal = horizontal
        self.anim_frame = 0.0

    def update(self):
        self.anim_frame = (self.anim_frame + 0.4) % len(self.frames)
        self.image = self.frames[int(self.anim_frame)]

        if self.move_range > 0:
            self.pos += self.speed
            base = self.start_x if self.horizontal else self.start_y
            if self.pos > base + self.move_range or self.pos < base:
                self.speed *= -1

            if self.horizontal:
                self.rect.x = int(self.pos) + 12
            else:
                self.rect.y = int(self.pos) + 12

    def draw(self, win, offset_x=0, offset_y=0):
        px = self.rect.centerx - 38 - offset_x
        py = self.rect.centery - 38 - offset_y
        win.blit(self.image, (px, py))

class Fire(pygame.sprite.Sprite):
    def __init__(self, x, y, on_duration=100, off_duration=70):
        super().__init__()
        trap_data = sprites.load_traps(scale=2)["fire"]
        self.off_frames = trap_data["off"]
        self.on_frames = trap_data["on"]
        self.hit_frames = trap_data["hit"]
        self.image = self.on_frames[0]
        self.rect = pygame.Rect(x + 6, y, 20, 64)
        self.x = x
        self.y = y
        self.on_duration = on_duration
        self.off_duration = off_duration
        self.timer = random.randint(0, on_duration + off_duration)
        self.is_on = True
        self.anim_frame = 0.0

    def update(self):
        self.timer = (self.timer + 1) % (self.on_duration + self.off_duration)
        self.is_on = self.timer < self.on_duration

        if self.is_on:
            self.anim_frame = (self.anim_frame + 0.3) % len(self.on_frames)
            self.image = self.on_frames[int(self.anim_frame)]
        else:
            self.image = self.off_frames[0]

    def draw(self, win, offset_x=0, offset_y=0):
        win.blit(self.image, (self.x - offset_x, self.y - offset_y))
