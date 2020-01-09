import os
import sys
import pygame
from random import choice

# Initialization PyGame
pygame.init()
# Screen Size
WIDTH, HEIGHT = SIZE_SCREEN = 1000, 500
# Main Display
screen = pygame.display.set_mode(SIZE_SCREEN)
screen_rect = screen.get_rect()

TILE_SIZE = 48

ROTATION_LEFT = 1
ROTATION_RIGHT = 2

MAIN_MENU = 1
RESTART_LEVEL = 2

COLLIDED = 1
COLLIDED_DO_KILL = 2
COLLIDED_PLAYER = 3
COLLIDED_ENEMY = 4
SIZE = 5

MOVE_SPEED = 7
SPEED_UP_BOOST = 1.75
JUMP_BOOST = 1.35
ENEMY_MOVE_SPEED = 1
JUMP_POWER = 15
GRAVITY = 1

FPS = 100

BACKGROUND_SOUND_VOLUME = 0.5

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
          {COLLIDED: True, COLLIDED_DO_KILL: True, COLLIDED_PLAYER: True,
           COLLIDED_ENEMY: False, SIZE: (48, 96)}),
    '$': ('bush1.png',
          {COLLIDED: False, COLLIDED_DO_KILL: False, COLLIDED_PLAYER: False,
           COLLIDED_ENEMY: False, SIZE: (48, 48)}),
    '%': ('bush2.png',
          {COLLIDED: False, COLLIDED_DO_KILL: False, COLLIDED_PLAYER: False,
           COLLIDED_ENEMY: False, SIZE: (48, 48)}),
    '^': ('button.png',
          {COLLIDED: True, COLLIDED_DO_KILL: False, COLLIDED_PLAYER: True,
           COLLIDED_ENEMY: False, SIZE: (48, 12)}),
    ':': ('cell.png',
          {COLLIDED: False, COLLIDED_DO_KILL: False, COLLIDED_PLAYER: False,
           COLLIDED_ENEMY: False, SIZE: (48, 48)}),
    '&': ('door.png',
          {COLLIDED: True, COLLIDED_DO_KILL: False, COLLIDED_PLAYER: False,
           COLLIDED_ENEMY: False, SIZE: (48, 48)}),
    '+': ('coin.png',
          {COLLIDED: True, COLLIDED_DO_KILL: False, COLLIDED_PLAYER: False,
           COLLIDED_ENEMY: False, SIZE: (32, 32)}),
    '|': ('crystal.png',
          {COLLIDED: True, COLLIDED_DO_KILL: False, COLLIDED_PLAYER: False,
           COLLIDED_ENEMY: False, SIZE: (32, 32)}),
    '1': ('flower1.png',
          {COLLIDED: False, COLLIDED_DO_KILL: False, COLLIDED_PLAYER: False,
           COLLIDED_ENEMY: False, SIZE: (48, 48)}),
    '2': ('flower2.png',
          {COLLIDED: False, COLLIDED_DO_KILL: False, COLLIDED_PLAYER: False,
           COLLIDED_ENEMY: False, SIZE: (48, 48)}),
    '3': ('flower3.png',
          {COLLIDED: False, COLLIDED_DO_KILL: False, COLLIDED_PLAYER: False,
           COLLIDED_ENEMY: False, SIZE: (48, 48)}),
    '4': ('flower4.png',
          {COLLIDED: False, COLLIDED_DO_KILL: False, COLLIDED_PLAYER: False,
           COLLIDED_ENEMY: False, SIZE: (48, 48)}),
    '5': ('flower5.png',
          {COLLIDED: False, COLLIDED_DO_KILL: False, COLLIDED_PLAYER: False,
           COLLIDED_ENEMY: False, SIZE: (48, 48)}),
    '6': ('heart.png',
          {COLLIDED: True, COLLIDED_DO_KILL: False, COLLIDED_PLAYER: False,
           COLLIDED_ENEMY: False, SIZE: (32, 32)}),
    '7': ('key.png',
          {COLLIDED: True, COLLIDED_DO_KILL: False, COLLIDED_PLAYER: False,
           COLLIDED_ENEMY: False, SIZE: (32, 32)}),
    '8': ('box1.png',
          {COLLIDED: True, COLLIDED_DO_KILL: False, COLLIDED_PLAYER: True,
           COLLIDED_ENEMY: True, SIZE: (48, 48)}),
    '9': ('tree1.png',
          {COLLIDED: False, COLLIDED_DO_KILL: False, COLLIDED_PLAYER: False,
           COLLIDED_ENEMY: False, SIZE: (48, 48)}),
    '0': ('tree2.png',
          {COLLIDED: False, COLLIDED_DO_KILL: False, COLLIDED_PLAYER: False,
           COLLIDED_ENEMY: False, SIZE: (48, 48)}),
    '*': ('pointer.png',
          {COLLIDED: True, COLLIDED_DO_KILL: False, COLLIDED_PLAYER: False,
           COLLIDED_ENEMY: False, SIZE: (48, 48)}),
    '/': ('zero_enemy.png',
          {COLLIDED: True, COLLIDED_DO_KILL: False, COLLIDED_PLAYER: False,
           COLLIDED_ENEMY: True, SIZE: (48, 48)}),
    '\\': ('zero_player.png',
           {COLLIDED: True, COLLIDED_DO_KILL: False, COLLIDED_PLAYER: True,
            COLLIDED_ENEMY: False, SIZE: (48, 48)}),
    '\'': ('thorns1.png',
           {COLLIDED: True, COLLIDED_DO_KILL: True, COLLIDED_PLAYER: True,
            COLLIDED_ENEMY: True, SIZE: (48, 48)}),
    '"': ('thorns2.png',
          {COLLIDED: True, COLLIDED_DO_KILL: True, COLLIDED_PLAYER: True,
           COLLIDED_ENEMY: True, SIZE: (48, 96)}),
    ',': ('stairs.png',
          {COLLIDED: True, COLLIDED_DO_KILL: False, COLLIDED_PLAYER: False,
           COLLIDED_ENEMY: False, SIZE: (48, 48)}),
    '-': ('scarecrow.png',
          {COLLIDED: False, COLLIDED_DO_KILL: False, COLLIDED_PLAYER: False,
           COLLIDED_ENEMY: False, SIZE: (48, 48)}),
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


