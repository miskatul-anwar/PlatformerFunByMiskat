from src.platformer.config import BLOCK_SIZE

def build_level_1():
    """Level 1: Greenfield Trail - Introduction to jumping, fruits, simple spikes."""
    b = BLOCK_SIZE
    blocks = []
    fruits = []
    boxes = []
    spikes = []
    fires = []
    saws = []
    trampolines = []
    fans = []
    falling = []
    moving = []
    checkpoints = [(1500, 7 * b - 64)]
    start_pos = (120, 7 * b - 64)
    end_pos = (2800, 6 * b - 64)

    # Ground floor sections
    for col in range(-2, 14):
        blocks.append((col * b, 8 * b, "grass_top"))
        blocks.append((col * b, 9 * b, "grass_center"))

    for col in range(16, 26):
        blocks.append((col * b, 8 * b, "grass_top"))
        blocks.append((col * b, 9 * b, "grass_center"))

    for col in range(21, 26):
        blocks.append((col * b, 7 * b, "grass_top"))

    for col in range(4, 7):
        blocks.append((col * b, 5 * b, "grass_top"))

    for col in range(9, 12):
        blocks.append((col * b, 4 * b, "grass_top"))

    blocks.append((14 * b, 6 * b, "grass_top"))
    blocks.append((15 * b, 4 * b, "grass_top"))

    for col in range(28, 32):
        blocks.append((col * b, 7 * b, "grass_top"))

    for col in range(34, 38):
        blocks.append((col * b, 6 * b, "grass_top"))

    for col in range(41, 48):
        blocks.append((col * b, 7 * b, "grass_top"))
        blocks.append((col * b, 8 * b, "grass_center"))

    for col in range(4, 7):
        fruits.append((col * b + 16, 4 * b, "Apple"))
    for col in range(9, 12):
        fruits.append((col * b + 16, 3 * b, "Bananas"))
    fruits.append((14 * b + 16, 5 * b, "Cherries"))
    fruits.append((15 * b + 16, 3 * b, "Cherries"))
    for col in range(28, 32):
        fruits.append((col * b + 16, 6 * b, "Apple"))
    for col in range(35, 38):
        fruits.append((col * b + 16, 5 * b, "Bananas"))

    boxes.append((5 * b, 2 * b, "Box1", "Melon"))
    boxes.append((10 * b, 1 * b, "Box2", "Pineapple"))
    boxes.append((36 * b, 3 * b, "Box1", "Strawberry"))

    spikes.append((7 * b, 8 * b - 32))
    spikes.append((8 * b, 8 * b - 32))
    spikes.append((18 * b, 8 * b - 32))
    fires.append((19 * b, 8 * b - 64))

    trampolines.append((25 * b, 7 * b - 40))

    return {
        "id": 1,
        "name": "Greenfield Trail",
        "bg_image": "Green.png",
        "style": "grass_top",
        "start_pos": start_pos,
        "end_pos": end_pos,
        "blocks": blocks,
        "fruits": fruits,
        "boxes": boxes,
        "spikes": spikes,
        "fires": fires,
        "saws": saws,
        "trampolines": trampolines,
        "fans": fans,
        "falling_platforms": falling,
        "moving_platforms": moving,
        "checkpoints": checkpoints,
        "level_width": 3200,
        "level_height": 720
    }

