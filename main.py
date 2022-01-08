import os
import sys

import pygame
import pytmx
import pygame_gui

from random import choice
from copy import copy
from math import sqrt, degrees, atan, inf

from constants import *
from UI import manager, show_level_btns, hide_level_btns, show_main_btns, hide_main_btns, \
    show_endgame_btns, hide_endgame_btns, to_beginning, to_exit, \
    level_mode_btn, hardcore_mode_btn, exit_button1, back_btn, level_btns

pygame.init()
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
screen_rect = pygame.Rect(0, 0, *size)
pygame.display.set_caption('Soul Knight')
clock = pygame.time.Clock()
pygame.mixer.music.set_volume(VOLUME)


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


def start_screen():
    pygame.mixer.music.load('data/music/start_music.mp3')
    pygame.mixer.music.play(-1)
    global running, current_level, do_exit
    show_main_btns()
    hide_level_btns()
    hide_endgame_btns()
    while running:
        events = pygame.event.get()
        time_delta = clock.tick(fps) / 1000.0
        for event in events:
            if event.type == pygame.QUIT:
                running = False
                do_exit = True
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == exit_button1:
                        running = False
                        do_exit = True
                    if event.ui_element == level_mode_btn:
                        hide_main_btns()
                        show_level_btns()
                    if event.ui_element == back_btn:
                        hide_level_btns()
                        show_main_btns()
                    if event.ui_element in level_btns and event.ui_element != back_btn:
                        current_level = int(event.ui_element.text[-1]) - 1
                        running = False
                        do_exit = False
                        hide_level_btns()

                        pygame.mixer.music.fadeout(1000)
                        if current_level in (0, 1, 2):
                            pygame.mixer.music.load('data/music/first_floor.mp3')
                        elif current_level in (3, 4, 5):
                            pygame.mixer.music.load('data/music/second_floor.mp3')
                        else:
                            pygame.mixer.music.load('data/music/third_floor.mp3')
                        pygame.mixer.music.play(-1)
                        return

            manager.process_events(event)
        manager.update(time_delta)
        screen.blit(pygame.transform.scale(load_image('background.png'), (w, h)), (0, 0))
        manager.draw_ui(screen)
        pygame.display.flip()
        clock.tick(fps)


def endgame_screen():
    global running, do_exit, VICTORY, REBOOT_GAME
    hide_level_btns()
    hide_main_btns()
    show_endgame_btns()
    pygame.mixer.music.fadeout(1000)
    if not VICTORY:
        pygame.mixer.music.load('data/music/end_music.mp3')
    else:
        pygame.mixer.music.load('data/music/win_music.mp3')
    pygame.mixer.music.play(-1)

    while not do_exit:
        events = pygame.event.get()
        time_delta = clock.tick(fps) / 1000.0
        for event in events:
            if event.type == pygame.QUIT:
                running = False
                do_exit = True
                return
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == to_beginning:
                        REBOOT_GAME = False
                        start_screen()
                        return
                    if event.ui_element == to_exit:
                        do_exit = True
                        running = False
            manager.process_events(event)
        manager.update(time_delta)
        if VICTORY:
            screen.blit(pygame.transform.scale(load_image('win_screen.png'), (w, h)), (0, 0))
        else:
            screen.blit(pygame.transform.scale(load_image('gameover_screen.jpg'), (w, h)), (0, 0))
        manager.draw_ui(screen)
        pygame.display.flip()
        clock.tick(fps)


