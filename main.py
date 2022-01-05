import os
import sys

import pygame
import pytmx
import pygame_gui

from copy import copy
from math import sqrt, degrees, atan

from constants import *
from UI import manager, show_level_btns, hide_level_btns, show_main_btns, hide_main_btns, \
    level_mode_btn, hardcore_mode_btn, back_btn, level_btns

pygame.init()
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Soul Knight')
clock = pygame.time.Clock()


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
    global running, current_level
    hide_level_btns()
    while running:
        events = pygame.event.get()
        time_delta = clock.tick(fps) / 1000.0
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == level_mode_btn:
                        hide_main_btns()
                        show_level_btns()
                    if event.ui_element == back_btn:
                        hide_level_btns()
                        show_main_btns()
                    if event.ui_element in level_btns and event.ui_element != back_btn:
                        current_level = int(event.ui_element.text[-1]) - 1
                        return
            manager.process_events(event)
        manager.update(time_delta)
        screen.blit(pygame.transform.scale(load_image('background.png'), (w, h)), (0, 0))
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
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            self.gun.shoot(self.gun.id_bullets)

    def render(self):
        self.show_gun(self.gun_id)
        self.gun.render()

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
        self.guns = [Gun(pygame.transform.scale(load_image('Aurora.png'), (60, 45)), (5, 5), 0, 10),
                     # размеры, сдвиг относительно центра перса, тип патронов, средняя скорость пуль
                     Gun(pygame.transform.scale(load_image('Gas_blaster.png', -1), (50, 20)), (0, -5), 0, 10)]
        self.gun = self.guns[gun_id]


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos: tuple, hp, image: pygame.image, gun_id):
        super(Enemy, self).__init__(all_sprites, enemies)
        self.rect = image.get_rect()
        self.rect.x, self.rect.y = level_mode.levels[level_mode.current_level].get_left_top_pixel_of_cell(pos)
        self.pos = pos
        self.hp = hp
        self.next_shot = 200
        self.next_move = 0
        self.n_ticks = 0
        self.reloading = False
        self.effect = None
        self.effect_end = 0
        self.image = image
        self.guns = None
        self.gun = None
        self.gun_id = gun_id

    def show_gun(self, gun_id):
        self.guns = [Gun(pygame.transform.scale(load_image('Aurora.png'), (60, 45)), (5, 5), 0, 10),
                     # размеры, сдвиг относительно центра перса, тип патронов, средняя скорость пуль
                     Gun(pygame.transform.scale(load_image('Gas_blaster.png', -1), (50, 20)), (0, -5), 0, 10)]
        self.gun = self.guns[gun_id]

    def move(self):  # можно в update, наверное, засунуть, ведь есть метод встроенный self.rect.move(x, y)
        pass

    def shoot(self):
        self.gun.enemy_shoot(0, self.rect)

    def update(self, n_ticks):
        global ticks
        if not self.reloading:
            self.n_ticks = n_ticks
            self.reloading = True
        # if ticks - self.n_ticks > self.effect_end:
        #     self.effect = None
        if ticks - self.n_ticks > self.next_shot:
            self.shoot()
            self.reloading = False

    def apply_effect(self, effect, time):
        self.effect = effect
        self.effect_end = pygame.time.get_ticks() + time

    def get_damage(self):
        pass

    def render(self):
        self.show_gun(self.gun_id)
        self.gun.enemy_render()


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
                    line.append(1)
                else:
                    line.append(0)
            map_arr.append(line)
        return rects, map_arr

    def spawn_enemies(self):
        e = []
        for enemy in self.enemies_list:
            pos = self.tile_size * enemy[0][0], self.tile_size * enemy[0][1]
            if 0 <= enemy[0][0] < self.map.width and 0 <= enemy[0][1] < self.map.height:
                if enemy[1] == 1:
                    e.append(EnemyRifler(pos, 10, load_image('knight.png'), 'тут будет передача поля', 0))
                if enemy[1] == 0:
                    e.append(EnemyRifler(pos, 10, load_image('knight.png'), 'тут будет передача поля', 0))
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
    def __init__(self, img: pygame.image, shift: tuple, id_bullets, v_bullets):
        super(Gun, self).__init__()
        self.shift_x, self.shift_y = shift
        self.image = self.source_img = img
        self.rect = pygame.rect.Rect(knight_main.rect.center[0] - self.shift_x,
                                     knight_main.rect.center[1] - self.shift_y,
                                     self.image.get_width(), self.image.get_height())
        self.last_image = None
        self.angle = None

        self.id_bullets = id_bullets
        self.v_bullets = v_bullets

        self.adjacent_cathet = 0
        self.opposite_cathet = 0

    def rot_around_center(self, image, angle, x, y):
        rotated_image = pygame.transform.rotate(image, angle)
        new_rect = rotated_image.get_rect(center=image.get_rect(center=(x - 5, y)).center)
        return rotated_image, new_rect

    def render(self):
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

    def enemy_render(self, rect: pygame.Rect):
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
            self.image, self.rect = self.rot_around_center(self.source_img, self.angle, *center_coords)
        else:
            self.image, self.rect = self.rot_around_center(self.source_img, self.angle, *center_coords)
            self.image = pygame.transform.flip(self.image, True, False)
            self.rect.x -= 40

        screen.blit(self.image, self.rect)

    def shoot(self, id_bullets):
        mouse_pos = pygame.mouse.get_pos()

        right = True if mouse_pos[0] > knight_main.rect.center[0] else False
        top = True if mouse_pos[1] < knight_main.rect.center[1] else False

        bullet = Bullet(right, top, self.v_bullets, self.adjacent_cathet, self.opposite_cathet)

        normal_img = load_image(db_bullets[id_bullets])
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

    def enemy_shoot(self, id_bullets, rect):
        x, y = knight_main.rect.center

        right = True if x > rect.center[0] else False
        top = True if y < rect.center[1] else False

        bullet = Bullet(right, top, self.v_bullets, self.adjacent_cathet, self.opposite_cathet)

        normal_img = load_image(db_bullets[id_bullets])
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