def build_level_2():
    """Level 2: Sawblade Heights - Trampolines, moving saws, wooden terrain."""
    b = BLOCK_SIZE
    blocks = []
    fruits = []
    boxes = []
    spikes = []
    fires = []
    saws = []
    trampolines = []
    fans = []
    falling = []
    moving = []
    checkpoints = [(1600, 7 * b - 64)]
    start_pos = (120, 7 * b - 64)
    end_pos = (3000, 5 * b - 64)

    for col in range(-2, 10):
        blocks.append((col * b, 8 * b, "wood_top"))
        blocks.append((col * b, 9 * b, "wood_center"))

    for col in range(12, 22):
        blocks.append((col * b, 8 * b, "wood_top"))
        blocks.append((col * b, 9 * b, "wood_center"))

    for row in range(5, 8):
        blocks.append((11 * b, row * b, "wood_top"))

    trampolines.append((8 * b, 8 * b - 40))

    for col in range(13, 17):
        blocks.append((col * b, 4 * b, "wood_top"))

    for col in range(18, 22):
        blocks.append((col * b, 4 * b, "wood_top"))

    for col in range(23, 28):
        blocks.append((col * b, 7 * b, "wood_top"))
        blocks.append((col * b, 8 * b, "wood_center"))

    falling.append((29 * b, 7 * b))
    falling.append((31 * b, 6 * b))
    falling.append((33 * b, 6 * b))
    falling.append((35 * b, 5 * b))

    trampolines.append((37 * b, 7 * b - 40))
    for col in range(36, 39):
        blocks.append((col * b, 7 * b, "wood_top"))

    for col in range(43, 50):
        blocks.append((col * b, 6 * b, "wood_top"))
        blocks.append((col * b, 7 * b, "wood_center"))

    saws.append((13 * b, 8 * b - 70, 180, 2.8, True))
    saws.append((18 * b, 8 * b - 70, 180, -2.8, True))
    saws.append((15 * b, 3 * b - 70, 120, 2.5, True))

    for col in range(23, 26):
        spikes.append((col * b, 7 * b - 32))

    for col in range(13, 17):
        fruits.append((col * b + 16, 3 * b, "Kiwi"))
    for col in range(18, 22):
        fruits.append((col * b + 16, 3 * b, "Orange"))
    fruits.append((31 * b + 16, 5 * b, "Melon"))
    fruits.append((33 * b + 16, 5 * b, "Melon"))
    fruits.append((35 * b + 16, 4 * b, "Strawberry"))
    for col in range(44, 48):
        fruits.append((col * b + 16, 5 * b, "Kiwi"))

    boxes.append((14 * b, 1 * b, "Box2", "Pineapple"))
    boxes.append((20 * b, 1 * b, "Box3", "Strawberry"))
    boxes.append((45 * b, 3 * b, "Box1", "Melon"))

    return {
        "id": 2,
        "name": "Sawblade Heights",
        "bg_image": "Yellow.png",
        "style": "wood_top",
        "start_pos": start_pos,
        "end_pos": end_pos,
        "blocks": blocks,
        "fruits": fruits,
        "boxes": boxes,
        "spikes": spikes,
        "fires": fires,
        "saws": saws,
        "trampolines": trampolines,
        "fans": fans,
        "falling_platforms": falling,
        "moving_platforms": moving,
        "checkpoints": checkpoints,
        "level_width": 3400,
        "level_height": 720
    }

def build_level_3():
    """Level 3: Windy Skies - Wind fans, falling platforms, high precision leaps."""
    b = BLOCK_SIZE
    blocks = []
    fruits = []
    boxes = []
    spikes = []
    fires = []
    saws = []
    trampolines = []
    fans = []
    falling = []
    moving = []
    checkpoints = [(1550, 6 * b - 64)]
    start_pos = (120, 7 * b - 64)
    end_pos = (3100, 5 * b - 64)

    for col in range(-2, 8):
        blocks.append((col * b, 8 * b, "grass_top"))
        blocks.append((col * b, 9 * b, "grass_center"))

    fans.append((6 * b, 8 * b - 16, 220))

    for col in range(8, 12):
        blocks.append((col * b, 4 * b, "grass_top"))

    falling.append((13 * b, 4 * b))
    falling.append((15 * b, 5 * b))
    falling.append((17 * b, 4 * b))

    for col in range(21, 27):
        blocks.append((col * b, 7 * b, "grass_top"))
        blocks.append((col * b, 8 * b, "grass_center"))

    spikes.append((22 * b, 7 * b - 32))
    spikes.append((23 * b, 7 * b - 32))

    fans.append((26 * b, 7 * b - 16, 260))

    for col in range(28, 33):
        blocks.append((col * b, 3 * b, "grass_top"))
    saws.append((28 * b, 3 * b - 70, 160, 2.5, True))

    moving.append((34 * b, 5 * b, 180, 2.2, True, "brown"))
    moving.append((39 * b, 4 * b, 140, 2.0, False, "brown"))

    for col in range(45, 52):
        blocks.append((col * b, 6 * b, "grass_top"))
        blocks.append((col * b, 7 * b, "grass_center"))

    for col in range(8, 12):
        fruits.append((col * b + 16, 3 * b, "Melon"))
    fruits.append((13 * b + 16, 3 * b, "Pineapple"))
    fruits.append((15 * b + 16, 4 * b, "Pineapple"))
    fruits.append((17 * b + 16, 3 * b, "Pineapple"))
    fruits.append((29 * b + 16, 2 * b, "Strawberry"))
    fruits.append((31 * b + 16, 2 * b, "Strawberry"))
    for col in range(46, 50):
        fruits.append((col * b + 16, 5 * b, "Pineapple"))

    boxes.append((10 * b, 1 * b, "Box1", "Strawberry"))
    boxes.append((47 * b, 3 * b, "Box2", "Pineapple"))

    return {
        "id": 3,
        "name": "Windy Skies",
        "bg_image": "Blue.png",
        "style": "grass_top",
        "start_pos": start_pos,
        "end_pos": end_pos,
        "blocks": blocks,
        "fruits": fruits,
        "boxes": boxes,
        "spikes": spikes,
        "fires": fires,
        "saws": saws,
        "trampolines": trampolines,
        "fans": fans,
        "falling_platforms": falling,
        "moving_platforms": moving,
        "checkpoints": checkpoints,
        "level_width": 3500,
        "level_height": 720
    }

