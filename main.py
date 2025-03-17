from pygame import *
from random import randint
import json
import time as tm
import os
import sys
# Инициализация Pygame
font.init()
mixer.init()
window = display.set_mode((0, 0), FULLSCREEN)
w1, h1 = window.get_size()
bg = transform.scale(image.load("fon.png"), (w1, h1))
bg2 = transform.scale(image.load("fon2.png"), (w1, h1))
clock = time.Clock()
FPS = 60

# Начальные переменные
start_time = tm.time()
killed = 0
lost = 0
x_bg_move = 0
x_bg2_move = -w1

# Загрузка музыки
mixer.music.load("Martian_Madness.ogg")
mixer.music.play(-1)  # Зацикливаем музыку
music_hurt = mixer.Sound("item_12.wav")
music_hurt.set_volume(2)

# Шрифты
font1 = font.Font("Comic Sans MS.ttf", 30)
font2 = font.Font("Comic Sans MS.ttf", 70)
lose = font2.render("You were slain...", False, (187, 22, 43))
lose2 = font2.render("You were slain...", False, (0, 0, 0))
restart_text=font2.render("Для перезапуска нажмите R",False, (187, 22, 43))
# Лор игры
lore_text = [
    "Вы последний обитатель мира игры Terraria.",
    "После нападения марсиан и прохождения лабиринта вы получили их НЛО",
    "С его помощью которого вы будете сражаться против посланников Лунного Лорда, его глаз.",
    " Ваша задача - уничтожить всех врагов!",
    "Сможете ли вы спасти свой мир от нашествия Лунного лорда?"
    
]
# Классы игры
class GameSprite(sprite.Sprite):
    def __init__(self, im, speed, x, y, w, h):
        super().__init__()
        self.image = transform.scale(image.load(im), (w, h))
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 0:
            self.rect.x -= self.speed
        elif keys[K_RIGHT] and self.rect.x < w1 - 30:
            self.rect.x += self.speed
        elif keys[K_UP] and self.rect.y > 0:
            self.rect.y -= self.speed
        elif keys[K_DOWN] and self.rect.y < h1 - 30:
            self.rect.y += self.speed

    def fire(self):
        bullet = Bullet("laser.png", 5, self.rect.centerx, self.rect.top, 60, 100)
        lasers.add(bullet)
        music_hurt.play()

class Bullet(GameSprite):
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < -100:
            self.kill()
        hits = sprite.spritecollide(self, monsters, True)
        if hits:
            global killed
            killed += len(hits)  # Увеличиваем количество убитых врагов на количество уничтоженных врагов
            
            # Создаем новых врагов для каждого убитого
            for hit in hits:
                new_enemy = Enemy("monster.png",randint(1,5),randint(100,w1-100),-100,100,140)
                monsters.add(new_enemy)

class Enemy(GameSprite):
    def update(self):
        global lost
        self.rect.y += self.speed
        if self.rect.y > h1:
            lost += 1
            self.rect.y = -100
            self.rect.x = randint(100, w1 - 100)

