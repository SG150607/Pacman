import math
import os
import random
import sys

import pygame

if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Pacman')
    size = width, height = 700, 875
    screen = pygame.display.set_mode(size)
    screen.fill((0, 0, 0))

    tile_size = 25  # размер объекта на поле
    HP_size = tile_size + 8  # размер иконок хп пакмена
    clock = pygame.time.Clock()
    FPS = 50
    SPEED = 2

    SCORE = 0  # счетчик очков
    BEST_SCORE = int(open('data/best_score', encoding='utf8').read())

    UP_BAR_SIZE = 3 * tile_size
    DOWN_BAR_SIZE = 2 * tile_size

    font = pygame.font.Font('data/Righteous-Regular.ttf', 20)

    '''ЗАГРУЗКИ'''


    def load_level(filename):
        filename = "data/" + filename
        with open(filename, 'r') as mapFile:
            level_map = [list(line.strip()) for line in mapFile]
        return level_map


    def load_image(name, size_=None, colorkey=None):
        fullname = os.path.join('images', name)
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
        if size_ and type(size_) == int:
            image = pygame.transform.scale(image, (size_, size_))
        elif size_ and (type(size_) == list or type(size_) == tuple):
            image = pygame.transform.scale(image, (size_[0], size_[1]))
        else:
            image = pygame.transform.scale(image, (tile_size, tile_size))
        return image


    def show_overlay():  # визуалки
        UP_text = font.render("1UP", True, 'white')
        screen.blit(UP_text, (50, 8))
        score_text = font.render(f"{SCORE}", True, 'white')
        screen.blit(score_text, (50, 38))

        highest_score_text = font.render("HIGH SCORE", True, 'white')
        screen.blit(highest_score_text, (300, 8))
        best_score_text = font.render(f"{BEST_SCORE}", True, 'white')
        screen.blit(best_score_text, (300, 38))

        if player.bonus_on:  # отображаем кружочек если действует бонус (пока для самопроверки, тк нет врагов)
            pygame.draw.circle(screen, pygame.Color('yellow'), (35, 51), 8)

        for i in range(player.lives - 1):  # отображается на 1 жизнь меньше
            screen.blit(load_image('characters/pacman.png', (HP_size * 8, HP_size)).subsurface(
                pygame.Rect((4 * HP_size, 0), (HP_size, HP_size))),
                (30 + i * HP_size, height - 1.5 * HP_size))


    '''КЛАССЫ'''


    class AnimatedSprite(pygame.sprite.Sprite):
        def __init__(self, sheet, columns, rows, x, y):
            super().__init__(all_sprites)
            self.rect = pygame.Rect(x, y, 0, 0)
            self.frames = []
            self.cut_sheet(sheet, columns, rows)
            self.cur_frame = 0
            self.image = self.frames[self.cur_frame]
            self.start_frame = 0

        def cut_sheet(self, sheet, columns, rows):
            self.rect = pygame.Rect(self.rect.x, self.rect.y, sheet.get_width() // columns, sheet.get_height() // rows)
            for row in range(rows):
                for col in range(columns):
                    frame_location = (self.rect.w * col, self.rect.h * row)
                    self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

        def update(self):
            self.cur_frame = (self.cur_frame + 1) % 2 + self.start_frame
            self.image = self.frames[self.cur_frame]


    class Player:
        def __init__(self, pos_x, pos_y):
            self.image = load_image('characters/pacman.png', (tile_size * 8, tile_size))
            self.rect = self.image.get_rect().move(tile_size * pos_x, tile_size * pos_y)
            self.rect.width = tile_size

            self.animated_object = AnimatedSprite(self.image, 8, 1, tile_size * pos_x, tile_size * pos_y)

            self.direction = 0
            self.move_var = [(0, SPEED), (0, -SPEED), (-SPEED, 0), (SPEED, 0)]

            self.turns_allowed = [False, False, False, False]

            self.bonus_on = False
            self.bonus_time = 0
            self.eaten_ghousts = [False, False, False, False]
            # чтоб когда призраки возраждались их нельзя было снова съесть

            self.lives = 3

        def move(self, direction):  # направление движения
            self.direction = direction - 1
            self.animated_object.start_frame = self.direction * 2

        def check_position(self):  # проверка возможности движения
            # 0 - down; 1 - up; 2 - left; 3 - right
            self.turns_allowed = [False, False, False, False]

            pos_x = self.rect.x + self.rect.width // 2
            pos_y = self.rect.y + self.rect.height // 2
            pogr = 13

            if pos_x // tile_size < 27:
                '''НЕ СТЕНА'''
                if self.direction == 0 and Level[(pos_y + pogr) // tile_size][pos_x // tile_size] not in ['#', '_']:
                    self.turns_allowed[0] = True

                if self.direction == 1 and Level[(pos_y - pogr) // tile_size][pos_x // tile_size] not in ['#', '_']:
                    self.turns_allowed[1] = True

                if self.direction == 2 and Level[pos_y // tile_size][(pos_x + pogr) // tile_size - 1] not in ['#', '_']:
                    self.turns_allowed[2] = True

                if self.direction == 3 and Level[pos_y // tile_size][(pos_x - pogr) // tile_size + 1] not in ['#', '_']:
                    self.turns_allowed[3] = True

                '''ПО ЦЕНТРУ'''
                if self.direction == 0 or self.direction == 1:
                    if 9 <= pos_x % tile_size <= 15:  # почти в центре
                        if Level[(pos_y + pogr) // tile_size][pos_x // tile_size] not in ['#', '_']:
                            self.turns_allowed[0] = True
                        if Level[(pos_y - pogr) // tile_size][pos_x // tile_size] not in ['#', '_']:
                            self.turns_allowed[1] = True
                    if 9 <= pos_y % tile_size <= 15:  # между КВАДРАТАМИ
                        if Level[pos_y // tile_size][(pos_x - tile_size) // tile_size] not in ['#', '_']:
                            self.turns_allowed[2] = True
                        if Level[pos_y // tile_size][(pos_x + tile_size) // tile_size] not in ['#', '_']:
                            self.turns_allowed[3] = True

                if self.direction == 2 or self.direction == 3:
                    if 9 <= pos_x % tile_size <= 15:  # почти в центре
                        if Level[(pos_y + tile_size) // tile_size][pos_x // tile_size] not in ['#', '_']:
                            self.turns_allowed[0] = True
                        if Level[(pos_y - tile_size) // tile_size][pos_x // tile_size] not in ['#', '_']:  # !
                            self.turns_allowed[1] = True
                    if 9 <= pos_y % tile_size <= 15:  # между КВАДРАТАМИ
                        if Level[pos_y // tile_size][(pos_x - pogr) // tile_size] not in ['#', '_']:
                            self.turns_allowed[2] = True
                        if Level[pos_y // tile_size][(pos_x + pogr) // tile_size] not in ['#', '_']:
                            self.turns_allowed[3] = True
            else:
                self.turns_allowed[2] = True
                self.turns_allowed[3] = True

        def eating(self):
            global SCORE, BEST_SCORE
            mid_x = self.rect.x + self.rect.width // 2
            mid_y = self.rect.y + self.rect.height // 2
            if -self.rect.width < mid_x < width:  # если игрок в пределах поля
                if Level[mid_y // tile_size][mid_x // tile_size] == "+":
                    Level[mid_y // tile_size][mid_x // tile_size] = ""
                    SCORE += 10
                if Level[mid_y // tile_size][mid_x // tile_size] == "0":
                    Level[mid_y // tile_size][mid_x // tile_size] = ""
                    SCORE += 50
                    self.bonus_on = True
                    self.bonus_time = 1
                    self.eaten_ghousts = [False, False, False, False]

                for point in points:
                    if not Level[point.rect.y // tile_size][point.rect.x // tile_size]:
                        points.remove(point)
                for bonus in bonuses:
                    if not Level[bonus.rect.y // tile_size][bonus.rect.x // tile_size]:
                        bonuses.remove(bonus)

            if SCORE > BEST_SCORE:  # если набрали рекордное кол-во очков
                BEST_SCORE = SCORE

        def update(self):
            self.animated_object.update()
            self.check_position()
            for i in range(4):  # движение
                if self.direction == i and self.turns_allowed[i]:
                    self.rect = self.rect.move(self.move_var[self.direction])
                    self.animated_object.rect = self.animated_object.rect.move(self.move_var[self.direction])

            if self.rect.x > width:  # если вышел за края
                self.rect.x = -self.rect.width + 3
                self.animated_object.rect.x = -self.animated_object.rect.width + 3
            elif self.rect.x < -self.rect.width:
                self.rect.x = width - 3
                self.animated_object.rect.x = width - 3

            self.eating()
            if self.bonus_on and self.bonus_time:
                self.bonus_time = (self.bonus_time + 1) % (10 * FPS + 1)  # бонус действует 10 секунд
            elif self.bonus_on and not self.bonus_time:
                self.bonus_on = False
                self.eaten_ghousts = [False, False, False, False]


    class Ghost:
        def __init__(self, image, pos_x, pos_y, start_direction, inbox, speed):
            self.image = load_image(image, (tile_size * 11, tile_size))
            self.rect = self.image.get_rect().move(tile_size * pos_x, tile_size * pos_y)
            self.rect.width = tile_size

            # 0 - idle; 1 - down; 2 - up; 3 - left; 4 - right; 5 - dead
            self.animated_object = AnimatedSprite(self.image, 11, 1, tile_size * pos_x, tile_size * pos_y)
            self.animated_object.start_frame = start_direction * 2

            self.direction = start_direction
            self.move_var = [(0, speed), (0, -speed), (-speed, 0), (speed, 0)]

            self.turns_allowed = [False, False, False, False]
            self.turns_allowed[start_direction] = True

            self.target = None

            self.alive = True
            self.inbox = inbox

        def check_position(self):  # проверка возможности движения
            # 0 - down; 1 - up; 2 - left; 3 - right
            self.turns_allowed = [False, False, False, False]

            pos_x = self.rect.x + self.rect.width // 2
            pos_y = self.rect.y + self.rect.height // 2
            pogr = 13

            if pos_x // tile_size < 27:
                '''НЕ СТЕНА'''
                if self.direction == 0 and Level[(pos_y + pogr) // tile_size][pos_x // tile_size] not in ['#', '_']:
                    self.turns_allowed[0] = True
                elif self.direction == 0 and Level[(pos_y + pogr) // tile_size][pos_x // tile_size] == '_' and \
                        not self.alive:
                    self.turns_allowed[0] = True  # когда возвращаются домой после смерти

                if self.direction == 1 and Level[(pos_y - pogr) // tile_size][pos_x // tile_size] not in ['#', '_']:
                    self.turns_allowed[1] = True
                elif self.direction == 1 and Level[(pos_y - pogr) // tile_size][
                    pos_x // tile_size] == '_' and self.inbox:
                    self.turns_allowed[1] = True  # когда вылезают из коробки

                if self.direction == 2 and Level[pos_y // tile_size][(pos_x + pogr) // tile_size - 1] not in ['#', '_']:
                    self.turns_allowed[2] = True

                if self.direction == 3 and Level[pos_y // tile_size][(pos_x - pogr) // tile_size + 1] not in ['#', '_']:
                    self.turns_allowed[3] = True

                '''ПО ЦЕНТРУ'''
                if self.direction == 0 or self.direction == 1:
                    if 9 <= pos_x % tile_size <= 15:  # почти в центре
                        if Level[(pos_y + pogr) // tile_size][pos_x // tile_size] not in ['#', '_']:
                            self.turns_allowed[0] = True
                        elif Level[(pos_y + pogr) // tile_size][pos_x // tile_size] == '_' and not self.alive:
                            self.turns_allowed[0] = True
                        if Level[(pos_y - pogr) // tile_size][pos_x // tile_size] not in ['#', '_']:
                            self.turns_allowed[1] = True
                        elif Level[(pos_y - pogr) // tile_size][pos_x // tile_size] == '_' and self.inbox:
                            self.turns_allowed[1] = True
                    if 9 <= pos_y % tile_size <= 15:  # между КВАДРАТАМИ
                        if Level[pos_y // tile_size][(pos_x - tile_size) // tile_size] not in ['#', '_']:
                            self.turns_allowed[2] = True
                        if Level[pos_y // tile_size][(pos_x + tile_size) // tile_size] not in ['#', '_']:
                            self.turns_allowed[3] = True

                if self.direction == 2 or self.direction == 3:
                    if 9 <= pos_x % tile_size <= 15:  # почти в центре
                        if Level[(pos_y + tile_size) // tile_size][pos_x // tile_size] not in ['#', '_']:
                            self.turns_allowed[0] = True
                        if Level[(pos_y - tile_size) // tile_size][pos_x // tile_size] not in ['#', '_']:
                            self.turns_allowed[1] = True
                    if 9 <= pos_y % tile_size <= 15:  # между КВАДРАТАМИ
                        if Level[pos_y // tile_size][(pos_x - pogr) // tile_size] not in ['#', '_']:
                            self.turns_allowed[2] = True
                        if Level[pos_y // tile_size][(pos_x + pogr) // tile_size] not in ['#', '_']:
                            self.turns_allowed[3] = True
            else:
                self.turns_allowed[2] = True
                self.turns_allowed[3] = True

            # определяем inbox
            if gate.rect.x - 4 * tile_size < self.rect.x < gate.rect.x + 3 * tile_size and \
                    gate.rect.y - 4 * tile_size < self.rect.y < gate.rect.y:
                self.inbox = True
            else:
                self.inbox = False

        def dead(self):
            self.animated_object.start_frame = ...

        def choose_direction(self):  # у каждого призрака отдельный класс и свой тип движения
            # считаю расстояние по X и Y
            # хотя можно было бы и через прямоугольный треугольник и теорему Пифагора рассчитать расстояние
            pass

        def escape_direction(self):  # когда герой находится под бафом
            pass

        def escape_box(self):
            pass

        def get_target(self):  # определяем цель
            if self.inbox:  # если в коробке, цель - выбраться -> target = gate
                self.target = gate
            elif not self.alive:  # если съедены, цель - вернуться домой -> target = gate
                self.target = gate
            else:  # если мы вне коробки, цель - съесть игрока -> target = player
                self.target = player

        def update(self):
            self.check_position()
            self.get_target()

            if self.alive and player.bonus_on:  # направление движения и выбор спрайта
                self.escape_direction()
            elif not self.turns_allowed[self.direction] or (self.turns_allowed.count(True) > 1 and not self.inbox):
                # дошли до стены / идея: когда есть несколько вариантов направления и призрак НЕ в коробке
                self.choose_direction()

            if self.alive and player.bonus_on:  # картинка призрака
                self.animated_object.start_frame = 9  # под бафом
            else:
                self.animated_object.start_frame = (self.direction + 1) * 2  # потому что 0 - idle

            self.animated_object.update()

            for i in range(4):  # движение
                if self.direction == i and self.turns_allowed[i]:
                    self.rect = self.rect.move(self.move_var[self.direction])
                    self.animated_object.rect = self.animated_object.rect.move(self.move_var[self.direction])

            if self.rect.x > width:  # если вышел за края
                self.rect.x = -self.rect.width + 3
                self.animated_object.rect.x = -self.animated_object.rect.width + 3
            elif self.rect.x < -self.rect.width:
                self.rect.x = width - 3
                self.animated_object.rect.x = width - 3


    class VioletGhost(Ghost):
        # предпочитает преследование игрока
        def __init__(self, pos_x, pos_y):
            super().__init__('characters/ghost_violet.png', pos_x, pos_y, 3, False, SPEED + 0.3)
            self.turns = [3, 1, 0, 2]

        def choose_direction(self):
            # 0 - down; 1 - up; 2 - left; 3 - right
            if self.turns_allowed.count(True) > 1:
                if (self.rect.x - self.target.rect[1]) // tile_size < 8 and (
                        self.rect.y - self.target.rect[0]) // tile_size < 8:  # если цель близко
                    for id in self.turns:
                        if self.turns_allowed[id] and self.rect.x < self.target.rect[1] and id == 3 and \
                                self.direction != 2:
                            self.direction = 3
                            break
                        elif self.turns_allowed[id] and self.rect.y > self.target.rect[0] and id == 1 and \
                                self.direction != 0:
                            self.direction = 1
                            break
                        elif self.turns_allowed[id] and self.rect.y < self.target.rect[0] and id == 0 and \
                                self.direction != 1:
                            self.direction = 0
                            break
                        elif self.turns_allowed[id] and self.rect.x > self.target.rect[1] and id == 2 and \
                                self.direction != 3:
                            self.direction = 2
                            break
                        elif self.turns_allowed[id] and id == 3 and self.direction != 2:
                            self.direction = 3
                            break
                        elif self.turns_allowed[id] and id == 1 and self.direction != 0:
                            self.direction = 1
                            break
                        elif self.turns_allowed[id] and id == 0 and self.direction != 1:
                            self.direction = 0
                            break
                        elif self.turns_allowed[id] and id == 2 and self.direction != 3:
                            self.direction = 2
                            break
                else:
                    for id in self.turns:
                        if self.turns_allowed[id] and id == 3 and self.direction != 2:
                            self.direction = 3
                            break
                        elif self.turns_allowed[id] and id == 1 and self.direction != 0:
                            self.direction = 1
                            break
                        elif self.turns_allowed[id] and id == 0 and self.direction != 1:
                            self.direction = 0
                            break
                        elif self.turns_allowed[id] and id == 2 and self.direction != 3:
                            self.direction = 2
                            break
            elif self.turns_allowed.count(True) == 1:
                self.direction = self.turns_allowed.index(True)

        def escape_direction(self):
            # 0 - down; 1 - up; 2 - left; 3 - right
            if self.turns_allowed.count(True) > 1:
                for id in self.turns:
                    if self.turns_allowed[id] and self.rect.x > self.target.rect[1] and id == 3 and \
                            self.direction != 2:
                        self.direction = 3
                        break
                    elif self.turns_allowed[id] and self.rect.y < self.target.rect[0] and id == 1 and \
                            self.direction != 0:
                        self.direction = 1
                        break
                    elif self.turns_allowed[id] and self.rect.y > self.target.rect[0] and id == 0 and \
                            self.direction != 1:
                        self.direction = 0
                        break
                    elif self.turns_allowed[id] and self.rect.x < self.target.rect[1] and id == 2 and \
                            self.direction != 3:
                        self.direction = 2
                        break
                    elif self.turns_allowed[id] and id == 3 and self.direction != 2:
                        self.direction = 3
                        break
                    elif self.turns_allowed[id] and id == 1 and self.direction != 0:
                        self.direction = 1
                        break
                    elif self.turns_allowed[id] and id == 0 and self.direction != 1:
                        self.direction = 0
                        break
                    elif self.turns_allowed[id] and id == 2 and self.direction != 3:
                        self.direction = 2
                        break
            elif self.turns_allowed.count(True) == 1:
                self.direction = self.turns_allowed.index(True)


    class PinkGhost(Ghost):
        def __init__(self, pos_x, pos_y):
            super().__init__('characters/ghost_pink.png', pos_x, pos_y, 1, True, SPEED - 0.3)
            self.turns = [2, 1, 0, 3]

        def choose_direction(self):
            # 0 - down; 1 - up; 2 - left; 3 - right
            if self.turns_allowed.count(True) > 1:
                if (self.rect.x - self.target.rect[1]) // tile_size < 7 and (
                        self.rect.y - self.target.rect[0]) // tile_size < 7:  # если цель близко
                    for id in self.turns:
                        if self.turns_allowed[id] and self.rect.x > self.target.rect[1] and id == 2 and \
                                self.direction != 3:
                            self.direction = 2
                            break
                        elif self.turns_allowed[id] and self.rect.y > self.target.rect[0] and id == 1 and \
                                self.direction != 0:
                            self.direction = 1
                            break
                        elif self.turns_allowed[id] and self.rect.y < self.target.rect[0] and id == 0 and \
                                self.direction != 1:
                            self.direction = 0
                            break
                        elif self.turns_allowed[id] and self.rect.x < self.target.rect[1] and id == 3 and \
                                self.direction != 2:
                            self.direction = 3
                            break
                        elif self.turns_allowed[id] and id == 2 and self.direction != 3:
                            self.direction = 2
                            break
                        elif self.turns_allowed[id] and id == 1 and self.direction != 0:
                            self.direction = 1
                            break
                        elif self.turns_allowed[id] and id == 0 and self.direction != 1:
                            self.direction = 0
                            break
                        elif self.turns_allowed[id] and id == 3 and self.direction != 2:
                            self.direction = 3
                            break
                else:
                    for id in self.turns:
                        if self.turns_allowed[id] and id == 2 and self.direction != 3:
                            self.direction = 2
                            break
                        elif self.turns_allowed[id] and id == 1 and self.direction != 0:
                            self.direction = 1
                            break
                        elif self.turns_allowed[id] and id == 0 and self.direction != 1:
                            self.direction = 0
                            break
                        elif self.turns_allowed[id] and id == 3 and self.direction != 2:
                            self.direction = 3
                            break
            elif self.turns_allowed.count(True) == 1:
                self.direction = self.turns_allowed.index(True)

        def escape_direction(self):
            # 0 - down; 1 - up; 2 - left; 3 - right
            if self.turns_allowed.count(True) > 1:
                for id in self.turns:
                    if self.turns_allowed[id] and self.rect.x < self.target.rect[1] and id == 2 and \
                            self.direction != 3:
                        self.direction = 2
                        break
                    elif self.turns_allowed[id] and self.rect.y < self.target.rect[0] and id == 1 and \
                            self.direction != 0:
                        self.direction = 1
                        break
                    elif self.turns_allowed[id] and self.rect.y > self.target.rect[0] and id == 0 and \
                            self.direction != 1:
                        self.direction = 0
                        break
                    elif self.turns_allowed[id] and self.rect.x > self.target.rect[1] and id == 3 and \
                            self.direction != 2:
                        self.direction = 3
                        break
                    elif self.turns_allowed[id] and id == 2 and self.direction != 3:
                        self.direction = 2
                        break
                    elif self.turns_allowed[id] and id == 1 and self.direction != 0:
                        self.direction = 1
                        break
                    elif self.turns_allowed[id] and id == 0 and self.direction != 1:
                        self.direction = 0
                        break
                    elif self.turns_allowed[id] and id == 3 and self.direction != 2:
                        self.direction = 3
                        break
            elif self.turns_allowed.count(True) == 1:
                self.direction = self.turns_allowed.index(True)


    class OrangeGhost(Ghost):
        def __init__(self, pos_x, pos_y):
            super().__init__('characters/ghost_orange.png', pos_x, pos_y, 2, True, SPEED)
            self.turns = [0, 2, 1, 3]

        def choose_direction(self):
            # 0 - down; 1 - up; 2 - left; 3 - right
            if self.turns_allowed.count(True) > 1:
                if (self.rect.x - self.target.rect[1]) // tile_size < 7 and (
                        self.rect.y - self.target.rect[0]) // tile_size < 7:  # если цель близко
                    for id in self.turns:
                        if self.turns_allowed[id] and self.rect.y < self.target.rect[0] and id == 0 and \
                                self.direction != 1:
                            self.direction = 0
                            break
                        elif self.turns_allowed[id] and self.rect.x > self.target.rect[1] and id == 2 and \
                                self.direction != 3:
                            self.direction = 2
                            break
                        elif self.turns_allowed[id] and self.rect.y > self.target.rect[0] and id == 1 and \
                                self.direction != 0:
                            self.direction = 1
                            break
                        elif self.turns_allowed[id] and self.rect.x < self.target.rect[1] and id == 3 and \
                                self.direction != 2:
                            self.direction = 3
                            break
                        elif self.turns_allowed[id] and id == 0 and self.direction != 1:
                            self.direction = 0
                            break
                        elif self.turns_allowed[id] and id == 2 and self.direction != 3:
                            self.direction = 2
                            break
                        elif self.turns_allowed[id] and id == 1 and self.direction != 0:
                            self.direction = 1
                            break
                        elif self.turns_allowed[id] and id == 3 and self.direction != 2:
                            self.direction = 3
                            break
                else:
                    for id in self.turns:
                        if self.turns_allowed[id] and id == 0 and self.direction != 1:
                            self.direction = 0
                            break
                        elif self.turns_allowed[id] and id == 2 and self.direction != 3:
                            self.direction = 2
                            break
                        elif self.turns_allowed[id] and id == 1 and self.direction != 0:
                            self.direction = 1
                            break
                        elif self.turns_allowed[id] and id == 3 and self.direction != 2:
                            self.direction = 3
                            break
            elif self.turns_allowed.count(True) == 1:
                self.direction = self.turns_allowed.index(True)

        def escape_direction(self):
            # 0 - down; 1 - up; 2 - left; 3 - right
            if self.turns_allowed.count(True) > 1:
                for id in self.turns:
                    if self.turns_allowed[id] and self.rect.y > self.target.rect[0] and id == 0 and \
                            self.direction != 1:
                        self.direction = 0
                        break
                    elif self.turns_allowed[id] and self.rect.x < self.target.rect[1] and id == 2 and \
                            self.direction != 3:
                        self.direction = 2
                        break
                    elif self.turns_allowed[id] and self.rect.y < self.target.rect[0] and id == 1 and \
                            self.direction != 0:
                        self.direction = 1
                        break
                    elif self.turns_allowed[id] and self.rect.x > self.target.rect[1] and id == 3 and \
                            self.direction != 2:
                        self.direction = 3
                        break
                    elif self.turns_allowed[id] and id == 0 and self.direction != 1:
                        self.direction = 0
                        break
                    elif self.turns_allowed[id] and id == 2 and self.direction != 3:
                        self.direction = 2
                        break
                    elif self.turns_allowed[id] and id == 1 and self.direction != 0:
                        self.direction = 1
                        break
                    elif self.turns_allowed[id] and id == 3 and self.direction != 2:
                        self.direction = 3
                        break
            elif self.turns_allowed.count(True) == 1:
                self.direction = self.turns_allowed.index(True)


    class BlueGhost(Ghost):
        def __init__(self, pos_x, pos_y):
            super().__init__('characters/ghost_blue.png', pos_x, pos_y, 2, True, SPEED)
            self.turns = [3, 0, 2, 1]

        def choose_direction(self):
            # 0 - down; 1 - up; 2 - left; 3 - right
            if self.turns_allowed.count(True) > 1:
                if (self.rect.x - self.target.rect[1]) // tile_size < 5 and (
                        self.rect.y - self.target.rect[0]) // tile_size < 5:  # если цель близко
                    for id in self.turns:
                        if self.turns_allowed[id] and self.rect.x < self.target.rect[1] and id == 3 and \
                                self.direction != 2:
                            self.direction = 3
                            break
                        elif self.turns_allowed[id] and self.rect.y < self.target.rect[0] and id == 0 and \
                                self.direction != 1:
                            self.direction = 0
                            break
                        elif self.turns_allowed[id] and self.rect.y > self.target.rect[0] and id == 1 and \
                                self.direction != 0:
                            self.direction = 1
                            break
                        elif self.turns_allowed[id] and self.rect.x > self.target.rect[1] and id == 2 and \
                                self.direction != 3:
                            self.direction = 2
                            break
                        elif self.turns_allowed[id] and id == 3 and self.direction != 2:
                            self.direction = 3
                            break
                        elif self.turns_allowed[id] and id == 0 and self.direction != 1:
                            self.direction = 0
                            break
                        elif self.turns_allowed[id] and id == 1 and self.direction != 0:
                            self.direction = 1
                            break
                        elif self.turns_allowed[id] and id == 2 and self.direction != 3:
                            self.direction = 2
                            break
                else:
                    for id in self.turns:
                        if self.turns_allowed[id] and id == 3 and self.direction != 2:
                            self.direction = 3
                            break
                        elif self.turns_allowed[id] and id == 0 and self.direction != 1:
                            self.direction = 0
                            break
                        elif self.turns_allowed[id] and id == 1 and self.direction != 0:
                            self.direction = 1
                            break
                        elif self.turns_allowed[id] and id == 2 and self.direction != 3:
                            self.direction = 2
                            break
            elif self.turns_allowed.count(True) == 1:
                self.direction = self.turns_allowed.index(True)

        def escape_direction(self):
            # 0 - down; 1 - up; 2 - left; 3 - right
            if self.turns_allowed.count(True) > 1:
                for id in self.turns:
                    if self.turns_allowed[id] and self.rect.x > self.target.rect[1] and id == 3 and \
                            self.direction != 2:
                        self.direction = 3
                        break
                    elif self.turns_allowed[id] and self.rect.y > self.target.rect[0] and id == 0 and \
                            self.direction != 1:
                        self.direction = 0
                        break
                    elif self.turns_allowed[id] and self.rect.y < self.target.rect[0] and id == 1 and \
                            self.direction != 0:
                        self.direction = 1
                        break
                    elif self.turns_allowed[id] and self.rect.x < self.target.rect[1] and id == 2 and \
                            self.direction != 3:
                        self.direction = 2
                        break
                    elif self.turns_allowed[id] and id == 3 and self.direction != 2:
                        self.direction = 3
                        break
                    elif self.turns_allowed[id] and id == 0 and self.direction != 1:
                        self.direction = 0
                        break
                    elif self.turns_allowed[id] and id == 1 and self.direction != 0:
                        self.direction = 1
                        break
                    elif self.turns_allowed[id] and id == 2 and self.direction != 3:
                        self.direction = 2
                        break
            elif self.turns_allowed.count(True) == 1:
                self.direction = self.turns_allowed.index(True)


    class Wall(pygame.sprite.Sprite):
        def __init__(self, pos_x, pos_y, size_=(tile_size, tile_size)):
            super().__init__(walls, all_sprites)
            self.image = load_image('field_builder/wall.png')
            self.rect = self.image.get_rect().move(size_[0] * pos_x, size_[1] * pos_y)
            self.mask = pygame.mask.from_surface(self.image)


    class Gate(Wall):
        def __init__(self, pos_x, pos_y):
            super().__init__(pos_x, pos_y)
            self.image = load_image('field_builder/door.png')
            self.rect = self.image.get_rect().move(tile_size * pos_x, tile_size * pos_y)
            self.mask = pygame.mask.from_surface(self.image)  # think about remove


    class Point(pygame.sprite.Sprite):
        def __init__(self, pos_x, pos_y):
            super().__init__(points)
            self.image = load_image('field_builder/dot.png')
            self.rect = self.image.get_rect().move(tile_size * pos_x, tile_size * pos_y)


    class Bonus(pygame.sprite.Sprite):
        # было бы логичнее наследовать от Point, но хочу чтобы они мигали,
        # так что пришлось наследовать класс от Sprite и делать отдельную группу
        def __init__(self, pos_x, pos_y):
            super().__init__(bonuses)
            self.image = load_image('field_builder/bonus.png')
            self.rect = self.image.get_rect().move(tile_size * pos_x, tile_size * pos_y)


    '''
    ---КАРТА---:
    
    P - игрок
    V - фиолетовый призрак
    I - розовый призрак
    B - синий призрак
    O - оранжевый призрак
    # - стены
    + - точки
    0 - бонус(для поедания врагов)
    / - порталы(коридор справа и слева карты для перемещения между краями)
    _ - "калитка" для призраков
    " " - пустая клетка
    "?" - пространство для визуала
    (28 в длину и 35 в высоту)
    '''

    # группы спрайтов
    all_sprites = pygame.sprite.Group()
    walls = pygame.sprite.Group()
    points = pygame.sprite.Group()
    bonuses = pygame.sprite.Group()
    ghosts = pygame.sprite.Group()

    '''ГЕНЕРАЦИЯ УРОВНЯ'''


    def generate_level(level):
        new_player, violet_ghost, pink_ghost, blue_ghost, orange_ghost, gate = None, None, None, None, None, None
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == '#':
                    Wall(x, y)
                elif level[y][x] == '+':
                    Point(x, y)
                elif level[y][x] == '0':
                    Bonus(x, y)
                elif level[y][x] == '_':
                    gate = Gate(x, y)  # сохранится 2-я по счету калитка
                elif level[y][x] == 'P':
                    new_player = Player(x, y)
                    level[y][x] = ''
                elif level[y][x] == 'V':
                    violet_ghost = VioletGhost(x, y)
                    level[y][x] = ''
                elif level[y][x] == 'I':
                    pink_ghost = PinkGhost(x, y)
                    level[y][x] = ''
                elif level[y][x] == 'B':
                    blue_ghost = BlueGhost(x, y)
                    level[y][x] = ''
                elif level[y][x] == 'O':
                    orange_ghost = OrangeGhost(x, y)
                    level[y][x] = ''
        # вернем объекты
        return new_player, violet_ghost, pink_ghost, blue_ghost, orange_ghost, gate


    player, violet_ghost, pink_ghost, blue_ghost, orange_ghost, gate = generate_level(load_level('map.txt'))
    Level = load_level('map.txt')

    running = True
    all_sprites.draw(screen)

    points.draw(screen)
    bonuses.draw(screen)

    player.update()

    violet_ghost.target = player
    pink_ghost.target = gate
    blue_ghost.target = gate
    orange_ghost.target = gate
    violet_ghost.update()
    pink_ghost.update()
    blue_ghost.update()
    orange_ghost.update()

    show_overlay()

    pygame.display.flip()
    pygame.time.wait(3000)  # ждем 3 секунды перед началом игры

    while running:
        clock.tick(FPS)
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player.move(2)
                if event.key == pygame.K_DOWN:
                    player.move(1)
                if event.key == pygame.K_LEFT:
                    player.move(3)
                if event.key == pygame.K_RIGHT:
                    player.move(4)
        all_sprites.draw(screen)
        points.draw(screen)
        if pygame.time.get_ticks() % 1000 < 500:
            bonuses.draw(screen)
        player.update()
        violet_ghost.update()
        pink_ghost.update()
        blue_ghost.update()
        orange_ghost.update()
        show_overlay()
        pygame.display.flip()
    with open('data/best_score', "w", encoding='utf8') as file:
        file.write(str(BEST_SCORE))
    pygame.quit()
