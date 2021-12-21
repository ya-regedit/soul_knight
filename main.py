import os
import sys

import pygame
import pytmx

from copy import copy

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


class Knight(pygame.sprite.Sprite):

    def __init__(self, pos: tuple, hp,
                 sheet: pygame.image):
        super(Knight, self).__init__(all_sprites)
        self.v = 2
        self.pos = pos
        self.next_pos = pos
        self.hp = hp
        self.effect = None
        self.effect_end = 0
        self.dx, self.dy = 0, 0

        self.sheet = sheet
        self.sheet = pygame.transform.scale(self.sheet, (224, 224))
        self.rect = None

        self.normal_frames = []
        self.reversed_frames = []

        self.cut_sheet(self.sheet, 4, 4)

        self.normal_static_frames = copy(self.normal_frames)
        self.reversed_static_frames = copy(self.reversed_frames)

        del self.normal_static_frames[4:8]
        del self.normal_static_frames[8:]
        del self.reversed_static_frames[4:8]
        del self.reversed_static_frames[8:]
        del self.normal_frames[:4]
        del self.normal_frames[3:8]
        del self.reversed_frames[:4]
        del self.reversed_frames[3:8]

        self.cur_frame = 0
        self.image = self.normal_frames[self.cur_frame]

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(self.pos[0], self.pos[1], sheet.get_width() // columns - 5,
                                sheet.get_height() // rows - 5)
        for j in range(rows):
            for i in range(columns):
                frame_location = ((self.rect.w + 5) * i, (self.rect.h + 5) * j)
                self.normal_frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

                img = sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size))
                self.reversed_frames.append(pygame.transform.flip(img, True, False))

    def update(self, ev):
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_LEFT:
                self.dx -= self.v
            elif ev.key == pygame.K_RIGHT:
                self.dx += self.v
            elif ev.key == pygame.K_UP:
                self.dy -= self.v
            elif ev.key == pygame.K_DOWN:
                self.dy += self.v
        if ev.type == pygame.KEYUP:
            if ev.key == pygame.K_LEFT:
                self.dx += self.v
            elif ev.key == pygame.K_RIGHT:
                self.dx -= self.v
            elif ev.key == pygame.K_UP:
                self.dy += self.v
            elif ev.key == pygame.K_DOWN:
                self.dy -= self.v

    def move(self):
        self.next_pos = self.pos[0] + self.dx, self.pos[1] + self.dy
        if self.is_free(self.dx, 0):
            self.rect = self.rect.move(self.dx, 0)
        if self.is_free(0, self.dy):
            self.rect = self.rect.move(0, self.dy)
        self.pos = self.next_pos

    def is_free(self, dx, dy):  # метод, который будет проверять клетку в которую мы пытаемся пойти,
        # если там препятствие - вернет False, иначе True
        newrect = self.rect.move(dx, dy)
        if newrect.collidelist(level_mode.levels[level_mode.current_level].not_free_rects) != -1:
            return False
        return True

    def do_animate(self):
        global animation_frequency
        if animation_frequency > 10:
            self.cur_frame = (self.cur_frame + 1) % len(self.normal_frames)
            if self.dx > 0:
                self.image = self.normal_frames[self.cur_frame]
            elif self.dx < 0:
                self.image = self.reversed_frames[self.cur_frame]
            elif self.dx == 0 and self.dy != 0:
                if self.image in self.normal_frames:
                    self.image = self.normal_frames[self.cur_frame]
                else:
                    self.image = self.reversed_frames[self.cur_frame]
            else:
                try:
                    if self.image in self.normal_frames or self.image in self.normal_static_frames:
                        self.image = self.normal_static_frames[self.cur_frame]
                    else:
                        self.image = self.reversed_static_frames[self.cur_frame]
                except IndexError:
                    self.cur_frame = self.cur_frame % len(self.normal_static_frames)
            animation_frequency = 0


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos: tuple, hp, image: pygame.image):
        super(Enemy, self).__init__(all_sprites, enemies)
        self.rect = image.get_rect()
        self.rect.x, self.rect.y = level_mode.levels[level_mode.current_level].get_left_top_pixel_of_cell(pos)
        self.pos = pos
        self.hp = hp
        self.next_shot = 0
        self.next_move = 0
        self.effect = None
        self.effect_end = 0
        self.image = image

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
        super(EnemyShotguner, self).__init__(pos, hp, image)
        self.gun = gun

    def calc_move(self):
        pass


class EnemyRifler(Enemy):
    def __init__(self, pos: tuple, hp, image, field, gun):
        super(EnemyRifler, self).__init__(pos, hp, image)
        self.gun = gun


class Level:
    def __init__(self, map_path, enemies_path, not_free_tiles: list):
        self.map = pytmx.load_pygame(map_path)
        self.width = self.map.width
        self.height = self.map.height
        self.tile_size = self.map.tilewidth
        self.enemies = enemies_path
        self.not_free_tiles = not_free_tiles
        self.not_free_rects = self.generate_rects()

    def get_left_top_pixel_of_cell(self, pixel_pos):
        x, y = pixel_pos
        if x not in range(0, self.width * self.tile_size) \
                or y not in range(0, self.height * self.tile_size):
            return None
        return x // self.tile_size * self.tile_size, y // self.tile_size * self.tile_size

    def get_cell(self, pos):
        x, y = pos
        column = x // self.tile_size
        row = y // self.tile_size
        if 0 <= row < self.height and 0 <= column < self.width:
            return column, row
        return None

    def generate_rects(self):
        rects = []
        for i in range(self.map.width):
            for j in range(self.map.height):
                if self.map.tiledgidmap[self.map.get_tile_gid(i, j, 0)] in self.not_free_tiles:
                    rect = pygame.Rect(i * self.map.tilewidth, j * self.map.tileheight,
                                       self.map.tilewidth, self.map.tileheight)
                    rects.append(rect)
        return rects

    def spawn_enemies(self, enemies):
        pass

    def render(self):
        for x in range(self.width):
            for y in range(self.height):
                image = self.map.get_tile_image(x, y, 0)
                screen.blit(image, (x * self.tile_size, y * self.tile_size))

    def get_tile_id(self, pos):
        if pos:
            return self.map.tiledgidmap[self.map.get_tile_gid(*pos, 0)]


class ModeWithLevels:
    def __init__(self, knight: Knight):
        self.knight = knight
        self.levels = [[None] * 15]
        self.current_level = 0  # будет зависеть от нажатой кнопки с номером уровня

    def render(self):
        self.levels[self.current_level].render()


class HardcoreMode:
    pass


if __name__ == '__main__':
    size = w, h = 2560, 1440
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Start')
    clock = pygame.time.Clock()
    running = True
    fps = 100
    ticks = 0
    animation_frequency = 0

    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()  # это пока будет тут, потом пойдет в класс режима игры

    knight_main = Knight((150, 150), 100, load_image('knight.png'))

    level_mode = ModeWithLevels(knight_main)  # в дальнейшем это будет вызываться при
    # нажатии на экране кнопки "Режим уровней"
    level_mode.levels = [Level('maps/Level1.tmx', 'enemies/enemies1', [21])]

    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            knight_main.update(event)
        knight_main.move()
        knight_main.do_animate()
        pygame.display.update()
        level_mode.render()
        all_sprites.draw(screen)
        ticks += 1
        animation_frequency += 1
        # enemies.update(ticks)
        # enemies.draw(screen)
        clock.tick(fps)
    pygame.quit()