def build_level_4():
    """Level 4: Industrial Core - Moving platforms, timing fire hazards, moving saws."""
    b = BLOCK_SIZE
    blocks = []
    fruits = []
    boxes = []
    spikes = []
    fires = []
    saws = []
    trampolines = []
    fans = []
    falling = []
    moving = []
    checkpoints = [(1550, 7 * b - 64)]
    start_pos = (120, 7 * b - 64)
    end_pos = (3200, 6 * b - 64)

    for col in range(-2, 7):
        blocks.append((col * b, 8 * b, "stone_top"))
        blocks.append((col * b, 9 * b, "stone_center"))

    moving.append((7 * b, 7 * b, 180, 2.5, True, "grey"))

    for col in range(7, 13):
        spikes.append((col * b, 9 * b - 32))

    for col in range(12, 17):
        blocks.append((col * b, 7 * b, "stone_top"))
        blocks.append((col * b, 8 * b, "stone_center"))
    fires.append((13 * b, 7 * b - 64))
    fires.append((15 * b, 7 * b - 64))

    moving.append((18 * b, 7 * b, 160, 2.0, False, "grey"))

    for col in range(21, 29):
        blocks.append((col * b, 4 * b, "stone_top"))
    saws.append((22 * b, 4 * b - 70, 200, 3.0, True))

    for col in range(23, 27):
        blocks.append((col * b, 8 * b, "stone_top"))
        blocks.append((col * b, 9 * b, "stone_center"))

    trampolines.append((26 * b, 8 * b - 40))

    moving.append((30 * b, 5 * b, 200, 2.5, True, "grey"))
    moving.append((35 * b, 6 * b, 180, -2.5, True, "grey"))

    falling.append((40 * b, 6 * b))
    falling.append((42 * b, 5 * b))
    falling.append((44 * b, 6 * b))

    for col in range(47, 54):
        blocks.append((col * b, 7 * b, "stone_top"))
        blocks.append((col * b, 8 * b, "stone_center"))

    fruits.append((9 * b + 16, 5 * b, "Orange"))
    fruits.append((14 * b + 16, 5 * b, "Apple"))
    for col in range(23, 28):
        fruits.append((col * b + 16, 3 * b, "Orange"))
    fruits.append((31 * b + 16, 4 * b, "Strawberry"))
    fruits.append((36 * b + 16, 5 * b, "Strawberry"))
    for col in range(48, 52):
        fruits.append((col * b + 16, 6 * b, "Orange"))

    boxes.append((14 * b, 2 * b, "Box3", "Pineapple"))
    boxes.append((49 * b, 4 * b, "Box2", "Melon"))

    return {
        "id": 4,
        "name": "Industrial Core",
        "bg_image": "Gray.png",
        "style": "stone_top",
        "start_pos": start_pos,
        "end_pos": end_pos,
        "blocks": blocks,
        "fruits": fruits,
        "boxes": boxes,
        "spikes": spikes,
        "fires": fires,
        "saws": saws,
        "trampolines": trampolines,
        "fans": fans,
        "falling_platforms": falling,
        "moving_platforms": moving,
        "checkpoints": checkpoints,
        "level_width": 3600,
        "level_height": 720
    }

