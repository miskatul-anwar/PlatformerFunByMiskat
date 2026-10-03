import random
import pygame
from src.platformer.config import BLOCK_SIZE
from src.platformer.graphics import sprites

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, style="grass_top", size=BLOCK_SIZE):
        super().__init__()
        self.image = sprites.get_terrain_tile(style, size)
        self.rect = pygame.Rect(x, y, size, size)
        self.style = style

    def draw(self, win, offset_x=0, offset_y=0):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))

class FallingPlatform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        data = sprites.load_traps(scale=2)["falling_platform"]
        self.off_frames = data["off"]
        self.on_frames = data["on"]
        self.image = self.on_frames[0]
        self.rect = pygame.Rect(x, y, 64, 20)
        self.origin_x = x
        self.origin_y = y
        self.stepped = False
        self.fall_timer = 0
        self.falling = False
        self.vy = 0.0
        self.respawn_timer = 0
        self.anim_frame = 0.0

    def on_stepped(self, player):
        if not self.stepped and not self.falling:
            self.stepped = True
            self.fall_timer = 25

    def update(self):
        self.anim_frame = (self.anim_frame + 0.25) % len(self.on_frames)
        self.image = self.on_frames[int(self.anim_frame)]

        if self.stepped:
            self.fall_timer -= 1
            self.rect.x = self.origin_x + random.choice([-2, 2])
            if self.fall_timer <= 0:
                self.falling = True
                self.stepped = False
                self.vy = 2.0

        if self.falling:
            self.vy += 0.4
            self.rect.y += int(self.vy)
            if self.rect.y > self.origin_y + 600:
                self.falling = False
                self.respawn_timer = 120
                self.rect.x = -1000
                self.rect.y = -1000

        if self.respawn_timer > 0:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0:
                self.rect.x = self.origin_x
                self.rect.y = self.origin_y
                self.vy = 0.0

    def draw(self, win, offset_x=0, offset_y=0):
        if self.respawn_timer == 0:
            win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))

class MovingPlatform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_range=160, speed=2.0, horizontal=True, style="brown"):
        super().__init__()
        data = sprites.load_traps(scale=2)["moving_platform"]
        self.frames = data[style]
        self.image = self.frames[0]
        self.rect = pygame.Rect(x, y, 64, 16)
        self.start_x = float(x)
        self.start_y = float(y)
        self.pos = float(x if horizontal else y)
        self.move_range = move_range
        self.speed = speed
        self.horizontal = horizontal
        self.anim_frame = 0.0
        self.riders = []

    def on_stepped(self, player):
        if player not in self.riders:
            self.riders.append(player)

    def update(self):
        self.anim_frame = (self.anim_frame + 0.3) % len(self.frames)
        self.image = self.frames[int(self.anim_frame)]

        dx = 0.0
        dy = 0.0
        if self.move_range > 0:
            self.pos += self.speed
            base = self.start_x if self.horizontal else self.start_y
            if self.pos > base + self.move_range or self.pos < base:
                self.speed *= -1

            if self.horizontal:
                new_x = self.pos
                dx = new_x - self.rect.x
                self.rect.x = int(new_x)
            else:
                new_y = self.pos
                dy = new_y - self.rect.y
                self.rect.y = int(new_y)

        for rider in self.riders:
            rider.x += dx
            rider.rect.x = int(rider.x)
            rider.y += dy
            rider.rect.y = int(rider.y)
        self.riders.clear()

    def draw(self, win, offset_x=0, offset_y=0):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))
