import random
import pygame
from src.platformer.config import (
    GRAVITY, MAX_FALL_SPEED, JUMP_FORCE, DOUBLE_JUMP_FORCE,
    COYOTE_TIME, JUMP_BUFFER, INVULN_FRAMES, MAX_HEALTH,
    CHARACTERS
)
from src.platformer.core.sound import SoundManager
from src.platformer.graphics import sprites
from .items import Box
from .effects import Particle

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, character="VirtualGuy"):
        super().__init__()
        self.character = character
        self.sprites = sprites.load_character_sprites(character, scale=2)
        appear_frames, disappear_frames = sprites.load_appear_disappear(scale=2)
        self.appear_frames = appear_frames
        self.disappear_frames = disappear_frames

        char_info = CHARACTERS.get(character, CHARACTERS["VirtualGuy"])
        self.speed = char_info["speed"]
        self.jump_force = char_info["jump"]

        self.rect = pygame.Rect(x + 14, y + 14, 36, 50)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.vx = 0.0
        self.vy = 0.0

        self.direction = "right"
        self.on_ground = False
        self.can_double_jump = True
        self.coyote_timer = 0
        self.jump_buffer_timer = 0
        self.is_wall_sliding = False
        self.wall_dir = 0

        self.health = MAX_HEALTH
        self.invuln_timer = 0
        self.is_dead = False
        self.death_timer = 0

        self.anim_state = "idle"
        self.anim_frame = 0.0
        self.anim_speed = 0.25
        self.image = self.sprites["idle_right"][0]

        self.is_spawning = True
        self.spawn_frame = 0.0
        self.sound = SoundManager.get_instance()

    def set_pos(self, x, y):
        self.rect.x = x
        self.rect.y = y
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

    def reset(self, x, y):
        self.rect.x = x + 14
        self.rect.y = y + 14
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.vx = 0.0
        self.vy = 0.0
        self.health = MAX_HEALTH
        self.invuln_timer = 0
        self.is_dead = False
        self.death_timer = 0
        self.is_spawning = True
        self.spawn_frame = 0.0
        self.can_double_jump = True

    def take_damage(self, amount=1, knockback_dir=0):
        if self.invuln_timer > 0 or self.is_dead or self.is_spawning:
            return False

        self.health -= amount
        self.sound.play("hit")
        self.invuln_timer = INVULN_FRAMES

        if knockback_dir != 0:
            self.vx = knockback_dir * 5.0
        else:
            self.vx = -4.0 if self.direction == "right" else 4.0
        self.vy = -6.0

        if self.health <= 0:
            self.die()
        return True

    def die(self):
        if not self.is_dead:
            self.is_dead = True
            self.death_timer = 40
            self.sound.play("game_over")

    def jump(self):
        if self.is_dead or self.is_spawning:
            return

        if self.on_ground or self.coyote_timer > 0:
            self.vy = -self.jump_force
            self.coyote_timer = 0
            self.on_ground = False
            self.sound.play("jump")
        elif self.is_wall_sliding and self.wall_dir != 0:
            self.vy = -self.jump_force * 0.95
            self.vx = -self.wall_dir * self.speed * 1.2
            self.direction = "right" if self.vx > 0 else "left"
            self.sound.play("jump")
        elif self.can_double_jump:
            self.vy = -DOUBLE_JUMP_FORCE
            self.can_double_jump = False
            self.sound.play("double_jump")
        else:
            self.jump_buffer_timer = JUMP_BUFFER

    def release_jump(self):
        if self.vy < -3.0:
            self.vy *= 0.5

    def update_horizontal(self, keys, blocks):
        if self.is_dead or self.is_spawning:
            self.vx = 0.0
            return

        move_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        move_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]

        target_vx = 0.0
        if move_left and not move_right:
            target_vx = -self.speed
            self.direction = "left"
        elif move_right and not move_left:
            target_vx = self.speed
            self.direction = "right"

        accel = 0.8 if self.on_ground else 0.4
        self.vx += (target_vx - self.vx) * accel

        self.x += self.vx
        self.rect.x = int(self.x)

        for block in blocks:
            if self.rect.colliderect(block.rect):
                if self.vx > 0:
                    self.rect.right = block.rect.left
                    self.x = float(self.rect.x)
                    self.vx = 0
                elif self.vx < 0:
                    self.rect.left = block.rect.right
                    self.x = float(self.rect.x)
                    self.vx = 0

    def update_vertical(self, blocks, platforms, boxes, particles):
        if self.is_spawning:
            self.spawn_frame += 0.3
            if self.spawn_frame >= len(self.appear_frames):
                self.is_spawning = False
            return

        if self.is_dead:
            self.death_timer -= 1
            return

        if self.invuln_timer > 0:
            self.invuln_timer -= 1
        if self.coyote_timer > 0:
            self.coyote_timer -= 1
        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= 1
            if self.on_ground:
                self.jump()

        self.is_wall_sliding = False
        self.wall_dir = 0
        if not self.on_ground and self.vy > 0:
            for b in blocks:
                if self.rect.top < b.rect.bottom and self.rect.bottom > b.rect.top:
                    if abs(self.rect.right - b.rect.left) <= 3 and self.vx >= 0:
                        self.is_wall_sliding = True
                        self.wall_dir = 1
                        break
                    elif abs(self.rect.left - b.rect.right) <= 3 and self.vx <= 0:
                        self.is_wall_sliding = True
                        self.wall_dir = -1
                        break

        max_fall = 3.0 if self.is_wall_sliding else MAX_FALL_SPEED
        self.vy = min(max_fall, self.vy + GRAVITY)

        old_bottom = self.rect.bottom
        self.y += self.vy
        self.rect.y = int(self.y)

        was_on_ground = self.on_ground
        self.on_ground = False

        all_solids = list(blocks) + [b for b in boxes if not b.broken]
        for solid in all_solids:
            if self.rect.colliderect(solid.rect):
                if self.vy > 0:
                    self.rect.bottom = solid.rect.top
                    self.y = float(self.rect.y)
                    self.vy = 0
                    self.on_ground = True
                    self.can_double_jump = True
                    self.coyote_timer = COYOTE_TIME
                elif self.vy < 0:
                    self.rect.top = solid.rect.bottom
                    self.y = float(self.rect.y)
                    self.vy = 0
                    if isinstance(solid, Box):
                        solid.hit()

        for plat in platforms:
            if plat.rect.colliderect(self.rect):
                if self.vy > 0 and old_bottom <= plat.rect.top + 10:
                    self.rect.bottom = plat.rect.top
                    self.y = float(self.rect.y)
                    self.vy = 0
                    self.on_ground = True
                    self.can_double_jump = True
                    self.coyote_timer = COYOTE_TIME
                    plat.on_stepped(self)

        if not was_on_ground and self.on_ground:
            for _ in range(3):
                particles.append(Particle(
                    self.rect.centerx + random.uniform(-10, 10),
                    self.rect.bottom,
                    random.uniform(-1.5, 1.5),
                    random.uniform(-1.0, -0.2),
                    color=(200, 200, 200),
                    lifetime=18,
                    size=3,
                    gravity=0.05
                ))

        self.update_animation()

    def update_animation(self):
        if self.is_dead:
            return

        if self.invuln_timer > 0:
            anim = "hit"
            speed = 0.2
        elif self.is_wall_sliding:
            anim = "wall_jump"
            speed = 0.2
        elif not self.on_ground:
            if self.vy < 0:
                anim = "double_jump" if not self.can_double_jump else "jump"
            else:
                anim = "fall"
            speed = 0.2
        elif abs(self.vx) > 0.5:
            anim = "run"
            speed = 0.3
        else:
            anim = "idle"
            speed = 0.2

        if anim != self.anim_state:
            self.anim_state = anim
            self.anim_frame = 0.0

        key = f"{self.anim_state}_{self.direction}"
        frames = self.sprites.get(key, self.sprites.get(f"idle_{self.direction}"))
        self.anim_frame = (self.anim_frame + speed) % len(frames)
        self.image = frames[int(self.anim_frame)]

    def draw(self, win, offset_x=0, offset_y=0):
        px = self.rect.centerx - 32 - offset_x
        py = self.rect.bottom - 64 - offset_y

        if self.is_spawning:
            idx = min(int(self.spawn_frame), len(self.appear_frames) - 1)
            ax = self.rect.centerx - 48 - offset_x
            ay = self.rect.bottom - 76 - offset_y
            win.blit(self.appear_frames[idx], (ax, ay))
            return

        if self.is_dead:
            progress = max(0, 40 - self.death_timer) / 40.0
            idx = min(int(progress * len(self.disappear_frames)), len(self.disappear_frames) - 1)
            ax = self.rect.centerx - 48 - offset_x
            ay = self.rect.bottom - 76 - offset_y
            win.blit(self.disappear_frames[idx], (ax, ay))
            return

        if self.invuln_timer > 0 and (self.invuln_timer // 4) % 2 == 1:
            return

        win.blit(self.image, (px, py))
