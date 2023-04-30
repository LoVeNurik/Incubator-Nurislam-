import pygame
from pygame.locals import *
import pickle
from pygame import mixer
import json
from os import path

pygame.mixer.pre_init(44100, -16,2,512)
pygame.init()
mixer.init()

clock = pygame.time.Clock()
fps = 60


screen_width = 750
screen_height = 750

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')

#Переменные, основные
tile_size = 50
game_over = 0
main_menu = True
level = 0


#Картинки
bg = pygame.image.load("images/bg_1.png")
bg = pygame.transform.scale(bg, (750, 750))
restart_img = pygame.image.load("images/restart_btn.png")
start_img = pygame.image.load("images/start_btn.png")
exit_img = pygame.image.load("images/exit_btn.png")

#zvuki
game_over_fx = pygame.mixer.Sound('images/img_game_over.wav')
game_over_fx.set_volume(0.5)

class Lever(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('images/red_button.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Platform(pygame.sprite.Sprite):
    def __init__(self,x,y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('images/platform.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y


    def update(self):
        self.rect.x += self.move_direction *self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


def reset_level(level):
    player_1.reset(100,screen_height - 90, "images/Watergirl.png")
    player_2.reset(100,screen_height - 190, "images/Fireboy.png")
    lava_group.empty()
    exit_group.empty()
    platform_group.empty()
    lever_group.empty()
    if path.exists(f'level{level}_data'):
        level_file = open(f'level{level}_data', 'r')
        world_data = json.load(level_file)
    world = World(world_data)

    return world

class Button():
    def __init__(self,x,y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False

        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] ==1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] ==0:
            self.clicked =False

        screen.blit(self.image, self.rect)

        return action

class Player_blue():
    def __init__(self,x,y, img_path):
        self.reset(x,y,img_path)

    def update(self, game_over):
        dx = 0
        dy = 0
        col_thresh = 20

        if game_over == 0:

            #Управление и прыжок
            key = pygame.key.get_pressed()
            if key[pygame.K_UP] and self.jumped == False and self.in_air == False:
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_UP] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -=5
            if key[pygame.K_RIGHT]:
                dx +=5

            #Гравитация
            self.vel_y +=1
            if self.vel_y>10:
                self.vel_y = 10
            dy += self.vel_y

            #Проверка столкновений
            self.in_air = True
            for tile in world.tile_list:

                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0

                #Проверка по y
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                game_over_fx.play()



            for plaform in platform_group:
                if plaform.rect.colliderect(self.rect.x +dx, self.rect.y, self.width, self.height):
                    dx = 0
                if plaform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if abs((self.rect.top + dy) - plaform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = plaform.rect.bottom - self.rect.top
                    elif abs((self.rect.bottom + dy) - plaform.rect.top) < col_thresh:
                        self.rect.bottom = plaform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    if plaform.move_x != 0:
                        self.rect.x += plaform.move_direction






            #Обновляю координаты персонажа
            self.rect.x += dx
            self.rect.y += dy

            if self.rect.bottom > screen_height:
                 self.rect.bottom = screen_height

        elif game_over == -1:
            self.image = self.dead_image
            if self.rect.y > 200:
                self.rect.y -=5

        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, (255,255,255), self.rect,2)

        return game_over


    def reset(self, x, y, img_path):
        img = pygame.image.load(img_path)
        self.dead_image = pygame.image.load("images/ghost.png")
        self.dead_image = pygame.transform.scale(self.dead_image, (40, 40))
        self.image = pygame.transform.scale(img, (40, 40))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.in_air = True

class Player_red():
    def __init__(self,x,y, img_path):
        self.reset(x,y,img_path)

    def update(self, game_over):
        dx = 0
        dy = 0
        col_thresh = 20


        if game_over == 0:

            #Управление и прыжок
            key = pygame.key.get_pressed()
            if key[pygame.K_w] and self.jumped == False and self.in_air == False:
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_w] == False:
                self.jumped = False
            if key[pygame.K_a]:
                dx -=5
            if key[pygame.K_d]:
                dx +=5

            #Гравитация
            self.vel_y +=1
            if self.vel_y>10:
                self.vel_y = 10
            dy += self.vel_y

            #Проверка столкновений
            self.in_air = True
            for tile in world.tile_list:

                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0

                #Проверка по y
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                game_over_fx.play()


            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1


            for plaform in platform_group:
                if plaform.rect.colliderect(self.rect.x +dx, self.rect.y, self.width, self.height):
                    dx = 0
                if plaform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if abs((self.rect.top + dy) - plaform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = plaform.rect.bottom - self.rect.top
                    elif abs((self.rect.bottom + dy) - plaform.rect.top) < col_thresh:
                        self.rect.bottom = plaform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    if plaform.move_x != 0:
                        self.rect.x += plaform.move_direction




            #Обновляю координаты персонажа
            self.rect.x += dx
            self.rect.y += dy

            if self.rect.bottom > screen_height:
                 self.rect.bottom = screen_height

        elif game_over == -1:
            self.image = self.dead_image
            if self.rect.y > 200:
                self.rect.y -=5

        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, (255,255,255), self.rect,2)

        return game_over


    def reset(self, x, y, img_path):
        img = pygame.image.load(img_path)
        self.dead_image = pygame.image.load("images/ghost.png")
        self.dead_image = pygame.transform.scale(self.dead_image, (40, 40))
        self.image = pygame.transform.scale(img, (40, 40))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.in_air = True


class Lava(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('images/Slime[1].jpg')
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

class Exit_1(pygame.sprite.Sprite):
    def __init__(self,x,y, img_path):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load(img_path)
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class World():
    def __init__(self, data):
        self.tile_list = []

        dirt_img = pygame.image.load("images/border.png")

        row_count =0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count*tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 8:
                    exit = Exit_1(col_count *tile_size,row_count* tile_size, 'images/blue_door.png')
                    exit_group.add(exit)
                if tile == 7:
                    exit = Exit_1(col_count * tile_size, row_count * tile_size, 'images/red_door.png')
                    exit_group.add(exit)
                if tile == 6:
                    lava =Lava(col_count *tile_size,row_count* tile_size )
                    lava_group.add(lava)
                if tile == 3:
                    lever = Lever(col_count * tile_size,row_count * tile_size)
                    lever_group.add(lever)
                if tile == 4:
                    platform = Platform(col_count *tile_size,row_count* tile_size,0, 1 )
                    platform_group.add(platform)
                if tile == 5:
                    platform = Platform(col_count * tile_size, row_count * tile_size,1,0)
                    platform_group.add(platform)
                col_count +=1
            row_count +=1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])





