import os
import sys

import pygame
import pytmx
import pygame_gui

from random import choice, randint
from copy import copy
from math import sqrt, degrees, atan, inf

from constants import *
from UI import manager, show_level_btns, hide_level_btns, show_main_btns, hide_main_btns, \
    show_endgame_btns, hide_endgame_btns, to_beginning, to_exit, \
    level_mode_btn, hardcore_mode_btn, exit_button1, back_btn, level_btns, esc_window, reset_btn

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
    global running, current_level, do_exit, mode, current_mode
    pygame.mixer.music.load('data/music/start_music.mp3')
    pygame.mixer.music.play(-1)

    show_main_btns()
    hide_level_btns()
    hide_endgame_btns()
    star_image = pygame.transform.scale(load_image('star.png', -1), (round(size[0] / 37.273), round(size[1] / 29.09)))
    show_stars = False
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
                        mode = 0
                        show_stars = True
                    if event.ui_element == reset_btn:
                        with open('scores/levels_score.txt', 'w') as file1:
                            file1.write('')
                    if event.ui_element == back_btn:
                        hide_level_btns()
                        show_main_btns()
                        show_stars = False
                    if event.ui_element in level_btns and event.ui_element != back_btn and \
                            event.ui_element != reset_btn:
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
                    if event.ui_element == hardcore_mode_btn:
                        hide_main_btns()
                        mode = 1
                        running = False
                        do_exit = False
                        return

            manager.process_events(event)
        manager.update(time_delta)
        screen.blit(pygame.transform.scale(load_image('background.png'), (w, h)), (0, 0))
        if mode == 0 and show_stars:
            with open('scores/levels_score.txt', 'r') as file:
                scores = {}
                for string in file.readlines():
                    key, val = string.strip().split(':')
                    scores[key] = val
            for key, val in scores.items():
                key, val = int(key), int(val)
                for i in range(val):
                    screen.blit(star_image, (
                        round(size[0] / 17.57) + max((key % 3), 0) * round(size[0] / 12.3) +
                        max((key % 3), 0) * (round(size[0] / 5.857) - (
                                round(size[0] / 17.57) + round(size[0] / 12.3))) - star_image.get_width(),
                        (round(size[1] / 3.2) + round(size[1] / 9.6) * (key // 3) + (round(size[1] / 2.2857) - (
                                round(size[1] / 3.2) + round(size[1] / 9.6))) * (
                                 key // 3)) + star_image.get_height() * i))
        if not show_stars:
            try:
                with open('scores/hardcore_score.txt', 'r') as file:
                    best_score = int(file.read().strip())
            except ValueError:
                best_score = 0
            font1 = pygame.font.SysFont('impact', round(size[0] / 39.6774), bold=False)
            hardcore_score_txt = font1.render(f'Ваш рекорд: {best_score}', True, (51, 209, 255))
            screen.blit(hardcore_score_txt, (
                round(size[0] / 3.6936), round(size[1] / 1.2307), round(size[0] / 5.8571), round(size[1] / 32)))
        manager.draw_ui(screen)
        pygame.display.flip()
        clock.tick(fps)


def endgame_screen():
    global running, do_exit, victory, reboot_game, knight_main, MAX_HP
    if mode == 0 and victory:
        hp_left_in_percents = (knight_main.hp / MAX_HP) * 100
        if hp_left_in_percents > 80:
            stars = '3'
        elif 50 < hp_left_in_percents < 80:
            stars = '2'
        else:
            stars = '1'
        with open('scores/levels_score.txt', 'r') as file:
            scores = {}
            for string in file.readlines():
                key, val = string.strip().split(':')
                scores[key] = val
        with open('scores/levels_score.txt', 'w') as file:
            if int(scores.get(str(current_level), 0)) < int(stars):
                scores[str(current_level)] = stars
            scores = sorted(scores.items())
            for key, val in scores:
                file.write('{}:{}\n'.format(key, val))

    if mode == 1 and not victory:
        if current_mode.current_score > current_mode.best_score:
            with open('scores/hardcore_score.txt', 'w') as file:
                file.write(str(round(current_mode.current_score)))

    if not victory:
        pygame.mixer.music.fadeout(1000)
        pygame.mixer.music.load('data/music/end_music.mp3')
        pygame.mixer.music.play(1)
    elif victory and mode == 0:
        pygame.mixer.music.fadeout(1000)
        pygame.mixer.music.load('data/music/win_music.mp3')
        pygame.mixer.music.play(1)
    if not victory or (victory and mode == 0):
        hide_level_btns()
        hide_main_btns()
        show_endgame_btns()
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
                            reboot_game = False
                            start_screen()
                            return
                        if event.ui_element == to_exit:
                            do_exit = True
                            running = False
                manager.process_events(event)
            manager.update(time_delta)
            if victory:
                screen.blit(pygame.transform.scale(load_image('win_screen.png'), (w, h)), (0, 0))
            else:
                screen.blit(pygame.transform.scale(load_image('gameover_screen.jpg'), (w, h)), (0, 0))
            manager.draw_ui(screen)
            pygame.display.flip()
            clock.tick(fps)
    else:
        reboot_game = False
        running = True
        current_mode.next_level()
        current_mode.levels[current_level].spawn_enemies(tile_size)
        for e in current_mode.levels[current_level].enemies:
            e.show_gun(e.gun_id)
        hp_left = knight_main.hp
        knight_main.kill()
        knight_main = Knight((50, 50), hp_left, load_image('knight.png'), 1)
        knight_main.hp_bar = HpBar(knight_main, MAX_HP)


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
        self.sheet = pygame.transform.scale(self.sheet, (round(size[0] / 5.125), round(size[1] / 4)))
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
        self.hp_bar = HpBar(self, self.hp)

        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False

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
        global running, victory, reboot_game
        if ev.type == pygame.KEYDOWN:
            if (ev.key == pygame.K_LEFT or ev.key == pygame.K_a) and self.dx >= 0:
                self.dx -= self.v
                self.left_pressed = True
            elif (ev.key == pygame.K_RIGHT or ev.key == pygame.K_d) and self.dx <= 0:
                self.dx += self.v
                self.right_pressed = True
            elif (ev.key == pygame.K_UP or ev.key == pygame.K_w) and self.dy >= 0:
                self.dy -= self.v
                self.up_pressed = True
            elif (ev.key == pygame.K_DOWN or ev.key == pygame.K_s) and self.dy <= 0:
                self.dy += self.v
                self.down_pressed = True
        if ev.type == pygame.KEYUP:
            if (ev.key == pygame.K_LEFT or ev.key == pygame.K_a) and self.dx <= 0 and self.left_pressed:
                self.dx += self.v
                self.left_pressed = False
            elif (ev.key == pygame.K_RIGHT or ev.key == pygame.K_d) and self.dx >= 0 and self.right_pressed:
                self.dx -= self.v
                self.right_pressed = False
            elif (ev.key == pygame.K_UP or ev.key == pygame.K_w) and self.dy <= 0 and self.up_pressed:
                self.dy += self.v
                self.up_pressed = False
            elif (ev.key == pygame.K_DOWN or ev.key == pygame.K_s) and self.dy >= 0 and self.down_pressed:
                self.dy -= self.v
                self.down_pressed = False
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if mode == 1:
                if self.gun.angle_status == 0:
                    self.gun.shoot(ticks)
            else:
                self.gun.shoot(ticks)
        if self.hp <= 0:
            self.kill()
            reboot_game = True
            victory = False

    def render(self, ticks):
        if not reboot_game:
            self.gun.render(ticks)
            self.hp_bar.render(screen)

    def move(self):
        self.next_pos = self.pos[0] + self.dx, self.pos[1] + self.dy
        if self.is_free(self.dx, 0):
            self.rect = self.rect.move(self.dx, 0)
            self.pos = self.next_pos
        if self.is_free(0, self.dy):
            self.rect = self.rect.move(0, self.dy)
            self.pos = self.next_pos

    def is_free(self, dx, dy):  # метод, который будет проверять клетку в которую мы пытаемся пойти,
        # если там препятствие - вернет False, иначе True
        newrect = self.rect.move(dx, dy)
        if newrect.collidelist(current_mode.levels[current_mode.current_level].not_free_rects) != -1:
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
        self.guns = [
            Gun(pygame.transform.scale(load_image('Aurora.png'), (round(size[0] / 20.5), round(size[1] / 21.33))),
                (round(size[0] / 246), round(size[1] / 192)), 0, 10, self, 2),
            # размеры, сдвиг относительно центра перса, тип патронов,
            # средняя скорость пуль, владелец (для пуль), урон
            # у дробовика размеры, сдвиг, владелец, урон, радиус
            Shotgun(pygame.transform.scale(load_image('hammer.jpg', -1),
                                           (round(size[0] / 24.6), round(size[1] / 32))),
                    (round(size[0] / 123), round(size[1] / 192)), self, 10, 100)]
        self.gun = self.guns[gun_id]


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos: tuple, hp, image: pygame.image, gun_id):
        super(Enemy, self).__init__(all_sprites, current_mode.levels[current_level].enemies_sprites)
        self.rect = image.get_rect()
        self.rect.x, self.rect.y = current_mode.levels[current_mode.current_level].get_left_top_pixel_of_cell(pos)
        self.pos = pos
        self.hp = hp
        self.next_shot = 300
        self.next_move = 100
        self.n_ticks_shoot = 0
        self.n_ticks_move = 0
        self.n_ticks_effect = 0

        self.reloading = False
        self.moving = False
        self.v = round(size[0] / 41), round(size[1] / 32)
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
        self.hp_bar = HpBar(self, self.hp)

    def show_gun(self, gun_id):
        self.guns = [
            Gun(pygame.transform.scale(load_image('Aurora.png'), (round(size[0] / 30.75), round(size[1] / 32))),
                (round(size[0] / 246), round(size[1] / 192)),
                0, 10, self, 35),
            # размеры, сдвиг относительно центра перса, тип патронов,
            # средняя скорость пуль, владелец (для пуль), урон
            # у дробовика размеры, сдвиг, владелец, урон, радиус
            Shotgun(pygame.transform.scale(load_image('hammer.jpg', -1),
                                           (round(size[0] / 35.143), round(size[1] / 38.4))),
                    (round(size[0] / 61.5), -round(size[1] / 192)), self, 60, 100)]
        self.gun = self.guns[gun_id]

    def shoot(self, ticks):
        self.gun.enemy_shoot(ticks)

    def update(self, n_ticks):
        global ticks, victory, reboot_game
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
            current_mode.levels[current_level].enemies.remove(self)
            self.gun.kill()
            self.kill()
            if not current_mode.levels[current_level].enemies:
                victory = True
                reboot_game = True

        r0, c0 = current_mode.levels[current_level].get_cell((self.rect.x, self.rect.y))
        r, c = current_mode.levels[current_level].get_cell((knight_main.rect.x, knight_main.rect.y))

        width = current_mode.levels[current_level].width
        height = current_mode.levels[current_level].height
        if self.find_path(r0, c0, r, c):
            for dr, dc in ((0, -1), (-1, 0), (0, 1), (1, 0)):
                next_r, next_c = r0 + dr, c0 + dc
                if (0 <= next_r < height and 0 <= next_c < width and
                        self.distances[next_r][next_c] == self.distances[r0][c0] + 1):
                    if ticks - self.n_ticks_move > self.next_move:
                        self.dx, self.dy = 0.0625 * (self.v[0] * dr), 0.0625 * (self.v[1] * dc)
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
        width = current_mode.levels[current_level].width
        height = current_mode.levels[current_level].height
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
                            current_mode.levels[current_level].map_arr[next_r][next_c] != -1 and
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
        self.hp_bar.render(screen)


class EnemyShotguner(Enemy):
    def __init__(self, pos: tuple, hp, image, field, gun_id):
        super(EnemyShotguner, self).__init__(pos, hp, image, gun_id)
        self.field = field


class EnemyRifler(Enemy):
    def __init__(self, pos: tuple, hp, image, field, gun_id):
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
        tile_size = round(size[0] / 41), round(size[1] / 32)
        column = x // tile_size[0]
        row = y // tile_size[1]
        if 0 <= row < self.height and 0 <= column < self.width:
            return column, row
        return None

    def generate_rects_and_map_array(self):
        rects = []
        map_arr = []
        tile_size = round(size[0] / 41), round(size[1] / 32)
        for i in range(self.map.width):
            line = []
            for j in range(self.map.height):
                if self.map.tiledgidmap[self.map.get_tile_gid(i, j, 0)] in self.not_free_tiles:
                    rect = pygame.Rect(i * tile_size[0], j * tile_size[1],
                                       tile_size[0], tile_size[1])
                    rects.append(rect)
                    line.append(-1)
                else:
                    line.append(0)
            map_arr.append(line)
        return rects, map_arr

    def spawn_enemies(self, tile_size):
        e = []
        if current_level in (0, 1, 2):
            image1 = load_image('snow_enemy1.png')
            image2 = load_image('snow_enemy2.png')
        elif current_level in (3, 4, 5):
            image1 = load_image('desert_enemy1.png')
            image2 = load_image('desert_enemy2.png')
        elif current_level in (6, 7, 8):
            image1 = load_image('alien_enemy1.png')
            image2 = load_image('alien_enemy2.png')
        else:
            image1 = image2 = load_image('lava_enemy.png')
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
            tile_size = round(size[0] / 41), round(size[1] / 32)
            pos = tile_size[0] * enemy[0][0], tile_size[1] * enemy[0][1]
            if 0 <= enemy[0][0] < self.map.width and 0 <= enemy[0][1] < self.map.height:
                if enemy[1] == 1:
                    e.append(EnemyRifler(pos, 10, image1, 'тут будет передача поля', 0))
                if enemy[1] == 0:
                    e.append(EnemyShotguner(pos, 10, image2, 'тут будет передача поля', 1))
                self.enemies_sprites.add(e[-1])
        self.enemies = e

    def render(self):
        for x in range(self.width):
            for y in range(self.height):
                image = self.map.get_tile_image(x, y, 0)
                tile_size = round(size[0] / 41), round(size[1] / 32)
                image = pygame.transform.scale(image, tile_size)
                screen.blit(image, (x * tile_size[0], y * tile_size[1]))

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
                self.last_image = self.image

                knight_main.direction_of_vision['Right'], \
                knight_main.direction_of_vision['Left'] = True, False

            else:
                if knight_main.dx == 0 and knight_main.dy == 0:
                    knight_main.image = knight_main.reversed_static_frames[knight_main.cur_frame]
                else:
                    knight_main.image = knight_main.reversed_frames[knight_main.cur_frame]

                self.image, self.rect = self.rot_around_center(self.source_img, self.angle, *self.rect.center)
                self.image = pygame.transform.flip(self.image, True, False)
                self.last_image = self.image
                if knight_main.direction_of_vision['Right']:
                    self.rect.x -= 40
                knight_main.direction_of_vision['Right'], \
                knight_main.direction_of_vision['Left'] = False, True

        else:
            if knight_main.direction_of_vision['Right']:
                self.image = self.source_img
            else:
                self.image = pygame.transform.flip(self.source_img, True, False)
                if knight_main.direction_of_vision['Right']:
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
            self.last_image = self.image
        else:
            self.image, self.rect = self.rot_around_center(self.source_img, self.angle,
                                                           *(center_coords[0], center_coords[1] + 5))
            self.image = pygame.transform.flip(self.image, True, False)
            self.last_image = self.image

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
                self.last_image = self.image

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
                self.last_image = self.image
                knight_main.direction_of_vision['Right'], \
                knight_main.direction_of_vision['Left'] = False, True

        else:
            if knight_main.direction_of_vision['Right']:
                self.image = self.source_img
            else:
                self.image = pygame.transform.flip(self.source_img, True, False)
        screen.blit(self.image, self.rect)

    def enemy_render(self, rect: pygame.Rect, ticks):
        center_coords = rect.center[0], rect.center[1] - self.shift_y
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
        damage_zones.add(DamageZone((x, y), self.radius, ticks, 100))
        for enemy in current_mode.levels[current_mode.current_level].enemies:
            if damage_zone.colliderect(enemy.rect) and type(self.owner) != EnemyRifler and \
                    type(self.owner) != EnemyShotguner:

                distance = (sqrt((x - enemy.rect.center[0]) ** 2 + (y - enemy.rect.center[1]) ** 2) + 1)
                damage = self.damage * (self.radius - distance) / self.radius

                if damage > 0:
                    enemy.hp -= damage
                    create_particles(enemy.rect.center)
                    if self.owner == knight_main and mode == 1:
                        current_mode.current_score += damage
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
        global mode
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

        if self.rect.collidelist(current_mode.levels[current_mode.current_level].not_free_rects) != -1:
            self.kill()

        for enemy in current_mode.levels[current_mode.current_level].enemies:
            if pygame.sprite.collide_mask(enemy, self) and type(self.owner) != EnemyRifler and \
                    type(self.owner) != EnemyShotguner:
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
        super().__init__()
        self.image = pygame.transform.scale(load_image('hammer_shot.png', -1), (radius, radius))
        self.rect = pygame.rect.Rect(pos[0] - radius // 2, pos[1] - radius // 2, radius, radius)
        self.spawn_tick = tick
        self.death_tick = tick + lifetime

    def update(self, ticks):
        if ticks > self.death_tick:
            self.kill()


class HpBar:
    def __init__(self, owner, max_hp):
        self.owner = owner
        self.max_hp = max_hp

    def render(self, screen):
        red_rect = pygame.Rect(self.owner.rect.x, self.owner.rect.y - 20, self.owner.rect.w, 5)
        green_rect = pygame.Rect(self.owner.rect.x, self.owner.rect.y - 20,
                                 self.owner.rect.w * self.owner.hp // self.max_hp, 5)

        pygame.draw.rect(screen, 'red', red_rect)
        pygame.draw.rect(screen, 'green', green_rect)


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
    def __init__(self, knight: Knight):
        self.knight = knight
        self.levels = [[None] * 10]
        self.current_level = None
        self.not_first_level = False
        self.current_score = 0
        try:
            with open('scores/hardcore_score.txt', 'r') as file:
                self.best_score = int(file.read().strip())
        except ValueError:
            self.best_score = 0

    def render(self):
        self.levels[self.current_level].render()

    def next_level(self):
        global current_level
        self.current_level = current_level = randint(0, 9)
        self.not_first_level = True


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
        time_delta = clock.tick(fps) / 1000.0
        if mode == 0:
            knight_main = Knight((50, 50), MAX_HP, load_image('knight.png'), 0)  # выбор оружия выполняется здесь
            current_mode = ModeWithLevels(knight_main, current_level)  # в дальнейшем это будет вызываться при
            # нажатии на экране кнопки "Режим уровней"
            current_mode.levels = [Level('maps/Level1.tmx', [((19, 4), 0), ((5, 14), 0), ((28, 19), 1)], [21]),
                                   Level('maps/Level2.tmx', [((13, 19), 0), ((27, 12), 0), ((5, 20), 1)], [21]),
                                   Level('maps/Level3.tmx', [((10, 14), 0), ((18, 10), 0), ((30, 12), 1)], [21]),
                                   Level('maps/Level4.tmx', [((14, 21), 0), ((26, 9), 0), ((6, 26), 1), ((32, 9), 1)],
                                         [21]),
                                   Level('maps/Level5.tmx', [((10, 6), 0), ((31, 5), 0), ((32, 11), 0), ((17, 29), 1)],
                                         [21]),
                                   Level('maps/Level6.tmx', [((2, 26), 1), ((10, 27), 1), ((29, 3), 1), ((19, 15), 0)],
                                         [21]),
                                   Level('maps/Level7.tmx', [((8, 27), 1), ((23, 2), 1), ((27, 17), 0),
                                                             ((33, 6), 0), ((33, 27), 0), ((12, 2), 1)], [13, 14]),
                                   Level('maps/Level8.tmx', [((13, 12), 0), ((13, 19), 0), ((27, 12), 0),
                                                             ((27, 19), 0), ((20, 29), 1), ((34, 16), 1)], [13, 14]),
                                   Level('maps/Level9.tmx', [((28, 6), 1), ((34, 10), 0), ((10, 25), 1),
                                                             ((6, 21), 0), ((25, 15), 1), ((26, 20), 0)], [13, 14])]

            tile_size = round(size[0] / 41), round(size[1] / 32)
            current_mode.levels[current_level].spawn_enemies(tile_size)
            for e in current_mode.levels[current_level].enemies:
                e.show_gun(e.gun_id)
        else:
            knight_main = Knight((50, 50), MAX_HP, load_image('knight.png'), 1)
            current_mode = HardcoreMode(knight_main)
            current_mode.next_level()
            current_mode.levels = [Level('maps/Hardcore_room1.tmx', [((11, 20), 1), ((21, 10), 1),
                                                                     ((30, 20), 1), ((3, 28), 1),
                                                                     ((29, 28), 1), ((5, 7), 0),
                                                                     ((7, 6), 0)], [21]),
                                   Level('maps/Hardcore_room2.tmx', [((18, 6), 1), ((2, 26), 1),
                                                                     ((13, 25), 1), ((16, 15), 1),
                                                                     ((6, 6), 0), ((10, 3), 0),
                                                                     ((32, 25), 1)], [21]),
                                   Level('maps/Hardcore_room3.tmx', [((15, 11), 1), ((26, 9), 1),
                                                                     ((20, 16), 1), ((26, 25), 1), ((13, 27), 0)],
                                         [21]),
                                   Level('maps/Hardcore_room4.tmx', [((10, 20), 1), ((30, 22), 1),
                                                                     ((3, 29), 1), ((37, 5), 1),
                                                                     ((6, 24), 0), ((9, 2), 0)], [21]),
                                   Level('maps/Hardcore_room5.tmx', [((16, 17), 0), ((26, 17), 1),
                                                                     ((2, 16), 1), ((38, 6), 1),
                                                                     ((32, 29), 1), ((9, 29), 0)], [21]),
                                   Level('maps/Hardcore_room6.tmx', [((20, 15), 1), ((8, 16), 1),
                                                                     ((33, 13), 1), ((36, 2), 1),
                                                                     ((21, 7), 1), ((6, 10), 0), ((29, 29), 0)], [21]),
                                   Level('maps/Hardcore_room7.tmx', [((2, 8), 0), ((21, 3), 0), ((37, 28), 1),
                                                                     ((3, 28), 1), ((7, 12), 1), ((31, 17), 0)],
                                         [13, 14]),
                                   Level('maps/Hardcore_room8.tmx', [((8, 5), 0), ((25, 5), 1), ((20, 17), 1),
                                                                     ((3, 28), 1), ((37, 28), 0), ((32, 13), 0),
                                                                     ((24, 13), 1)], [13, 14]),
                                   Level('maps/Hardcore_room9.tmx', [((20, 12), 1), ((4, 16), 1), ((34, 3), 1),
                                                                     ((20, 19), 0), ((14, 25), 0), ((26, 20), 1)],
                                         [13, 14]),
                                   Level('maps/Hardcore_room10.tmx', [((34, 15), 1),
                                                                      ((7, 15), 1), ((30, 5), 1),
                                                                      ((6, 5), 1), ((5, 28), 1)], [13])]
            tile_size = round(size[0] / 41), round(size[1] / 32)
            current_mode.levels[current_level].spawn_enemies(tile_size)
            for e in current_mode.levels[current_level].enemies:
                e.show_gun(e.gun_id)
        while running:
            if not reboot_game:
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT:
                        running = False
                        do_exit = True
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                        print(current_mode.levels[current_mode.current_level].get_cell(event.pos))
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                        if fullscreen:
                            screen = pygame.display.set_mode(size)
                        else:
                            screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
                        fullscreen = not fullscreen
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        if not esc_win_showed:
                            esc_window = pygame_gui.windows.ui_confirmation_dialog.UIConfirmationDialog(
                                pygame.Rect(215, 280, 800, 400),
                                manager, action_long_desc='Вернуться в главное меню?',
                                window_title='Выход в меню',
                                action_short_name='Выйти',
                                visible=False)
                            esc_window.show()
                            esc_win_showed = True
                        else:
                            esc_window.kill()
                            esc_win_showed = False
                    if event.type == pygame.USEREVENT:
                        if event.ui_element == esc_window:
                            if event.user_type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                                reboot_game = False
                                if mode == 1:
                                    if current_mode.current_score > current_mode.best_score:
                                        with open('scores/hardcore_score.txt', 'w') as file:
                                            file.write(str(round(current_mode.current_score)))
                                start_screen()
                            if event.user_type == pygame_gui.UI_WINDOW_CLOSE:
                                esc_win_showed = False
                                esc_window.hide()
                    knight_main.update(event, ticks)
                    manager.process_events(event)
                manager.draw_ui(screen)
                manager.update(time_delta)
                if not esc_win_showed:
                    knight_main.move()
                    knight_main.do_animate()

                    bullets.update()
                    bullets.draw(screen)

                    damage_zones.update(ticks)
                    damage_zones.draw(screen)

                    knight_main.render(ticks)

                    particles.update()

                    current_mode.levels[current_level].enemies_sprites.draw(screen)
                    for e in current_mode.levels[current_level].enemies:
                        e.render(ticks)

                    ticks += 1
                    animation_frequency += 1

                    current_mode.levels[current_level].enemies_sprites.update(ticks)
                    clock.tick(fps)

                pygame.display.update()
                current_mode.render()

                all_sprites.draw(screen)
                particles.draw(screen)
            else:
                endgame_screen()
                continue
    pygame.quit()