class Bullet(pygame.sprite.Sprite):
    def __init__(self, right, top, average_v, adjacent_cathet, opposite_cathet):
        super(Bullet, self).__init__(bullets)

        self.right = right  # направления полета пули
        self.top = top

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
            # здесь будет нанесение урона врагу


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
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()  # это пока будет тут, потом пойдет в класс режима игры
    bullets = pygame.sprite.Group()

    knight_main = Knight((60, 60), 100, load_image('knight.png'), 0)  # выбор оружия выполняется здесь

    level_mode = ModeWithLevels(knight_main, current_level)  # в дальнейшем это будет вызываться при
    # нажатии на экране кнопки "Режим уровней"
    level_mode.levels = [Level('maps/Level1.tmx', [((18, 5), 1), ((6, 14), 1), ((28, 19), 0)], [21]),
                         Level('maps/Level2.tmx', [((13, 19), 1), ((27, 12), 1), ((5, 20), 0)], [21]),
                         Level('maps/Level3.tmx', [((10, 14), 1), ((18, 10), 1), ((30, 12), 0)], [21]),
                         Level('maps/Level4.tmx', [((14, 21), 1), ((26, 9), 1), ((6, 26), 0), ((33, 5), 0)], [21]),
                         Level('maps/Level5.tmx', [((10, 6), 1), ((31, 5), 1), ((32, 11), 1), ((17, 29), 0)], [21]),
                         Level('maps/Level6.tmx', [((2, 26), 0), ((10, 27), 0), ((29, 3), 0), ((19, 15), 1)], [21]),
                         Level('maps/Level7.tmx', [((8, 27), 0), ((23, 2), 0), ((27, 17), 1),
                                                   ((33, 6), 1), ((33, 27), 1), ((12, 2), 0)], [13, 14]),
                         Level('maps/Level8.tmx', [((13, 12), 1), ((13, 19), 1), ((27, 12), 1),
                                                   ((27, 19), 1), ((20, 29), 0), ((34, 16), 0)], [13, 14]),
                         Level('maps/Level9.tmx', [((28, 6), 0), ((34, 10), 1), ((10, 25), 0),
                                                   ((6, 21), 1), ((25, 15), 0), ((26, 20), 1)], [13, 14])]

    level_mode.levels[level_mode.current_level].spawn_enemies()
    for e in level_mode.levels[current_level].enemies:
        e.show_gun(e.gun_id)

    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                print(level_mode.levels[level_mode.current_level].get_cell(event.pos))
            knight_main.update(event)

        knight_main.move()
        knight_main.do_animate()

        bullets.update()
        bullets.draw(screen)

        knight_main.render()

        level_mode.levels[current_level].enemies_sprites.draw(screen)
        for e in level_mode.levels[current_level].enemies:
            e.gun.enemy_render(e.rect)
        pygame.display.update()
        level_mode.render()
        all_sprites.draw(screen)
        ticks += 1
        animation_frequency += 1

        level_mode.levels[current_level].enemies_sprites.update(ticks)
        # enemies.draw(screen)
        clock.tick(fps)
    pygame.quit()
