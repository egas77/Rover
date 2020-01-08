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
screen_rect = screen.get_rect()

TILE_SIZE = 48

ROTATION_LEFT = 0
ROTATION_RIGHT = 1
MAIN_MENU = 1
RESTART_LEVEL = 2

MOVE_SPEED = 7
ENEMY_MOVE_SPEED = 1
JUMP_POWER = 15
GRAVITY = 1

FPS = 100

BACKGROUND_SOUND_VOLUME = 0.5
MUSIC_ON = False

ELEMENT_TEXTURE_FOLDER = 'data/textures/elements'
TILES_TEXTURE_FOLDER = 'data/textures/tiles'
ICONS_FOLDER = 'data/textures/icons'
TEXT_FOLDER = 'data/textures/text'
MUSIC_FOLDER = 'data/music'
LEVELS_FOLDER = 'data/levels'
PLAYER_TEXTURE_PATH = 'data/textures/player/player.png'
ENEMY_TEXTURE_PATH = 'data/textures/enemy/soldier.png'

GAME_OBJECTS_DICT = {
    '!': ('blade.png',
          {'collided': True, 'collided_do_kill': True, 'ignore_player': False,
           'ignore_enemy': True, 'size': (48, 96)}),
    '$': ('bush1.png',
          {'collided': False, 'collided_do_kill': False, 'ignore_player': False,
           'ignore_enemy': True, 'size': (48, 48)}),
    '%': ('bush2.png',
          {'collided': False, 'collided_do_kill': False, 'ignore_player': False,
           'ignore_enemy': True, 'size': (48, 48)}),
    '^': ('button.png',
          {'collided': True, 'collided_do_kill': False, 'ignore_player': False,
           'ignore_enemy': True, 'size': (48, 12)}),
    ':': ('cell.png',
          {'collided': True, 'collided_do_kill': False, 'ignore_player': False,
           'ignore_enemy': True, 'size': (48, 48)}),
    '&': ('door.png',
          {'collided': True, 'collided_do_kill': False, 'ignore_player': False,
           'ignore_enemy': True, 'size': (48, 48)}),
    '+': ('coin.png',
          {'collided': True, 'collided_do_kill': False, 'ignore_player': False,
           'ignore_enemy': True, 'size': (32, 32)}),
    '|': ('crystal.png',
          {'collided': True, 'collided_do_kill': False, 'ignore_player': False,
           'ignore_enemy': True, 'size': (32, 32)}),
    '1': ('flower1.png',
          {'collided': False, 'collided_do_kill': False, 'ignore_player': False,
           'ignore_enemy': True, 'size': (48, 48)}),
    '2': ('flower2.png',
          {'collided': False, 'collided_do_kill': False, 'ignore_player': False,
           'ignore_enemy': True, 'size': (48, 48)}),
    '3': ('flower3.png',
          {'collided': False, 'collided_do_kill': False, 'ignore_player': False,
           'ignore_enemy': True, 'size': (48, 48)}),
    '4': ('flower4.png',
          {'collided': False, 'collided_do_kill': False, 'ignore_player': False,
           'ignore_enemy': True, 'size': (48, 48)}),
    '5': ('flower5.png',
          {'collided': False, 'collided_do_kill': False, 'ignore_player': False,
           'ignore_enemy': True, 'size': (48, 48)}),
    '6': ('heart.png',
          {'collided': True, 'collided_do_kill': False, 'ignore_player': False,
           'ignore_enemy': True, 'size': (32, 32)}),
    '7': ('key.png',
          {'collided': True, 'collided_do_kill': False, 'ignore_player': False,
           'ignore_enemy': True, 'size': (32, 32)}),
    '8': ('box1.png',
          {'collided': True, 'collided_do_kill': False, 'ignore_player': False,
           'ignore_enemy': False, 'size': (48, 48)}),
    '9': ('tree1.png',
          {'collided': False, 'collided_do_kill': False, 'ignore_player': False,
           'ignore_enemy': True, 'size': (48, 48)}),
    '0': ('tree2.png',
          {'collided': False, 'collided_do_kill': False, 'ignore_player': False,
           'ignore_enemy': True, 'size': (48, 48)}),
    '*': ('pointer.png',
          {'collided': True, 'collided_do_kill': False, 'ignore_player': False,
           'ignore_enemy': True, 'size': (48, 48)}),
    '/': ('zero_enemy.png',
          {'collided': True, 'collided_do_kill': False, 'ignore_player': True,
           'ignore_enemy': False, 'size': (48, 48)}),
    '\\': ('zero_player.png',
           {'collided': True, 'collided_do_kill': False, 'ignore_player': False,
            'ignore_enemy': True, 'size': (48, 48)}),
    '\'': ('thorns1.png',
           {'collided': True, 'collided_do_kill': True, 'ignore_player': False,
            'ignore_enemy': False, 'size': (240, 48)}),
    '"': ('thorns2.png',
          {'collided': True, 'collided_do_kill': True, 'ignore_player': False,
           'ignore_enemy': False, 'size': (240, 48)}),
}


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