class Meteor(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > h1:
            self.rect.y = -100
            self.rect.x = randint(0, w1 - 50)

def show_game_over_screen():
    #Отображает экран Game Over и обрабатывает ввод пользователя
    running = True
    while running:
        for ev in event.get():
            if ev.type == QUIT:
                return False  # Завершить игру
            if ev.type == KEYDOWN:
                if ev.key == K_r:  # Нажмите 'R' для перезагрузки игры
                    return True  # Перезапустить игру

        window.blit(bg2, (0, 0))  # Фон остается видимым

        window.blit(lose2, (w1 / 3 - 3, h1 / 3 + 3))
        window.blit(lose2, (w1 / 3, h1 / 3 - 2))
        window.blit(lose, (w1 / 3, h1 / 3))
        
        restart_text = font1.render("Нажмите 'R' для перезагрузки", True, (255, 255, 255))
        window.blit(restart_text, (w1 / 4 + 50, h1 - 100))
        
        display.update()
# Начальное меню

def start_menu():
    global num_monsters
    num_monsters = 3  # Значение по умолчанию
    menu = True
    
    while menu:
        window.fill((0, 0, 0))  # Очистка экрана
        # Отображаем текст лора
        y_offset = h1 / 10
        for line in lore_text:
            lore_line = font1.render(line, True, (255, 255, 255))
            window.blit(lore_line, (w1 / 10, y_offset))
            y_offset += 40
        
        title_text = font2.render("Выберите количество врагов:", True, (255, 255, 255))
        window.blit(title_text, (w1 / 4, y_offset + 20))

        for i in range(1, 6):
            enemy_text = font1.render(f"{i}", True, (255, 255, 255))
            enemy_rect = enemy_text.get_rect(center=(w1 / 4 + (i+1) * 100 + 50, y_offset + 150))
            window.blit(enemy_text, enemy_rect)

            # Проверка нажатия мыши на текст врагов
            mouse_pos = mouse.get_pos()
            if enemy_rect.collidepoint(mouse_pos) and mouse.get_pressed()[0]:
                num_monsters = i
                menu = False
        
        for ev in event.get():
            if ev.type == QUIT:
                menu = False
            if ev.type == KEYDOWN:
                if ev.key in [K_1, K_2, K_3, K_4, K_5]:
                    num_monsters = int(ev.unicode)  # Устанавливаем количество врагов на основе нажатой клавиши
                    menu = False

        display.update()
        









# Загрузка лучших результатов из файлов или обнуление
best_results = {}
for i in range(1, 6):
    filename = f"result{i}.json"
    if os.path.exists(filename):
        with open(filename, "r") as file:
            best_results[i] = json.load(file)
    else:
        best_results[i] = 0
def save_best_results():
    global best_results, num_monsters, killed
    if killed > best_results[num_monsters]:  # Если текущий счёт лучше сохранённого
        best_results[num_monsters] = killed
        filename = f"result{num_monsters}.json"
        with open(filename, "w") as file:
            json.dump(killed, file)  # Записываем новый рекорд  

def main_game():
    global num_monsters, x_bg_move, x_bg2_move, killed, lost,meteors
    killed = 0
    lost = 0
    # Создание групп спрайтов
    global lasers, monsters
    lasers = sprite.Group()
    monsters = sprite.Group()
    # Создание игрока
    gg=Player("UFO2.gif",15,500,500,210,94)
    
    # Создание врагов и метеоритов на основе выбранного количества врагов
    for _ in range(num_monsters):
        enemy = Enemy("monster.png",randint(1,5),randint(100,w1-100),-100,100,140)
        monsters.add(enemy)
    meteors = sprite.Group()
    for _ in range(3):  # Добавляем несколько метеоритов в игру
        meteor = Meteor("meteor.png", randint(1, 3), randint(0, w1 - 50), randint(-100, -40), 50, 50)
        meteors.add(meteor)
    life=True
    game = True


    while game:
        for ev in event.get():
            # проверка событий с клавиатуры
            if ev.type == QUIT:
                quit()
                sys.exit()
            if ev.type == MOUSEBUTTONDOWN:
                x, y = ev.pos
            if ev.type == KEYUP and ev.key == K_SPACE and life:
                gg.fire()
                
            if key.get_pressed()[K_ESCAPE]:
                quit()
                sys.exit()

        if life:

            
            
            # Проверка на поражение
            if lost >= num_monsters+1:  # Условие окончания игры
                life = False

            # Отрисовка объектов на экране
            window.blit(bg, (x_bg_move, 0))
            window.blit(bg, (x_bg2_move, 0))
            x_bg_move += 1.25
            x_bg2_move += 1.25

            if x_bg_move >= w1:
                x_bg_move = -w1
            if x_bg2_move >= w1:
                x_bg2_move = -w1
            # Обновление игровых объектов
            gg.update()
            monsters.update()
            meteors.update() 
            lasers.update()
            gg.reset()
            monsters.draw(window)
            lasers.draw(window)
            meteors.draw(window)
            
                 # Проверка на столкновение с игроком
            if sprite.spritecollide(gg,meteors,False):
                life=False
            if sprite.spritecollide(gg,monsters,False):
                life=False
            if  sprite.groupcollide(monsters,lasers,True,True):
                killed+=1
                monsters.add(Enemy("monster.png",randint(1,5),randint(100,w1-100),-100,100,140))
                
            
            # отРисовка текста
            window.blit(font1.render(f"Пропущено: {lost}", 1, (255, 69, 0)), (5, 5))
            window.blit(font1.render(f"Вбито: {killed}", 1, (255, 69, 0)), (5, 70))
            window.blit(font1.render(f"Выбранная сложность: {num_monsters} ", 1, (255, 69, 0)), (5, 135))

            # Draw best results for all difficulties
            for i in range(1, 6):
                window.blit(font1.render(f"Лучший результат на сложности {i}: {best_results[i]}", 1, (255, 69, 0)), (5, 200 + (i - 1) * 25-10))


            display.update()
            clock.tick(FPS)
        else:
            save_best_results()  # Сохранение рекорда перед экраном Game Over
            game = False
            
    return show_game_over_screen()  # Возвращаем результат экрана проигрыша
            
    
    
    

# Создание групп спрайтов
lasers = sprite.Group()
monsters = sprite.Group()

# Основной игровой цикл с перезапуском
while True:
    start_menu()  
    if not main_game(): 
        break  

# Завершение Pygame
quit()
for i in range(1, 6):
    print(f"Кращий результат для {i} монстров: {best_results[i]}")

#pyinstaller --onefile --icon=shooter.ico --noconsole main.py