class Knight(pygame.sprite.Sprite):
    def __init__(self, pos: tuple, hp,
                 sheet: pygame.image, gun_id):
        super(Knight, self).__init__(all_sprites)
        self.v = 2
        self.pos = pos
        self.next_pos = pos
        self.hp = hp
        self.effect = None
        self.effect_end = 0
        self.dx, self.dy = 0, 0
        self.direction_of_vision = {'Right': True, 'Left': False}

        self.sheet = sheet
        self.sheet = pygame.transform.scale(self.sheet, (240, 240))
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.sheet.get_width() // 4 - 5,
                                self.sheet.get_height() // 4 - 5)

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

        self.gun_id = gun_id
        self.guns = None
        self.gun = None
        self.show_gun(self.gun_id)

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

    def update(self, ev, ticks):
        global running, VICTORY, REBOOT_GAME
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
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            self.gun.shoot(ticks)
        if self.hp <= 0:
            self.kill()
            REBOOT_GAME = True
            VICTORY = False

    def render(self, ticks):
        if not REBOOT_GAME:
            self.gun.render(ticks)

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
            if self.dx > 0:  # если идет вправо
                if self.direction_of_vision['Right']:  # и при этом смотрит вправо
                    self.image = self.normal_frames[self.cur_frame]
                else:
                    self.image = self.reversed_frames[self.cur_frame]

            elif self.dx < 0:  # если идет влево
                if self.direction_of_vision['Left']:  # и при этом смотрит влево
                    self.image = self.reversed_frames[self.cur_frame]
                else:
                    self.image = self.normal_frames[self.cur_frame]

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

    def show_gun(self, gun_id):
        self.guns = [Gun(pygame.transform.scale(load_image('Aurora.png'), (60, 45)), (5, 5), 0, 10, self, 2),
                     # размеры, сдвиг относительно центра перса, тип патронов,
                     # средняя скорость пуль, владелец (для пуль), урон
                     # у дробовика размеры, сдвиг, владелец, урон, радиус
                     Shotgun(pygame.transform.scale(load_image('hammer.jpg', -1),
                                                    (75, 30)), (5, 10), self, 10, 100)]
        self.gun = self.guns[gun_id]


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos: tuple, hp, image: pygame.image, gun_id):
        super(Enemy, self).__init__(all_sprites, level_mode.levels[current_level].enemies_sprites)
        self.rect = image.get_rect()
        self.rect.x, self.rect.y = level_mode.levels[level_mode.current_level].get_left_top_pixel_of_cell(pos)
        self.pos = pos
        self.hp = hp
        self.next_shot = 300
        self.next_move = 100
        self.n_ticks_shoot = 0
        self.n_ticks_move = 0
        self.n_ticks_effect = 0

        self.reloading = False
        self.moving = False
        self.v = level_mode.levels[current_level].tile_size
        self.flag_float = 0
        self.distances = []
        self.dx, self.dy = 0, 0

        self.effect = None
        self.effect_end = 0
        self.image = self.source_image = image
        self.reversed_image = pygame.transform.flip(image, True, False)
        self.guns = None
        self.gun = None
        self.gun_id = gun_id
        self.show_gun(self.gun_id)

    def show_gun(self, gun_id):
        self.guns = [Gun(pygame.transform.scale(load_image('Aurora.png'), (60, 45)), (5, 5), 0, 10, self, 2),
                     # размеры, сдвиг относительно центра перса, тип патронов,
                     # средняя скорость пуль, владелец (для пуль), урон
                     # у дробовика размеры, сдвиг, владелец, урон, радиус
                     Shotgun(pygame.transform.scale(load_image('hammer.jpg', -1),
                                                    (50, 25)), (20, 20), self, 10, 100)]
        self.gun = self.guns[gun_id]

    def shoot(self, ticks):
        self.gun.enemy_shoot(ticks)

    def update(self, n_ticks):
        global ticks, VICTORY, REBOOT_GAME
        if not self.reloading:
            self.n_ticks_shoot = n_ticks
            self.reloading = True

        if not self.moving:
            self.n_ticks_move = n_ticks
            self.moving = True

        if ticks - self.n_ticks_effect > self.effect_end:
            self.effect = None

        if ticks - self.n_ticks_shoot > self.next_shot:
            self.shoot(ticks)
            self.reloading = False
        if self.hp <= 0:
            level_mode.levels[current_level].enemies.remove(self)
            self.gun.kill()
            self.kill()
            if not level_mode.levels[current_level].enemies:
                VICTORY = True
                REBOOT_GAME = True

        r0, c0 = level_mode.levels[current_level].get_cell((self.rect.x, self.rect.y))
        r, c = level_mode.levels[current_level].get_cell((knight_main.rect.x, knight_main.rect.y))

        width = level_mode.levels[current_level].width
        height = level_mode.levels[current_level].height
        if self.find_path(r0, c0, r, c):
            for dr, dc in ((0, -1), (-1, 0), (0, 1), (1, 0)):
                next_r, next_c = r0 + dr, c0 + dc
                if (0 <= next_r < height and 0 <= next_c < width and
                        self.distances[next_r][next_c] == self.distances[r0][c0] + 1):
                    if ticks - self.n_ticks_move > self.next_move:
                        self.dx, self.dy = 0.0625 * (self.v * dr), 0.0625 * (self.v * dc)
                        if self.dx > 0:
                            self.image = self.source_image
                        elif self.dx < 0:
                            self.image = self.reversed_image

                        self.rect = self.rect.move(self.dx, self.dy)
                        self.flag_float += 1
                        if self.flag_float == 60:  # отвечает за "длину" шага
                            self.moving = False
                            self.flag_float = 0

    def find_path(self, r0, c0, r1, c1):
        width = level_mode.levels[current_level].width
        height = level_mode.levels[current_level].height
        self.distances = [[inf] * height for _ in range(width)]
        self.distances[r0][c0] = 0
        queue = [(r0, c0)]
        while queue:
            r, c = queue.pop(0)
            if (r, c) == (r1, c1):
                return True
            if r1 >= r0:
                priority_x = (1, 0)
            else:
                priority_x = (-1, 0)
            if c1 >= c0:
                priority_y = (1, 0)
            else:
                priority_y = (-1, 0)
            for dr in priority_x:
                for dc in priority_y:
                    next_r, next_c = r + dr, c + dc
                    if (0 <= next_r < height and 0 <= next_c < width and
                            level_mode.levels[current_level].map_arr[next_r][next_c] != -1 and
                            self.distances[next_r][next_c] == inf):
                        self.distances[next_r][next_c] = self.distances[r][c] + 1
                        queue.append((next_r, next_c))
        return False

    def apply_effect(self, effect, time):
        self.effect = effect
        self.effect_end = pygame.time.get_ticks() + time

    def get_damage(self):
        pass

    def render(self, ticks):
        self.gun.enemy_render(self.rect, ticks)


