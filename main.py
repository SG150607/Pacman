import math
import os
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
            screen.blit(load_image('pacman.png', (HP_size * 8, HP_size)).subsurface(
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
            self.image = load_image('pacman.png', (tile_size * 8, tile_size))
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
            self.animated_object.start_frame = self.direction

        def check_position(self):  # проверка возможности движения
            # 0 - down; 1 - up; 2 - left; 3 - right
            self.turns_allowed = [False, False, False, False]

            pos_x = self.rect.x + self.rect.width // 2
            pos_y = self.rect.y + self.rect.height // 2
            pogr = 13

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

        def eating(self):
            global SCORE, BEST_SCORE
            mid_x = self.rect.x + self.rect.width // 2
            mid_y = self.rect.y + self.rect.height // 2
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


    class Ghoust(pygame.sprite.Sprite):
        # 0 - idle; 1 - down; 2 - up; 3 - left; 4 - right
        ...


    class Wall(pygame.sprite.Sprite):
        def __init__(self, pos_x, pos_y, size_=(tile_size, tile_size)):
            super().__init__(walls, all_sprites)
            self.image = load_image('wall.png')
            self.rect = self.image.get_rect().move(size_[0] * pos_x, size_[1] * pos_y)
            self.mask = pygame.mask.from_surface(self.image)


    class Gate(Wall):
        def __init__(self, pos_x, pos_y):
            super().__init__(pos_x, pos_y)
            self.image = load_image('door.png')
            self.rect = self.image.get_rect().move(tile_size * pos_x, tile_size * pos_y)
            self.mask = pygame.mask.from_surface(self.image)  # think about remove


    class Point(pygame.sprite.Sprite):
        def __init__(self, pos_x, pos_y):
            super().__init__(points)
            self.image = load_image('dot.png')
            self.rect = self.image.get_rect().move(tile_size * pos_x, tile_size * pos_y)


    class Bonus(pygame.sprite.Sprite):
        # было бы логичнее наследовать от Point, но хочу чтобы они мигали,
        # так что пришлось наследовать класс от Sprite и делать отдельную группу
        def __init__(self, pos_x, pos_y):
            super().__init__(bonuses)
            self.image = load_image('bonus.png')
            self.rect = self.image.get_rect().move(tile_size * pos_x, tile_size * pos_y)


    '''
    ---КАРТА---:
    
    P - игрок
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

    '''ГЕНЕРАЦИЯ УРОВНЯ'''


    def generate_level(level):
        new_player, x, y = None, None, None
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == '#':
                    Wall(x, y)
                elif level[y][x] == '+':
                    Point(x, y)
                elif level[y][x] == '0':
                    Bonus(x, y)
                elif level[y][x] == '_':
                    Gate(x, y)
                elif level[y][x] == 'P':
                    new_player = Player(x, y)
                    level[y][x] = ''
        # вернем игрока, а также размер поля в клетках
        return new_player, x, y


    player, level_x, level_y = generate_level(load_level('map.txt'))
    Level = load_level('map.txt')

    running = True
    all_sprites.draw(screen)
    points.draw(screen)
    bonuses.draw(screen)
    player.update()
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
        if pygame.time.get_ticks() % 2000 < 1000:
            bonuses.draw(screen)
        player.update()
        show_overlay()
        pygame.display.flip()
    with open('data/best_score', "w", encoding='utf8') as file:
        file.write(str(BEST_SCORE))
    pygame.quit()
