import random
import math
import pygame
from constants import (
    BLOCK_SIZE, GRAVITY, MAX_FALL_SPEED, PLAYER_SPEED,
    JUMP_FORCE, DOUBLE_JUMP_FORCE, TRAMPOLINE_BOUNCE, FAN_PUSH,
    COYOTE_TIME, JUMP_BUFFER, INVULN_FRAMES, MAX_HEALTH,
    CHARACTERS, COLOR_WHITE, COLOR_ACCENT
)
from sound import SoundManager
import sprites

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
        self.font = pygame.font.SysFont("arial", font_size, bold=True)

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

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, style="grass_top", size=BLOCK_SIZE):
        super().__init__()
        self.image = sprites.get_terrain_tile(style, size)
        self.rect = pygame.Rect(x, y, size, size)
        self.style = style

    def draw(self, win, offset_x=0, offset_y=0):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, character="VirtualGuy"):
        super().__init__()
        self.character = character
        self.sprites = sprites.load_character_sprites(character, scale=2)
        appear_frames, disappear_frames = sprites.load_appear_disappear(scale=2)
        self.appear_frames = appear_frames
        self.disappear_frames = disappear_frames

        # Stats
        char_info = CHARACTERS.get(character, CHARACTERS["VirtualGuy"])
        self.speed = char_info["speed"]
        self.jump_force = char_info["jump"]

        # Physics hitbox: tuned to 36x50 inside the 64x64 sprite for tight platforming
        self.rect = pygame.Rect(x + 14, y + 14, 36, 50)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.vx = 0.0
        self.vy = 0.0

        # State
        self.direction = "right"
        self.on_ground = False
        self.can_double_jump = True
        self.coyote_timer = 0
        self.jump_buffer_timer = 0
        self.is_wall_sliding = False
        self.wall_dir = 0

        # Health & Invulnerability
        self.health = MAX_HEALTH
        self.invuln_timer = 0
        self.is_dead = False
        self.death_timer = 0

        # Animations
        self.anim_state = "idle"
        self.anim_frame = 0.0
        self.anim_speed = 0.25
        self.image = self.sprites["idle_right"][0]

        # Spawning animation
        self.is_spawning = True
        self.spawn_frame = 0.0

        # Sounds
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

        # Knockback
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

        # Ground or coyote jump
        if self.on_ground or self.coyote_timer > 0:
            self.vy = -self.jump_force
            self.coyote_timer = 0
            self.on_ground = False
            self.sound.play("jump")
        # Wall jump
        elif self.is_wall_sliding and self.wall_dir != 0:
            self.vy = -self.jump_force * 0.95
            self.vx = -self.wall_dir * self.speed * 1.2
            self.direction = "right" if self.vx > 0 else "left"
            self.sound.play("jump")
        # Double jump
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

        # Horizontal input
        target_vx = 0.0
        if move_left and not move_right:
            target_vx = -self.speed
            self.direction = "left"
        elif move_right and not move_left:
            target_vx = self.speed
            self.direction = "right"

        # Acceleration / deceleration
        accel = 0.8 if self.on_ground else 0.4
        self.vx += (target_vx - self.vx) * accel

        # Move X
        self.x += self.vx
        self.rect.x = int(self.x)

        # Check horizontal collisions
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

        # Timers
        if self.invuln_timer > 0:
            self.invuln_timer -= 1
        if self.coyote_timer > 0:
            self.coyote_timer -= 1
        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= 1
            if self.on_ground:
                self.jump()

        # Wall slide check
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

        # Gravity
        max_fall = 3.0 if self.is_wall_sliding else MAX_FALL_SPEED
        self.vy = min(max_fall, self.vy + GRAVITY)

        old_bottom = self.rect.bottom
        self.y += self.vy
        self.rect.y = int(self.y)

        was_on_ground = self.on_ground
        self.on_ground = False

        # Collisions with solid blocks
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
                    # Hit box from below!
                    if isinstance(solid, Box):
                        solid.hit()

        # Collisions with one-way platforms (Moving and Falling platforms)
        for plat in platforms:
            if plat.rect.colliderect(self.rect):
                # Only land if falling downward and player's feet were above platform top previously
                if self.vy > 0 and old_bottom <= plat.rect.top + 10:
                    self.rect.bottom = plat.rect.top
                    self.y = float(self.rect.y)
                    self.vy = 0
                    self.on_ground = True
                    self.can_double_jump = True
                    self.coyote_timer = COYOTE_TIME
                    plat.on_stepped(self)

        # Landed dust particles
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
            # appear sprite is 96x96
            ax = self.rect.centerx - 48 - offset_x
            ay = self.rect.bottom - 76 - offset_y
            win.blit(self.appear_frames[idx], (ax, ay))
            return

        if self.is_dead:
            # disappear animation (96x96)
            progress = max(0, 40 - self.death_timer) / 40.0
            idx = min(int(progress * len(self.disappear_frames)), len(self.disappear_frames) - 1)
            ax = self.rect.centerx - 48 - offset_x
            ay = self.rect.bottom - 76 - offset_y
            win.blit(self.disappear_frames[idx], (ax, ay))
            return

        # Invulnerability flicker
        if self.invuln_timer > 0 and (self.invuln_timer // 4) % 2 == 1:
            return

        win.blit(self.image, (px, py))

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

        # Check if player is above the fan
        lift_zone = pygame.Rect(self.rect.x - 10, self.rect.y - self.lift_height, self.rect.width + 20, self.lift_height)
        if lift_zone.colliderect(player.rect):
            player.vy -= FAN_PUSH
            if player.vy < -8:
                player.vy = -8
            player.can_double_jump = True

        # Wind particle effects
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
            # Shake effect
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

        # Move any players standing on top
        for rider in self.riders:
            rider.x += dx
            rider.rect.x = int(rider.x)
            rider.y += dy
            rider.rect.y = int(rider.y)
        self.riders.clear()

    def draw(self, win, offset_x=0, offset_y=0):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))

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