class EnemyShotguner(Enemy):
    def __init__(self, pos: tuple, hp, image, field, gun_id):
        super(EnemyShotguner, self).__init__(pos, hp, image, gun_id)
        self.field = field


class EnemyRifler(Enemy):
    def __init__(self, pos: tuple, hp, image, field, gun_id):  # зачем тут field
        super(EnemyRifler, self).__init__(pos, hp, image, gun_id)
        self.field = field


class Level:
    def __init__(self, map_path, enemies_list, not_free_tiles: list):
        self.map = pytmx.load_pygame(map_path)
        self.width = self.map.width
        self.height = self.map.height
        self.tile_size = self.map.tilewidth
        self.enemies_list = enemies_list
        self.not_free_tiles = not_free_tiles
        self.not_free_rects, self.map_arr = self.generate_rects_and_map_array()
        self.enemies_sprites = pygame.sprite.Group()
        self.enemies = []

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

    def generate_rects_and_map_array(self):
        rects = []
        map_arr = []
        for i in range(self.map.width):
            line = []
            for j in range(self.map.height):
                if self.map.tiledgidmap[self.map.get_tile_gid(i, j, 0)] in self.not_free_tiles:
                    rect = pygame.Rect(i * self.map.tilewidth, j * self.map.tileheight,
                                       self.map.tilewidth, self.map.tileheight)
                    rects.append(rect)
                    line.append(-1)
                else:
                    line.append(0)
            map_arr.append(line)
        return rects, map_arr

    def spawn_enemies(self, tile_size):
        e = []
        image1 = load_image('enemy_1.png', -1)
        image2 = load_image('enemy_2.png')

        if image1.get_width() < image1.get_height():
            k = tile_size[1] / image1.get_height()
            image1 = pygame.transform.scale(image1, (round(k * image1.get_width()), tile_size[1]))
        else:
            k = tile_size[0] / image1.get_width()
            image1 = pygame.transform.scale(image1, (tile_size[0], round(k * image1.get_height())))

        if image2.get_width() < image2.get_height():
            k = tile_size[1] / image2.get_height()
            image2 = pygame.transform.scale(image2, (round(k * image2.get_width()), tile_size[1]))
        else:
            k = tile_size[0] / image2.get_width()
            image2 = pygame.transform.scale(image2, (tile_size[0], round(k * image2.get_height())))

        for enemy in self.enemies_list:
            pos = self.tile_size * enemy[0][0], self.tile_size * enemy[0][1]
            if 0 <= enemy[0][0] < self.map.width and 0 <= enemy[0][1] < self.map.height:
                if enemy[1] == 1:
                    e.append(EnemyRifler(pos, 10, image1, 'тут будет передача поля', 0))
                if enemy[1] == 0:
                    e.append(EnemyRifler(pos, 10, image2, 'тут будет передача поля', 1))
                self.enemies_sprites.add(e[-1])
        self.enemies = e

    def render(self):
        for x in range(self.width):
            for y in range(self.height):
                image = self.map.get_tile_image(x, y, 0)
                screen.blit(image, (x * self.tile_size, y * self.tile_size))

    def get_tile_id(self, pos):
        if pos:
            return self.map.tiledgidmap[self.map.get_tile_gid(*pos, 0)]


