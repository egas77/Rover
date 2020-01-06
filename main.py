import os
import sys
import pygame
from random import choice

# Initialization PyGame
pygame.init()
# Screen Size
WIDTH, HEIGHT = SIZE = 1000, 500
# Main Display
screen = pygame.display.set_mode(SIZE)

TILE_SIZE = 48

OFFSET_RECT_PLAYER = 10

ROTATION_LEFT = 0
ROTATION_RIGHT = 1

MOVE_SPEED = TILE_SIZE * 0.2
JUMP_POWER = TILE_SIZE * 0.6
GRAVITY = TILE_SIZE * 0.05

FPS = 120

element_texture_folder = 'data\\textures\\png\\elements'
tiles_texture_folder = 'data\\textures\\png\\tiles'
levels_folder = 'data\\levels'
player_texture_folder = 'data\\textures\\player'
background_path = os.path.join(element_texture_folder, 'background.png')


def load_image(path, color_key=None):
    image = pygame.image.load(path)
    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


class Player(pygame.sprite.Sprite):
    def __init__(self, sheet, x, y):
        super().__init__(all_sprite, player_group)
        self.frames = {
            'idle_right': self.cut_sheet(sheet, 13, 1),
            'run_right': self.cut_sheet(sheet, 8, 2),
            'attack_right_1': self.cut_sheet(sheet, 10, 3),
            'attack_right_2': self.cut_sheet(sheet, 10, 4),
            'attack_right_3': self.cut_sheet(sheet, 10, 5),
            'jump_right': self.cut_sheet(sheet, 6, 6),
            'damage_right': self.cut_sheet(sheet, 4, 7),
            'death_right': self.cut_sheet(sheet, 7, 8),

            'idle_left': self.cut_sheet(sheet, 13, 9),
            'run_left': self.cut_sheet(sheet, 8, 10),
            'attack_left_1': self.cut_sheet(sheet, 10, 11),
            'attack_left_2': self.cut_sheet(sheet, 10, 12),
            'attack_left_3': self.cut_sheet(sheet, 10, 13),
            'jump_left': self.cut_sheet(sheet, 6, 14),
            'damage_left': self.cut_sheet(sheet, 4, 15),
            'death_left': self.cut_sheet(sheet, 7, 16)
        }
        self.attack_groups = (
            {
                ROTATION_RIGHT: 'attack_right_1',
                ROTATION_LEFT: 'attack_left_1'
            },
            {
                ROTATION_RIGHT: 'attack_right_2',
                ROTATION_LEFT: 'attack_left_2'
            },
            {
                ROTATION_RIGHT: 'attack_right_3',
                ROTATION_LEFT: 'attack_left_3'
            }
        )

        self.image = self.frames['idle_right'][0]
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.mask = pygame.mask.Mask(self.rect.size, False)
        for x in range(self.rect.width):
            for y in range(self.rect.height):
                if 18 <= x <= self.rect.width - 18 and 18 <= y <= self.rect.height - 5:
                    self.mask.set_at((x, y), 1)
        for x in range(self.rect.width):
            for y in range(self.rect.height):
                print(self.mask.get_at((y, x)), end='')
            print()
        self.xvel = 0
        self.yvel = 0
        self.onGround = False
        self.attack_group = None
        self.rotation = ROTATION_RIGHT
        self.cut_frame = 0
        self.cut_frame_update = 0

    def cut_sheet(self, sheet, columns, row):
        frames = []
        for col in range(columns):
            frame_location = (TILE_SIZE * col, TILE_SIZE * (row - 1))
            cur_frame = sheet.subsurface(pygame.Rect(
                frame_location, (TILE_SIZE, TILE_SIZE)))
            cur_frame = cur_frame.convert_alpha()
            frames.append(cur_frame)
        return frames

    def update(self, left, right, up):
        if left:
            self.xvel = -MOVE_SPEED
        if right:
            self.xvel = MOVE_SPEED
        if not (left or right):
            self.xvel = 0
        if up:
            if self.onGround:
                self.yvel = -JUMP_POWER
        self.update_sprite_image()
        if not self.onGround:
            self.yvel += GRAVITY
        self.onGround = False
        self.rect.y += self.yvel
        self.collide(0, self.yvel)
        self.rect.x += self.xvel
        self.collide(self.xvel, 0)

    def collide(self, xvel, yvel):
        for tile in pygame.sprite.spritecollide(self, tiles_group, False,
                                                collided=pygame.sprite.collide_mask):
            if xvel > 0:  # если движется вправо
                self.rect.right = tile.rect.left + 17  # то не движется вправо
            if xvel < 0:  # если движется влево
                self.rect.left = tile.rect.right - 17  # то не движется влево
            if yvel > 0:  # если падает вниз
                self.rect.bottom = tile.rect.top + 4  # то не падает вниз
                self.onGround = True  # и становится на что-то твердое
                self.yvel = 0
            if yvel < 0:  # если движется вверх
                self.rect.top = tile.rect.bottom - 17  # то не движется вверх
                self.yvel = 0  # и энергия прыжка пропадает

    def update_sprite_image(self):
        if self.xvel > 0:
            self.rotation = ROTATION_RIGHT
        elif self.xvel < 0:
            self.rotation = ROTATION_LEFT
        if self.cut_frame % 5 == 0:
            if self.rotation == ROTATION_RIGHT:
                if self.attack_group:
                    self.image = self.frames[self.attack_group[ROTATION_RIGHT]][
                        self.cut_frame_update]
                    if self.cut_frame_update == len(
                            self.frames[self.attack_group[ROTATION_RIGHT]]) - 1:
                        self.attack_group = None
                        self.cut_frame_update = 0

                elif self.xvel == 0 and self.yvel == 0:
                    self.image = self.frames['idle_right'][
                        self.cut_frame_update % len(self.frames['idle_right'])]

                elif self.yvel != 0 and not self.onGround:
                    if self.onGround and self.yvel < 0:
                        self.cut_frame_update = 0
                    self.image = self.frames['jump_right'][
                        self.cut_frame_update % len(self.frames['jump_right'])]

                elif self.xvel != 0:
                    self.image = self.frames['run_right'][
                        self.cut_frame_update % len(self.frames['run_right'])]

            elif self.rotation == ROTATION_LEFT:
                if self.attack_group:
                    self.image = self.frames[self.attack_group[ROTATION_LEFT]][
                        self.cut_frame_update]
                    if self.cut_frame_update == len(
                            self.frames[self.attack_group[ROTATION_LEFT]]) - 1:
                        self.attack_group = None
                        self.cut_frame_update = 0

                elif self.xvel == 0 and self.yvel == 0 and self.onGround:
                    self.image = self.frames['idle_left'][
                        self.cut_frame_update % len(self.frames['idle_left'])]

                elif self.yvel != 0 and not self.onGround:
                    if self.onGround and self.yvel > 0:
                        self.cut_frame_update = 0
                    self.image = self.frames['jump_left'][
                        self.cut_frame_update % len(self.frames['jump_left'])]

                elif self.xvel != 0:
                    self.image = self.frames['run_left'][
                        self.cut_frame_update % len(self.frames['run_left'])]
            self.cut_frame_update += 1
        self.cut_frame += 1

    def attack(self):
        self.attack_group = choice(self.attack_groups)
        self.cut_frame_update = 0


