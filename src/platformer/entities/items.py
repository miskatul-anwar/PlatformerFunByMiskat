import math
import random
import pygame
from src.platformer.core.sound import SoundManager
from src.platformer.graphics import sprites

class Fruit(pygame.sprite.Sprite):
    FRUIT_TYPES = ["Apple", "Bananas", "Cherries", "Kiwi", "Melon", "Orange", "Pineapple", "Strawberry"]

    def __init__(self, x, y, fruit_type=None):
        super().__init__()
        self.fruit_type = fruit_type or random.choice(self.FRUIT_TYPES)
        self.frames, self.collected_frames = sprites.load_fruit_sprites(self.fruit_type, scale=2)
        self.image = self.frames[0]
        self.rect = pygame.Rect(x + 16, y + 16, 32, 32)
        self.base_y = float(self.rect.y)
        self.anim_frame = random.uniform(0, len(self.frames))
        self.bob_time = random.uniform(0, 6.28)
        self.collected = False
        self.collected_frame = 0.0
        self.alive = True

    def update(self):
        if self.collected:
            self.collected_frame += 0.3
            if self.collected_frame >= len(self.collected_frames):
                self.alive = False
            else:
                self.image = self.collected_frames[int(self.collected_frame)]
        else:
            self.anim_frame = (self.anim_frame + 0.25) % len(self.frames)
            self.image = self.frames[int(self.anim_frame)]
            self.bob_time += 0.06
            self.rect.y = int(self.base_y + math.sin(self.bob_time) * 5)

    def collect(self):
        if not self.collected:
            self.collected = True
            SoundManager.get_instance().play("fruit")
            return 100
        return 0

    def draw(self, win, offset_x=0, offset_y=0):
        if self.alive:
            win.blit(self.image, (self.rect.centerx - 32 - offset_x, self.rect.centery - 32 - offset_y))

class Box(pygame.sprite.Sprite):
    def __init__(self, x, y, box_type="Box1", fruit_type="Apple"):
        super().__init__()
        self.idle_frames, self.hit_frames, self.break_frames = sprites.load_box_sprites(box_type, scale=2)
        self.image = self.idle_frames[0]
        self.rect = pygame.Rect(x, y, 56, 48)
        self.hits_left = 2
        self.broken = False
        self.is_hit = False
        self.anim_frame = 0.0
        self.fruit_type = fruit_type

    def hit(self):
        if self.broken:
            return None
        self.hits_left -= 1
        self.is_hit = True
        self.anim_frame = 0.0
        SoundManager.get_instance().play("box_break")
        if self.hits_left <= 0:
            self.broken = True
            return Fruit(self.rect.x + 12, self.rect.y - 48, self.fruit_type)
        return None

    def update(self):
        if self.broken:
            if self.anim_frame < len(self.break_frames) - 1:
                self.anim_frame += 0.25
                self.image = self.break_frames[int(self.anim_frame)]
        elif self.is_hit:
            self.anim_frame += 0.3
            if self.anim_frame >= len(self.hit_frames):
                self.is_hit = False
                self.image = self.idle_frames[0]
            else:
                self.image = self.hit_frames[int(self.anim_frame)]
        else:
            self.image = self.idle_frames[0]

    def draw(self, win, offset_x=0, offset_y=0):
        if not (self.broken and self.anim_frame >= len(self.break_frames) - 1):
            win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))