class Gun(pygame.sprite.Sprite):
    def __init__(self, img: pygame.image, shift: tuple, id_bullets, v_bullets, owner, damage):
        super(Gun, self).__init__()
        self.shift_x, self.shift_y = shift
        self.image = self.source_img = img
        self.rect = pygame.rect.Rect(owner.rect.center[0] - self.shift_x,
                                     owner.rect.center[1] - self.shift_y,
                                     self.image.get_width(), self.image.get_height())
        self.last_image = None
        self.angle = None

        self.id_bullets = id_bullets
        self.v_bullets = v_bullets

        self.adjacent_cathet = 0
        self.opposite_cathet = 0
        self.owner = owner
        self.damage = damage
        self.old_owner_rect = self.owner.rect

    def rot_around_center(self, image, angle, x, y):
        rotated_image = pygame.transform.rotate(image, angle)
        new_rect = rotated_image.get_rect(center=image.get_rect(center=(x, y)).center)
        return rotated_image, new_rect

    def render(self, ticks):
        move_x, move_y = self.old_owner_rect.x - self.owner.rect.x, self.old_owner_rect.y - self.owner.rect.y
        self.rect.x -= move_x
        self.rect.y -= move_y
        self.old_owner_rect = self.owner.rect
        if pygame.mouse.get_focused():
            mouse_pos = pygame.mouse.get_pos()
            center_coords = knight_main.rect.center

            self.adjacent_cathet = sqrt((mouse_pos[0] - center_coords[0]) ** 2)
            self.opposite_cathet = sqrt((mouse_pos[1] - center_coords[1]) ** 2)

            if self.adjacent_cathet != 0:
                self.angle = degrees(atan(self.opposite_cathet / self.adjacent_cathet))
            else:
                self.angle = 90

            if mouse_pos[1] > center_coords[1]:  # если курсор выше персонажа
                self.angle = -self.angle

            if mouse_pos[0] > center_coords[0]:  # если курсор правее персонажа
                if knight_main.direction_of_vision['Left']:
                    self.rect.x += 40
                if knight_main.dx == 0 and knight_main.dy == 0:  # если персонаж стоит на месте
                    knight_main.image = knight_main.normal_static_frames[knight_main.cur_frame]
                else:
                    knight_main.image = knight_main.normal_frames[knight_main.cur_frame]

                self.image, self.rect = self.rot_around_center(self.source_img, self.angle, *self.rect.center)

                knight_main.direction_of_vision['Right'], \
                knight_main.direction_of_vision['Left'] = True, False

            else:
                if knight_main.dx == 0 and knight_main.dy == 0:
                    knight_main.image = knight_main.reversed_static_frames[knight_main.cur_frame]
                else:
                    knight_main.image = knight_main.reversed_frames[knight_main.cur_frame]

                self.image, self.rect = self.rot_around_center(self.source_img, self.angle, *self.rect.center)
                self.image = pygame.transform.flip(self.image, True, False)
                if knight_main.direction_of_vision['Right']:
                    self.rect.x -= 40
                knight_main.direction_of_vision['Right'], \
                knight_main.direction_of_vision['Left'] = False, True

        else:
            if knight_main.direction_of_vision['Right']:
                self.image = self.source_img
            else:
                self.image = pygame.transform.flip(self.source_img, True, False)
                self.rect.x -= 40
        screen.blit(self.image, self.rect)

    def enemy_render(self, rect: pygame.Rect, ticks):
        center_coords = rect.center
        x, y = knight_main.rect.center
        self.adjacent_cathet = sqrt((x - center_coords[0]) ** 2)
        self.opposite_cathet = sqrt((y - center_coords[1]) ** 2)

        if self.adjacent_cathet != 0:
            self.angle = degrees(atan(self.opposite_cathet / self.adjacent_cathet))
        else:
            self.angle = 90
        if y > center_coords[1]:  # если курсор выше персонажа
            self.angle = -self.angle
        if x > center_coords[0]:  # если курсор правее персонажа
            self.image, self.rect = self.rot_around_center(self.source_img, self.angle,
                                                           *(center_coords[0], center_coords[1] + 5))
        else:
            self.image, self.rect = self.rot_around_center(self.source_img, self.angle,
                                                           *(center_coords[0], center_coords[1] + 5))
            self.image = pygame.transform.flip(self.image, True, False)

        screen.blit(self.image, self.rect)

    def shoot(self, ticks):
        mouse_pos = pygame.mouse.get_pos()

        right = True if mouse_pos[0] > knight_main.rect.center[0] else False
        top = True if mouse_pos[1] < knight_main.rect.center[1] else False

        bullet = Bullet(right, top, self.v_bullets, self.adjacent_cathet, self.opposite_cathet, self.owner, self.damage)

        normal_img = load_image(db_bullets[self.id_bullets])
        reversed_img = pygame.transform.flip(normal_img, True, False)

        bullet.image = normal_img
        bullet.rect = bullet.image.get_rect()
        bullet.rect.center = (self.rect.center[0], self.rect.center[1])

        if self.angle:
            if not right:
                bullet.image = reversed_img
                bullet.image, bullet.rect = self.rot_around_center(bullet.image, -self.angle, *bullet.rect.center)
            else:
                bullet.image, bullet.rect = self.rot_around_center(bullet.image, self.angle, *bullet.rect.center)
            screen.blit(bullet.image, bullet.rect)

    def enemy_shoot(self, ticks):
        x, y = knight_main.rect.center

        right = True if x > self.owner.rect.center[0] else False
        top = True if y < self.owner.rect.center[1] else False

        bullet = Bullet(right, top, self.v_bullets, self.adjacent_cathet, self.opposite_cathet, self.owner, self.damage)

        normal_img = load_image(db_bullets[self.id_bullets])
        reversed_img = pygame.transform.flip(normal_img, True, False)

        bullet.image = normal_img
        bullet.rect = bullet.image.get_rect()
        bullet.rect.center = (self.rect.center[0] + 7, self.rect.center[1])

        if self.angle:
            if not right:
                bullet.image = reversed_img
                bullet.image, bullet.rect = self.rot_around_center(bullet.image, -self.angle, *bullet.rect.center)
            else:
                bullet.image, bullet.rect = self.rot_around_center(bullet.image, self.angle, *bullet.rect.center)
            screen.blit(bullet.image, bullet.rect)