player_1 = Player_blue(100, screen_height - 90, "images/Watergirl.png")
player_2 = Player_red(100, screen_height - 190, "images/Fireboy.png")
lava_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
lever_group = pygame.sprite.Group()

if path.exists(f'level{level}_data'):
    level_file = open(f'level{level}_data', 'r')
    world_data = json.load(level_file)
world = World(world_data )

restart_button = Button(screen_width//2 - 50, screen_height//2 +100, restart_img)
start_btn = Button(screen_width // 2-150, screen_height//2 -150, start_img)
exit_btn = Button(screen_width // 2-125, screen_height // 2 + 100, exit_img)

run = True
while run:

    clock.tick(fps)
    screen.blit(bg, (0,0))
    if main_menu == True:
        if exit_btn.draw():
            run = False
        if start_btn.draw():
            main_menu = False
    else:

        world.draw()

        lava_group.draw(screen)
        exit_group.draw(screen)
        platform_group.draw(screen)
        lever_group.draw(screen)

        game_over = player_1.update(game_over)
        game_over = player_2.update(game_over)

        if game_over == -1:
            if restart_button.draw():
                player_1.reset(100, screen_height - 90, "images/Watergirl.png")
                player_2.reset(100, screen_height - 190, "images/Fireboy.png")
                world = reset_level(level)
                game_over = 0

        if game_over == 0 :
            platform_group.update()

        if game_over == 1:
            level += 1
            if level <= 1:
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                if restart_button.draw():
                    level = 1
                world_data= []
                world = reset_level(level)
                game_over = 0


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()