def cut_sheet(sheet, columns, row, width_image, height_image):
    frames = []
    for col in range(columns):
        frame_location = (height_image * col, width_image * (row - 1))
        cur_frame = sheet.subsurface(pygame.Rect(
            frame_location, (height_image, width_image)))
        cur_frame = cur_frame.convert_alpha()
        frames.append(cur_frame)
    return frames


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


class SelectLevelSprite(pygame.sprite.Sprite):
    font = pygame.font.Font(None, 100)
    size_sprite_level = (100, 100)
    background_image_level = load_image(os.path.join(ELEMENT_TEXTURE_FOLDER, 'box1.png'))
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


class HeartIcon(pygame.sprite.Sprite):
    image = load_image(os.path.join(ELEMENT_TEXTURE_FOLDER, 'heart.png'))
    width_heart = image.get_width()
    space_x = 5

    def __init__(self, x):
        super().__init__(hearts_group)
        self.rect = self.image.get_rect(x=x * self.width_heart + self.space_x * (x + 1), y=10)


class KeyIcon(pygame.sprite.Sprite):
    image = load_image(os.path.join(ELEMENT_TEXTURE_FOLDER, 'key.png'))
    image = pygame.transform.scale(image, (48, 48))

    def __init__(self):
        super().__init__(key_group)
        self.rect = self.image.get_rect(x=WIDTH - 70, y=20)


class GamePerson(pygame.sprite.Sprite):
    def __init__(self, x, y, *groups):
        super().__init__(groups)
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.xvel = 0
        self.yvel = 0
        self.on_ground = False
        self.death_mode = False
        self.damage_mode = False
        self.attack_group = None
        self.rotation = ROTATION_RIGHT
        self.cut_frame = 0
        self.cut_frame_update = 0
        self.moving = False
        self.lose = False

    def collide(self, xvel, yvel,
                space_mask_right, space_mask_left, space_mask_up, space_mask_bottom,
                reverse_x=False):
        for game_object in pygame.sprite.spritecollide(self, game_objects, False,
                                                       collided=pygame.sprite.collide_mask):
            if isinstance(self, Player):
                if game_object.ignore_player:
                    continue
                if game_object.collision_do_kill:
                    if not self.damage_mode and not self.death_mode:
                        self.lives -= 1
                        if self.lives > 0:
                            self.damage()
                        else:
                            self.death()
                        self.visible_hearts()
                if isinstance(game_object, Heart):
                    self.lives += 1
                    game_object.kill()
                    self.visible_hearts()
                    continue
                if isinstance(game_object, CheckPoint):
                    camera.set_memory(0, 0)
                    width, height = game_object.rect.size
                    image = game_object.image
                    for y in range(width):
                        for x in range(height):
                            pixel = image.get_at((x, y))
                            if pixel.a != 0:
                                image.set_at((x, y), (100, 100, 100, 200))
                            game_object.mask = pygame.mask.Mask((width, height), fill=0)
                            game_object.collision = False
                            game_object.collision_do_kill = False
                    continue
                if isinstance(game_object, Key):
                    game_object.kill()
                    self.key = True
                    self.visible_key()
                    continue
                if isinstance(game_object, Door):
                    if self.key:
                        self.finish = True
                    continue
                if isinstance(game_object, Coin):
                    self.coins += 1
                    game_object.kill()
                    continue
                if isinstance(game_object, Crystal):
                    self.crystals += 1
                    game_object.kill()
                    continue
                if isinstance(game_object, ButtonJump):
                    if yvel:
                        self.yvel = -JUMP_POWER * 1.35
                    return None
            else:
                if game_object.ignore_enemy:
                    continue

            if reverse_x and xvel != 0:
                self.xvel = -self.xvel
            if xvel > 0:  # если движется вправо
                self.rect.right = game_object.rect.left + space_mask_right - 1  # то не движется вправо
            if xvel < 0:  # если движется влево
                self.rect.left = game_object.rect.right - space_mask_left + 1  # то не движется влево
            if yvel > 0:  # если падает вниз
                self.rect.bottom = game_object.rect.top + space_mask_bottom - 1  # то не падает вниз
                self.on_ground = True  # и становится на что-то твердое
                self.yvel = 0
            if yvel < 0:  # если движется вверх
                self.rect.top = game_object.rect.bottom - space_mask_up + 1  # то не движется вверх
                self.yvel = 0  # и энергия прыжка пропадает

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
            self.lose = True
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
                            self.restart()

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

                elif self.yvel != 0 and not self.on_ground:
                    if self.on_ground and self.yvel < 0:
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
                            self.restart()

                elif self.attack_group:
                    self.image = self.frames[self.attack_group[ROTATION_LEFT]][
                        self.cut_frame_update]
                    if self.cut_frame_update == len(
                            self.frames[self.attack_group[ROTATION_LEFT]]) - 1:
                        self.attack_group = None
                        self.cut_frame_update = 0

                elif self.xvel == 0 and self.yvel == 0 and self.on_ground:
                    self.image = self.frames['idle_left'][
                        self.cut_frame_update % len(self.frames['idle_left'])]

                elif self.yvel != 0 and not self.on_ground:
                    if self.on_ground and self.yvel > 0:
                        self.cut_frame_update = 0
                    self.image = self.frames['jump_left'][
                        self.cut_frame_update % len(self.frames['jump_left'])]

                elif self.xvel != 0:
                    self.image = self.frames['run_left'][
                        self.cut_frame_update % len(self.frames['run_left'])]
            self.cut_frame_update += 1
        self.cut_frame += 1

    def check_in_screen(self):
        if self.rect.colliderect(screen_rect) and not self.moving:
            return True
        return False