class Shotgun(pygame.sprite.Sprite):
    def __init__(self, img: pygame.image, shift: tuple, owner, damage, radius):
        super(Shotgun, self).__init__()
        self.shift_x, self.shift_y = shift
        self.image = self.source_img = img
        self.rect = pygame.rect.Rect(owner.rect.center[0] - self.shift_x,
                                     owner.rect.center[1] - self.shift_y,
                                     self.image.get_width(), self.image.get_height())
        self.last_image = None
        self.angle = None

        self.adjacent_cathet = 0
        self.opposite_cathet = 0
        self.owner = owner
        self.damage = damage
        self.radius = radius
        self.angle = 65
        self.angle_status = 0  # 0 - остаётся, 1 - наклоняется к полу, 2 - поднимается от пола
        self.next_angle_iter_tick = 0
        self.old_owner_rect = self.owner.rect

    def rot_around_center(self, image, angle, x, y):
        rotated_image = pygame.transform.rotate(image, angle)
        new_rect = rotated_image.get_rect(center=image.get_rect(center=(x, y)).center)
        return rotated_image, new_rect

    def render(self, ticks):
        move_x, move_y = self.old_owner_rect.x - self.owner.rect.x, self.old_owner_rect.y - self.owner.rect.y
        self.rect.x -= move_x
        self.rect.y -= move_y
        self.old_owner_rect = self.owner.rect

        if pygame.mouse.get_focused():
            mouse_pos = pygame.mouse.get_pos()
            center_coords = knight_main.rect.center

            self.adjacent_cathet = sqrt((mouse_pos[0] - center_coords[0]) ** 2)
            self.opposite_cathet = sqrt((mouse_pos[1] - center_coords[1]) ** 2)

            if self.angle_status != 0 and ticks >= self.next_angle_iter_tick:
                self.next_angle_iter_tick = ticks + 1
                if self.angle_status == 1:
                    self.angle -= 2
                    if self.angle <= 0:
                        self.angle_status = 2
                elif self.angle_status == 2:
                    self.angle += 2
                    if self.angle >= 65:
                        self.angle_status = 0

            if mouse_pos[0] > center_coords[0]:  # если курсор правее персонажа
                if knight_main.direction_of_vision['Left']:
                    self.rect.x += 40
                if knight_main.dx == 0 and knight_main.dy == 0:  # если персонаж стоит на месте
                    knight_main.image = knight_main.normal_static_frames[knight_main.cur_frame]
                else:
                    knight_main.image = knight_main.normal_frames[knight_main.cur_frame]

                self.image, self.rect = self.rot_around_center(self.source_img, self.angle, *self.rect.center)

                knight_main.direction_of_vision['Right'], \
                    knight_main.direction_of_vision['Left'] = True, False

            else:
                if knight_main.direction_of_vision['Right']:
                    self.rect.x -= 40
                if knight_main.dx == 0 and knight_main.dy == 0:
                    knight_main.image = knight_main.reversed_static_frames[knight_main.cur_frame]
                else:
                    knight_main.image = knight_main.reversed_frames[knight_main.cur_frame]

                self.image, self.rect = self.rot_around_center(self.source_img, self.angle, *self.rect.center)
                self.image = pygame.transform.flip(self.image, True, False)
                knight_main.direction_of_vision['Right'], \
                    knight_main.direction_of_vision['Left'] = False, True

        else:
            if knight_main.direction_of_vision['Right']:
                self.image = self.source_img
            else:
                self.image = pygame.transform.flip(self.source_img, True, False)
        screen.blit(self.image, self.rect)

    def enemy_render(self, rect: pygame.Rect, ticks):
        center_coords = rect.center
        x, y = knight_main.rect.center
        self.adjacent_cathet = sqrt((x - center_coords[0]) ** 2)
        self.opposite_cathet = sqrt((y - center_coords[1]) ** 2)

        if self.angle_status != 0 and ticks >= self.next_angle_iter_tick:
            self.next_angle_iter_tick = ticks + 1
            if self.angle_status == 1:
                self.angle -= 2
                if self.angle <= 0:
                    self.angle_status = 2
            elif self.angle_status == 2:
                self.angle += 2
                if self.angle >= 65:
                    self.angle_status = 0

        if x > center_coords[0]:  # если курсор правее персонажа
            self.image, self.rect = self.rot_around_center(self.source_img, self.angle, *center_coords)
        else:
            self.image, self.rect = self.rot_around_center(self.source_img, self.angle, *center_coords)
            self.image = pygame.transform.flip(self.image, True, False)

        screen.blit(self.image, self.rect)

    def shoot(self, ticks):
        x, y = self.rect.center
        damage_zone = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)
        self.angle_status = 1
        damage_zones.add(DamageZone((x, y), self.radius, ticks, 200))
        for enemy in level_mode.levels[level_mode.current_level].enemies:
            if damage_zone.colliderect(enemy.rect) and type(enemy) != type(self.owner):

                distance = (sqrt((x - enemy.rect.center[0]) ** 2 + (y - enemy.rect.center[1]) ** 2) + 1)
                damage = self.damage * (self.radius - distance) / self.radius

                if damage > 0:
                    enemy.hp -= damage
                    create_particles(enemy.rect.center)
                    print(damage)

        if damage_zone.colliderect(knight_main.rect) and knight_main != self.owner:

            distance = (sqrt((x - knight_main.rect.center[0]) ** 2 + (y - knight_main.rect.center[1]) ** 2) + 1)
            damage = self.damage * (self.radius - distance) / self.radius

            if damage > 0:
                knight_main.hp -= damage
                create_particles(knight_main.rect.center)
                print(damage)

    def enemy_shoot(self, ticks):
        self.shoot(ticks)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, right, top, average_v, adjacent_cathet, opposite_cathet, owner, damage):
        super(Bullet, self).__init__(bullets)

        self.right = right  # направления полета пули
        self.top = top
        self.owner = owner
        self.damage = damage
        self.vec_x = adjacent_cathet
        self.vec_y = opposite_cathet

        self.average_v = average_v

    def update(self):
        vx, vy = None, None
        try:
            coeff = max(abs(self.vec_x), abs(self.vec_y)) / min(abs(self.vec_x), abs(self.vec_y))

            vx, vy = self.average_v * coeff, self.average_v

            if vx > self.average_v:
                vx = self.average_v
                vy = self.average_v / coeff

            if self.vec_x < self.vec_y:
                vx, vy = vy, vx

        except ZeroDivisionError:
            if not self.vec_y:
                vx, vy = self.average_v, 0
            elif not self.vec_x:
                vx, vy = 0, self.average_v

        if self.right:
            self.rect.x += vx
        else:
            self.rect.x -= vx
        if self.top:
            self.rect.y -= vy
        else:
            self.rect.y += vy

        if self.rect.collidelist(level_mode.levels[level_mode.current_level].not_free_rects) != -1:
            self.kill()

        for enemy in level_mode.levels[level_mode.current_level].enemies:
            if pygame.sprite.collide_mask(enemy, self) and type(enemy) != type(self.owner):
                enemy.hp -= self.damage
                create_particles(enemy.rect.center)
                self.kill()
                break
        if pygame.sprite.collide_mask(knight_main, self) and self.owner != knight_main:
            knight_main.hp -= self.damage
            create_particles(knight_main.rect.center)
            self.kill()


