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

MOVE_SPEED = 7
ENEMY_MOVE_SPEED = 1
JUMP_POWER = 20
GRAVITY = 1

FPS = 100

element_texture_folder = 'data\\textures\\png\\elements'
tiles_texture_folder = 'data\\textures\\png\\tiles'
levels_folder = 'data\\levels'
player_texture_path = 'data\\textures\\player\\textures_48.png'
enemy_texture_path = 'data\\textures\\enemy\\textures_48.png'
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
        self.memory_dx = 0
        self.memory_dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)
        self.memory_dx += self.dx
        self.memory_dy += self.dy

    def set_memory(self, x, y):
        self.memory_dx = x
        self.memory_dy = y

    def get_memory(self):
        return self.memory_dx, self.memory_dy

    def get_memory_x(self):
        return self.memory_dx

    def get_memory_y(self):
        return self.memory_dy


class GamePerson(pygame.sprite.Sprite):
    def __init__(self, x, y, *groups):
        super().__init__(groups)
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.xvel = 0
        self.yvel = 0
        self.onGround = False
        self.death_mode = False
        self.damage_mode = False
        self.attack_group = None
        self.rotation = ROTATION_RIGHT
        self.cut_frame = 0
        self.cut_frame_update = 0

    def collide(self, xvel, yvel,
                space_mask_right, space_mask_left, space_mask_up, space_mask_bottom,
                reverse_x=False):
        for tile in pygame.sprite.spritecollide(self, tiles_group, False,
                                                collided=pygame.sprite.collide_mask):
            if reverse_x and xvel != 0:
                self.xvel = -self.xvel
            if xvel > 0:  # если движется вправо
                self.rect.right = tile.rect.left + space_mask_right - 1  # то не движется вправо
            if xvel < 0:  # если движется влево
                self.rect.left = tile.rect.right - space_mask_left + 1  # то не движется влево
            if yvel > 0:  # если падает вниз
                self.rect.bottom = tile.rect.top + space_mask_bottom - 1  # то не падает вниз
                self.onGround = True  # и становится на что-то твердое
                self.yvel = 0
            if yvel < 0:  # если движется вверх
                self.rect.top = tile.rect.bottom - space_mask_up + 1  # то не движется вверх
                self.yvel = 0  # и энергия прыжка пропадает

    def cut_sheet(self, sheet, columns, row, width_image, height_image):
        frames = []
        for col in range(columns):
            frame_location = (height_image * col, width_image * (row - 1))
            cur_frame = sheet.subsurface(pygame.Rect(
                frame_location, (height_image, width_image)))
            cur_frame = cur_frame.convert_alpha()
            frames.append(cur_frame)
        return frames

    def attack(self):
        if not self.attack_group and not self.damage_mode and not self.death_mode:
            self.attack_group = choice(self.attack_groups)
            self.cut_frame_update = 0

    def damage(self):
        if not self.damage_mode and not self.attack_group and not self.death_mode:
            self.damage_mode = True
            self.cut_frame_update = 0

    def death(self):
        if not self.death_mode and not self.attack_group and not self.damage_mode:
            self.death_mode = True
            self.cut_frame_update = 0

    def update_sprite_image(self):
        if self.xvel > 0:
            self.rotation = ROTATION_RIGHT
        elif self.xvel < 0:
            self.rotation = ROTATION_LEFT
        if self.cut_frame % 5 == 0:
            if self.rotation == ROTATION_RIGHT:
                if self.death_mode:
                    self.image = self.frames['death_right'][self.cut_frame_update]
                    if self.cut_frame_update == len(self.frames['death_right']) - 1:
                        self.death_mode = False
                        self.cut_frame_update = 0
                        self.kill()

                elif self.damage_mode:
                    self.image = self.frames['damage_right'][self.cut_frame_update]
                    if self.cut_frame_update == len(self.frames['damage_right']) - 1:
                        self.damage_mode = False
                        self.cut_frame_update = 0
                        if isinstance(self, Player):
                            self.spawn_check_point()

                elif self.attack_group:
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
                if self.death_mode:
                    self.image = self.frames['death_left'][self.cut_frame_update]
                    if self.cut_frame_update == len(self.frames['death_left']) - 1:
                        self.death_mode = False
                        self.cut_frame_update = 0
                        self.kill()

                elif self.damage_mode:
                    self.image = self.frames['damage_left'][self.cut_frame_update]
                    if self.cut_frame_update == len(self.frames['damage_left']) - 1:
                        self.damage_mode = False
                        self.cut_frame_update = 0
                        if isinstance(self, Player):
                            self.spawn_check_point()

                elif self.attack_group:
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


