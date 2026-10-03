import os
import sys
import json
import math
import random
import pygame

from constants import (
    WIDTH, HEIGHT, FPS, BLOCK_SIZE,
    STATE_MENU, STATE_CHAR_SELECT, STATE_LEVEL_SELECT,
    STATE_PLAYING, STATE_PAUSED, STATE_LEVEL_CLEAR,
    STATE_GAME_OVER, STATE_VICTORY,
    CHARACTERS, CHARACTER_NAMES,
    COLOR_WHITE, COLOR_BLACK, COLOR_ACCENT, COLOR_GREEN, COLOR_RED,
    COLOR_BLUE, COLOR_CYAN, COLOR_PURPLE, COLOR_TEXT, COLOR_TEXT_MUTED
)
from sound import SoundManager
import sprites
import levels
import ui
from entities import (
    Player, Block, Fruit, Box, Fire, Spike, Saw,
    Trampoline, Fan, FallingPlatform, MovingPlatform,
    Checkpoint, LevelEnd, Particle, FloatingText
)

SAVE_FILE = "save_data.json"

def load_save_data():
    try:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"Save load warning: {e}")
    return {"high_score": 0, "unlocked_level": 1, "stars": {}}

def write_save_data(data):
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Save write warning: {e}")

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Platformer Fun by Miskat")

        # Set game window icon
        try:
            icon_img = sprites.get_image(os.path.join("assets", "Items", "Fruits", "Apple.png"))
            icon_sub = icon_img.subsurface(pygame.Rect(0, 0, 32, 32))
            pygame.display.set_icon(icon_sub)
        except Exception:
            pass

        self.clock = pygame.time.Clock()
        self.sound = SoundManager.get_instance()
        self.save_data = load_save_data()

        # Global Game State
        self.state = STATE_MENU
        self.selected_character = "VirtualGuy"
        self.current_level_idx = 0
        self.total_score = 0
        self.level_score = 0
        self.lives = 3
        self.level_time = 0.0
        self.total_game_time = 0.0

        # Camera & Screen Shake
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.screen_shake = 0

        # Particles & Effects
        self.particles = []
        self.floating_texts = []

        # Current Level Entities
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

        # UI Menus
        self._init_menu_buttons()

        # Start BGM
        self.sound.start_music()

    def _init_menu_buttons(self):
        cx = WIDTH // 2
        # Main Menu Buttons
        self.btn_play = ui.Button(cx - 150, 290, 300, 52, "PLAY GAME", bg_color=COLOR_GREEN, hover_color=(46, 204, 113), font_size=26)
        self.btn_select_level = ui.Button(cx - 150, 360, 300, 52, "SELECT LEVEL", bg_color=COLOR_BLUE, hover_color=COLOR_CYAN, font_size=24)
        self.btn_select_char = ui.Button(cx - 150, 430, 300, 52, "SELECT CHARACTER", bg_color=COLOR_PURPLE, hover_color=(170, 150, 220), font_size=24)
        self.btn_sound_toggle = ui.Button(cx - 150, 500, 300, 48, "AUDIO: ON" if self.sound.enabled else "AUDIO: OFF", bg_color=(80, 90, 110), hover_color=(110, 120, 140), font_size=20)
        self.btn_quit = ui.Button(cx - 150, 565, 300, 48, "QUIT", bg_color=(120, 50, 50), hover_color=COLOR_RED, font_size=22)

        # Pause Menu Buttons
        self.btn_pause_resume = ui.Button(cx - 130, HEIGHT // 2 - 60, 260, 48, "RESUME", bg_color=COLOR_GREEN, hover_color=(46, 204, 113))
        self.btn_pause_restart = ui.Button(cx - 130, HEIGHT // 2 + 5, 260, 48, "RESTART", bg_color=COLOR_BLUE, hover_color=COLOR_CYAN)
        self.btn_pause_level_select = ui.Button(cx - 130, HEIGHT // 2 + 70, 260, 48, "LEVEL SELECT", bg_color=COLOR_PURPLE, hover_color=(170, 150, 220))
        self.btn_pause_menu = ui.Button(cx - 130, HEIGHT // 2 + 135, 260, 48, "MAIN MENU", bg_color=(80, 90, 110), hover_color=(110, 120, 140))

        # Level Clear Buttons
        self.btn_clear_next = ui.Button(cx - 130, HEIGHT // 2 + 80, 260, 48, "NEXT LEVEL", bg_color=COLOR_GREEN, hover_color=(46, 204, 113))
        self.btn_clear_retry = ui.Button(cx - 130, HEIGHT // 2 + 140, 260, 44, "REPLAY LEVEL", bg_color=COLOR_BLUE, hover_color=COLOR_CYAN)
        self.btn_clear_menu = ui.Button(cx - 130, HEIGHT // 2 + 195, 260, 44, "MAIN MENU", bg_color=(80, 90, 110), hover_color=(110, 120, 140))

        # Game Over Buttons
        self.btn_gameover_retry = ui.Button(cx - 130, HEIGHT // 2 + 15, 260, 50, "TRY AGAIN", bg_color=COLOR_GREEN, hover_color=(46, 204, 113))
        self.btn_gameover_menu = ui.Button(cx - 130, HEIGHT // 2 + 80, 260, 50, "MAIN MENU", bg_color=(80, 90, 110), hover_color=(110, 120, 140))

        # Victory Buttons
        self.btn_vic_again = ui.Button(cx - 140, HEIGHT // 2 + 105, 280, 52, "PLAY AGAIN", bg_color=COLOR_GREEN, hover_color=(46, 204, 113), font_size=24)
        self.btn_vic_menu = ui.Button(cx - 140, HEIGHT // 2 + 170, 280, 48, "MAIN MENU", bg_color=COLOR_BLUE, hover_color=COLOR_CYAN, font_size=22)

        # Back Buttons
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

        # Background
        self.bg_tiles, self.bg_image = sprites.get_background(self.level_data["bg_image"], WIDTH, HEIGHT)

        # Player
        sp = self.level_data["start_pos"]
        self.respawn_pos = sp
        self.player = Player(sp[0], sp[1], self.selected_character)

        # Blocks
        self.blocks = [Block(bx, by, b_style) for bx, by, b_style in self.level_data["blocks"]]

        # Fruits
        self.fruits = [Fruit(fx, fy, f_type) for fx, fy, f_type in self.level_data["fruits"]]
        self.total_fruits = len(self.fruits)

        # Boxes
        self.boxes = [Box(bx, by, b_type, f_drop) for bx, by, b_type, f_drop in self.level_data["boxes"]]

        # Hazards & Traps
        self.spikes = [Spike(sx, sy) for sx, sy in self.level_data["spikes"]]
        self.fires = [Fire(fx, fy) for fx, fy in self.level_data["fires"]]
        self.saws = [Saw(sx, sy, rng, spd, horiz) for sx, sy, rng, spd, horiz in self.level_data["saws"]]
        self.trampolines = [Trampoline(tx, ty) for tx, ty in self.level_data["trampolines"]]
        self.fans = [Fan(fx, fy, h) for fx, fy, h in self.level_data["fans"]]
        self.falling_platforms = [FallingPlatform(fx, fy) for fx, fy in self.level_data["falling_platforms"]]
        self.moving_platforms = [MovingPlatform(mx, my, rng, spd, horiz, style) for mx, my, rng, spd, horiz, style in self.level_data["moving_platforms"]]

        # Checkpoints & End
        self.checkpoints = [Checkpoint(cx, cy) for cx, cy in self.level_data["checkpoints"]]
        ep = self.level_data["end_pos"]
        self.level_end = LevelEnd(ep[0], ep[1])

        # Camera
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

            # Screen Shake decay
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
                # Character cards click
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
                # Level cards click
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

            # Player horizontal update
            self.player.update_horizontal(keys, self.blocks)

            # Platforms update
            one_way_platforms = list(self.moving_platforms) + [f for f in self.falling_platforms if f.respawn_timer == 0]

            # Player vertical update
            self.player.update_vertical(self.blocks, one_way_platforms, self.boxes, self.particles)

            # Moving Platforms update
            for mp in self.moving_platforms:
                mp.update()

            # Falling Platforms update
            for fp in self.falling_platforms:
                fp.update()

            # Fans update
            for fan in self.fans:
                fan.update(self.player)

            # Trampolines update & collision
            for tramp in self.trampolines:
                tramp.update()
                if self.player.rect.colliderect(tramp.rect) and self.player.vy >= 0:
                    tramp.bounce(self.player)

            # Saws update & collision
            for saw in self.saws:
                saw.update()
                if self.player.rect.colliderect(saw.rect):
                    if self.player.take_damage(1):
                        self.screen_shake = 14

            # Fire update & collision
            for fire in self.fires:
                fire.update()
                if fire.is_on and self.player.rect.colliderect(fire.rect):
                    if self.player.take_damage(1):
                        self.screen_shake = 14

            # Spikes collision
            for spike in self.spikes:
                if self.player.rect.colliderect(spike.rect):
                    if self.player.take_damage(1):
                        self.screen_shake = 14

            # Boxes update & hit check
            for box in self.boxes:
                box.update()

            # Fruits update & collection
            for fruit in self.fruits:
                fruit.update()
                if not fruit.collected and self.player.rect.colliderect(fruit.rect):
                    pts = fruit.collect()
                    self.fruits_collected += 1
                    self.level_score += pts
                    self.total_score += pts
                    self.floating_texts.append(FloatingText(fruit.rect.centerx, fruit.rect.top, f"+{pts}"))

            # Checkpoints check
            for cp in self.checkpoints:
                cp.update()
                if self.player.rect.colliderect(cp.rect):
                    if cp.activate():
                        self.respawn_pos = (cp.rect.x, cp.rect.y + 40)
                        self.floating_texts.append(FloatingText(cp.rect.centerx, cp.rect.top - 10, "CHECKPOINT!", color=COLOR_GREEN))

            # Level End check
            if self.level_end:
                self.level_end.update()
                if not self.level_end.reached and self.player.rect.colliderect(self.level_end.rect):
                    self.level_end.reach()
                    self.spawn_confetti(self.level_end.rect.centerx, self.level_end.rect.centery, 50)
                    self._on_level_cleared()

            # Bottomless Pit check
            if self.player.rect.top > self.level_data["level_height"] + 50:
                self.player.die()

            # Player death respawn / Game Over
            if self.player.is_dead and self.player.death_timer <= 0:
                self.lives -= 1
                if self.lives <= 0:
                    self.state = STATE_GAME_OVER
                else:
                    self.player.reset(*self.respawn_pos)

            # Particles update
            for p in self.particles[:]:
                p.update()
                if not p.alive:
                    self.particles.remove(p)

            # Floating text update
            for ft in self.floating_texts[:]:
                ft.update()
                if not ft.alive:
                    self.floating_texts.remove(ft)

            # Smooth camera tracking
            target_cx = self.player.rect.centerx - WIDTH // 3
            target_cy = self.player.rect.centery - HEIGHT // 2
            # Clamp camera to level bounds
            target_cx = max(0, min(self.level_data["level_width"] - WIDTH, target_cx))
            target_cy = max(0, min(self.level_data["level_height"] - HEIGHT, target_cy))
            self.camera_x += (target_cx - self.camera_x) * 0.1
            self.camera_y += (target_cy - self.camera_y) * 0.1

        elif self.state in (STATE_LEVEL_CLEAR, STATE_VICTORY):
            # Keep updating particles on victory/clear screens
            if random.random() < 0.2:
                self.spawn_confetti(random.randint(0, WIDTH), random.randint(0, HEIGHT // 2), 4)
            for p in self.particles[:]:
                p.update()
                if not p.alive:
                    self.particles.remove(p)

    def _on_level_cleared(self):
        # Calculate stars based on collected fruits & time
        fruit_ratio = self.fruits_collected / max(1, self.total_fruits)
        if fruit_ratio >= 0.85 and self.level_time <= 75.0:
            stars = 3
        elif fruit_ratio >= 0.5:
            stars = 2
        else:
            stars = 1

        self.last_cleared_stars = stars
        # Unlock next level
        unlocked = self.save_data.get("unlocked_level", 1)
        if self.current_level_idx + 2 > unlocked:
            self.save_data["unlocked_level"] = min(levels.total_levels(), self.current_level_idx + 2)

        # Update high score
        best = self.save_data.get("high_score", 0)
        if self.total_score > best:
            self.save_data["high_score"] = self.total_score

        # Save star rating
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
            # Background
            for tile in self.bg_tiles:
                self.screen.blit(self.bg_image, tile)

            # Blocks
            for block in self.blocks:
                # View frustum culling
                if -BLOCK_SIZE <= block.rect.x - cam_x <= WIDTH + BLOCK_SIZE:
                    block.draw(self.screen, cam_x, cam_y)

            # Platforms
            for mp in self.moving_platforms:
                mp.draw(self.screen, cam_x, cam_y)
            for fp in self.falling_platforms:
                fp.draw(self.screen, cam_x, cam_y)

            # Interactive objects
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

            # Player
            self.player.draw(self.screen, cam_x, cam_y)

            # Particles & Floating text
            for p in self.particles:
                p.draw(self.screen, cam_x, cam_y)
            for ft in self.floating_texts:
                ft.draw(self.screen, cam_x, cam_y)

            # HUD
            ui.draw_hud(
                self.screen, self.player, self.fruits_collected,
                self.total_fruits, self.total_score,
                self.level_data["name"], self.level_time, self.lives
            )

            # State Overlays
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
            self._draw_main_menu()
        elif self.state == STATE_CHAR_SELECT:
            self._draw_character_select()
        elif self.state == STATE_LEVEL_SELECT:
            self._draw_level_select()

    def _draw_main_menu(self):
        # Menu background
        menu_bg, bg_img = sprites.get_background("Blue.png", WIDTH, HEIGHT)
        for tile in menu_bg:
            self.screen.blit(bg_img, tile)

        # Title Card
        title_font = ui.get_font(52, bold=True)
        sub_font = ui.get_font(22, bold=True)

        t_text = "PLATFORMER FUN BY MISKAT"
        # Shadow
        t_shadow = title_font.render(t_text, True, (15, 20, 30))
        t_surf = title_font.render(t_text, True, COLOR_ACCENT)
        cx = WIDTH // 2
        self.screen.blit(t_shadow, t_shadow.get_rect(center=(cx + 3, 113)))
        self.screen.blit(t_surf, t_surf.get_rect(center=(cx, 110)))

        s_surf = sub_font.render("Classic Pixel Adventure Platformer Experience", True, COLOR_WHITE)
        self.screen.blit(s_surf, s_surf.get_rect(center=(cx, 165)))

        # High Score banner
        hs = self.save_data.get("high_score", 0)
        hs_surf = ui.get_font(20, bold=True).render(f"HIGH SCORE: {hs}", True, COLOR_CYAN)
        self.screen.blit(hs_surf, hs_surf.get_rect(center=(cx, 205)))

        # Character showcase preview on left
        char_info = CHARACTERS.get(self.selected_character, CHARACTERS["VirtualGuy"])
        char_sprites = sprites.load_character_sprites(self.selected_character, scale=3)
        run_frames = char_sprites.get("run_right", char_sprites.get("idle_right"))
        frame_idx = int((pygame.time.get_ticks() / 120) % len(run_frames))
        preview_sprite = run_frames[frame_idx]

        # Draw character box on left
        box_left = pygame.Rect(cx - 430, 320, 220, 260)
        pygame.draw.rect(self.screen, (25, 30, 45, 220), box_left, border_radius=16)
        pygame.draw.rect(self.screen, char_info["color"], box_left, width=3, border_radius=16)

        self.screen.blit(preview_sprite, (box_left.centerx - preview_sprite.get_width() // 2, box_left.y + 40))
        c_name_surf = ui.get_font(20, bold=True).render(char_info["name"], True, COLOR_WHITE)
        self.screen.blit(c_name_surf, c_name_surf.get_rect(center=(box_left.centerx, box_left.bottom - 60)))
        click_hint = ui.get_font(14, bold=False).render("(Click 'Select Character' to change)", True, COLOR_TEXT_MUTED)
        self.screen.blit(click_hint, click_hint.get_rect(center=(box_left.centerx, box_left.bottom - 25)))

        # Draw Menu Buttons
        for btn in [self.btn_play, self.btn_select_level, self.btn_select_char, self.btn_sound_toggle, self.btn_quit]:
            btn.draw(self.screen)

        # Controls hint bar
        hint_surf = ui.get_font(16, bold=False).render(
            "Controls:  [A/D] or [Arrows] Move  |  [Space/W] Jump / Double Jump  |  [ESC] Pause  |  [R] Restart  |  [M] Audio",
            True, COLOR_TEXT_MUTED
        )
        self.screen.blit(hint_surf, hint_surf.get_rect(center=(cx, HEIGHT - 25)))

    def _draw_character_select(self):
        menu_bg, bg_img = sprites.get_background("Purple.png", WIDTH, HEIGHT)
        for tile in menu_bg:
            self.screen.blit(bg_img, tile)

        self.btn_char_back.draw(self.screen)

        title_font = ui.get_font(42, bold=True)
        title_surf = title_font.render("CHOOSE YOUR HERO", True, COLOR_ACCENT)
        self.screen.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, 70)))

        sub_font = ui.get_font(20, bold=False)
        sub_surf = sub_font.render("Each hero possesses unique platforming traits and style!", True, COLOR_WHITE)
        self.screen.blit(sub_surf, sub_surf.get_rect(center=(WIDTH // 2, 115)))

        card_w, card_h = 220, 360
        start_x = WIDTH // 2 - (4 * card_w + 3 * 20) // 2
        for i, c_name in enumerate(CHARACTER_NAMES):
            cx = start_x + i * (card_w + 20)
            cy = 180
            rect = pygame.Rect(cx, cy, card_w, card_h)
            is_selected = (c_name == self.selected_character)

            bg_col = (35, 40, 60) if not is_selected else (45, 60, 90)
            border_col = COLOR_ACCENT if is_selected else (80, 90, 120)
            border_w = 4 if is_selected else 2

            pygame.draw.rect(self.screen, bg_col, rect, border_radius=16)
            pygame.draw.rect(self.screen, border_col, rect, width=border_w, border_radius=16)

            info = CHARACTERS[c_name]
            # Animated preview
            c_sprites = sprites.load_character_sprites(c_name, scale=3)
            frames = c_sprites.get("run_right", c_sprites.get("idle_right"))
            frame_idx = int((pygame.time.get_ticks() / 120) % len(frames))
            spr = frames[frame_idx]
            self.screen.blit(spr, (rect.centerx - spr.get_width() // 2, rect.y + 30))

            # Character Name
            name_surf = ui.get_font(22, bold=True).render(info["name"], True, COLOR_WHITE)
            self.screen.blit(name_surf, name_surf.get_rect(center=(rect.centerx, rect.y + 145)))

            # Stats
            stat_font = ui.get_font(16, bold=False)
            s_spd = stat_font.render(f"Speed: {info['speed']}", True, COLOR_CYAN)
            s_jmp = stat_font.render(f"Jump: {info['jump']}", True, COLOR_GREEN)
            self.screen.blit(s_spd, (rect.x + 24, rect.y + 185))
            self.screen.blit(s_jmp, (rect.x + 24, rect.y + 215))

            # Description (word wrap)
            words = info["desc"].split(" ")
            line1 = " ".join(words[:len(words)//2])
            line2 = " ".join(words[len(words)//2:])
            d1_surf = ui.get_font(14, bold=False).render(line1, True, COLOR_TEXT_MUTED)
            d2_surf = ui.get_font(14, bold=False).render(line2, True, COLOR_TEXT_MUTED)
            self.screen.blit(d1_surf, (rect.x + 16, rect.y + 250))
            self.screen.blit(d2_surf, (rect.x + 16, rect.y + 270))

            # Selection status
            status_text = "✓ SELECTED" if is_selected else "CLICK TO SELECT"
            status_col = COLOR_ACCENT if is_selected else (120, 130, 150)
            st_surf = ui.get_font(16, bold=True).render(status_text, True, status_col)
            self.screen.blit(st_surf, st_surf.get_rect(center=(rect.centerx, rect.bottom - 30)))

    def _draw_level_select(self):
        menu_bg, bg_img = sprites.get_background("Gray.png", WIDTH, HEIGHT)
        for tile in menu_bg:
            self.screen.blit(bg_img, tile)

        self.btn_lvl_back.draw(self.screen)

        title_font = ui.get_font(42, bold=True)
        title_surf = title_font.render("SELECT ADVENTURE LEVEL", True, COLOR_ACCENT)
        self.screen.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, 70)))

        unlocked = self.save_data.get("unlocked_level", 1)
        stars_dict = self.save_data.get("stars", {})

        card_w, card_h = 180, 260
        tot_levels = levels.total_levels()
        total_w = tot_levels * card_w + (tot_levels - 1) * 20
        start_x = WIDTH // 2 - total_w // 2

        for i in range(tot_levels):
            cx = start_x + i * (card_w + 20)
            cy = 220
            rect = pygame.Rect(cx, cy, card_w, card_h)
            is_unlocked = (i < unlocked)

            bg_col = (35, 42, 60) if is_unlocked else (25, 26, 32)
            border_col = COLOR_GREEN if is_unlocked else (60, 65, 75)
            pygame.draw.rect(self.screen, bg_col, rect, border_radius=16)
            pygame.draw.rect(self.screen, border_col, rect, width=3 if is_unlocked else 2, border_radius=16)

            # Level Number
            num_surf = ui.get_font(42, bold=True).render(f"{i + 1}", True, COLOR_WHITE if is_unlocked else (90, 95, 110))
            self.screen.blit(num_surf, num_surf.get_rect(center=(rect.centerx, rect.y + 60)))

            # Level Name
            lvl_meta = levels.get_level(i)
            name_parts = lvl_meta["name"].split(" ")
            p1 = name_parts[0]
            p2 = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
            n1_surf = ui.get_font(18, bold=True).render(p1, True, COLOR_ACCENT if is_unlocked else (90, 95, 110))
            n2_surf = ui.get_font(18, bold=True).render(p2, True, COLOR_ACCENT if is_unlocked else (90, 95, 110))
            self.screen.blit(n1_surf, n1_surf.get_rect(center=(rect.centerx, rect.y + 115)))
            self.screen.blit(n2_surf, n2_surf.get_rect(center=(rect.centerx, rect.y + 138)))

            # Stars Rating
            stars_earned = stars_dict.get(str(i + 1), 0)
            star_str = "★ " * stars_earned + "☆ " * (3 - stars_earned)
            star_surf = ui.get_font(24, bold=True).render(star_str.strip(), True, COLOR_ACCENT if is_unlocked else (80, 80, 90))
            self.screen.blit(star_surf, star_surf.get_rect(center=(rect.centerx, rect.y + 185)))

            # Status
            btn_txt = "PLAY" if is_unlocked else "LOCKED"
            btn_col = COLOR_GREEN if is_unlocked else (100, 100, 110)
            st_surf = ui.get_font(18, bold=True).render(btn_txt, True, btn_col)
            self.screen.blit(st_surf, st_surf.get_rect(center=(rect.centerx, rect.bottom - 30)))

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