class Tile(pygame.sprite.Sprite):
    images = dict()

    def __init__(self, tile_name, x, y):
        super().__init__(all_sprite, tiles_group)
        if tile_name not in self.images:
            image = load_image(
                os.path.join(tiles_texture_folder, tile_name + '.png'))
            image = pygame.transform.scale(image, tile_size)
            self.images[tile_name] = image
        self.tile_name = tile_name
        self.image = self.images[tile_name]
        self.rect = self.image.get_rect(x=tile_size[0] * x, y=tile_size[1] * y)
        self.mask = pygame.mask.Mask(self.rect.size, fill=True)


class SelectLevelSprite(pygame.sprite.Sprite):
    font = pygame.font.Font(None, 100)
    size_sprite_level = (100, 100)
    background_image_level = load_image(os.path.join(element_texture_folder, 'box1.png'))
    background_image_level = pygame.transform.scale(background_image_level, size_sprite_level)

    def __init__(self, center_x, center_y, number_level):
        super().__init__(levels_group)
        self.image = self.background_image_level.copy()
        self.rect = self.image.get_rect(centerx=center_x, centery=center_y,
                                        size=self.size_sprite_level)
        self.number_level = number_level
        self.number_level_sprite = self.font.render(str(number_level), 1,
                                                    pygame.color.Color(206, 225, 66))
        self.image.blit(self.number_level_sprite,
                        (self.image.get_width() // 2 - self.number_level_sprite.get_width() // 2,
                         self.image.get_height() // 2 - self.number_level_sprite.get_height() // 2))


def terminate():
    """Function terminate this game"""
    pygame.quit()
    sys.exit(0)


def start_game():
    start_game_screen = pygame.Surface(SIZE)
    start_game_screen.set_colorkey(start_game_screen.get_at((0, 0)))
    button_radius = 50
    button_rect = pygame.Rect(WIDTH // 2 - button_radius, HEIGHT // 2 - button_radius + 100,
                              button_radius * 2, button_radius * 2)
    pygame.draw.circle(start_game_screen, pygame.Color(250, 250, 232),
                       button_rect.center, button_radius)
    name_game = load_image(os.path.join(element_texture_folder, 'name-game.png'))
    start_game_screen.blit(name_game, (0, 0))
    screen.blit(background_image, (0, 0))
    screen.blit(start_game_screen, (0, 0))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if (event.button == pygame.BUTTON_LEFT and
                        button_rect.collidepoint(event.pos[0], event.pos[1])):
                    number_level = select_level()
                    generate_level(number_level)
                    return None


def select_level():
    screen.blit(background_image, (0, 0))
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    size_sprite_level = SelectLevelSprite.size_sprite_level
    indent_level_px = 50
    SelectLevelSprite(center_x - size_sprite_level[0] * 2 - indent_level_px * 2, center_y, 1)
    SelectLevelSprite(center_x - size_sprite_level[0] - indent_level_px, center_y, 2)
    SelectLevelSprite(center_x, center_y, 3)
    SelectLevelSprite(center_x + size_sprite_level[0] + indent_level_px, center_y, 4)
    SelectLevelSprite(center_x + size_sprite_level[0] * 2 + indent_level_px * 2, center_y, 5)
    levels_group.draw(screen)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
                pos = event.pos
                for level_sprite in levels_group.sprites():
                    if level_sprite.rect.collidepoint(pos):
                        return level_sprite.number_level


def show_loading_level(percent):
    if percent > 100:
        percent = 100
    screen.blit(background_image, (0, 0))
    percent_label = load_level_font.render(str(percent) + ' %', 1,
                                           pygame.color.Color(0, 225, 45))
    screen.blit(percent_label,
                (WIDTH // 2 - percent_label.get_width() // 2,
                 HEIGHT // 2 - percent_label.get_height() // 2))
    pygame.display.flip()


def load_level(level_path):
    with open(level_path, mode='r', encoding='utf8') as mapFile:
        level_map = [line.rstrip() for line in mapFile]
    max_width = max(map(len, level_map))
    level_map = list(map(lambda row: row.ljust(max_width, '#'), level_map))
    return level_map


def generate_level(number_level):
    level_path = os.path.join(levels_folder, str(number_level) + '.lvl')
    level_map = load_level(level_path)
    count_tiles = len(level_map * len(level_map[0]))
    percent_one_tile = count_tiles // 100
    if not percent_one_tile:
        percent_one_tile = 1
    current_tile = 0
    for y in range(len(level_map)):
        for x in range(len(level_map[0])):
            if level_map[y][x] == '@':
                if not player_group.sprite:
                    Player(player_sheet, x, y)
                else:
                    print('Fatal Error: The player has already been created before')
                    terminate()
            elif level_map[y][x] != '#' and level_map[y][x] != ' ':
                Tile(level_map[y][x], x, y)
            current_tile += 1
            show_loading_level(current_tile // percent_one_tile)


clock = pygame.time.Clock()

tile_size = (TILE_SIZE, TILE_SIZE)

load_level_font = pygame.font.Font(None, 150)

background_image = load_image(background_path)
background_image = pygame.transform.scale(background_image, SIZE)

if TILE_SIZE == 48:
    player_sheet = load_image(os.path.join(player_texture_folder, 'textures_48.png'))
elif TILE_SIZE == 32:
    player_sheet = load_image(os.path.join(player_texture_folder, 'textures_32.png'))

all_sprite = pygame.sprite.Group()
levels_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.GroupSingle()

start_game()

camera = Camera()
player = player_group.sprite
left, right, up = False, False, False

frames = 0

camera.update(player)
for sprite in all_sprite.sprites():
    camera.apply(sprite)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                right = True
            elif event.key == pygame.K_a:
                left = True
            elif event.key == pygame.K_SPACE:
                up = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                right = False
            elif event.key == pygame.K_a:
                left = False
            elif event.key == pygame.K_SPACE:
                up = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                player.attack()
    screen.blit(background_image, (0, 0))
    all_sprite.draw(screen)
    player_group.draw(screen)
    if frames % 3 == 0:
        player.update(left, right, up)
    camera.update(player)
    for sprite in all_sprite.sprites():
        camera.apply(sprite)
    pygame.display.flip()
    clock.tick(FPS)
    frames += 1