class Player(GamePerson):
    sheet = load_image(PLAYER_TEXTURE_PATH)

    frames = {
        'idle_right': cut_sheet(sheet, 13, 1, 48, 48),
        'run_right': cut_sheet(sheet, 8, 2, 48, 48),
        'attack_right_1': cut_sheet(sheet, 10, 3, 48, 48),
        'attack_right_2': cut_sheet(sheet, 10, 4, 48, 48),
        'attack_right_3': cut_sheet(sheet, 10, 5, 48, 48),
        'jump_right': cut_sheet(sheet, 6, 6, 48, 48),
        'damage_right': cut_sheet(sheet, 4, 7, 48, 48),
        'death_right': cut_sheet(sheet, 7, 8, 48, 48),

        'idle_left': cut_sheet(sheet, 13, 9, 48, 48),
        'run_left': cut_sheet(sheet, 8, 10, 48, 48),
        'attack_left_1': cut_sheet(sheet, 10, 11, 48, 48),
        'attack_left_2': cut_sheet(sheet, 10, 12, 48, 48),
        'attack_left_3': cut_sheet(sheet, 10, 13, 48, 48),
        'jump_left': cut_sheet(sheet, 6, 14, 48, 48),
        'damage_left': cut_sheet(sheet, 4, 15, 48, 48),
        'death_left': cut_sheet(sheet, 7, 16, 48, 48)
    }
    attack_groups = (
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

    def __init__(self, x, y):
        super().__init__(x, y, all_sprite, player_group)
        self.check_point = (self.rect.x, self.rect.y)
        self.image = self.frames['idle_right'][0]
        self.mask = pygame.mask.Mask(self.rect.size, False)
        self.space_mask_right = 19
        self.space_mask_left = 18
        self.space_mask_up = 18
        self.space_mask_bottom = 5
        self.lives = 3
        self.key = False
        self.finish = False
        self.coins = 0
        self.crystals = 0
        for x in range(self.rect.width):
            for y in range(self.rect.height):
                if (self.space_mask_left <= x <= self.rect.width - self.space_mask_right
                        and self.space_mask_up <= y <= self.rect.height - self.space_mask_bottom):
                    self.mask.set_at((x, y), 1)
        self.visible_hearts()

    def update(self, left, right, up, boost):
        if left:
            self.xvel = -MOVE_SPEED
        if right:
            self.xvel = MOVE_SPEED
        if not (left or right) or self.damage_mode or self.death_mode:
            self.xvel = 0
        if boost:
            self.xvel *= 1.75
        if up:
            if self.on_ground:
                self.yvel = -JUMP_POWER
        if not self.on_ground:
            self.yvel += GRAVITY
        self.on_ground = False
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
            elif not self.damage_mode and not self.death_mode:
                self.lives -= 1
                if self.lives > 0:
                    self.damage()
                else:
                    self.death()
                self.visible_hearts()
                if self.rotation == enemy.rotation:
                    enemy.xvel = -enemy.xvel
                    if enemy.rotation == ROTATION_LEFT:
                        enemy.rotation = ROTATION_RIGHT
                    else:
                        enemy.rotation = ROTATION_LEFT
                enemy.attack()

    def restart(self):
        self.spawn_check_point()
        self.visible_hearts()

    def spawn_check_point(self):
        self.rect.x += camera.get_memory_x()
        self.rect.y += camera.get_memory_y()

    def visible_hearts(self):
        hearts_group.empty()
        for x in range(self.lives):
            HeartIcon(x)

    def visible_key(self):
        KeyIcon()


class Enemy(GamePerson):
    sheet = load_image(ENEMY_TEXTURE_PATH)

    frames = {
        'idle_right': cut_sheet(sheet, 5, 1, 48, 57),
        'run_right': cut_sheet(sheet, 8, 2, 48, 57),
        'attack_right_1': cut_sheet(sheet, 7, 3, 48, 57),
        'attack_right_2': cut_sheet(sheet, 6, 4, 48, 57),
        'attack_right_3': cut_sheet(sheet, 2, 5, 48, 57),
        'jump_right': cut_sheet(sheet, 5, 6, 48, 57),
        'damage_right': cut_sheet(sheet, 4, 7, 48, 57),
        'death_right': cut_sheet(sheet, 7, 8, 48, 57),

        'idle_left': cut_sheet(sheet, 5, 9, 48, 57),
        'run_left': cut_sheet(sheet, 8, 10, 48, 57),
        'attack_left_1': cut_sheet(sheet, 7, 11, 48, 57),
        'attack_left_2': cut_sheet(sheet, 6, 12, 48, 57),
        'attack_left_3': cut_sheet(sheet, 2, 13, 48, 57),
        'jump_left': cut_sheet(sheet, 5, 14, 48, 57),
        'damage_left': cut_sheet(sheet, 4, 15, 48, 57),
        'death_left': cut_sheet(sheet, 7, 16, 48, 57)
    }

    attack_groups = (
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

    def __init__(self, x, y, rotation):
        super().__init__(x, y, all_sprite, enemy_group)
        self.image = self.frames['idle_right'][0]
        self.mask = pygame.mask.Mask(self.rect.size, False)
        self.space_mask_right = 5
        self.space_mask_left = 5
        self.space_mask_up = 18
        self.space_mask_bottom = 5
        for x in range(self.rect.width):
            for y in range(self.rect.height):
                if (self.space_mask_left <= x <= self.rect.width - self.space_mask_right
                        and self.space_mask_up <= y <= self.rect.height - self.space_mask_bottom):
                    self.mask.set_at((x, y), 1)
        if rotation == ROTATION_LEFT:
            self.xvel = -ENEMY_MOVE_SPEED
        elif rotation == ROTATION_RIGHT:
            self.xvel = ENEMY_MOVE_SPEED

    def update(self, *args):
        if not self.moving:
            self.moving = self.check_in_screen()
        if self.moving:
            self.update_sprite_image()
            if not self.on_ground:
                self.yvel += GRAVITY
            self.on_ground = False
            self.rect.y += self.yvel
            self.collide(0, self.yvel, self.space_mask_right, self.space_mask_left,
                         self.space_mask_up, self.space_mask_bottom, reverse_x=True)
            self.rect.x += self.xvel
            self.collide(self.xvel, 0, self.space_mask_right, self.space_mask_left,
                         self.space_mask_up, self.space_mask_bottom, reverse_x=True)


class GameObject(pygame.sprite.Sprite):
    images = dict()

    def __init__(self, x, y, file_name=None, collision=False, collision_do_kill=False,
                 ignore_player=False, ignore_enemy=True, is_tile=False, size=(48, 48)):
        super().__init__(game_objects, all_sprite)
        self.collision = collision
        self.collision_do_kill = False
        self.ignore_player = ignore_player
        self.ignore_enemy = ignore_enemy
        self.is_tile = is_tile
        if not is_tile:
            if file_name not in self.images:
                image = load_image(os.path.join(ELEMENT_TEXTURE_FOLDER, file_name))
                if file_name == 'blade.png':
                    image = pygame.transform.scale(image, size)
                else:
                    image = pygame.transform.scale(image, size)
                self.images[file_name] = image
            self.image = self.images[file_name].copy()
            self.rect = self.image.get_rect(x=tile_size[0] * x, y=tile_size[1] * y)
            if collision:
                self.mask = pygame.mask.Mask(self.rect.size, 1)
                self.collision_do_kill = collision_do_kill
            else:
                self.mask = pygame.mask.Mask(self.rect.size, 0)


class Tile(GameObject):
    images = dict()

    def __init__(self, tile_name, x, y):
        super().__init__(x, y, is_tile=True, ignore_enemy=False, collision=True)
        self.add(tiles_group)
        if tile_name not in self.images:
            image = load_image(
                os.path.join(TILES_TEXTURE_FOLDER, tile_name + '.png'))
            if tile_name == 'k':
                image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE // 2))
            else:
                image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
            self.images[tile_name] = image
        self.image = self.images[tile_name]
        self.rect = self.image.get_rect(x=tile_size[0] * x, y=tile_size[1] * y)
        self.mask = pygame.mask.from_surface(self.image)


class Heart(GameObject):
    def __init__(self, x, y, file_name='heart.png', collision=True, collision_do_kill=False,
                 ignore_player=False, ignore_enemy=True, size=(32, 32)):
        super().__init__(x, y, file_name=file_name, collision=collision,
                         collision_do_kill=collision_do_kill, ignore_player=ignore_player,
                         ignore_enemy=ignore_enemy, size=size)


class Key(GameObject):
    def __init__(self, x, y, file_name='key.png', collision=True, collision_do_kill=False,
                 ignore_player=False, ignore_enemy=True, size=(32, 32)):
        super().__init__(x, y, file_name=file_name, collision=collision,
                         collision_do_kill=collision_do_kill, ignore_player=ignore_player,
                         ignore_enemy=ignore_enemy, size=size)


class Door(GameObject):
    def __init__(self, x, y, file_name='door.png', collision=True, collision_do_kill=False,
                 ignore_player=False, ignore_enemy=True, size=(48, 48)):
        super().__init__(x, y, file_name=file_name, collision=collision,
                         collision_do_kill=collision_do_kill, ignore_player=ignore_player,
                         ignore_enemy=ignore_enemy, size=size)


class Coin(GameObject):
    def __init__(self, x, y, file_name='coin.png', collision=True, collision_do_kill=False,
                 ignore_player=False, ignore_enemy=True, size=(32, 32)):
        super().__init__(x, y, file_name=file_name, collision=collision,
                         collision_do_kill=collision_do_kill, ignore_player=ignore_player,
                         ignore_enemy=ignore_enemy, size=size)


class Crystal(GameObject):
    def __init__(self, x, y, file_name='crystal.png', collision=True, collision_do_kill=False,
                 ignore_player=False, ignore_enemy=True, size=(32, 32)):
        super().__init__(x, y, file_name=file_name, collision=collision,
                         collision_do_kill=collision_do_kill, ignore_player=ignore_player,
                         ignore_enemy=ignore_enemy, size=size)


class CheckPoint(GameObject):
    def __init__(self, x, y, file_name='pointer.png', collision=True, collision_do_kill=False,
                 ignore_player=False, ignore_enemy=True, size=(48, 48)):
        super().__init__(x, y, file_name=file_name, collision=collision,
                         collision_do_kill=collision_do_kill, ignore_player=ignore_player,
                         ignore_enemy=ignore_enemy, size=size)


class ButtonJump(GameObject):
    def __init__(self, x, y, file_name='button.png', collision=True, collision_do_kill=False,
                 ignore_player=False, ignore_enemy=True, size=(48, 12)):
        super().__init__(x, y, file_name=file_name, collision=collision,
                         collision_do_kill=collision_do_kill, ignore_player=ignore_player,
                         ignore_enemy=ignore_enemy, size=size)
        self.rect.y += (TILE_SIZE - size[1])


class GamePanel:
    menu_image = load_image(os.path.join(ICONS_FOLDER, 'menu.png'))
    restart_level_image = load_image(os.path.join(ICONS_FOLDER, 'restart_level.png'))
    play_image = load_image(os.path.join(ICONS_FOLDER, 'pause_play.png'))
    music_on_image = load_image(os.path.join(ICONS_FOLDER, 'pause_music_on.png'))
    music_off_image = load_image(os.path.join(ICONS_FOLDER, 'pause_music_off.png'))
    lose_image = load_image(os.path.join(TEXT_FOLDER, 'lose.png'))

    font = pygame.font.Font(None, 150)

    def __init__(self):
        self.surface = pygame.Surface((WIDTH // 3, HEIGHT))
        self.rect = self.surface.get_rect(x=WIDTH // 2 - self.surface.get_width() // 2,
                                          y=HEIGHT // 2 - self.surface.get_height() // 2)
        self.surface.fill(pygame.color.Color(190, 201, 225))
        self.surface.set_alpha(30)

    def init_buttons(self):
        self.menu_btn = pygame.sprite.Sprite(game_panel_group)
        self.menu_btn.image = self.menu_image
        self.menu_btn.rect = self.menu_btn.image.get_rect(
            x=self.surface.get_width() // 2 - self.menu_btn.image.get_width() // 2 - 80,
            y=self.surface.get_height() // 2 - self.menu_btn.image.get_height() // 2 + 150
        )

        self.restart_level_btn = pygame.sprite.Sprite(game_panel_group)
        self.restart_level_btn.image = self.restart_level_image
        self.restart_level_btn.rect = self.restart_level_btn.image.get_rect(
            x=self.surface.get_width() // 2 - self.restart_level_btn.image.get_width() // 2 + 80,
            y=self.surface.get_height() // 2 - self.restart_level_btn.image.get_height() // 2 + 150
        )

    def show(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == pygame.BUTTON_LEFT:
                        pos = event.pos
                        pos = (pos[0] - self.rect.x, pos[1] - self.rect.y)
                        if self.menu_btn.rect.collidepoint(pos):
                            return MAIN_MENU
                        elif self.restart_level_btn.rect.collidepoint(pos):
                            return RESTART_LEVEL
            game_panel_group.draw(self.surface)
            screen.blit(self.surface, self.rect.topleft)
            pygame.display.flip()


class Pause(GamePanel):
    def __init__(self):
        super().__init__()
        self.init_buttons()

    def init_buttons(self):
        self.play_btn = pygame.sprite.Sprite(pause_group)
        self.play_btn.image = self.play_image
        self.play_btn.rect = self.play_btn.image.get_rect(
            x=self.surface.get_width() // 2 - self.play_btn.image.get_width() // 2,
            y=self.surface.get_height() // 2 - self.play_btn.image.get_height() // 2 - 80 + 30
        )

        self.menu_btn = pygame.sprite.Sprite(pause_group)
        self.menu_btn.image = self.menu_image
        self.menu_btn.rect = self.menu_btn.image.get_rect(
            x=self.surface.get_width() // 2 - self.play_btn.image.get_width() // 2 - 90,
            y=self.surface.get_height() // 2 - self.play_btn.image.get_height() // 2 + 50
        )

        self.music_btn = pygame.sprite.Sprite(pause_group)
        self.music_btn.image = self.music_on_image if MUSIC_ON else self.music_off_image
        self.music_btn.rect = self.music_btn.image.get_rect(
            x=self.surface.get_width() // 2 - self.play_btn.image.get_width() // 2 + 90,
            y=self.surface.get_height() // 2 - self.play_btn.image.get_height() // 2 + 50
        )

        self.restart_level_btn = pygame.sprite.Sprite(pause_group)
        self.restart_level_btn.image = self.restart_level_image
        self.restart_level_btn.rect = self.restart_level_btn.image.get_rect(
            x=self.surface.get_width() // 2 - self.play_btn.image.get_width() // 2,
            y=self.surface.get_height() // 2 - self.play_btn.image.get_height() // 2 + 80 + 70
        )

    def show(self):
        global MUSIC_ON
        self.music_btn.image = self.music_on_image if MUSIC_ON else self.music_off_image
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == pygame.BUTTON_LEFT:
                        pos = event.pos
                        pos = (pos[0] - self.rect.x, pos[1] - self.rect.y)
                        if self.play_btn.rect.collidepoint(pos):
                            return None
                        elif self.menu_btn.rect.collidepoint(pos):
                            return MAIN_MENU
                        elif self.music_btn.rect.collidepoint(pos):
                            if MUSIC_ON:
                                self.music_btn.image = self.music_off_image
                                MUSIC_ON = False
                                background_chanel.stop()
                            else:
                                self.music_btn.image = self.music_on_image
                                MUSIC_ON = True
                                background_chanel.play(background_game_play_music, loops=-1)
                        elif self.restart_level_btn.rect.collidepoint(pos):
                            return RESTART_LEVEL
            pause_group.draw(self.surface)
            screen.blit(self.surface, self.rect.topleft)
            pygame.display.flip()


class Finish(GamePanel):
    def __init__(self):
        super().__init__()
        self.init_buttons()

    def set_progress(self, progress):
        self.surface.fill(pygame.color.Color('gray'))
        progress_surface = self.font.render(str(progress) + '%', True,
                                            pygame.color.Color("red"))
        progress_surface.set_colorkey(progress_surface.get_at((0, 0)))
        self.surface.blit(
            progress_surface,
            (self.surface.get_width() // 2 - progress_surface.get_width() // 2, 80)
        )


class Lose(GamePanel):
    def __init__(self):
        super().__init__()
        self.surface.blit(
            self.lose_image,
            (self.surface.get_width() // 2 - self.lose_image.get_width() // 2, 25)
        )
        self.init_buttons()


def terminate():
    """Function terminate this game"""
    pygame.quit()
    sys.exit(0)


def start_game():
    global MUSIC_ON
    if MUSIC_ON:
        background_chanel.play(background_menu_music, loops=-1)
    start_btn = pygame.sprite.Sprite(menu_group)
    start_btn.image = play_icon
    start_btn.rect = start_btn.image.get_rect(x=WIDTH // 2 - start_btn.image.get_width() // 2 + 100,
                                              y=HEIGHT // 2 + 30)
    music_btn = pygame.sprite.Sprite(menu_group)
    music_btn.image = music_on_icon if MUSIC_ON else music_off_icon
    music_btn.rect = music_btn.image.get_rect(x=WIDTH // 2 - start_btn.image.get_width() // 2 - 100,
                                              y=HEIGHT // 2 + 30)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if event.button == pygame.BUTTON_LEFT:
                    if start_btn.rect.collidepoint(pos):
                        number_level = select_level()
                        if number_level:
                            player, coins, crystals = generate_level(number_level)
                            if MUSIC_ON:
                                background_chanel.play(background_game_play_music, loops=-1)
                            return player, coins, crystals, number_level
                    elif music_btn.rect.collidepoint(pos):
                        if MUSIC_ON:
                            MUSIC_ON = False
                            music_btn.image = music_off_icon
                            background_chanel.stop()
                        else:
                            MUSIC_ON = True
                            music_btn.image = music_on_icon
                            background_chanel.play(background_menu_music, loops=-1)
        screen.blit(background_image, (0, 0))
        screen.blit(name_game_image, (0, 0))
        menu_group.draw(screen)
        pygame.display.flip()


def select_level():
    levels_group.empty()
    screen.blit(background_image, (0, 0))
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    size_sprite_level = SelectLevelSprite.size_sprite_level
    indent_level_px = 50
    SelectLevelSprite(center_x - size_sprite_level[0] * 2 - indent_level_px * 2, center_y, 1)
    SelectLevelSprite(center_x - size_sprite_level[0] - indent_level_px, center_y, 2)
    SelectLevelSprite(center_x, center_y, 3)
    SelectLevelSprite(center_x + size_sprite_level[0] + indent_level_px, center_y, 4)
    SelectLevelSprite(center_x + size_sprite_level[0] * 2 + indent_level_px * 2, center_y, 5)

    back_to_menu_btn = pygame.sprite.Sprite(levels_group)
    back_to_menu_btn.image = back_icon
    back_to_menu_btn.rect = back_to_menu_btn.image.get_rect(x=30, y=30)

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
                        if level_sprite.image == back_icon:
                            return None
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
    all_sprite.empty()
    levels_group.empty()
    menu_group.empty()
    tiles_group.empty()
    game_objects.empty()
    enemy_group.empty()
    hearts_group.empty()
    key_group.empty()
    player_group.empty()
    level_path = os.path.join(LEVELS_FOLDER, str(number_level) + '.lvl')
    level_map = load_level(level_path)
    count_tiles = len(level_map * len(level_map[0]))
    percent_one_tile = count_tiles // 100
    if not percent_one_tile:
        percent_one_tile = 1
    current_tile = 0
    coins = 0
    crystals = 0
    for y in range(len(level_map)):
        for x in range(len(level_map[0])):
            if level_map[y][x] == '@':
                if not player_group.sprite:
                    player = Player(x, y)
                else:
                    print('Fatal Error: The player has already been created before')
                    terminate()
            elif level_map[y][x] == '>':
                Enemy(x, y, ROTATION_RIGHT)
            elif level_map[y][x] == '<':
                Enemy(x, y, ROTATION_LEFT)
            elif level_map[y][x] in GAME_OBJECTS_DICT:
                collided = False
                collided_do_kill = False
                ignore_player = False
                ignore_enemy = True
                file_name, args = GAME_OBJECTS_DICT[level_map[y][x]]
                size = tile_size
                if 'collided' in args:
                    collided = args['collided']
                if 'collided_do_kill' in args:
                    collided_do_kill = args['collided_do_kill']
                if 'ignore_player' in args:
                    ignore_player = args['ignore_player']
                if 'ignore_enemy' in args:
                    ignore_enemy = args['ignore_enemy']
                if 'size' in args:
                    size = args['size']
                if file_name == 'heart.png':
                    Heart(x, y,
                          file_name=file_name,
                          collision=collided,
                          collision_do_kill=collided_do_kill,
                          ignore_player=ignore_player,
                          ignore_enemy=ignore_enemy, size=size)
                elif file_name == 'pointer.png':
                    CheckPoint(x, y,
                               file_name=file_name,
                               collision=collided,
                               collision_do_kill=collided_do_kill,
                               ignore_player=ignore_player,
                               ignore_enemy=ignore_enemy, size=size)
                elif file_name == 'button.png':
                    ButtonJump(x, y,
                               file_name=file_name,
                               collision=collided,
                               collision_do_kill=collided_do_kill,
                               ignore_player=ignore_player,
                               ignore_enemy=ignore_enemy, size=size)
                elif file_name == 'key.png':
                    Key(x, y,
                        file_name=file_name,
                        collision=collided,
                        collision_do_kill=collided_do_kill,
                        ignore_player=ignore_player,
                        ignore_enemy=ignore_enemy, size=size)
                elif file_name == 'door.png':
                    Door(x, y,
                         file_name=file_name,
                         collision=collided,
                         collision_do_kill=collided_do_kill,
                         ignore_player=ignore_player,
                         ignore_enemy=ignore_enemy, size=size)
                elif file_name == 'coin.png':
                    Coin(x, y,
                         file_name=file_name,
                         collision=collided,
                         collision_do_kill=collided_do_kill,
                         ignore_player=ignore_player,
                         ignore_enemy=ignore_enemy, size=size)
                    coins += 1
                elif file_name == 'crystal.png':
                    Crystal(x, y,
                            file_name=file_name,
                            collision=collided,
                            collision_do_kill=collided_do_kill,
                            ignore_player=ignore_player,
                            ignore_enemy=ignore_enemy, size=size)
                    crystals += 1
                else:
                    GameObject(x, y,
                               file_name=file_name,
                               collision=collided,
                               collision_do_kill=collided_do_kill,
                               ignore_player=ignore_player,
                               ignore_enemy=ignore_enemy, size=size)
            elif level_map[y][x] != '#' and level_map[y][x] != ' ':
                Tile(level_map[y][x], x, y)
            current_tile += 1
            show_loading_level(current_tile // percent_one_tile)
    if not player_group.sprite:
        print('На уровне отсутсвует игрок')
        terminate()
    camera.update(player)
    for sprite in all_sprite.sprites():
        camera.apply(sprite)
    camera.set_memory(0, 0)
    return player, coins, crystals


all_sprite = pygame.sprite.Group()
levels_group = pygame.sprite.Group()
menu_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
game_objects = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
hearts_group = pygame.sprite.Group()
key_group = pygame.sprite.Group()
game_panel_group = pygame.sprite.Group()
pause_group = pygame.sprite.Group()
player_group = pygame.sprite.GroupSingle()

background_image = load_image(os.path.join(ELEMENT_TEXTURE_FOLDER, 'background.png'))
background_image = pygame.transform.scale(background_image, SIZE)
play_icon = load_image(os.path.join(ICONS_FOLDER, 'play.png'))
music_on_icon = load_image(os.path.join(ICONS_FOLDER, 'music_on.png'))
music_off_icon = load_image(os.path.join(ICONS_FOLDER, 'music_off.png'))
back_icon = load_image(os.path.join(ICONS_FOLDER, 'back.png'))
name_game_image = load_image(os.path.join(TEXT_FOLDER, 'name-game.png'))

background_chanel = pygame.mixer.Channel(0)
background_menu_music = pygame.mixer.Sound(file=os.path.join(MUSIC_FOLDER, 'menu_background.wav'))
background_game_play_music = pygame.mixer.Sound(file=os.path.join(MUSIC_FOLDER, 'background.wav'))

pause = Pause()
finish = Finish()
lose = Lose()

tile_size = (TILE_SIZE, TILE_SIZE)

load_level_font = pygame.font.Font(None, 150)

clock = pygame.time.Clock()
camera = Camera()

frames = 0

player, coins, crystals, number_level = start_game()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                result = pause.show()
                if result == MAIN_MENU:
                    player, coins, crystals, number_level = start_game()
                    break
                elif result == RESTART_LEVEL:
                    player, coins, crystals = generate_level(number_level)
                    break
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                player.attack()
    screen.blit(background_image, (0, 0))
    if frames % 2 == 0:
        left, right, up, boost = False, False, False, False
        keys_status = pygame.key.get_pressed()
        if keys_status[pygame.K_d]:
            right = True
        if keys_status[pygame.K_a]:
            left = True
        if keys_status[pygame.K_SPACE]:
            up = True
        if pygame.key.get_mods() & pygame.KMOD_LSHIFT:
            boost = True
        player.update(left, right, up, boost)
        for enemy in enemy_group.sprites():
            enemy.update()
        camera.update(player)
        for sprite in all_sprite.sprites():
            camera.apply(sprite)
    tiles_group.draw(screen)
    game_objects.draw(screen)
    enemy_group.draw(screen)
    player_group.draw(screen)
    hearts_group.draw(screen)
    key_group.draw(screen)
    pygame.display.flip()
    if player.finish:
        player_crystal_coins = player.crystals + player.coins
        level_coins_crystals = coins + crystals
        if not player_crystal_coins:
            player_crystal_coins = 1
        if not level_coins_crystals:
            level_coins_crystals = 1
        progress = int(player_crystal_coins / level_coins_crystals * 100)
        finish.set_progress(progress)
        result = finish.show()
        if result == MAIN_MENU:
            player, coins, crystals, number_level = start_game()
        elif result == RESTART_LEVEL:
            player, coins, crystals = generate_level(number_level)
    if player.lose and not player.death_mode:
        result = lose.show()
        if result == MAIN_MENU:
            player, coins, crystals, number_level = start_game()
        elif result == RESTART_LEVEL:
            player, coins, crystals = generate_level(number_level)
    clock.tick(FPS)
    frames += 1
