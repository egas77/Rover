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

OFFSET_RECT_PLAYER = 10

ROTATION_LEFT = 0
ROTATION_RIGHT = 1

MOVE_SPEED = 7
ENEMY_MOVE_SPEED = 1
JUMP_POWER = 15
GRAVITY = 1

FPS = 100

BACKGROUND_SOUND_VOLUME = 0.5
MUSIC_ON = True

element_texture_folder = 'data\\textures\\png\\elements'
tiles_texture_folder = 'data\\textures\\png\\tiles'
icons_folder = 'data\\textures\\icons'
music_folder = 'data\\music'
levels_folder = 'data\\levels'
player_texture_path = 'data\\textures\\player\\textures_48.png'
enemy_texture_path = 'data\\textures\\enemy\\textures_48.png'


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
                image = load_image(os.path.join(element_texture_folder, file_name))
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
        self.moving = False

    def collide(self, xvel, yvel,
                space_mask_right, space_mask_left, space_mask_up, space_mask_bottom,
                reverse_x=False):
        for game_object in pygame.sprite.spritecollide(self, game_objects, False,
                                                       collided=pygame.sprite.collide_mask):
            if isinstance(self, Player):
                if game_object.ignore_player:
                    continue
                elif isinstance(game_object, Heart):
                    self.lives += 1
                    game_object.kill()
                    self.visible_hearts()
                elif isinstance(game_object, CheckPoint):
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
                elif isinstance(game_object, ButtonJump):
                    if yvel:
                        self.yvel = -JUMP_POWER * 1.25
                    return None

                if game_object.collision_do_kill:
                    if not self.damage_mode and not self.death_mode:
                        self.lives -= 1
                        if self.lives > 0:
                            self.damage()
                        else:
                            self.death()
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
                self.onGround = True  # и становится на что-то твердое
                self.yvel = 0
            if yvel < 0:  # если движется вверх
                self.rect.top = game_object.rect.bottom - space_mask_up + 1  # то не движется вверх
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
                            self.restart()

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
        self.space_mask_right = 19
        self.space_mask_left = 18
        self.space_mask_up = 18
        self.space_mask_bottom = 5
        self.lives = 5
        for x in range(self.rect.width):
            for y in range(self.rect.height):
                if (self.space_mask_left <= x <= self.rect.width - self.space_mask_right
                        and self.space_mask_up <= y <= self.rect.height - self.space_mask_bottom):
                    self.mask.set_at((x, y), 1)
        self.visible_hearts()

    def update(self, left, right, up, speed_up):
        if left:
            self.xvel = -MOVE_SPEED
        if right:
            self.xvel = MOVE_SPEED
        if not (left or right) or self.damage_mode or self.death_mode:
            self.xvel = 0
        if speed_up:
            self.xvel *= 1.75
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
            elif not self.damage_mode and not self.death_mode:
                self.lives -= 1
                if self.lives > 0:
                    self.damage()
                else:
                    self.death()
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


class HeartIcon(pygame.sprite.Sprite):
    heart_image = load_image(os.path.join(element_texture_folder, 'heart.png'))
    width_heart = heart_image.get_width()
    space_x = 5

    def __init__(self, x):
        super().__init__(hearts_group)
        self.image = self.heart_image
        self.rect = self.image.get_rect(x=x * self.width_heart + self.space_x * (x + 1), y=10)


class Enemy(GamePerson):
    def __init__(self, sheet, x, y, rotation):
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
            if not self.onGround:
                self.yvel += GRAVITY
            self.onGround = False
            self.rect.y += self.yvel
            self.collide(0, self.yvel, self.space_mask_right, self.space_mask_left,
                         self.space_mask_up, self.space_mask_bottom, reverse_x=True)
            self.rect.x += self.xvel
            self.collide(self.xvel, 0, self.space_mask_right, self.space_mask_left,
                         self.space_mask_up, self.space_mask_bottom, reverse_x=True)

    def check_in_screen(self):
        if self.rect.colliderect(screen_rect) and not self.moving:
            return True
        return False


class Tile(GameObject):
    images = dict()

    def __init__(self, tile_name, x, y):
        super().__init__(x, y, is_tile=True, ignore_enemy=False, collision=True)
        self.add(tiles_group)
        if tile_name not in self.images:
            image = load_image(
                os.path.join(tiles_texture_folder, tile_name + '.png'))
            image = pygame.transform.scale(image, tile_size)
            self.images[tile_name] = image
        self.image = self.images[tile_name]
        self.rect = self.image.get_rect(x=tile_size[0] * x, y=tile_size[1] * y)
        self.mask = pygame.mask.Mask(self.rect.size, fill=True)


