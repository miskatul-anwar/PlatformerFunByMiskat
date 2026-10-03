import os
import sys
import random
import pygame

from src.platformer.config import (
    WIDTH, HEIGHT, FPS, BLOCK_SIZE, TITLE, ASSETS_DIR,
    STATE_MENU, STATE_CHAR_SELECT, STATE_LEVEL_SELECT,
    STATE_PLAYING, STATE_PAUSED, STATE_LEVEL_CLEAR,
    STATE_GAME_OVER, STATE_VICTORY,
    CHARACTERS, CHARACTER_NAMES,
    COLOR_GREEN, COLOR_RED, COLOR_BLUE, COLOR_CYAN, COLOR_PURPLE,
    COLOR_WHITE, COLOR_ACCENT
)
from src.platformer.core.sound import SoundManager
from src.platformer.core.storage import load_save_data, write_save_data
from src.platformer.graphics import sprites
from src.platformer.levels import levels
from src.platformer import ui
from src.platformer.entities import (
    Player, Block, Fruit, Box, Fire, Spike, Saw,
    Trampoline, Fan, FallingPlatform, MovingPlatform,
    Checkpoint, LevelEnd, Particle, FloatingText
)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)

        try:
            icon_img = sprites.get_image(ASSETS_DIR / "Items" / "Fruits" / "Apple.png")
            icon_sub = icon_img.subsurface(pygame.Rect(0, 0, 32, 32))
            pygame.display.set_icon(icon_sub)
        except Exception:
            pass

        self.clock = pygame.time.Clock()
        self.sound = SoundManager.get_instance()
        self.save_data = load_save_data()

        self.state = STATE_MENU
        self.selected_character = "VirtualGuy"
        self.current_level_idx = 0
        self.total_score = 0
        self.level_score = 0
        self.lives = 3
        self.level_time = 0.0
        self.total_game_time = 0.0

        self.camera_x = 0.0
        self.camera_y = 0.0
        self.screen_shake = 0

        self.particles = []
        self.floating_texts = []

        self.player = None
        self.blocks = []
        self.fruits = []
        self.boxes = []
        self.fires = []
        self.spikes = []
        self.saws = []
        self.trampolines = []
        self.fans = []
        self.falling_platforms = []
        self.moving_platforms = []
        self.checkpoints = []
        self.level_end = None
        self.level_data = None
        self.fruits_collected = 0
        self.total_fruits = 0
        self.respawn_pos = (100, 100)

        self._init_buttons()
        self.sound.start_music()

    def _init_buttons(self):
        cx = WIDTH // 2
        # Menu buttons
        self.btn_play = ui.Button(cx - 150, 290, 300, 52, "PLAY GAME", bg_color=COLOR_GREEN, hover_color=(46, 204, 113), font_size=26)
        self.btn_select_level = ui.Button(cx - 150, 360, 300, 52, "SELECT LEVEL", bg_color=COLOR_BLUE, hover_color=COLOR_CYAN, font_size=24)
        self.btn_select_char = ui.Button(cx - 150, 430, 300, 52, "SELECT CHARACTER", bg_color=COLOR_PURPLE, hover_color=(170, 150, 220), font_size=24)
        self.btn_sound_toggle = ui.Button(cx - 150, 500, 300, 48, "AUDIO: ON" if self.sound.enabled else "AUDIO: OFF", bg_color=(80, 90, 110), hover_color=(110, 120, 140), font_size=20)
        self.btn_quit = ui.Button(cx - 150, 565, 300, 48, "QUIT", bg_color=(120, 50, 50), hover_color=COLOR_RED, font_size=22)

        # Pause buttons
        self.btn_pause_resume = ui.Button(cx - 130, HEIGHT // 2 - 60, 260, 48, "RESUME", bg_color=COLOR_GREEN, hover_color=(46, 204, 113))
        self.btn_pause_restart = ui.Button(cx - 130, HEIGHT // 2 + 5, 260, 48, "RESTART", bg_color=COLOR_BLUE, hover_color=COLOR_CYAN)
        self.btn_pause_level_select = ui.Button(cx - 130, HEIGHT // 2 + 70, 260, 48, "LEVEL SELECT", bg_color=COLOR_PURPLE, hover_color=(170, 150, 220))
        self.btn_pause_menu = ui.Button(cx - 130, HEIGHT // 2 + 135, 260, 48, "MAIN MENU", bg_color=(80, 90, 110), hover_color=(110, 120, 140))

        # Level Clear buttons
        self.btn_clear_next = ui.Button(cx - 130, HEIGHT // 2 + 80, 260, 48, "NEXT LEVEL", bg_color=COLOR_GREEN, hover_color=(46, 204, 113))
        self.btn_clear_retry = ui.Button(cx - 130, HEIGHT // 2 + 140, 260, 44, "REPLAY LEVEL", bg_color=COLOR_BLUE, hover_color=COLOR_CYAN)
        self.btn_clear_menu = ui.Button(cx - 130, HEIGHT // 2 + 195, 260, 44, "MAIN MENU", bg_color=(80, 90, 110), hover_color=(110, 120, 140))

        # Game Over buttons
        self.btn_gameover_retry = ui.Button(cx - 130, HEIGHT // 2 + 15, 260, 50, "TRY AGAIN", bg_color=COLOR_GREEN, hover_color=(46, 204, 113))
        self.btn_gameover_menu = ui.Button(cx - 130, HEIGHT // 2 + 80, 260, 50, "MAIN MENU", bg_color=(80, 90, 110), hover_color=(110, 120, 140))

        # Victory buttons
        self.btn_vic_again = ui.Button(cx - 140, HEIGHT // 2 + 105, 280, 52, "PLAY AGAIN", bg_color=COLOR_GREEN, hover_color=(46, 204, 113), font_size=24)
        self.btn_vic_menu = ui.Button(cx - 140, HEIGHT // 2 + 170, 280, 48, "MAIN MENU", bg_color=COLOR_BLUE, hover_color=COLOR_CYAN, font_size=22)

        # Navigation buttons
        self.btn_char_back = ui.Button(40, 30, 120, 44, "← BACK", bg_color=(60, 65, 85), hover_color=COLOR_CYAN, font_size=20)
        self.btn_lvl_back = ui.Button(40, 30, 120, 44, "← BACK", bg_color=(60, 65, 85), hover_color=COLOR_CYAN, font_size=20)

    def load_level(self, level_idx):
        self.current_level_idx = level_idx
        self.level_data = levels.get_level(level_idx)
        self.level_score = 0
        self.level_time = 0.0
        self.fruits_collected = 0
        self.particles.clear()
        self.floating_texts.clear()
        self.screen_shake = 0

        self.bg_tiles, self.bg_image = sprites.get_background(self.level_data["bg_image"], WIDTH, HEIGHT)

        sp = self.level_data["start_pos"]
        self.respawn_pos = sp
        self.player = Player(sp[0], sp[1], self.selected_character)

        self.blocks = [Block(bx, by, b_style) for bx, by, b_style in self.level_data["blocks"]]
        self.fruits = [Fruit(fx, fy, f_type) for fx, fy, f_type in self.level_data["fruits"]]
        self.total_fruits = len(self.fruits)

        self.boxes = [Box(bx, by, b_type, f_drop) for bx, by, b_type, f_drop in self.level_data["boxes"]]
        self.spikes = [Spike(sx, sy) for sx, sy in self.level_data["spikes"]]
        self.fires = [Fire(fx, fy) for fx, fy in self.level_data["fires"]]
        self.saws = [Saw(sx, sy, rng, spd, horiz) for sx, sy, rng, spd, horiz in self.level_data["saws"]]
        self.trampolines = [Trampoline(tx, ty) for tx, ty in self.level_data["trampolines"]]
        self.fans = [Fan(fx, fy, h) for fx, fy, h in self.level_data["fans"]]
        self.falling_platforms = [FallingPlatform(fx, fy) for fx, fy in self.level_data["falling_platforms"]]
        self.moving_platforms = [MovingPlatform(mx, my, rng, spd, horiz, style) for mx, my, rng, spd, horiz, style in self.level_data["moving_platforms"]]

        self.checkpoints = [Checkpoint(cx, cy) for cx, cy in self.level_data["checkpoints"]]
        ep = self.level_data["end_pos"]
        self.level_end = LevelEnd(ep[0], ep[1])

        self.camera_x = float(sp[0] - WIDTH // 3)
        self.camera_y = float(sp[1] - HEIGHT // 2)

    def spawn_confetti(self, x, y, count=35):
        confetti_frames, _ = sprites.load_particles(scale=2)
        for _ in range(count):
            img = random.choice(confetti_frames) if confetti_frames else None
            self.particles.append(Particle(
                x + random.uniform(-40, 40),
                y + random.uniform(-40, 40),
                random.uniform(-5.0, 5.0),
                random.uniform(-8.0, -2.0),
                image=img,
                color=(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)),
                lifetime=random.randint(50, 90),
                size=random.randint(3, 6),
                gravity=0.25
            ))

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0

            if self.screen_shake > 0:
                self.screen_shake -= 1

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                    break
                self.handle_event(event)

            self.update(dt)
            self.draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def handle_event(self, event):
        if self.state == STATE_MENU:
            if self.btn_play.handle_event(event):
                self.lives = 3
                self.total_score = 0
                self.total_game_time = 0.0
                self.load_level(0)
                self.state = STATE_PLAYING
            elif self.btn_select_level.handle_event(event):
                self.state = STATE_LEVEL_SELECT
            elif self.btn_select_char.handle_event(event):
                self.state = STATE_CHAR_SELECT
            elif self.btn_sound_toggle.handle_event(event):
                is_on = self.sound.toggle_sound()
                self.btn_sound_toggle.text = "AUDIO: ON" if is_on else "AUDIO: OFF"
            elif self.btn_quit.handle_event(event):
                pygame.quit()
                sys.exit()

        elif self.state == STATE_CHAR_SELECT:
            if self.btn_char_back.handle_event(event):
                self.state = STATE_MENU
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                card_w, card_h = 220, 290
                start_x = WIDTH // 2 - (4 * card_w + 3 * 20) // 2
                for i, c_name in enumerate(CHARACTER_NAMES):
                    bx = start_x + i * (card_w + 20)
                    by = 220
                    card_rect = pygame.Rect(bx, by, card_w, card_h)
                    if card_rect.collidepoint(event.pos):
                        self.selected_character = c_name
                        self.sound.play("click")

        elif self.state == STATE_LEVEL_SELECT:
            if self.btn_lvl_back.handle_event(event):
                self.state = STATE_MENU
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                card_w, card_h = 170, 200
                total_w = levels.total_levels() * card_w + (levels.total_levels() - 1) * 20
                start_x = WIDTH // 2 - total_w // 2
                for i in range(levels.total_levels()):
                    bx = start_x + i * (card_w + 20)
                    by = 260
                    card_rect = pygame.Rect(bx, by, card_w, card_h)
                    unlocked = i < self.save_data.get("unlocked_level", 1)
                    if card_rect.collidepoint(event.pos) and unlocked:
                        self.lives = 3
                        self.total_score = 0
                        self.load_level(i)
                        self.sound.play("click")
                        self.state = STATE_PLAYING

        elif self.state == STATE_PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    self.player.jump()
                elif event.key in (pygame.K_ESCAPE, pygame.K_p):
                    self.state = STATE_PAUSED
                elif event.key == pygame.K_r:
                    self.load_level(self.current_level_idx)
                elif event.key == pygame.K_m:
                    is_on = self.sound.toggle_sound()
                    self.btn_sound_toggle.text = "AUDIO: ON" if is_on else "AUDIO: OFF"
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    self.player.release_jump()

        elif self.state == STATE_PAUSED:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_p):
                self.state = STATE_PLAYING
            elif self.btn_pause_resume.handle_event(event):
                self.state = STATE_PLAYING
            elif self.btn_pause_restart.handle_event(event):
                self.load_level(self.current_level_idx)
                self.state = STATE_PLAYING
            elif self.btn_pause_level_select.handle_event(event):
                self.state = STATE_LEVEL_SELECT
            elif self.btn_pause_menu.handle_event(event):
                self.state = STATE_MENU

        elif self.state == STATE_LEVEL_CLEAR:
            if self.btn_clear_next.handle_event(event):
                if self.current_level_idx + 1 < levels.total_levels():
                    self.load_level(self.current_level_idx + 1)
                    self.state = STATE_PLAYING
                else:
                    self.state = STATE_VICTORY
            elif self.btn_clear_retry.handle_event(event):
                self.load_level(self.current_level_idx)
                self.state = STATE_PLAYING
            elif self.btn_clear_menu.handle_event(event):
                self.state = STATE_MENU

        elif self.state == STATE_GAME_OVER:
            if self.btn_gameover_retry.handle_event(event):
                self.lives = 3
                self.load_level(self.current_level_idx)
                self.state = STATE_PLAYING
            elif self.btn_gameover_menu.handle_event(event):
                self.state = STATE_MENU

        elif self.state == STATE_VICTORY:
            if self.btn_vic_again.handle_event(event):
                self.lives = 3
                self.total_score = 0
                self.total_game_time = 0.0
                self.load_level(0)
                self.state = STATE_PLAYING
            elif self.btn_vic_menu.handle_event(event):
                self.state = STATE_MENU

    def update(self, dt):
        if self.state == STATE_PLAYING:
            self.level_time += dt
            self.total_game_time += dt
            keys = pygame.key.get_pressed()

            self.player.update_horizontal(keys, self.blocks)
            one_way_platforms = list(self.moving_platforms) + [f for f in self.falling_platforms if f.respawn_timer == 0]
            self.player.update_vertical(self.blocks, one_way_platforms, self.boxes, self.particles)

            for mp in self.moving_platforms:
                mp.update()

            for fp in self.falling_platforms:
                fp.update()

            for fan in self.fans:
                fan.update(self.player)

            for tramp in self.trampolines:
                tramp.update()
                if self.player.rect.colliderect(tramp.rect) and self.player.vy >= 0:
                    tramp.bounce(self.player)

            for saw in self.saws:
                saw.update()
                if self.player.rect.colliderect(saw.rect):
                    if self.player.take_damage(1):
                        self.screen_shake = 14

            for fire in self.fires:
                fire.update()
                if fire.is_on and self.player.rect.colliderect(fire.rect):
                    if self.player.take_damage(1):
                        self.screen_shake = 14

            for spike in self.spikes:
                if self.player.rect.colliderect(spike.rect):
                    if self.player.take_damage(1):
                        self.screen_shake = 14

            for box in self.boxes:
                box.update()

            for fruit in self.fruits:
                fruit.update()
                if not fruit.collected and self.player.rect.colliderect(fruit.rect):
                    pts = fruit.collect()
                    self.fruits_collected += 1
                    self.level_score += pts
                    self.total_score += pts
                    self.floating_texts.append(FloatingText(fruit.rect.centerx, fruit.rect.top, f"+{pts}"))

            for cp in self.checkpoints:
                cp.update()
                if self.player.rect.colliderect(cp.rect):
                    if cp.activate():
                        self.respawn_pos = (cp.rect.x, cp.rect.y + 40)
                        self.floating_texts.append(FloatingText(cp.rect.centerx, cp.rect.top - 10, "CHECKPOINT!", color=COLOR_GREEN))

            if self.level_end:
                self.level_end.update()
                if not self.level_end.reached and self.player.rect.colliderect(self.level_end.rect):
                    self.level_end.reach()
                    self.spawn_confetti(self.level_end.rect.centerx, self.level_end.rect.centery, 50)
                    self._on_level_cleared()

            if self.player.rect.top > self.level_data["level_height"] + 50:
                self.player.die()

            if self.player.is_dead and self.player.death_timer <= 0:
                self.lives -= 1
                if self.lives <= 0:
                    self.state = STATE_GAME_OVER
                else:
                    self.player.reset(*self.respawn_pos)

            for p in self.particles[:]:
                p.update()
                if not p.alive:
                    self.particles.remove(p)

            for ft in self.floating_texts[:]:
                ft.update()
                if not ft.alive:
                    self.floating_texts.remove(ft)

            target_cx = self.player.rect.centerx - WIDTH // 3
            target_cy = self.player.rect.centery - HEIGHT // 2
            target_cx = max(0, min(self.level_data["level_width"] - WIDTH, target_cx))
            target_cy = max(0, min(self.level_data["level_height"] - HEIGHT, target_cy))
            self.camera_x += (target_cx - self.camera_x) * 0.1
            self.camera_y += (target_cy - self.camera_y) * 0.1

        elif self.state in (STATE_LEVEL_CLEAR, STATE_VICTORY):
            if random.random() < 0.2:
                self.spawn_confetti(random.randint(0, WIDTH), random.randint(0, HEIGHT // 2), 4)
            for p in self.particles[:]:
                p.update()
                if not p.alive:
                    self.particles.remove(p)

    def _on_level_cleared(self):
        fruit_ratio = self.fruits_collected / max(1, self.total_fruits)
        if fruit_ratio >= 0.85 and self.level_time <= 75.0:
            stars = 3
        elif fruit_ratio >= 0.5:
            stars = 2
        else:
            stars = 1

        self.last_cleared_stars = stars
        unlocked = self.save_data.get("unlocked_level", 1)
        if self.current_level_idx + 2 > unlocked:
            self.save_data["unlocked_level"] = min(levels.total_levels(), self.current_level_idx + 2)

        best = self.save_data.get("high_score", 0)
        if self.total_score > best:
            self.save_data["high_score"] = self.total_score

        lvl_key = str(self.current_level_idx + 1)
        prev_stars = self.save_data.get("stars", {}).get(lvl_key, 0)
        if "stars" not in self.save_data:
            self.save_data["stars"] = {}
        self.save_data["stars"][lvl_key] = max(prev_stars, stars)
        write_save_data(self.save_data)

        self.state = STATE_LEVEL_CLEAR

    def draw(self):
        shake_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        shake_y = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        cam_x = int(self.camera_x) + shake_x
        cam_y = int(self.camera_y) + shake_y

        if self.state in (STATE_PLAYING, STATE_PAUSED, STATE_LEVEL_CLEAR, STATE_GAME_OVER, STATE_VICTORY):
            for tile in self.bg_tiles:
                self.screen.blit(self.bg_image, tile)

            for block in self.blocks:
                if -BLOCK_SIZE <= block.rect.x - cam_x <= WIDTH + BLOCK_SIZE:
                    block.draw(self.screen, cam_x, cam_y)

            for mp in self.moving_platforms:
                mp.draw(self.screen, cam_x, cam_y)
            for fp in self.falling_platforms:
                fp.draw(self.screen, cam_x, cam_y)

            for fan in self.fans:
                fan.draw(self.screen, cam_x, cam_y)
            for tramp in self.trampolines:
                tramp.draw(self.screen, cam_x, cam_y)
            for saw in self.saws:
                saw.draw(self.screen, cam_x, cam_y)
            for fire in self.fires:
                fire.draw(self.screen, cam_x, cam_y)
            for spike in self.spikes:
                spike.draw(self.screen, cam_x, cam_y)
            for box in self.boxes:
                box.draw(self.screen, cam_x, cam_y)
            for fruit in self.fruits:
                fruit.draw(self.screen, cam_x, cam_y)
            for cp in self.checkpoints:
                cp.draw(self.screen, cam_x, cam_y)
            if self.level_end:
                self.level_end.draw(self.screen, cam_x, cam_y)

            self.player.draw(self.screen, cam_x, cam_y)

            for p in self.particles:
                p.draw(self.screen, cam_x, cam_y)
            for ft in self.floating_texts:
                ft.draw(self.screen, cam_x, cam_y)

            ui.draw_hud(
                self.screen, self.player, self.fruits_collected,
                self.total_fruits, self.total_score,
                self.level_data["name"], self.level_time, self.lives
            )

            if self.state == STATE_PAUSED:
                ui.draw_pause_overlay(self.screen, [
                    self.btn_pause_resume, self.btn_pause_restart,
                    self.btn_pause_level_select, self.btn_pause_menu
                ])
            elif self.state == STATE_LEVEL_CLEAR:
                ui.draw_level_clear_overlay(
                    self.screen, self.level_data["name"],
                    self.fruits_collected, self.total_fruits,
                    self.level_score, self.level_time,
                    getattr(self, "last_cleared_stars", 3),
                    [self.btn_clear_next, self.btn_clear_retry, self.btn_clear_menu]
                )
            elif self.state == STATE_GAME_OVER:
                ui.draw_game_over_overlay(self.screen, self.total_score, [self.btn_gameover_retry, self.btn_gameover_menu])
            elif self.state == STATE_VICTORY:
                ui.draw_victory_screen(self.screen, self.total_score, self.total_game_time, [self.btn_vic_again, self.btn_vic_menu])

        elif self.state == STATE_MENU:
            ui.draw_main_menu(self.screen, self.selected_character, self.save_data.get("high_score", 0), [
                self.btn_play, self.btn_select_level, self.btn_select_char, self.btn_sound_toggle, self.btn_quit
            ])
        elif self.state == STATE_CHAR_SELECT:
            ui.draw_character_select(self.screen, self.selected_character, self.btn_char_back)
        elif self.state == STATE_LEVEL_SELECT:
            ui.draw_level_select(self.screen, self.save_data.get("unlocked_level", 1), self.save_data.get("stars", {}), self.btn_lvl_back)
