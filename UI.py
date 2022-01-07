import pygame
import pygame_gui

pygame.init()

manager = pygame_gui.UIManager((1230, 960))

level_mode_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(70.0, 700.0, 210.0, 75.0),
                                              text='Режим прохождения уровней', manager=manager)
hardcore_mode_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(330.0, 700.0, 210.0, 75.0),
                                                 text='Режим hardcore', manager=manager)
exit_button1 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(1040.0, 0, 190.0, 50.0),
                                            text='Выйти из игры', manager=manager)
back_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(70.0, 700.0, 210.0, 75.0),
                                        text='<-- Назад <--', manager=manager)
level1 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(70.0, 300.0, 100.0, 100.0),
                                      text='Уровень 1', manager=manager)
level2 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(190.0, 300.0, 100.0, 100.0),
                                      text='Уровень 2', manager=manager)
level3 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(310.0, 300.0, 100.0, 100.0),
                                      text='Уровень 3', manager=manager)
level4 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(70.0, 420.0, 100.0, 100.0),
                                      text='Уровень 4', manager=manager)
level5 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(190.0, 420.0, 100.0, 100.0),
                                      text='Уровень 5', manager=manager)
level6 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(310.0, 420.0, 100.0, 100.0),
                                      text='Уровень 6', manager=manager)
level7 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(70.0, 540.0, 100.0, 100.0),
                                      text='Уровень 7', manager=manager)
level8 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(190.0, 540.0, 100.0, 100.0),
                                      text='Уровень 8', manager=manager)
level9 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(310.0, 540.0, 100.0, 100.0),
                                      text='Уровень 9', manager=manager)
level_btns = [level1, level2, level3, level4, level5, level6, level7, level8, level9, back_btn]

to_beginning = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(365.0, 720.0, 210.0, 75.0),
                                            text='Вернуться в начало', manager=manager)
to_exit = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(625.0, 720.0, 210.0, 75.0),
                                       text='Выйти из игры', manager=manager)
endgame_btns = [to_beginning, to_exit]


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