class Heart(GameObject):
    def __init__(self, x, y, file_name=None, collision=False, collision_do_kill=False,
                 ignore_player=False, ignore_enemy=True, size=(48, 48)):
        super().__init__(x, y, file_name=file_name, collision=collision,
                         collision_do_kill=collision_do_kill, ignore_player=ignore_player,
                         ignore_enemy=ignore_enemy, size=size)


class CheckPoint(GameObject):
    def __init__(self, x, y, file_name=None, collision=False, collision_do_kill=False,
                 ignore_player=False, ignore_enemy=True, size=(48, 48)):
        super().__init__(x, y, file_name=file_name, collision=collision,
                         collision_do_kill=collision_do_kill, ignore_player=ignore_player,
                         ignore_enemy=ignore_enemy, size=size)


class ButtonJump(GameObject):
    def __init__(self, x, y, file_name=None, collision=False, collision_do_kill=False,
                 ignore_player=False, ignore_enemy=True, size=(48, 48)):
        super().__init__(x, y, file_name=file_name, collision=collision,
                         collision_do_kill=collision_do_kill, ignore_player=ignore_player,
                         ignore_enemy=ignore_enemy, size=size)
        self.rect.y += (TILE_SIZE - size[1])


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
    global MUSIC_ON
    start_btn = pygame.sprite.Sprite(menu_group)
    start_btn.image = play_image
    start_btn.rect = start_btn.image.get_rect(x=WIDTH // 2 - start_btn.image.get_width() // 2 + 100,
                                              y=HEIGHT // 2 + 30)
    music_btn = pygame.sprite.Sprite(menu_group)
    if MUSIC_ON:
        music_btn.image = music_on_image
        background_chanel.play(background_menu_music, loops=-1)
    else:
        music_btn.image = music_off_image
    music_btn.rect = music_btn.image.get_rect(x=WIDTH // 2 - start_btn.image.get_width() // 2 - 100,
                                              y=HEIGHT // 2 + 30)
    screen.blit(background_image, (0, 0))
    screen.blit(name_game_image, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if event.button == pygame.BUTTON_LEFT:
                    if start_btn.rect.collidepoint(pos):
                        number_level = select_level()
                        generate_level(number_level)
                        return None
                    elif music_btn.rect.collidepoint(pos):
                        if MUSIC_ON:
                            MUSIC_ON = False
                            music_btn.image = music_off_image
                            background_chanel.stop()
                        else:
                            MUSIC_ON = True
                            music_btn.image = music_on_image
                            background_chanel.play(background_menu_music, loops=-1)
        menu_group.draw(screen)
        pygame.display.flip()


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
            elif level_map[y][x] == '>':
                Enemy(ememy_sheet, x, y, ROTATION_RIGHT)
            elif level_map[y][x] == '<':
                Enemy(ememy_sheet, x, y, ROTATION_LEFT)
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


GAME_OBJECTS_DICT = {
    '!': ('blade.png',
          {'collided': True, 'collided_do_kill': True, 'ignore_player': False,
           'ignore_enemy': False, 'size': (48, 96)}),
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
           'ignore_enemy': True, 'size': (48, 48)}),
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
          {'collided': False, 'collided_do_kill': False, 'ignore_player': True,
           'ignore_enemy': False, 'size': (48, 48)}),
    '\\': ('zero_player.png',
           {'collided': False, 'collided_do_kill': False, 'ignore_player': False,
            'ignore_enemy': True, 'size': (48, 48)})
}

background_chanel = pygame.mixer.Channel(0)
background_menu_music = pygame.mixer.Sound(file=os.path.join(music_folder, 'menu_background.wav'))

clock = pygame.time.Clock()

tile_size = (TILE_SIZE, TILE_SIZE)

load_level_font = pygame.font.Font(None, 150)

background_image = load_image(os.path.join(element_texture_folder, 'background.png'))
background_image = pygame.transform.scale(background_image, SIZE)
play_image = load_image(os.path.join(icons_folder, 'play.png'))
music_on_image = load_image(os.path.join(icons_folder, 'music_on.png'))
music_off_image = load_image(os.path.join(icons_folder, 'music_off.png'))
name_game_image = load_image(os.path.join(element_texture_folder, 'name-game.png'))

player_sheet = load_image(player_texture_path)
ememy_sheet = load_image(enemy_texture_path)

all_sprite = pygame.sprite.Group()
levels_group = pygame.sprite.Group()
menu_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
game_objects = pygame.sprite.Group()
player_group = pygame.sprite.GroupSingle()
enemy_group = pygame.sprite.Group()
hearts_group = pygame.sprite.Group()

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
    screen.blit(background_image, (0, 0))
    if frames % 2 == 0:
        if pygame.key.get_mods() & pygame.KMOD_LSHIFT:
            player.update(left, right, up, True)
        else:
            player.update(left, right, up, False)
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
    pygame.display.flip()
    clock.tick(FPS)
    frames += 1
