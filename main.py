import os
import sys

import pygame
import pytmx

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


class Field:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.left = 10
        self.top = 10
        self.cell_size = 10

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

    def get_left_top_pixel_of_cell(self, pixel_pos):
        x, y = pixel_pos
        x -= self.left
        y -= self.top
        if x not in range(0, self.width * self.cell_size) \
                or y not in range(0, self.height * self.cell_size):
            return None
        return x // self.cell_size * self.cell_size, y // self.cell_size * self.cell_size

    def get_cell(self, pos):
        x, y = pos
        column = (x - self.left) // self.cell_size
        row = (y - self.top) // self.cell_size
        if 0 <= row < self.height and 0 <= column < self.width:
            return row, column
        return None

    def get_rect(self, pos):
        if not 0 <= pos[0] < self.width or not 0 <= pos[1] < self.height:
            return None
        return self.left + self.cell_size * pos[0], self.top + self.cell_size * pos[1]


class Knight(pygame.sprite.Sprite):
    def __init__(self, pos: tuple, hp,
                 image: pygame.image,
                 board: Field):
        super(Knight, self).__init__(all_sprites)
        self.v = 1
        self.rect = image.get_rect()
        self.pos = pos
        self.next_pos = pos
        self.hp = hp
        self.effect = None
        self.effect_end = 0
        self.image = image
        self.board = board
        self.dx, self.dy = 0, 0

    def update(self, ev):
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_LEFT:
                self.dx = -self.v
            elif ev.key == pygame.K_RIGHT:
                self.dx = self.v
            elif ev.key == pygame.K_UP:
                self.dy = -self.v
            elif ev.key == pygame.K_DOWN:
                self.dy = self.v
        if ev.type == pygame.KEYUP:
            if ev.key == pygame.K_LEFT:
                self.dx = 0
            elif ev.key == pygame.K_RIGHT:
                self.dx = 0
            elif ev.key == pygame.K_UP:
                self.dy = 0
            elif ev.key == pygame.K_DOWN:
                self.dy = 0

    def move(self):
        self.next_pos = self.pos[0] + self.dx, self.pos[1] + self.dy
        if self.is_free():
            self.rect = self.rect.move(self.dx, self.dy)

    def is_free(self):  # метод, который будет проверять клетку в которую мы пытаемся пойти,
        # если там препятствие - вернет False, иначе True
        return True


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos: tuple, hp, image: pygame.image, field: Field):
        super(Enemy, self).__init__(all_sprites, enemies)
        self.rect = image.get_rect()
        self.rect.x, self.rect.y = field.get_left_top_pixel_of_cell(pos)
        self.pos = pos
        self.hp = hp
        self.next_shot = 0
        self.next_move = 0
        self.effect = None
        self.effect_end = 0
        self.image = image
        self.board = field

    def move(self):  # можно в update, наверное, засунуть, ведь есть метод встроенный self.rect.move(x, y)
        pass

    def shoot(self):
        pass

    def update(self, n_ticks):
        if n_ticks > self.effect_end:
            self.effect = None
        if n_ticks > self.next_shot:
            self.shoot()

    def apply_effect(self, effect, time):
        self.effect = effect
        self.effect_end = pygame.time.get_ticks() + time

    def get_damage(self):
        pass


class EnemyShotguner(Enemy):
    def __init__(self, pos: tuple, hp, image, field, gun):
        super(EnemyShotguner, self).__init__(pos, hp, image, field)
        self.gun = gun

    def calc_move(self):
        pass


class EnemyRifler(Enemy):
    def __init__(self, pos: tuple, hp, image, field, gun):
        super(EnemyRifler, self).__init__(pos, hp, image, field)
        self.gun = gun


class Level:
    def __init__(self, map_path, enemies_path, free_cells: list):
        self.map = pytmx.load_pygame(map_path)
        self.width = self.map.width
        self.height = self.map.height
        self.tile_size = self.map.tilewidth
        self.enemies = enemies_path
        self.free_cells = free_cells

    def spawn_enemies(self, enemies):
        pass

    def render(self):
        for x in range(self.width):
            for y in range(self.height):
                image = self.map.get_tile_image(x, y, 0)
                screen.blit(image, (x * self.tile_size, y * self.tile_size))


class ModeWithLevels:
    def __init__(self, field: Field, knight: Knight):
        self.field = field
        self.knight = knight
        self.levels = [[None] * 15]
        self.current_level = 0  # будет зависеть от нажатой кнопки с номером уровня

    def render(self):
        self.field.render(screen)
        self.levels[self.current_level].render()


class HardcoreMode:
    pass


if __name__ == '__main__':
    size = w, h = 1050, 950
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Start')
    clock = pygame.time.Clock()
    running = True
    fps = 100
    ticks = 0

    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()  # это пока будет тут, потом пойдет в класс режима игры

    field_main = Field(10, 10)
    knight_main = Knight((0, 0), 100, load_image('knight.png'), field_main)

    level_mode = ModeWithLevels(field_main,
                                knight_main)  # в дальнейшем это будет вызываться при
    # нажатии на экране кнопки "Режим уровней"
    level_mode.levels = [Level('maps/test_level.tmx', 'enemies/enemies1', [0, 1, 2])]

    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            knight_main.update(event)
        knight_main.move()
        ticks += 1
        pygame.display.update()
        level_mode.render()
        all_sprites.draw(screen)

        # enemies.update(ticks)
        # enemies.draw(screen)
        clock.tick(fps)
    pygame.quit()
