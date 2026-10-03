import os
from pathlib import Path
import pygame
from src.platformer.config import BLOCK_SIZE, ASSETS_DIR

_IMAGE_CACHE = {}

def get_image(path):
    path_str = str(path)
    if path_str not in _IMAGE_CACHE:
        img = pygame.image.load(path_str).convert_alpha()
        _IMAGE_CACHE[path_str] = img
    return _IMAGE_CACHE[path_str]

def flip_sprites(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sheet(path, frame_width, frame_height, scale=2, flip_horizontal=False):
    sheet = get_image(path)
    sw, sh = sheet.get_size()
    frames = []
    num_frames = sw // frame_width
    for i in range(num_frames):
        rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
        sub = sheet.subsurface(rect)
        if scale != 1:
            scaled = pygame.transform.scale(sub, (int(frame_width * scale), int(frame_height * scale)))
        else:
            scaled = sub
        frames.append(scaled)
    if flip_horizontal:
        return flip_sprites(frames)
    return frames

def load_character_sprites(character_name, scale=2):
    base_dir = ASSETS_DIR / "MainCharacters" / character_name
    all_sprites = {}
    animations = ["idle", "run", "jump", "double_jump", "fall", "hit", "wall_jump"]
    for anim in animations:
        path = base_dir / f"{anim}.png"
        if path.is_file():
            right_frames = load_sheet(path, 32, 32, scale=scale)
            left_frames = flip_sprites(right_frames)
            all_sprites[f"{anim}_right"] = right_frames
            all_sprites[f"{anim}_left"] = left_frames
    return all_sprites

def load_appear_disappear(scale=2):
    appear_path = ASSETS_DIR / "MainCharacters" / "Appearing (96x96).png"
    disappear_path = ASSETS_DIR / "MainCharacters" / "Desappearing (96x96).png"
    appear_frames = load_sheet(appear_path, 96, 96, scale=scale)
    disappear_frames = load_sheet(disappear_path, 96, 96, scale=scale)
    return appear_frames, disappear_frames

def get_terrain_tile(style="grass_top", size=BLOCK_SIZE):
    path = ASSETS_DIR / "Terrain" / "Terrain.png"
    sheet = get_image(path)
    coords = {
        "grass_top": (112, 0),
        "grass_center": (112, 16),
        "grass_left": (96, 0),
        "grass_right": (128, 0),
        "grass_single": (16, 0),
        "wood_top": (112, 64),
        "wood_center": (112, 80),
        "stone_top": (112, 128),
        "stone_center": (112, 144),
    }
    x, y = coords.get(style, (112, 0))
    sub = sheet.subsurface(pygame.Rect(x, y, 16, 16))
    return pygame.transform.scale(sub, (size, size))

def load_fruit_sprites(fruit_name, scale=2):
    path = ASSETS_DIR / "Items" / "Fruits" / f"{fruit_name}.png"
    frames = load_sheet(path, 32, 32, scale=scale)
    collected_path = ASSETS_DIR / "Items" / "Fruits" / "Collected.png"
    collected_frames = load_sheet(collected_path, 32, 32, scale=scale)
    return frames, collected_frames

def load_box_sprites(box_name="Box1", scale=2):
    base_dir = ASSETS_DIR / "Items" / "Boxes" / box_name
    idle = load_sheet(base_dir / "Idle.png", 28, 24, scale=scale)
    hit = load_sheet(base_dir / "Hit (28x24).png", 28, 24, scale=scale)
    broken = load_sheet(base_dir / "Break.png", 28, 24, scale=scale)
    return idle, hit, broken

def load_traps(scale=2):
    traps = {}
    traps_dir = ASSETS_DIR / "Traps"
    # Fire
    fire_dir = traps_dir / "Fire"
    fire_off = load_sheet(fire_dir / "off.png", 16, 32, scale=scale)
    fire_on = load_sheet(fire_dir / "on.png", 16, 32, scale=scale)
    fire_hit = load_sheet(fire_dir / "hit.png", 16, 32, scale=scale)
    traps["fire"] = {"off": fire_off, "on": fire_on, "hit": fire_hit}

    # Spikes
    spike_img = get_image(traps_dir / "Spikes" / "Idle.png")
    spike_scaled = pygame.transform.scale(spike_img, (int(16 * scale), int(16 * scale)))
    traps["spike"] = [spike_scaled]

    # Saw
    saw_on = load_sheet(traps_dir / "Saw" / "on.png", 38, 38, scale=scale)
    traps["saw"] = saw_on

    # Trampoline
    tramp_dir = traps_dir / "Trampoline"
    tramp_idle = load_sheet(tramp_dir / "Idle.png", 28, 28, scale=scale)
    tramp_jump = load_sheet(tramp_dir / "Jump (28x28).png", 28, 28, scale=scale)
    traps["trampoline"] = {"idle": tramp_idle, "jump": tramp_jump}

    # Fan
    fan_dir = traps_dir / "Fan"
    fan_off = load_sheet(fan_dir / "Off.png", 24, 8, scale=scale)
    fan_on = load_sheet(fan_dir / "On (24x8).png", 24, 8, scale=scale)
    traps["fan"] = {"off": fan_off, "on": fan_on}

    # Falling platform
    fall_dir = traps_dir / "Falling Platforms"
    fall_off = load_sheet(fall_dir / "Off.png", 32, 10, scale=scale)
    fall_on = load_sheet(fall_dir / "On (32x10).png", 32, 10, scale=scale)
    traps["falling_platform"] = {"off": fall_off, "on": fall_on}

    # Moving platforms
    plat_dir = traps_dir / "Platforms"
    brown_on = load_sheet(plat_dir / "Brown On (32x8).png", 32, 8, scale=scale)
    grey_on = load_sheet(plat_dir / "Grey On (32x8).png", 32, 8, scale=scale)
    traps["moving_platform"] = {"brown": brown_on, "grey": grey_on}

    # Rock Head
    rock_dir = traps_dir / "Rock Head"
    rock_idle = load_sheet(rock_dir / "Idle.png", 42, 42, scale=scale)
    rock_blink = load_sheet(rock_dir / "Blink (42x42).png", 42, 42, scale=scale)
    traps["rock_head"] = {"idle": rock_idle, "blink": rock_blink}

    return traps

def load_checkpoints(scale=2):
    checkpoints = {}
    cp_dir = ASSETS_DIR / "Items" / "Checkpoints"
    # Start
    start_dir = cp_dir / "Start"
    start_idle = load_sheet(start_dir / "Start (Idle).png", 64, 64, scale=scale)
    start_moving = load_sheet(start_dir / "Start (Moving) (64x64).png", 64, 64, scale=scale)
    checkpoints["start"] = {"idle": start_idle, "moving": start_moving}

    # Checkpoint flag
    flag_dir = cp_dir / "Checkpoint"
    flag_no = load_sheet(flag_dir / "Checkpoint (No Flag).png", 64, 64, scale=scale)
    flag_out = load_sheet(flag_dir / "Checkpoint (Flag Out) (64x64).png", 64, 64, scale=scale)
    flag_idle = load_sheet(flag_dir / "Checkpoint (Flag Idle)(64x64).png", 64, 64, scale=scale)
    checkpoints["checkpoint"] = {"no": flag_no, "out": flag_out, "idle": flag_idle}

    # End
    end_dir = cp_dir / "End"
    end_idle = load_sheet(end_dir / "End (Idle).png", 64, 64, scale=scale)
    end_pressed = load_sheet(end_dir / "End (Pressed) (64x64).png", 64, 64, scale=scale)
    checkpoints["end"] = {"idle": end_idle, "pressed": end_pressed}

    return checkpoints

def load_particles(scale=2):
    confetti_path = ASSETS_DIR / "Other" / "Confetti (16x16).png"
    dust_path = ASSETS_DIR / "Other" / "Dust Particle.png"
    confetti = load_sheet(confetti_path, 16, 16, scale=scale)
    dust = pygame.transform.scale(get_image(dust_path), (int(16 * scale), int(16 * scale)))
    return confetti, dust

def get_background(name, screen_width, screen_height):
    path = ASSETS_DIR / "Background" / name
    bg_image = get_image(path)
    w, h = bg_image.get_size()
    tiles = []
    for i in range(screen_width // w + 2):
        for j in range(screen_height // h + 2):
            tiles.append((i * w, j * h))
    return tiles, bg_image