def terminate():
    """Function terminate this game"""
    pygame.quit()
    sys.exit(0)


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

    def get_number_level(self):
        return self.number_level


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
        self.on_stairs = False
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
                if game_object.collision and game_object.collision_do_kill:
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
                if isinstance(game_object, Key):
                    game_object.kill()
                    self.key = True
                    self.visible_key()
                if isinstance(game_object, Door):
                    if self.key:
                        self.finish = True
                if isinstance(game_object, Coin):
                    self.coins += 1
                    game_object.kill()
                if isinstance(game_object, Crystal):
                    self.crystals += 1
                    game_object.kill()
                if isinstance(game_object, ButtonJump):
                    if yvel:
                        self.yvel = -JUMP_POWER * JUMP_BOOST
                    return
                if isinstance(game_object, Stairs):
                    keys_status = pygame.key.get_pressed()
                    if keys_status[pygame.K_w]:
                        self.yvel = -MOVE_SPEED
                    elif keys_status[pygame.K_s]:
                        self.yvel = MOVE_SPEED
                    else:
                        self.yvel = 0
                    if pygame.key.get_mods() & pygame.KMOD_LSHIFT:
                        self.yvel *= SPEED_UP_BOOST
                    self.on_stairs = True
                if not game_object.collision_player:
                    continue
            else:
                if not game_object.collision_enemy:
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
                            self.respawn()

                elif self.attack_group:
                    self.image = self.frames[self.attack_group[ROTATION_RIGHT]][
                        self.cut_frame_update]
                    if self.cut_frame_update == len(
                            self.frames[self.attack_group[ROTATION_RIGHT]]) - 1:
                        self.attack_group = None
                        self.cut_frame_update = 0

                elif self.xvel == 0 and self.yvel == 0 and (self.on_ground or self.on_stairs):
                    self.image = self.frames['idle_right'][
                        self.cut_frame_update % len(self.frames['idle_right'])]

                elif self.yvel != 0 and not self.on_ground:
                    if self.on_ground and self.yvel < 0:
                        self.cut_frame_update = 0
                    self.image = self.frames['jump_right'][
                        self.cut_frame_update % len(self.frames['jump_right'])]

                elif self.xvel != 0 or (self.on_stairs and self.yvel):
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
                            self.respawn()

                elif self.attack_group:
                    self.image = self.frames[self.attack_group[ROTATION_LEFT]][
                        self.cut_frame_update]
                    if self.cut_frame_update == len(
                            self.frames[self.attack_group[ROTATION_LEFT]]) - 1:
                        self.attack_group = None
                        self.cut_frame_update = 0

                elif self.xvel == 0 and self.yvel == 0 and (self.on_ground or self.on_stairs):
                    self.image = self.frames['idle_left'][
                        self.cut_frame_update % len(self.frames['idle_left'])]

                elif self.yvel != 0 and not self.on_ground:
                    if self.on_ground and self.yvel > 0:
                        self.cut_frame_update = 0
                    self.image = self.frames['jump_left'][
                        self.cut_frame_update % len(self.frames['jump_left'])]

                elif self.xvel != 0 or (self.on_stairs and self.yvel):
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

    def update(self):
        keys_status = pygame.key.get_pressed()
        if keys_status[pygame.K_a]:
            self.xvel = -MOVE_SPEED
        if keys_status[pygame.K_d]:
            self.xvel = MOVE_SPEED
        if (not (keys_status[pygame.K_a] or keys_status[pygame.K_d]) or
                self.damage_mode or self.death_mode):
            self.xvel = 0
        if pygame.key.get_mods() & pygame.KMOD_LSHIFT:
            self.xvel *= SPEED_UP_BOOST
        if keys_status[pygame.K_SPACE]:
            if self.on_ground:
                self.yvel = -JUMP_POWER
        if not self.on_ground and not self.on_stairs:
            self.yvel += GRAVITY
        self.on_ground = False
        self.on_stairs = False
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

    def respawn(self):
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

    def get_coins(self):
        if self.coins:
            return self.coins
        return 1

    def get_crystals(self):
        if self.crystals:
            return self.crystals
        return 1

    def get_bonus(self):
        if self.coins + self.crystals:
            return self.coins + self.crystals
        return 1


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
            if self.damage_mode or self.death_mode:
                self.xvel = 0
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

    def __init__(self, x, y, file_name, configuration=None, is_tile=False):
        super().__init__(game_objects, all_sprite)
        self.collision = False
        self.collision_do_kill = False
        self.collision_player = False
        self.collision_enemy = False
        self.size = (48, 48)
        if configuration:
            if COLLIDED in configuration:
                self.collision = configuration[COLLIDED]
            if COLLIDED_DO_KILL in configuration:
                self.collision_do_kill = configuration[COLLIDED_DO_KILL]
            if COLLIDED_PLAYER in configuration:
                self.collision_player = configuration[COLLIDED_PLAYER]
            if COLLIDED_ENEMY in configuration:
                self.collision_enemy = configuration[COLLIDED_ENEMY]
            if SIZE in configuration:
                self.size = configuration[SIZE]
        if is_tile:
            if file_name not in self.images:
                image = load_image(
                    os.path.join(TILES_TEXTURE_FOLDER, file_name + '.png'))
                self.images[file_name] = image
            self.image = self.images[file_name]
            self.collision = True
            self.collision_player = True
            self.collision_enemy = True
            self.add(tiles_group)
        else:
            if file_name not in self.images:
                image = load_image(os.path.join(ELEMENT_TEXTURE_FOLDER, file_name))
                image = pygame.transform.scale(image, self.size)
                self.images[file_name] = image
            self.image = self.images[file_name].copy()
        self.rect = self.image.get_rect(x=TILE_SIZE * x, y=TILE_SIZE * y)
        if self.collision:
            self.mask = pygame.mask.Mask(self.rect.size, 1)
        else:
            self.mask = pygame.mask.Mask(self.rect.size, 0)


