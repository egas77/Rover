import os
import sys
import pygame

# Initialization PyGame
pygame.init()
# Screen Size
WIDTH, HEIGHT = SIZE = 1000, 500
# Main Display
screen = pygame.display.set_mode(SIZE)

element_texture_folder = 'data\\textures\\png\\elements'
tiles_texture_folder = 'data\\textures\\png\\tiles'
levels_folder = 'data\\levels'
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


class Tile(pygame.sprite.Sprite):
    tile_size = (25, 25)

    def __init__(self, tile_name, x, y):
        super().__init__(all_sprite, tiles_group)
        self.image = load_image(os.path.join(tiles_texture_folder, tile_name + '.png'))
        self.image = pygame.transform.scale(self.image, self.tile_size)
        self.rect = self.image.get_rect(x=self.tile_size[0] * x, y=self.tile_size[1] * y)


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


def load_level(level_path):
    with open(level_path, mode='r', encoding='utf8') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    level_map = list(map(lambda row: row.ljust(max_width, '#'), level_map))
    return level_map


def generate_level(number_level):
    level_path = os.path.join(levels_folder, str(number_level) + '.lvl')
    level_map = load_level(level_path)
    for y in range(len(level_map)):
        for x in range(len(level_map[0])):
            if level_map[y][x] == '@':
                pass
            elif level_map[y][x] != '#':
                Tile(level_map[y][x], x, y)


background_image = load_image(background_path)
background_image = pygame.transform.scale(background_image, SIZE)
all_sprite = pygame.sprite.Group()
levels_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
start_game()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
    screen.blit(background_image, (0, 0))
    all_sprite.draw(screen)
    pygame.display.flip()