class Particle(pygame.sprite.Sprite):
    fire = [load_image("blood.png", -1)]

    for scale in (10, 13, 16):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))
    fire.pop(0)
    for e in fire:
        print(e.get_height())

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.image = choice(self.fire)
        self.rect = self.image.get_rect()

        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos

        self.gravity = GRAVITY

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        check_rect = pygame.Rect(self.rect.x + self.rect.w + 1, self.rect.y + self.rect.h + 1, 1, 1)
        if not check_rect.colliderect(screen_rect):
            self.kill()


class DamageZone(pygame.sprite.Sprite):
    def __init__(self, pos, radius, tick, lifetime):
        super().__init__(all_sprites)
        self.image = pygame.transform.scale(load_image('hammer_shot.png', -1), (radius, radius))
        self.rect = pygame.rect.Rect(pos[0] - radius // 2, pos[1] - radius // 2, radius, radius)
        self.spawn_tick = tick
        self.death_tick = tick + lifetime

    def update(self, ticks):
        if ticks > self.death_tick:
            self.kill()


def create_particles(position):
    particle_count = 5
    numbers = range(-5, 6)
    for _ in range(particle_count):
        particles.add(Particle(position, choice(numbers), choice(numbers)))


class ModeWithLevels:
    def __init__(self, knight: Knight, current_level):
        self.knight = knight
        self.levels = [[None] * 9]
        self.current_level = current_level  # зависит от нажатой кнопки с номером уровня

    def render(self):
        self.levels[self.current_level].render()


class HardcoreMode:
    pass


start_screen()
if __name__ == '__main__':
    while not do_exit:
        all_sprites = pygame.sprite.Group()
        enemies = pygame.sprite.Group()  # это пока будет тут, потом пойдет в класс режима игры
        bullets = pygame.sprite.Group()
        particles = pygame.sprite.Group()
        damage_zones = pygame.sprite.Group()
        fullscreen = True
        running = True
        knight_main = Knight((60, 60), 5, load_image('knight.png'), 1)  # выбор оружия выполняется здесь
        level_mode = ModeWithLevels(knight_main, current_level)  # в дальнейшем это будет вызываться при
        # нажатии на экране кнопки "Режим уровней"
        level_mode.levels = [Level('maps/Level1.tmx', [((19, 4), 1), ((5, 14), 1), ((28, 19), 0)], [21]),
                             Level('maps/Level2.tmx', [((13, 19), 1), ((27, 12), 1), ((5, 20), 0)], [21]),
                             Level('maps/Level3.tmx', [((10, 14), 1), ((18, 10), 1), ((30, 12), 0)], [21]),
                             Level('maps/Level4.tmx', [((14, 21), 1), ((26, 9), 1), ((6, 26), 0), ((32, 9), 0)], [21]),
                             Level('maps/Level5.tmx', [((10, 6), 1), ((31, 5), 1), ((32, 11), 1), ((17, 29), 0)], [21]),
                             Level('maps/Level6.tmx', [((2, 26), 0), ((10, 27), 0), ((29, 3), 0), ((19, 15), 1)], [21]),
                             Level('maps/Level7.tmx', [((8, 27), 0), ((23, 2), 0), ((27, 17), 1),
                                                       ((33, 6), 1), ((33, 27), 1), ((12, 2), 0)], [13, 14]),
                             Level('maps/Level8.tmx', [((13, 12), 1), ((13, 19), 1), ((27, 12), 1),
                                                       ((27, 19), 1), ((20, 29), 0), ((34, 16), 0)], [13, 14]),
                             Level('maps/Level9.tmx', [((28, 6), 0), ((34, 10), 1), ((10, 25), 0),
                                                       ((6, 21), 1), ((25, 15), 0), ((26, 20), 1)], [13, 14])]

        tile_size = level_mode.levels[current_level].map.tilewidth, \
                    level_mode.levels[current_level].map.tileheight
        level_mode.levels[current_level].spawn_enemies(tile_size)
        for e in level_mode.levels[current_level].enemies:
            e.show_gun(e.gun_id)

        while running:
            if not REBOOT_GAME:
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT:
                        running = False
                        do_exit = True
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                        print(level_mode.levels[level_mode.current_level].get_cell(event.pos))
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                        if fullscreen:
                            screen = pygame.display.set_mode(size)
                        else:
                            screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
                        fullscreen = not fullscreen
                    knight_main.update(event, ticks)

                knight_main.move()
                knight_main.do_animate()

                bullets.update()
                bullets.draw(screen)

                damage_zones.update(ticks)

                knight_main.render(ticks)

                particles.update()

                level_mode.levels[current_level].enemies_sprites.draw(screen)
                for e in level_mode.levels[current_level].enemies:
                    e.render(ticks)

                pygame.display.update()
                level_mode.render()
                all_sprites.draw(screen)
                particles.draw(screen)
                damage_zones.draw(screen)

                ticks += 1
                animation_frequency += 1

                level_mode.levels[current_level].enemies_sprites.update(ticks)
                clock.tick(fps)
            else:
                endgame_screen()
                continue
    pygame.quit()
