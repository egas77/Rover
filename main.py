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
background_path = os.path.join(element_texture_folder, 'background.png')


def terminate():
    """Function terminate this game"""
    pygame.quit()
    sys.exit(0)


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


class StartGameScreen(pygame.Surface):
    def __init__(self):
        super().__init__(SIZE)
        self.fill(pygame.Color('blue'))
        self.set_colorkey(self.get_at((0, 0)))

    def show(self):
        screen.blit(self, (0, 0))


def start_game():
    start_game_screen = pygame.Surface(SIZE)
    start_game_screen = start_game_screen.convert()
    start_game_screen.set_colorkey(start_game_screen.get_at((0, 0)))
    button_radius = 50
    button_rect = pygame.Rect(WIDTH // 2 - button_radius, HEIGHT // 2 - button_radius + 100,
                              button_radius * 2, button_radius * 2)
    pygame.draw.circle(start_game_screen, pygame.Color(14, 14, 232),
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
                    print('Click Start Game')


background_image = load_image(background_path)
background_image = pygame.transform.scale(background_image, SIZE)
start_game()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            screen.blit(background_image, (0, 0))

    pygame.display.flip()