class Tile(GameObject):
    def __init__(self, x, y, tile_name):
        super().__init__(x, y, tile_name, is_tile=True)


class Heart(GameObject):
    def __init__(self, x, y, file_name='heart.png', configuration=None):
        super().__init__(x, y, file_name, configuration)


class Key(GameObject):
    def __init__(self, x, y, file_name='key.png', configuration=None):
        super().__init__(x, y, file_name, configuration)


class Door(GameObject):
    def __init__(self, x, y, file_name='door.png', configuration=None):
        super().__init__(x, y, file_name, configuration)


class Coin(GameObject):
    def __init__(self, x, y, file_name='coin.png', configuration=None):
        super().__init__(x, y, file_name, configuration)


class Crystal(GameObject):
    def __init__(self, x, y, file_name='crystal.png', configuration=None):
        super().__init__(x, y, file_name, configuration)


class CheckPoint(GameObject):
    def __init__(self, x, y, file_name='pointer.png', configuration=None):
        super().__init__(x, y, file_name, configuration)


class ButtonJump(GameObject):
    def __init__(self, x, y, file_name='button.png', configuration=None):
        super().__init__(x, y, file_name, configuration)
        self.rect.y += TILE_SIZE - self.size[1]


class Stairs(GameObject):
    def __init__(self, x, y, file_name='stairs.png', configuration=None):
        super().__init__(x, y, file_name, configuration)


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
        self.music_btn.image = self.music_on_image if music_on else self.music_off_image
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
        global music_on
        self.music_btn.image = self.music_on_image if music_on else self.music_off_image
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
                            if music_on:
                                self.music_btn.image = self.music_off_image
                                music_on = False
                                background_chanel.stop()
                            else:
                                self.music_btn.image = self.music_on_image
                                music_on = True
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
        progress_surface = self.font.render(str(int(progress)) + '%', True,
                                            pygame.color.Color("red"))
        progress_surface.set_colorkey(progress_surface.get_at((0, 0)))
        self.surface.blit(
            progress_surface,
            (self.surface.get_width() // 2 - progress_surface.get_width() // 2, 80)
        )


class Lose(GamePanel):
    def __init__(self):
        super().__init__()
        self.surface.blit(self.lose_image,
                          (self.surface.get_width() // 2 - self.lose_image.get_width() // 2, 25))
        self.init_buttons()


class Level:
    load_level_font = pygame.font.Font(None, 150)

    def __init__(self, number_level):
        level_path = os.path.join(LEVELS_FOLDER, str(number_level) + '.lvl')
        with open(level_path, mode='r', encoding='utf8') as map_file:
            self.level_map = [line.rstrip() for line in map_file]
            max_width = max(map(len, self.level_map))
            self.level_map = list(map(lambda row: row.ljust(max_width, '#'), self.level_map))

    def generate(self):
        self.coins = 0
        self.crystals = 0
        all_sprite.empty()
        levels_group.empty()
        tiles_group.empty()
        game_objects.empty()
        enemy_group.empty()
        hearts_group.empty()
        key_group.empty()
        player_group.empty()
        count_tiles = len(self.level_map * len(self.level_map[0]))
        percent_one_tile = count_tiles // 100
        if not percent_one_tile:
            percent_one_tile = 1
        current_tile = 0
        for y in range(len(self.level_map)):
            for x in range(len(self.level_map[0])):
                if self.level_map[y][x] == '@':
                    if not player_group.sprite:
                        player = Player(x, y)
                    else:
                        print('На карте уже присутствует игрок')
                        terminate()
                elif self.level_map[y][x] == '>':
                    Enemy(x, y, ROTATION_RIGHT)
                elif self.level_map[y][x] == '<':
                    Enemy(x, y, ROTATION_LEFT)
                elif self.level_map[y][x] in GAME_OBJECTS_DICT:
                    file_name, configuration = GAME_OBJECTS_DICT[self.level_map[y][x]]
                    if file_name == 'heart.png':
                        Heart(x, y, configuration=configuration)
                    elif file_name == 'pointer.png':
                        CheckPoint(x, y, configuration=configuration)
                    elif file_name == 'button.png':
                        ButtonJump(x, y, configuration=configuration)
                    elif file_name == 'key.png':
                        Key(x, y, configuration=configuration)
                    elif file_name == 'door.png':
                        Door(x, y, configuration=configuration)
                    elif file_name == 'stairs.png':
                        Stairs(x, y, configuration=configuration)
                    elif file_name == 'coin.png':
                        Coin(x, y, configuration=configuration)
                        self.coins += 1
                    elif file_name == 'crystal.png':
                        Crystal(x, y, configuration=configuration)
                        self.crystals += 1
                    else:
                        GameObject(x, y, file_name, configuration=configuration)
                elif self.level_map[y][x] != '#' and self.level_map[y][x] != ' ':
                    Tile(x, y, self.level_map[y][x])
                current_tile += 1
                self.show_loading_level(current_tile // percent_one_tile)
        if not player_group.sprite:
            print('На уровне отсутсвует игрок')
            terminate()
        camera.update(player)
        for sprite in all_sprite.sprites():
            camera.apply(sprite)
        camera.set_memory(0, 0)
        return player

    def show_loading_level(self, percent):
        if percent > 100:
            percent = 100
        screen.blit(background_image, (0, 0))
        percent_label = self.load_level_font.render(str(percent) + ' %', 1,
                                                    pygame.color.Color(0, 225, 45))
        screen.blit(percent_label,
                    (WIDTH // 2 - percent_label.get_width() // 2,
                     HEIGHT // 2 - percent_label.get_height() // 2))
        pygame.display.flip()

    def get_coins(self):
        if self.coins:
            return self.coins
        return 1

    def get_crystals(self):
        if self.crystals:
            return self.crystals
        return 1

    def get_bonus(self):
        if self.coins + self.crystals:
            return self.coins + self.crystals
        return 1

    def get_progress(self):
        return player.get_bonus() / self.get_bonus() * 100


class Menu:
    play_icon = load_image(os.path.join(ICONS_FOLDER, 'play.png'))
    music_on_icon = load_image(os.path.join(ICONS_FOLDER, 'music_on.png'))
    music_off_icon = load_image(os.path.join(ICONS_FOLDER, 'music_off.png'))
    back_icon = load_image(os.path.join(ICONS_FOLDER, 'back.png'))
    name_game_image = load_image(os.path.join(TEXT_FOLDER, 'name-game.png'))

    def __init__(self):
        if music_on:
            background_chanel.play(background_menu_music, loops=-1)
        self.start_btn = pygame.sprite.Sprite(menu_group)
        self.start_btn.image = self.play_icon
        self.start_btn.rect = self.start_btn.image.get_rect(
            x=WIDTH // 2 - self.start_btn.image.get_width() // 2 + 100, y=HEIGHT // 2 + 30)
        self.music_btn = pygame.sprite.Sprite(menu_group)
        self.music_btn.image = self.music_on_icon if music_on else self.music_off_icon
        self.music_btn.rect = self.music_btn.image.get_rect(
            x=WIDTH // 2 - self.start_btn.image.get_width() // 2 - 100, y=HEIGHT // 2 + 30)

    def show(self):
        global music_on
        if music_on:
            self.music_btn.image = self.music_on_icon
            background_chanel.play(background_menu_music, loops=-1)
        else:
            self.music_btn.image = self.music_off_icon
            background_chanel.stop()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if event.button == pygame.BUTTON_LEFT:
                        if self.start_btn.rect.collidepoint(pos):
                            number_level = self.select_level()
                            if number_level:
                                level = Level(number_level)
                                player = level.generate()
                                if music_on:
                                    background_chanel.play(background_game_play_music, loops=-1)
                                return player, level
                        elif self.music_btn.rect.collidepoint(pos):
                            if music_on:
                                music_on = False
                                self.music_btn.image = self.music_off_icon
                                background_chanel.stop()
                            else:
                                music_on = True
                                self.music_btn.image = self.music_on_icon
                                background_chanel.play(background_menu_music, loops=-1)
            screen.blit(background_image, (0, 0))
            screen.blit(self.name_game_image, (0, 0))
            menu_group.draw(screen)
            pygame.display.flip()

    def select_level(self):
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
        back_to_menu_btn.image = self.back_icon
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
                            if level_sprite.image == self.back_icon:
                                return None
                            return level_sprite.get_number_level()


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
background_image = pygame.transform.scale(background_image, SIZE_SCREEN)

background_chanel = pygame.mixer.Channel(0)
background_menu_music = pygame.mixer.Sound(file=os.path.join(MUSIC_FOLDER, 'menu_background.wav'))
background_game_play_music = pygame.mixer.Sound(file=os.path.join(MUSIC_FOLDER, 'background.wav'))

music_on = False

clock = pygame.time.Clock()
camera = Camera()

menu = Menu()
pause = Pause()
finish = Finish()
lose = Lose()

frames = 0

# player, level = menu.show()
level = Level(3)
player = level.generate()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                result = pause.show()
                if result == MAIN_MENU:
                    player, level = menu.show()
                elif result == RESTART_LEVEL:
                    player = level.generate()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                player.attack()
    screen.blit(background_image, (0, 0))
    if frames % 2 == 0:
        all_sprite.update()
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
        finish.set_progress(level.get_progress())
        result = finish.show()
        if result == MAIN_MENU:
            player, level = menu.show()
        elif result == RESTART_LEVEL:
            player = level.generate()
    if player.lose and not player.death_mode:
        result = lose.show()
        if result == MAIN_MENU:
            player, level = menu.show()
        elif result == RESTART_LEVEL:
            player = level.generate()
    clock.tick(FPS)
    frames += 1