def build_level_5():
    """Level 5: The Castle Gauntlet - Grand finale combining all hazards!"""
    b = BLOCK_SIZE
    blocks = []
    fruits = []
    boxes = []
    spikes = []
    fires = []
    saws = []
    trampolines = []
    fans = []
    falling = []
    moving = []
    checkpoints = [(1550, 7 * b - 64), (2800, 5 * b - 64)]
    start_pos = (120, 7 * b - 64)
    end_pos = (4000, 5 * b - 64)

    for col in range(-2, 8):
        blocks.append((col * b, 8 * b, "stone_top"))
        blocks.append((col * b, 9 * b, "stone_center"))

    saws.append((4 * b, 8 * b - 70, 120, 3.0, True))
    spikes.append((7 * b, 8 * b - 32))

    trampolines.append((6 * b, 8 * b - 40))
    fans.append((10 * b, 8 * b, 260))

    for col in [11, 13, 15]:
        blocks.append((col * b, 5 * b, "stone_top"))
        fires.append((col * b, 5 * b - 64))

    for col in range(21, 28):
        blocks.append((col * b, 8 * b, "stone_top"))
        blocks.append((col * b, 9 * b, "stone_center"))

    saws.append((21 * b, 8 * b - 70, 180, 3.2, True))
    saws.append((25 * b, 8 * b - 70, 180, -3.2, True))

    moving.append((29 * b, 7 * b, 160, 2.6, True, "grey"))
    moving.append((33 * b, 5 * b, 160, 2.6, True, "brown"))

    for col in range(39, 45):
        blocks.append((col * b, 6 * b, "stone_top"))
        blocks.append((col * b, 7 * b, "stone_center"))
    trampolines.append((43 * b, 6 * b - 40))

    falling.append((46 * b, 5 * b))
    falling.append((48 * b, 4 * b))
    falling.append((50 * b, 3 * b))
    falling.append((52 * b, 4 * b))
    falling.append((54 * b, 5 * b))

    saws.append((51 * b, 1 * b, 160, 3.0, False))

    for col in range(58, 68):
        blocks.append((col * b, 6 * b, "stone_top"))
        blocks.append((col * b, 7 * b, "stone_center"))

    for i, f_type in enumerate(["Apple", "Bananas", "Cherries", "Kiwi", "Melon", "Orange", "Pineapple", "Strawberry"]):
        fruits.append(((59 + i) * b + 16, 5 * b, f_type))

    boxes.append((60 * b, 3 * b, "Box1", "Strawberry"))
    boxes.append((62 * b, 3 * b, "Box2", "Strawberry"))
    boxes.append((64 * b, 3 * b, "Box3", "Strawberry"))

    return {
        "id": 5,
        "name": "The Castle Gauntlet",
        "bg_image": "Purple.png",
        "style": "stone_top",
        "start_pos": start_pos,
        "end_pos": end_pos,
        "blocks": blocks,
        "fruits": fruits,
        "boxes": boxes,
        "spikes": spikes,
        "fires": fires,
        "saws": saws,
        "trampolines": trampolines,
        "fans": fans,
        "falling_platforms": falling,
        "moving_platforms": moving,
        "checkpoints": checkpoints,
        "level_width": 4500,
        "level_height": 720
    }

LEVEL_BUILDERS = [
    build_level_1,
    build_level_2,
    build_level_3,
    build_level_4,
    build_level_5,
]

def get_level(level_idx):
    if 0 <= level_idx < len(LEVEL_BUILDERS):
        return LEVEL_BUILDERS[level_idx]()
    return LEVEL_BUILDERS[0]()

def total_levels():
    return len(LEVEL_BUILDERS)