class Player(GamePerson):
    def __init__(self, sheet, x, y):
        super().__init__(x, y, all_sprite, player_group)
        self.check_point = (self.rect.x, self.rect.y)
        self.frames = {
            'idle_right': self.cut_sheet(sheet, 13, 1, 48, 48),
            'run_right': self.cut_sheet(sheet, 8, 2, 48, 48),
            'attack_right_1': self.cut_sheet(sheet, 10, 3, 48, 48),
            'attack_right_2': self.cut_sheet(sheet, 10, 4, 48, 48),
            'attack_right_3': self.cut_sheet(sheet, 10, 5, 48, 48),
            'jump_right': self.cut_sheet(sheet, 6, 6, 48, 48),
            'damage_right': self.cut_sheet(sheet, 4, 7, 48, 48),
            'death_right': self.cut_sheet(sheet, 7, 8, 48, 48),

            'idle_left': self.cut_sheet(sheet, 13, 9, 48, 48),
            'run_left': self.cut_sheet(sheet, 8, 10, 48, 48),
            'attack_left_1': self.cut_sheet(sheet, 10, 11, 48, 48),
            'attack_left_2': self.cut_sheet(sheet, 10, 12, 48, 48),
            'attack_left_3': self.cut_sheet(sheet, 10, 13, 48, 48),
            'jump_left': self.cut_sheet(sheet, 6, 14, 48, 48),
            'damage_left': self.cut_sheet(sheet, 4, 15, 48, 48),
            'death_left': self.cut_sheet(sheet, 7, 16, 48, 48)
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
        self.mask = pygame.mask.Mask(self.rect.size, False)
        self.space_mask_right = 18
        self.space_mask_left = 18
        self.space_mask_up = 18
        self.space_mask_bottom = 5
        self.lives = 100000
        for x in range(self.rect.width):
            for y in range(self.rect.height):
                if (self.space_mask_left <= x <= self.rect.width - self.space_mask_right
                        and self.space_mask_up <= y <= self.rect.height - self.space_mask_bottom):
                    self.mask.set_at((x, y), 1)

    def update(self, left, right, up):
        if left:
            self.xvel = -MOVE_SPEED
        if right:
            self.xvel = MOVE_SPEED
        if not (left or right) or self.damage_mode or self.death_mode:
            self.xvel = 0
        if up:
            if self.onGround:
                self.yvel = -JUMP_POWER
        if not self.onGround:
            self.yvel += GRAVITY
        self.onGround = False
        self.rect.y += self.yvel
        self.collide(0, self.yvel, self.space_mask_right, self.space_mask_left,
                     self.space_mask_up, self.space_mask_bottom)
        self.rect.x += self.xvel
        self.collide(self.xvel, 0, self.space_mask_right, self.space_mask_left,
                     self.space_mask_up, self.space_mask_bottom)
        self.check_collide_enemy()
        self.update_sprite_image()

    def check_collide_enemy(self):
        for enemy in pygame.sprite.spritecollide(self, enemy_group, False,
                                                 collided=pygame.sprite.collide_mask):
            if self.attack_group:
                enemy.death()
            else:
                self.lives -= 1
                if self.lives > 0:
                    self.damage()
                else:
                    self.death()
                enemy.attack()

    def spawn_check_point(self):
        self.rect.x += camera.get_memory_x()
        self.rect.y += camera.get_memory_y()


class Enemy(GamePerson):
    def __init__(self, sheet, x, y):
        super().__init__(x, y, all_sprite, enemy_group)
        self.frames = {
            'idle_right': self.cut_sheet(sheet, 5, 1, 48, 57),
            'run_right': self.cut_sheet(sheet, 8, 2, 48, 57),
            'attack_right_1': self.cut_sheet(sheet, 7, 3, 48, 57),
            'attack_right_2': self.cut_sheet(sheet, 6, 4, 48, 57),
            'attack_right_3': self.cut_sheet(sheet, 2, 5, 48, 57),
            'jump_right': self.cut_sheet(sheet, 5, 6, 48, 57),
            'damage_right': self.cut_sheet(sheet, 4, 7, 48, 57),
            'death_right': self.cut_sheet(sheet, 7, 8, 48, 57),

            'idle_left': self.cut_sheet(sheet, 5, 9, 48, 57),
            'run_left': self.cut_sheet(sheet, 8, 10, 48, 57),
            'attack_left_1': self.cut_sheet(sheet, 7, 11, 48, 57),
            'attack_left_2': self.cut_sheet(sheet, 6, 12, 48, 57),
            'attack_left_3': self.cut_sheet(sheet, 2, 13, 48, 57),
            'jump_left': self.cut_sheet(sheet, 5, 14, 48, 57),
            'damage_left': self.cut_sheet(sheet, 4, 15, 48, 57),
            'death_left': self.cut_sheet(sheet, 7, 16, 48, 57)
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
        self.image = pygame.Surface((self.image.get_size()))
        self.mask = pygame.mask.Mask(self.rect.size, False)
        self.space_mask_right = 12
        self.space_mask_left = 18
        self.space_mask_up = 18
        self.space_mask_bottom = 5
        for x in range(self.rect.width):
            for y in range(self.rect.height):
                if (self.space_mask_left <= x <= self.rect.width - self.space_mask_right
                        and self.space_mask_up <= y <= self.rect.height - self.space_mask_bottom):
                    self.mask.set_at((x, y), 1)
        self.xvel = choice((-ENEMY_MOVE_SPEED, ENEMY_MOVE_SPEED))

    def update(self, *args):
        self.update_sprite_image()
        if not self.onGround:
            self.yvel += GRAVITY
        self.onGround = False
        self.rect.y += self.yvel
        self.collide(0, self.yvel, self.space_mask_right, self.space_mask_left,
                     self.space_mask_up, self.space_mask_bottom, reverse_x=True)
        self.rect.x += self.xvel
        self.collide(self.xvel, 0, self.space_mask_right, self.space_mask_left,
                     self.space_mask_up, self.space_mask_bottom, reverse_x=True)


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
            elif level_map[y][x] == '!':
                Enemy(ememy_sheet, x, y)
            elif level_map[y][x] != '#' and level_map[y][x] != ' ':
                Tile(level_map[y][x], x, y)
            current_tile += 1
            show_loading_level(current_tile // percent_one_tile)


clock = pygame.time.Clock()

tile_size = (TILE_SIZE, TILE_SIZE)

load_level_font = pygame.font.Font(None, 150)

background_image = load_image(background_path)
background_image = pygame.transform.scale(background_image, SIZE)

player_sheet = load_image(player_texture_path)
ememy_sheet = load_image(enemy_texture_path)

all_sprite = pygame.sprite.Group()
levels_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.GroupSingle()
enemy_group = pygame.sprite.Group()

start_game()

camera = Camera()
player = player_group.sprite
left, right, up = False, False, False

frames = 0

camera.update(player)
for sprite in all_sprite.sprites():
    camera.apply(sprite)
camera.set_memory(0, 0)

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
            elif event.button == pygame.BUTTON_RIGHT:
                camera.set_memory(0, 0)
    screen.blit(background_image, (0, 0))
    if frames % 2 == 0:
        player.update(left, right, up)
        for enemy in enemy_group.sprites():
            enemy.update()
        camera.update(player)
        for sprite in all_sprite.sprites():
            camera.apply(sprite)
    tiles_group.draw(screen)
    enemy_group.draw(screen)
    player_group.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
    frames += 1
