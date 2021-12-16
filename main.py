import os
import sys

import pygame

pygame.init()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.left = 10
        self.top = 10
        self.cell_size = 30

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, surf):
        for r in range(self.height):
            for c in range(self.width):
                rect = pygame.Rect(self.left + c * self.cell_size,
                                   self.top + r * self.cell_size,
                                   self.cell_size, self.cell_size)
                pygame.draw.rect(surf, "white", rect, 1)

    def get_0_0_pixel_of_cell(self, pixel_pos):
        x, y = pixel_pos
        x -= self.left
        y -= self.top
        if x not in range(0, self.width * self.cell_size) \
                or y not in range(0, self.height * self.cell_size):
            return None
        return x // self.cell_size, y // self.cell_size

    def get_rect(self, pos):
        if not 0 <= pos[0] < self.width or not 0 <= pos[1] < self.height:
            return None
        return self.left + self.cell_size * pos[0], self.top + self.cell_size * pos[1]


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos: tuple, hp, image: pygame.image, board: Board):
        super(Enemy, self).__init__(enemies)
        self.rect = image.get_rect()
        self.rect.x, self.rect.y = board.get_0_0_pixel_of_cell(pos)
        self.pos = pos
        self.hp = hp
        self.next_shot = 0
        self.next_move = 0
        self.effect = None
        self.effect_end = 0
        self.image = image
        self.board = board

    def move(self):
        pass

    def shoot(self):
        pass

    def update(self, tick):
        if self.effect_end > tick:
            self.effect = None
        if self.next_shot > tick:
            self.shoot()

    def apply_effect(self, effect, time):
        self.effect = effect
        self.effect_end = pygame.time.get_ticks() + time

    def get_damage(self):
        pass


class EnemyShotguner(Enemy):
    def calc_move(self):
        pass


class EnemyRifler(Enemy):
    def __init__(self, pos: tuple, hp, image, board, gun):
        super(EnemyRifler, self).__init__(pos, hp, image, board)
        self.gun = gun


class Level:
    def __init__(self, map_path, enemies_path):
        self.map = self.load_map(map_path)
        self.enemies = enemies_path

    def load_map(self, map_path):
        pass

    def spawn_enemies(self, enemies):
        pass


class ModeWithLevels:
    def __init__(self):
        self.levels = [[None] * 15]


class HardcoreMode:
    pass


if __name__ == '__main__':
    size = w, h = 600, 600
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Start')
    clock = pygame.time.Clock()
    running = True
    fps = 100
    ticks = 0
    enemies = pygame.sprite.Group() # это пока будет тут, потом пойдет в класс режима игры
    # EnemyRifler((0,0), hp, load_image(''), enemies)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        ticks += 1
        pygame.display.update()
        screen.fill('white')
        enemies.draw(screen)
        enemies.update(ticks)
        clock.tick(fps)
    pygame.quit()
