import pygame
import pygame_gui
from constants import size

pygame.init()
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
manager = pygame_gui.UIManager(size)

level_mode_btn = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(round(size[0] / 17.57), round(size[1] / 1.37), round(size[0] / 5.8),
                              round(size[1] / 12.8)),
    text='Режим прохождения уровней', manager=manager)
hardcore_mode_btn = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(round(size[0] / 17.57) + round(size[0] / 5.8) + round(size[0] / 24.6),
                              round(size[1] / 1.37),
                              round(size[0] / 5.8), round(size[1] / 12.8)),
    text='Режим hardcore', manager=manager)
exit_button1 = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(round(size[0] / 1.183), 0, round(size[0] / 6.474), round(size[1] / 19.2)),
    text='Выйти из игры', manager=manager)
back_btn = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(round(size[0] / 17.57), round(size[1] / 1.37), round(size[0] / 5.8),
                              round(size[1] / 12.8)),
    text='<-- Назад <--', manager=manager)
level1 = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(round(size[0] / 17.57), round(size[1] / 3.2), round(size[0] / 12.3),
                              round(size[1] / 9.6)),
    text='Уровень 1', manager=manager)
level2 = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(round(size[0] / 5.857), round(size[1] / 3.2), round(size[0] / 12.3),
                              round(size[1] / 9.6)),
    text='Уровень 2', manager=manager)
level3 = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(round(size[0] / 3.514), round(size[1] / 3.2), round(size[0] / 12.3),
                              round(size[1] / 9.6)),
    text='Уровень 3', manager=manager)
level4 = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(round(size[0] / 17.57), round(size[1] / 2.2857), round(size[0] / 12.3),
                              round(size[1] / 9.6)),
    text='Уровень 4', manager=manager)
level5 = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(round(size[0] / 5.857), round(size[1] / 2.2857), round(size[0] / 12.3),
                              round(size[1] / 9.6)),
    text='Уровень 5', manager=manager)
level6 = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(round(size[0] / 3.514), round(size[1] / 2.2857), round(size[0] / 12.3),
                              round(size[1] / 9.6)),
    text='Уровень 6', manager=manager)
level7 = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(round(size[0] / 17.57), round(size[1] / 1.778), round(size[0] / 12.3),
                              round(size[1] / 9.6)),
    text='Уровень 7', manager=manager)
level8 = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(round(size[0] / 5.857), round(size[1] / 1.778), round(size[0] / 12.3),
                              round(size[1] / 9.6)),
    text='Уровень 8', manager=manager)
level9 = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(round(size[0] / 3.514), round(size[1] / 1.778), round(size[0] / 12.3),
                              round(size[1] / 9.6)),
    text='Уровень 9', manager=manager)

to_beginning = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(round(size[0] / 3.3698), round(size[1] / 1.333), round(size[0] / 5.857),
                              round(size[1] / 12.8)),
    text='Вернуться в начало', manager=manager)
to_exit = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(round(size[0] / 1.968), round(size[1] / 1.333), round(size[0] / 5.857),
                              round(size[1] / 12.8)),
    text='Выйти из игры', manager=manager)
endgame_btns = [to_beginning, to_exit]

esc_window = pygame_gui.windows.ui_confirmation_dialog.UIConfirmationDialog(
    pygame.Rect(round((size[0] / 2) - (round(size[0] / 3.075) / 2)), round((size[1] / 2) - (round(size[1] / 2.4) / 2)),
                round(size[0] / 3.075),
                round(size[1] / 2.4)),
    manager,
    action_long_desc='Вернуться в '
                     'главное меню?',
    window_title='Выход в меню',
    action_short_name='Выйти',
    visible=False)
reset_btn = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(round(size[0] / 1.1827), 0, round(size[0] / 6.474), round(size[1] / 19.2)),
    text='Сбросить прогресс', manager=manager)

level_btns = [level1, level2, level3, level4, level5, level6, level7, level8, level9, back_btn, reset_btn]


def show_level_btns():
    for btn in level_btns:
        btn.show()


def hide_level_btns():
    for btn in level_btns:
        btn.hide()


def show_main_btns():
    level_mode_btn.show()
    hardcore_mode_btn.show()
    exit_button1.show()


def hide_main_btns():
    level_mode_btn.hide()
    hardcore_mode_btn.hide()
    exit_button1.hide()


def show_endgame_btns():
    for btn in endgame_btns:
        btn.show()


def hide_endgame_btns():
    for btn in endgame_btns:
        btn.hide()
