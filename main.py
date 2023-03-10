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
        screen.blit(UP_text, (2 * tile_size, round(0.5 * tile_size)))
        score_text = font.render(f"{SCORE}", True, 'white')
        screen.blit(score_text, (2 * tile_size, round(1.5 * tile_size)))

        highest_score_text = font.render("HIGH SCORE", True, 'white')
        screen.blit(highest_score_text, (12 * tile_size, round(0.5 * tile_size)))
        best_score_text = font.render(f"{BEST_SCORE}", True, 'white')
        screen.blit(best_score_text, (12 * tile_size, round(1.5 * tile_size)))

        if player.bonus_on:  # отображаем кружочек если действует бонус (пока для самопроверки, тк нет врагов)
            pygame.draw.circle(screen, pygame.Color('yellow'), (round(1.5 * tile_size), 2 * tile_size),
                               round(0.5 * tile_size))

        for i in range(player.lives - 1):  # отображается на 1 жизнь меньше
            screen.blit(load_image('characters/pacman.png', (HP_size * 8, HP_size)).subsurface(
                pygame.Rect((4 * HP_size, 0), (HP_size, HP_size))),
                (tile_size + i * HP_size, height - 1.3 * HP_size))

        for num, fruit in enumerate(player.eaten_fruits):  # отображаем фрукты съеденные игроком
            screen.blit(fruit.image, (width - 1.3 * tile_size * (num + 1), height - 1.3 * tile_size))


    def restart(full=False):  # перезагружаем уровень
        global player, violet_ghost, pink_ghost, blue_ghost, orange_ghost, gate, Level
        screen.fill((0, 0, 0))
        if full:  # полностью сбрасываем уровень

            # очищаем группы спрайтов
            ghosts.empty()
            players_anim_obj.empty()
            walls.empty()
            points.empty()
            bonuses.empty()

            # заново заргружаем уровень
            player, violet_ghost, pink_ghost, blue_ghost, orange_ghost, gate = generate_level(load_level('map.txt'))
            Level = load_level('map.txt')

        '''ДВИГАЕМ ОБЪЕКТЫ НА НАЧАЛЬНУЮ ПОЗИЦИЮ И ВСЕ СБРАСЫВАЕМ'''

        # игрок
        player.rect = pygame.rect.Rect(tile_size * 13, tile_size * 19, tile_size, tile_size)
        player.animated_object.rect = pygame.rect.Rect(tile_size * 13, tile_size * 19, tile_size, tile_size)
        player.alive = True
        player.bonus_on = False

        # призраки
        ghosts.empty()  # создаем новые объекты, так что очищаем группу

        # фиолетовый призрак
        violet_ghost.rect = pygame.rect.Rect(tile_size * 13, tile_size * 13, tile_size, tile_size)
        violet_ghost.animated_object = AnimatedSprite(ghosts, violet_ghost.image, 30, 1, tile_size * 13, tile_size * 13)
        violet_ghost.animated_object.start_frame = (violet_ghost.direction + 1) * 2
        violet_ghost.move_var = [(0, violet_ghost.speed[0]), (0, -violet_ghost.speed[0]),
                                 (-violet_ghost.speed[0], 0), (violet_ghost.speed[0], 0)]

        # розовый призрак
        pink_ghost.rect = pygame.rect.Rect(tile_size * 13, tile_size * 16, tile_size, tile_size)
        pink_ghost.animated_object = AnimatedSprite(ghosts, pink_ghost.image, 30, 1, tile_size * 13, tile_size * 16)
        pink_ghost.animated_object.start_frame = (pink_ghost.direction + 1) * 2
        pink_ghost.move_var = [(0, pink_ghost.speed[0]), (0, -pink_ghost.speed[0]),
                               (-pink_ghost.speed[0], 0), (pink_ghost.speed[0], 0)]

        # оранжевый призрак
        orange_ghost.rect = pygame.rect.Rect(tile_size * 15, tile_size * 16, tile_size, tile_size)
        orange_ghost.animated_object = AnimatedSprite(ghosts, orange_ghost.image, 30, 1, tile_size * 15, tile_size * 16)
        orange_ghost.animated_object.start_frame = (orange_ghost.direction + 1) * 2
        orange_ghost.move_var = [(0, orange_ghost.speed[0]), (0, -orange_ghost.speed[0]),
                                 (-orange_ghost.speed[0], 0), (orange_ghost.speed[0], 0)]

        # синий призрак
        blue_ghost.rect = pygame.rect.Rect(tile_size * 11, tile_size * 16, tile_size, tile_size)
        blue_ghost.animated_object = AnimatedSprite(ghosts, blue_ghost.image, 30, 1, tile_size * 11, tile_size * 16)
        blue_ghost.animated_object.start_frame = (blue_ghost.direction + 1) * 2
        blue_ghost.move_var = [(0, blue_ghost.speed[0]), (0, -blue_ghost.speed[0]),
                               (-blue_ghost.speed[0], 0), (blue_ghost.speed[0], 0)]

        for ghost in [violet_ghost, pink_ghost, orange_ghost, blue_ghost]:  # оживляем всех призраков
            ghost.alive = True

        walls.draw(screen)
        points.draw(screen)
        bonuses.draw(screen)

        player.update()
        players_anim_obj.draw(screen)

        violet_ghost.target = player
        pink_ghost.target = gate
        blue_ghost.target = gate
        orange_ghost.target = gate
        violet_ghost.update()
        pink_ghost.update()
        blue_ghost.update()
        orange_ghost.update()
        ghosts.draw(screen)

        show_overlay()

        screen.blit(font.render("READY!", True, 'yellow'), (tile_size * 12.5, tile_size * 17))
        pygame.display.flip()
        pygame.time.wait(3000)  # ждем 3 секунды перед началом игры


    def game_over():  # если пакмен потерял все жизни
        global running
        running = False

        screen.fill(pygame.Color('black'))

        # отрисовываем карту
        walls.draw(screen)
        points.draw(screen)
        bonuses.draw(screen)

        show_overlay()

        # фразу проигрыша
        lose_text = font.render(f"GAME OVER", True, 'red')
        screen.blit(lose_text, (11.5 * tile_size, 17 * tile_size))

        # отрисовываем
        pygame.display.flip()

        lose = True
        while lose:  # новый цикл
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    lose = False
        pygame.quit()


    def win():  # если съели все точки
        for i in range(7):  # фликерная анимация стен
            if i % 2 == 1:
                white_walls.draw(screen)
            else:
                walls.draw(screen)

            # рисуем другие объекты
            players_anim_obj.draw(screen)
            ghosts.draw(screen)
            show_overlay()

            pygame.display.flip()
            pygame.time.wait(600)
        restart(full=True)


    '''КЛАССЫ'''


    class AnimatedSprite(pygame.sprite.Sprite):
        def __init__(self, group, sheet, columns, rows, x, y):
            super().__init__(group)
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
            self.alive = True

            self.image = load_image('characters/pacman.png', (tile_size * 8, tile_size))
            self.rect = self.image.get_rect().move(tile_size * pos_x, tile_size * pos_y)
            self.rect.width = tile_size

            self.animated_object = AnimatedSprite(players_anim_obj, self.image, 8, 1,
                                                  tile_size * pos_x, tile_size * pos_y)

            self.direction = 0
            self.move_var = [(0, SPEED), (0, -SPEED), (-SPEED, 0), (SPEED, 0)]

            self.turns_allowed = [False, False, False, False]

            self.bonus_on = False
            self.bonus_time = 0
            self.eaten_ghousts = [False, False, False, False]
            # чтоб когда призраки возраждались их нельзя было снова съесть

            self.lives = 3

            self.eaten_fruits = []  # съеденные фрукты

        def move(self, direction):  # направление движения
            self.direction = direction - 1
            self.animated_object.start_frame = self.direction * 2

        def check_position(self):  # проверка возможности движения
            # 0 - down; 1 - up; 2 - left; 3 - right
            self.turns_allowed = [False, False, False, False]

            pos_x = self.rect.x + self.rect.width // 2
            pos_y = self.rect.y + self.rect.height // 2
            pogr = tile_size // 2 + 1

            if pos_x // tile_size < 27:
                '''НЕ СТЕНА'''
                if self.direction == 0 and Level[(pos_y + pogr) // tile_size][pos_x // tile_size] not in ['#', '_']:
                    self.turns_allowed[0] = True

                if self.direction == 1 and Level[(pos_y - pogr) // tile_size][pos_x // tile_size] not in ['#', '_']:
                    self.turns_allowed[1] = True

                if self.direction == 2 and Level[pos_y // tile_size][(pos_x - pogr) // tile_size] not in ['#', '_']:
                    self.turns_allowed[2] = True

                if self.direction == 3 and Level[pos_y // tile_size][(pos_x + pogr) // tile_size] not in ['#', '_']:
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
                    for ghost in [violet_ghost, pink_ghost, orange_ghost, blue_ghost]:
                        ghost.revived = False
                if Level[mid_y // tile_size][mid_x // tile_size] == "F":
                    Level[mid_y // tile_size][mid_x // tile_size] = ""
                    SCORE += 100

                for point in points:
                    if not Level[point.rect.y // tile_size][point.rect.x // tile_size]:
                        points.remove(point)
                for bonus in bonuses:
                    if not Level[bonus.rect.y // tile_size][bonus.rect.x // tile_size]:
                        bonuses.remove(bonus)
                for fruit in fruits:
                    if not Level[fruit.rect.y // tile_size][fruit.rect.x // tile_size]:
                        fruits.remove(fruit)
                        self.eaten_fruits.append(fruit)
                        fruit_list.clear()

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

            # столкновение с призраками
            for id, ghost in enumerate([violet_ghost, pink_ghost, orange_ghost, blue_ghost]):
                # сталкиваемся, если маленькое расстоние
                if ((self.rect.x - ghost.rect.x) ** 2 + (self.rect.y - ghost.rect.y) ** 2) ** 0.5 < tile_size:
                    if self.bonus_on and ghost.alive and ghost.under_effect:  # если действует бонус - умирает призрак
                        ghost.alive = False
                        ghost.under_effect = False
                        self.eaten_ghousts[id] = True
                        # получаем очки пропорционально съеденному количеству призраков
                        global SCORE
                        SCORE += len([ghost_ for ghost_ in self.eaten_ghousts if ghost_]) * 200
                    elif not self.bonus_on:  # иначе - умирает пакмен
                        self.lives -= 1
                        self.alive = False


    class Ghost:
        def __init__(self, anim_obj_group, image, pos_x, pos_y, start_direction, inbox, speed, escape_con):
            self.image = load_image(image, (tile_size * 30, tile_size))
            self.rect = self.image.get_rect().move(tile_size * pos_x, tile_size * pos_y)
            self.rect.width = tile_size

            # 0 - idle; 1 - down; 2 - up; 3 - left; 4 - right; 5 - dead
            self.animated_object = AnimatedSprite(anim_obj_group, self.image, 30, 1,
                                                  tile_size * pos_x, tile_size * pos_y)
            self.animated_object.start_frame = start_direction * 2

            self.direction = start_direction
            self.speed = [speed, speed + 5]
            self.move_var = [(0, self.speed[0]), (0, -self.speed[0]), (-self.speed[0], 0), (self.speed[0], 0)]

            self.turns_allowed = [False, False, False, False]
            self.turns_allowed[start_direction] = True
            self.blocked_turns = []  # у каждого призрака своя логика движения и свой blocked_turns

            self.target = None

            self.alive = True
            self.inbox = inbox
            self.escape_con = escape_con  # в игре 240 точек, когда указанное кол-во съедено, призрак покидает дом

            self.under_effect = False  # находиться ли призрак под действием бонуса
            self.revived = False

            self.countdown = 0

        def check_position(self):  # проверка возможности движения + определяем inbox
            # 0 - down; 1 - up; 2 - left; 3 - right
            self.turns_allowed = [False, False, False, False]

            pos_x = self.rect.x + self.rect.width // 2
            pos_y = self.rect.y + self.rect.height // 2
            pogr = tile_size // 2 + 1

            if pos_x // tile_size < 27:  # если в пределах карты
                '''НЕ СТЕНА'''
                if self.direction == 0 and Level[pos_y // tile_size + 1][pos_x // tile_size] not in ['#', '_']:
                    self.turns_allowed[0] = True
                if self.direction == 1 and Level[pos_y // tile_size - 1][pos_x // tile_size] not in ['#', '_']:
                    self.turns_allowed[1] = True
                if self.direction == 2 and Level[pos_y // tile_size][pos_x // tile_size - 1] not in ['#', '_']:
                    self.turns_allowed[2] = True
                if self.direction == 3 and Level[pos_y // tile_size][pos_x // tile_size + 1] not in ['#', '_']:
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
                        if Level[(pos_y - tile_size) // tile_size][pos_x // tile_size] not in ['#', '_']:
                            self.turns_allowed[1] = True
                    if 9 <= pos_y % tile_size <= 15:  # между КВАДРАТАМИ
                        if Level[pos_y // tile_size][(pos_x - pogr) // tile_size] not in ['#', '_']:
                            self.turns_allowed[2] = True
                        if Level[pos_y // tile_size][(pos_x + pogr) // tile_size] not in ['#', '_']:
                            self.turns_allowed[3] = True
            else:  # за пределами (когда проходим через левый/правый края карты)
                self.turns_allowed[2] = True
                self.turns_allowed[3] = True

            # определяем inbox
            if gate.rect.x - 4 * tile_size < self.rect.x < gate.rect.x + 3 * tile_size and \
                    gate.rect.y + 4 * tile_size > self.rect.y > gate.rect.y - tile_size:
                self.inbox = True
            else:
                self.inbox = False

        def choose_direction(self):  # у каждого призрака отдельный класс и свой тип движения
            # считаю расстояние по X и Y
            # хотя можно было бы и через прямоугольный треугольник и теорему Пифагора рассчитать расстояние
            pass

        def flee_direction(self):  # когда герой находится под бафом
            pass  # у каждого призрака свой тип движения

        def check(self, turn):  # проверка что не призрак не может идти обратно
            if (turn == 0 and self.direction == 1) or (turn == 1 and self.direction == 0) or \
                    (turn == 2 and self.direction == 3) or (turn == 3 and self.direction == 2):
                return True  # идет обратно
            else:
                return False  # идет НЕ обратно

        def escape_box(self):  # выбираемся из коробки
            # дополнительные проверки
            pos_x = self.rect.x + self.rect.width // 2
            pos_y = self.rect.y + self.rect.height // 2
            if Level[pos_y // tile_size - 1][pos_x // tile_size] == '_':
                self.turns_allowed[1] = True  # когда вылезают из коробки

            # ДВИЖЕНИЕ
            pogr = 5

            # если почти в центре, то не двигаемся
            if abs(self.rect.x - gate.rect.x) > pogr:
                if self.rect.x < gate.rect.x and self.turns_allowed[3]:
                    self.direction = 3
                elif self.rect.x > gate.rect.x and self.turns_allowed[2]:
                    self.direction = 2
            else:
                self.direction = 1

            if self.rect.y <= gate.rect.y:  # пинок под зад
                self.inbox = False
                self.rect = self.rect.move(self.move_var[self.direction])
                self.animated_object.rect = self.animated_object.rect.move(self.move_var[self.direction])

        def get_in_box(self):  # добираемся до коробки
            # было бы лучше рекурсивно искать наименьший путь, но МЕЕХ, уж какой нашелся програмист ¯\_(ツ)_/¯

            self.choose_direction()
            if gate.rect.x - tile_size <= self.rect.x <= gate.rect.x and \
                    gate.rect.y - tile_size <= self.rect.y <= gate.rect.y:  # значит мы над 'калиткой' и идем вниз
                self.direction = 0
                self.rect = self.rect.move(self.move_var[0])  # пинок под зад-2
                self.animated_object.rect = self.animated_object.rect.move(self.move_var[0])
                self.revived = True

        def get_target(self):  # определяем цель
            if self.inbox:  # если в коробке, цель - выбраться -> target = gate
                self.target = gate
            elif not self.alive:  # если съедены, цель - вернуться домой -> target = gate
                self.target = gate
            else:  # если мы вне коробки, цель - съесть игрока -> target = player
                self.target = player

        def update(self):
            self.countdown += clock.tick()
            self.check_position()
            self.get_target()

            if not self.alive:  # если призрак мертв
                self.get_in_box()
            elif self.alive and player.bonus_on and not self.inbox:  # направление движения и выбор спрайта
                self.flee_direction()
            elif self.alive and self.inbox and 240 - len(points) >= self.escape_con:  # если в коробке и нужно выбраться
                self.escape_box()
            else:
                rect1 = self.rect.move(self.move_var[self.direction])  # квадрат,куда мы передвинемся
                # дошли до стены / когда есть несколько вариантов направления(без обратно) и призрак НЕ в коробке
                # также проверяем, что мы меняем направление, если передвигаемся в другую клетку
                # и чтоб не моментально меняли направление, а прошли минимум 1 клетку
                if not self.turns_allowed[self.direction] or \
                        (self.turns_allowed.count(True) - 1 >= 1 and not self.inbox and
                         [(rect1.y + rect1.height) // tile_size, (rect1.x + rect1.width) // tile_size] !=
                         [(self.rect.y + self.rect.height // 2) // tile_size,
                          (self.rect.x + self.rect.width // 2) // tile_size] and
                         self.countdown >= (tile_size // self.speed[0])):
                    self.choose_direction()
                    self.countdown = 0

            if not self.alive:  # картинка призрака (по 10 спрайтов на каждое состояние), +1 потому что 0 - idle
                self.animated_object.start_frame = (self.direction + 1) * 2 + 20  # мертв
                # self.under_effect изменяем в классе игрока
            elif self.alive and player.bonus_on and not self.revived:  # если у игрока активен бонус
                self.under_effect = True
                self.animated_object.start_frame = (self.direction + 1) * 2 + 10

            else:
                self.animated_object.start_frame = (self.direction + 1) * 2  # обычное состояние
                self.under_effect = False

            self.animated_object.update()

            if self.inbox:  # если дома, то живы
                self.alive = True

            if not self.alive:  # настройка скорости призрака
                # быстрая, если мертв
                self.move_var = [(0, self.speed[1]), (0, -self.speed[1]),
                                 (-self.speed[1], 0), (self.speed[1], 0)]
            else:
                # обычная, если жив
                self.move_var = [(0, self.speed[0]), (0, -self.speed[0]),
                                 (-self.speed[0], 0), (self.speed[0], 0)]

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
        # быстрее других призраков и замечает игрока, если он далеко
        def __init__(self, pos_x, pos_y):
            super().__init__(ghosts, 'characters/ghost_violet.png', pos_x, pos_y, 3, False, SPEED + 0.3, 0)
            self.turns_list = [3, 3, 3, 1, 1, 1, 0, 0, 2, 2]
            self.turns = [3, 1, 0, 2]

        def choose_direction(self):
            # 0 - down; 1 - up; 2 - left; 3 - right
            if self.turns_allowed.count(True) > 1:
                # если цель близко или надо вернуться в коробку
                if abs(self.rect.x - self.target.rect[0]) // tile_size < 8 and abs(
                        self.rect.y - self.target.rect[1]) // tile_size < 8 or not self.alive:
                    if self.rect.x < self.target.rect[0] and self.turns_allowed[3] and not self.check(3):
                        self.direction = 3
                    elif self.rect.y > self.target.rect[1] and self.turns_allowed[1] and not self.check(1):
                        self.direction = 1
                    elif self.rect.y < self.target.rect[1] and self.turns_allowed[0] and not self.check(0):
                        self.direction = 0
                    elif self.rect.x > self.target.rect[0] and self.turns_allowed[2] and not self.check(2):
                        self.direction = 2
                    else:
                        turn = random.choice(self.turns)
                        # если не можем идти в то направление, или выполняем разворот, что призраки не могут
                        while not self.turns_allowed[turn] or self.check(turn):
                            turn = random.choice(self.turns_list)
                        self.direction = turn

                else:
                    turn = random.choice(self.turns)
                    # если не можем идти в то направление, или выполняем разворот, что призраки не могут
                    while not self.turns_allowed[turn] or self.check(turn):
                        turn = random.choice(self.turns_list)
                    self.direction = turn

            elif self.turns_allowed.count(True) == 1:
                self.direction = self.turns_allowed.index(True)

        def flee_direction(self):
            # 0 - down; 1 - up; 2 - left; 3 - right
            if self.turns_allowed.count(True) > 1:
                if self.rect.x > self.target.rect[0] and self.turns_allowed[3] and not self.check(3):
                    self.direction = 3
                elif self.rect.y < self.target.rect[1] and self.turns_allowed[1] and not self.check(1):
                    self.direction = 1
                elif self.rect.y > self.target.rect[1] and self.turns_allowed[0] and not self.check(0):
                    self.direction = 0
                elif self.rect.x < self.target.rect[0] and self.turns_allowed[2] and not self.check(2):
                    self.direction = 2
                else:
                    turn = random.choice(self.turns)
                    # если не можем идти в то направление, или выполняем разворот, что призраки не могут
                    while not self.turns_allowed[turn] or self.check(turn):
                        turn = random.choice(self.turns_list)
                    self.direction = turn
            elif self.turns_allowed.count(True) == 1:
                self.direction = self.turns_allowed.index(True)


    class PinkGhost(Ghost):
        # медленнее других призраков, замечает игрока на нормальном расстоянии
        def __init__(self, pos_x, pos_y):
            super().__init__(ghosts, 'characters/ghost_pink.png', pos_x, pos_y, 1, True, SPEED - 0.1, 60)
            self.turns_list = [2, 2, 2, 1, 1, 1, 0, 0, 3, 3]
            self.turns = [2, 1, 0, 3]

        def choose_direction(self):
            # 0 - down; 1 - up; 2 - left; 3 - right
            if self.turns_allowed.count(True) > 1:
                # если цель близко или надо вернуться в коробку
                if abs(self.rect.x - self.target.rect[0]) // tile_size < 7 and abs(
                        self.rect.y - self.target.rect[1]) // tile_size < 7 or not self.alive:
                    if self.rect.x > self.target.rect[0] and self.turns_allowed[2] and not self.check(2):
                        self.direction = 2
                    elif self.rect.y > self.target.rect[1] and self.turns_allowed[1] and not self.check(1):
                        self.direction = 1
                    elif self.rect.y < self.target.rect[1] and self.turns_allowed[0] and not self.check(0):
                        self.direction = 0
                    elif self.rect.x < self.target.rect[0] and self.turns_allowed[3] and not self.check(3):
                        self.direction = 3
                    else:
                        turn = random.choice(self.turns)
                        # если не можем идти в то направление, или выполняем разворот, что призраки не могут
                        while not self.turns_allowed[turn] or self.check(turn):
                            turn = random.choice(self.turns_list)
                        self.direction = turn
                else:
                    turn = random.choice(self.turns)
                    # если не можем идти в то направление, или выполняем разворот, что призраки не могут
                    while not self.turns_allowed[turn] or self.check(turn):
                        turn = random.choice(self.turns_list)
                    self.direction = turn
            elif self.turns_allowed.count(True) == 1:
                self.direction = self.turns_allowed.index(True)

        def flee_direction(self):
            # 0 - down; 1 - up; 2 - left; 3 - right
            if self.turns_allowed.count(True) > 1:
                if self.rect.x < self.target.rect[0] and self.turns_allowed[2] and not self.check(2):
                    self.direction = 2
                elif self.rect.y < self.target.rect[1] and self.turns_allowed[1] and not self.check(1):
                    self.direction = 1
                elif self.rect.y > self.target.rect[1] and self.turns_allowed[0] and not self.check(0):
                    self.direction = 0
                elif self.rect.x < self.target.rect[0] and self.turns_allowed[3] and not self.check(3):
                    self.direction = 3
                else:
                    turn = random.choice(self.turns)
                    # если не можем идти в то направление, или выполняем разворот, что призраки не могут
                    while not self.turns_allowed[turn] or self.check(turn):
                        turn = random.choice(self.turns_list)
                    self.direction = turn
            elif self.turns_allowed.count(True) == 1:
                self.direction = self.turns_allowed.index(True)


    class OrangeGhost(Ghost):
        # обычная скорость, замечает игрока на нормальном расстоянии
        def __init__(self, pos_x, pos_y):
            super().__init__(ghosts, 'characters/ghost_orange.png', pos_x, pos_y, 2, True, SPEED + 0.1, 40)
            self.turns_list = [0, 0, 0, 2, 2, 2, 1, 1, 3, 3]
            self.turns = [0, 2, 1, 3]

        def choose_direction(self):
            # 0 - down; 1 - up; 2 - left; 3 - right
            if self.turns_allowed.count(True) > 1:
                # если цель близко или надо вернуться в коробку
                if abs(self.rect.x - self.target.rect[0]) // tile_size < 7 and abs(
                        self.rect.y - self.target.rect[1]) // tile_size < 7 or not self.alive:
                    if self.rect.y < self.target.rect[1] and self.turns_allowed[0] and not self.check(0):
                        self.direction = 0
                    elif self.rect.x > self.target.rect[0] and self.turns_allowed[2] and not self.check(2):
                        self.direction = 2
                    elif self.rect.y > self.target.rect[1] and self.turns_allowed[1] and not self.check(1):
                        self.direction = 1
                    elif self.rect.x < self.target.rect[0] and self.turns_allowed[3] and not self.check(3):
                        self.direction = 3
                    else:
                        turn = random.choice(self.turns)
                        # если не можем идти в то направление, или выполняем разворот, что призраки не могут
                        while not self.turns_allowed[turn] or self.check(turn):
                            turn = random.choice(self.turns_list)
                        self.direction = turn
                else:
                    turn = random.choice(self.turns)
                    # если не можем идти в то направление, или выполняем разворот, что призраки не могут
                    while not self.turns_allowed[turn] or self.check(turn):
                        turn = random.choice(self.turns_list)
                    self.direction = turn
            elif self.turns_allowed.count(True) == 1:
                self.direction = self.turns_allowed.index(True)

        def flee_direction(self):
            # 0 - down; 1 - up; 2 - left; 3 - right
            if self.turns_allowed.count(True) > 1:
                if self.rect.y > self.target.rect[1] and self.turns_allowed[0] and not self.check(0):
                    self.direction = 0
                elif self.rect.x < self.target.rect[0] and self.turns_allowed[2] and not self.check(2):
                    self.direction = 2
                elif self.rect.y < self.target.rect[1] and self.turns_allowed[1] and not self.check(1):
                    self.direction = 1
                elif self.rect.x > self.target.rect[0] and self.turns_allowed[3] and not self.check(3):
                    self.direction = 3
                else:
                    turn = random.choice(self.turns)
                    # если не можем идти в то направление, или выполняем разворот, что призраки не могут
                    while not self.turns_allowed[turn] or self.check(turn):
                        turn = random.choice(self.turns_list)
                    self.direction = turn
            elif self.turns_allowed.count(True) == 1:
                self.direction = self.turns_allowed.index(True)


    class BlueGhost(Ghost):
        # обычная скорость, замечает игрока, если он очень близко
        def __init__(self, pos_x, pos_y):
            super().__init__(ghosts, 'characters/ghost_blue.png', pos_x, pos_y, 2, True, SPEED + 0.1, 25)
            self.turns_list = [3, 3, 3, 0, 0, 0, 2, 2, 1, 1]
            self.turns = [3, 0, 2, 1]

        def choose_direction(self):
            # 0 - down; 1 - up; 2 - left; 3 - right
            if self.turns_allowed.count(True) > 1:
                # если цель близко или надо вернуться в коробку
                if abs(self.rect.x - self.target.rect[0]) // tile_size < 5 and abs(
                        self.rect.y - self.target.rect[1]) // tile_size < 5 or not self.alive:
                    if self.rect.x < self.target.rect[0] and self.turns_allowed[3] and not self.check(3):
                        self.direction = 3
                    elif self.rect.y < self.target.rect[1] and self.turns_allowed[0] and not self.check(0):
                        self.direction = 0
                    elif self.rect.x > self.target.rect[0] and self.turns_allowed[2] and not self.check(2):
                        self.direction = 2
                    elif self.rect.y > self.target.rect[1] and self.turns_allowed[1] and not self.check(1):
                        self.direction = 1
                    else:
                        turn = random.choice(self.turns)
                        # если не можем идти в то направление, или выполняем разворот, что призраки не могут
                        while not self.turns_allowed[turn] or self.check(turn):
                            turn = random.choice(self.turns_list)
                        self.direction = turn

                else:
                    turn = random.choice(self.turns)
                    # если не можем идти в то направление, или выполняем разворот, что призраки не могут
                    while not self.turns_allowed[turn] or self.check(turn):
                        turn = random.choice(self.turns_list)
                    self.direction = turn
            elif self.turns_allowed.count(True) == 1:
                self.direction = self.turns_allowed.index(True)

        def flee_direction(self):
            # 0 - down; 1 - up; 2 - left; 3 - right
            if self.turns_allowed.count(True) > 1:
                if self.rect.x > self.target.rect[0] and self.turns_allowed[3] and not self.check(3):
                    self.direction = 3
                elif self.rect.y > self.target.rect[1] and self.turns_allowed[0] and not self.check(0):
                    self.direction = 0
                elif self.rect.x < self.target.rect[0] and self.turns_allowed[2] and not self.check(2):
                    self.direction = 2
                elif self.rect.y < self.target.rect[1] and self.turns_allowed[1] and not self.check(1):
                    self.direction = 1
                else:
                    turn = random.choice(self.turns)
                    # если не можем идти в то направление, или выполняем разворот, что призраки не могут
                    while not self.turns_allowed[turn] or self.check(turn):
                        turn = random.choice(self.turns_list)
                    self.direction = turn
            elif self.turns_allowed.count(True) == 1:
                self.direction = self.turns_allowed.index(True)


    class Wall(pygame.sprite.Sprite):
        def __init__(self, pos_x, pos_y, size_=(tile_size, tile_size)):
            super().__init__(walls)
            self.image = load_image('field_builder/wall_blue.png')
            self.rect = self.image.get_rect().move(size_[0] * pos_x, size_[1] * pos_y)


    class WhiteWall(pygame.sprite.Sprite):
        def __init__(self, pos_x, pos_y, size_=(tile_size, tile_size)):
            super().__init__(white_walls)
            self.image = load_image('field_builder/wall_white.png')
            self.rect = self.image.get_rect().move(size_[0] * pos_x, size_[1] * pos_y)


    class Gate(Wall):
        def __init__(self, pos_x, pos_y):
            super().__init__(pos_x, pos_y)
            self.image = load_image('field_builder/door.png')
            self.rect = self.image.get_rect().move(tile_size * pos_x, tile_size * pos_y)


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


    class Fruit(pygame.sprite.Sprite):
        # фруктики - объекты за которые игрок может получить дополнительные очки
        # за их съедение игрок получает 100 очков, как на 1-ом уровне игры (а у нас всего 1 уровень, так что ГЫЫ)
        def __init__(self, pos_x, pos_y):
            super().__init__(fruits)
            self.fruit = random.choice(['fruit_banana', 'fruit_cherry', 'fruit_grapes',
                                        'fruit_lemon', 'fruit_orange', 'fruit_peach',
                                        'fruit_pear', 'fruit_tomato'])
            self.image = load_image(f'fruits/{self.fruit}.png')
            self.rect = self.image.get_rect().move(tile_size * pos_x, tile_size * pos_y)
            self.life_time = random.choice([9 + i * 0.01 for i in range(100)])  # время которое фрукт проведет на поле
            global Level
            Level[pos_y][pos_x] = "F"  # отображаем на поле

        def update(self):
            self.life_time -= 0.001


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
    F - место для фруктов
    / - порталы(коридор справа и слева карты для перемещения между краями)
    _ - "калитка" для призраков
    " " - пустая клетка
    "?" - пространство для визуала
    (28 в длину и 35 в высоту)
    '''

    # группы спрайтов
    ghosts = pygame.sprite.Group()
    players_anim_obj = pygame.sprite.Group()
    walls = pygame.sprite.Group()
    white_walls = pygame.sprite.Group()
    points = pygame.sprite.Group()
    bonuses = pygame.sprite.Group()
    fruits = pygame.sprite.Group()

    fruit_list = []

    '''ГЕНЕРАЦИЯ УРОВНЯ'''


    def generate_level(level):
        new_player, violet_ghost, pink_ghost, blue_ghost, orange_ghost, gate = None, None, None, None, None, None
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == '#':
                    Wall(x, y)
                    WhiteWall(x, y)
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

    walls.draw(screen)
    points.draw(screen)
    bonuses.draw(screen)

    show_overlay()

    ghosts.draw(screen)
    players_anim_obj.draw(screen)

    screen.blit(font.render("READY!", True, 'yellow'), (tile_size * 12.5, tile_size * 17))
    pygame.display.flip()
    pygame.time.wait(3000)  # ждем 3 секунды перед началом игры

    running = True
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
        walls.draw(screen)
        points.draw(screen)
        if pygame.time.get_ticks() % 1000 < 500:
            bonuses.draw(screen)

        if len(points) == 170 and not len(fruit_list):  # первый фруктик
            fruit_list.append(Fruit(13, 19))
        elif len(points) == 70 and not len(fruit_list):  # второй фруктик
            fruit_list.append(Fruit(13, 19))
        for fruit in fruit_list:
            fruit.update()
            if fruit.life_time <= 0:  # если 'время жизни' истекло, то фрукт исчезает
                fruit_list.remove(fruit)
                fruits.remove(fruit)
                Level[fruit.rect.y // tile_size][fruit.rect.x // tile_size] = ''
        fruits.draw(screen)

        players_anim_obj.draw(screen)
        player.update()
        if not player.lives:  # если пакмен потерял все жизни, то КОНЕЦ ИГРЫ
            game_over()
            break
        elif not player.alive:  # если игрок умер - перезагружаемся
            restart()
            continue
        elif not points and not bonuses:  # если съели все точки, то ПОБЕДА (и перезапуск игры)
            win()
            continue
        violet_ghost.update()
        pink_ghost.update()
        blue_ghost.update()
        orange_ghost.update()
        ghosts.draw(screen)

        show_overlay()
        pygame.display.flip()
    with open('data/best_score', "w", encoding='utf8') as file:
        file.write(str(BEST_SCORE))
    pygame.quit()
