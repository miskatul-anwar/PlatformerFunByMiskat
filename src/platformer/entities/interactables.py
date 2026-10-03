import random
import pygame
from src.platformer.config import TRAMPOLINE_BOUNCE, FAN_PUSH
from src.platformer.core.sound import SoundManager
from src.platformer.graphics import sprites

class Trampoline(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        data = sprites.load_traps(scale=2)["trampoline"]
        self.idle_frames = data["idle"]
        self.jump_frames = data["jump"]
        self.image = self.idle_frames[0]
        self.rect = pygame.Rect(x, y + 24, 56, 32)
        self.draw_y = y
        self.bouncing = False
        self.anim_frame = 0.0

    def bounce(self, player):
        player.vy = -TRAMPOLINE_BOUNCE
        player.can_double_jump = True
        self.bouncing = True
        self.anim_frame = 0.0
        SoundManager.get_instance().play("trampoline")

    def update(self):
        if self.bouncing:
            self.anim_frame += 0.35
            if self.anim_frame >= len(self.jump_frames):
                self.bouncing = False
                self.image = self.idle_frames[0]
            else:
                self.image = self.jump_frames[int(self.anim_frame)]
        else:
            self.image = self.idle_frames[0]

    def draw(self, win, offset_x=0, offset_y=0):
        win.blit(self.image, (self.rect.x - offset_x, self.draw_y - offset_y))

class Fan(pygame.sprite.Sprite):
    def __init__(self, x, y, lift_height=180):
        super().__init__()
        data = sprites.load_traps(scale=2)["fan"]
        self.on_frames = data["on"]
        self.image = self.on_frames[0]
        self.rect = pygame.Rect(x, y, 48, 16)
        self.lift_height = lift_height
        self.anim_frame = 0.0
        self.wind_particles = []

    def update(self, player):
        self.anim_frame = (self.anim_frame + 0.3) % len(self.on_frames)
        self.image = self.on_frames[int(self.anim_frame)]

        lift_zone = pygame.Rect(self.rect.x - 10, self.rect.y - self.lift_height, self.rect.width + 20, self.lift_height)
        if lift_zone.colliderect(player.rect):
            player.vy -= FAN_PUSH
            if player.vy < -8:
                player.vy = -8
            player.can_double_jump = True

        if random.random() < 0.3:
            self.wind_particles.append([
                self.rect.x + random.randint(4, self.rect.width - 4),
                self.rect.y,
                random.uniform(-4.0, -6.5),
                random.randint(20, 35)
            ])

        for p in self.wind_particles[:]:
            p[1] += p[2]
            p[3] -= 1
            if p[3] <= 0:
                self.wind_particles.remove(p)

    def draw(self, win, offset_x=0, offset_y=0):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))
        for p in self.wind_particles:
            alpha = max(0, min(180, int(p[3] * 6)))
            s = pygame.Surface((3, 6), pygame.SRCALPHA)
            s.fill((255, 255, 255, alpha))
            win.blit(s, (int(p[0] - offset_x), int(p[1] - offset_y)))

class Checkpoint(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        data = sprites.load_checkpoints(scale=2)["checkpoint"]
        self.no_flag = data["no"]
        self.flag_out = data["out"]
        self.flag_idle = data["idle"]
        self.image = self.no_flag[0]
        self.rect = pygame.Rect(x, y, 64, 128)
        self.activated = False
        self.anim_state = "no"
        self.anim_frame = 0.0

    def activate(self):
        if not self.activated:
            self.activated = True
            self.anim_state = "out"
            self.anim_frame = 0.0
            SoundManager.get_instance().play("checkpoint")
            return True
        return False

    def update(self):
        if self.anim_state == "out":
            self.anim_frame += 0.35
            if self.anim_frame >= len(self.flag_out):
                self.anim_state = "idle"
                self.anim_frame = 0.0
                self.image = self.flag_idle[0]
            else:
                self.image = self.flag_out[int(self.anim_frame)]
        elif self.anim_state == "idle":
            self.anim_frame = (self.anim_frame + 0.25) % len(self.flag_idle)
            self.image = self.flag_idle[int(self.anim_frame)]
        else:
            self.image = self.no_flag[0]

    def draw(self, win, offset_x=0, offset_y=0):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))

class LevelEnd(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        data = sprites.load_checkpoints(scale=2)["end"]
        self.idle_frames = data["idle"]
        self.pressed_frames = data["pressed"]
        self.image = self.idle_frames[0]
        self.rect = pygame.Rect(x, y, 64, 128)
        self.reached = False
        self.anim_frame = 0.0

    def reach(self):
        if not self.reached:
            self.reached = True
            self.anim_frame = 0.0
            SoundManager.get_instance().play("win")
            return True
        return False

    def update(self):
        if self.reached:
            if self.anim_frame < len(self.pressed_frames) - 1:
                self.anim_frame += 0.3
            self.image = self.pressed_frames[int(self.anim_frame)]
        else:
            self.image = self.idle_frames[0]

    def draw(self, win, offset_x=0, offset_y=0):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))
