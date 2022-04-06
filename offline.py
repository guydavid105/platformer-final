import pygame
import pickle
import tkinter as tk
from tkinter import simpledialog
from leaderboard import leader
from level_editor import level_editor
from pygame.locals import *
from os import path

ROOT = tk.Tk()
ROOT.withdraw()

l_message = "Select a level between 1-8 for pre-made levels, 9 for custom level"
l_error_message = "Level selected wasn't in range 1-8, try again"

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 600
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("game")

font_score = pygame.font.SysFont("Bauhaus 93", 20)
font = pygame.font.SysFont("Bauhaus 93", 50)

# Game variables
tile_size = 30
game_over = 0
game_over2 = 0
main_menu = True
max_levels = 7
score = 0
total_score = 0
level = 0
save_counter = 0
add = True

white = (255, 255, 255)
blue = (0, 0, 255)

# Load and scale images
bg_img = pygame.image.load("bg image.webp")
bg_img = pygame.transform.scale(bg_img, (600, 600))
restart_img = pygame.image.load("restart.png")
restart_img = pygame.transform.scale(restart_img, (tile_size * 2, tile_size))
start_img = pygame.image.load("start.png")
start_img = pygame.transform.scale(start_img, (200, 100))
exit_img = pygame.image.load("exit.png")
exit_img = pygame.transform.scale(exit_img, (200, 100))
save_img = pygame.image.load("save.png")
save_img = pygame.transform.scale(save_img, (tile_size * 2, tile_size))
leaderboard_img = pygame.image.load("leaderboard.png")
leaderboard_img = pygame.transform.scale(leaderboard_img, (300, 100))
level_editor_img = pygame.image.load("editor.png")
level_editor_img = pygame.transform.scale(level_editor_img, (350, 100))


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def reset_level(level):
    player.reset(60, screen_height - 75, 0)  # reset player position
    player2.reset(50, screen_height - 75, 1)
    blob_group.empty()
    platform_group.empty()  # empties all sprite groups
    lava_group.empty()
    end_group.empty()
    coin_group.empty()

    if path.exists(f"level{level}_data"):  # reloads the level
        pickle_in = open(f"level{level}_data", "rb")
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world


class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        # Checking for button clicked
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        screen.blit(self.image, self.rect)

        return action


class Player:
    def __init__(self, x, y, keys):
        self.reset(x, y, keys)

    # player movement
    def update(self, game_over):
        dx = 0
        dy = 0
        col_thresh = 12

        # check if game is mid level
        if game_over == 0:
            key = pygame.key.get_pressed()
            if key[self.keybind[self.keys][0]] and not self.jumped and not self.in_air:
                self.vel_y = -9
                self.jumped = True
            if not key[self.keybind[self.keys][0]]:
                self.jumped = False
            if key[self.keybind[self.keys][1]]:
                dx -= 3
            if key[self.keybind[self.keys][2]]:
                dx += 3

            # gravity mechanics
            self.vel_y += 0.6
            if self.vel_y > 6:
                self.vel_y = 6
            dy += self.vel_y

            self.in_air = True
            for tile in world.tile_list:
                # checking for horizontal collision with dirt and grass
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0

                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # checking for vertical collision and whether or not the player is above or below the tile
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            # checking for collision with other sprites
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1

            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1

            if pygame.sprite.spritecollide(self, end_group, False):
                game_over = 1

            # platform collision
            for platform in platform_group:
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y *= -0.5
                        dy = platform.rect.bottom - self.rect.top - 1
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        dy = 0
                        self.in_air = False
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction

            self.rect.x += dx
            self.rect.y += dy

        # death animation
        elif game_over == -1:
            self.img = pygame.transform.scale(self.ghost_img, (25, 59))  # changes image to ghost
            draw_text("GAME OVER!", font, blue, (screen_width // 2) - 120, screen_height // 2)
            if self.rect.y > 100:
                self.rect.y -= 5  # makes the ghost float up on the screen

        screen.blit(self.img, self.rect)

        return game_over

    def reset(self, x, y, keys):
        img = pygame.image.load("guy1.png")
        self.ghost_img = pygame.image.load("ghost.png")
        self.img = pygame.transform.scale(img, (25, 50))
        self.rect = self.img.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.vel_y = 0
        self.jumped = False
        self.in_air = True
        self.keys = keys
        self.keybind = {0: [pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT], 1: [pygame.K_w, pygame.K_a, pygame.K_d]}


class World:
    def __init__(self, data):
        self.tile_list = []

        dirt_img = pygame.image.load("dirt.png")
        grass_img = pygame.image.load("grass.png")

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:  # dirt block
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:  # grass block
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:  # enemy
                    blob = Enemy(col_count * tile_size, row_count * tile_size)
                    blob_group.add(blob)
                if tile == 4:  # horizontal moving platform
                    platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
                    platform_group.add(platform)
                if tile == 5:  # vertical moving platform
                    platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
                    platform_group.add(platform)
                if tile == 6:  # lava
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    lava_group.add(lava)
                if tile == 7:  # coin
                    coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    coin_group.add(coin)
                if tile == 8:  # end door
                    end = End(col_count * tile_size, (row_count - 1) * tile_size + 7)
                    end_group.add(end)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        enemy_img = pygame.image.load("enemy.png")
        self.image = pygame.transform.scale(enemy_img, (tile_size - 5, tile_size - 5))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 30:  # every 30 pixels direction is reversed
            self.move_direction *= -1
            self.move_counter *= -1


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        platform_img = pygame.image.load("platform.png")
        self.image = pygame.transform.scale(platform_img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 30:
            self.move_direction *= -1
            self.move_counter *= -1


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        lava_img = pygame.image.load("lava.png")
        self.image = pygame.transform.scale(lava_img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        coin_img = pygame.image.load("coin.png")
        self.image = pygame.transform.scale(coin_img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class End(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        end_img = pygame.image.load("end.png")
        self.image = pygame.transform.scale(end_img, (tile_size, tile_size * 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


def ask1(prompt1):
    USER_INP = simpledialog.askinteger(title="Level Select", prompt=prompt1)

    return USER_INP


player = Player(60, screen_height - 75, 0)
player2 = Player(50, screen_height - 75, 1)

blob_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
end_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
scoin_group = pygame.sprite.Group()

score_coin = Coin(tile_size // 2, tile_size // 2)
scoin_group.add(score_coin)

restart_button = Button(screen_width // 2 - 30, screen_height // 2 + 60, restart_img)
start_button = Button(screen_width // 2 - 230, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 50, screen_height // 2, exit_img)
save_button = Button(screen_width // 2 + 30, screen_height // 2 + 60, save_img)
leaderboard_button = Button(screen_width // 2 - 150, screen_height // 2 + 130, leaderboard_img)
level_editor_button = Button(screen_width // 2 - 170, screen_height // 2 - 150, level_editor_img)

run = True  # game loop
while run:

    clock.tick(fps)
    screen.blit(bg_img, (0, 0))

    if main_menu:  # stays on menu screen
        if start_button.draw():
            main_menu = False  # starts game/loads level
            level = ask1(l_message) - 1  # allows user to select level
            if level == 8:
                level = simpledialog.askstring(title="Level Name", prompt="What is your custom level called?")
            if type(level) == int:
                while level > 8 or level < 0:
                    level = ask1(l_error_message) - 1  # checks if level is in range
            if path.exists(f"level{level}_data"):
                pickle_in = open(f"level{level}_data", "rb")
                world_data = pickle.load(pickle_in)
                world = World(world_data)
            else:
                tk.messagebox.showinfo(title="Error", message="No level found", )
        elif exit_button.draw():
            run = False  # exits game loop, closes game window
        elif leaderboard_button.draw():
            leader()
        elif level_editor_button.draw():
            level_editor()
        else:
            draw_text("Level Maker", font, blue, screen_width // 2 - 120, screen_height // 2 - 130)

    else:
        world.draw()

        if game_over == 0 or game_over2 == 0:
            blob_group.update()
            platform_group.update()

            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
            elif pygame.sprite.spritecollide(player2, coin_group, True):
                score += 1
            draw_text("X " + str(score + total_score), font_score, white, tile_size - 6, 6)

        blob_group.draw(screen)
        platform_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        end_group.draw(screen)
        scoin_group.draw(screen)

        game_over = player.update(game_over)  # updates player 1 state
        game_over2 = player2.update(game_over2)  # updates player 2 state

        if game_over == -1 or game_over2 == -1:  # if player 1 or player 2 dies
            if restart_button.draw():
                world_data = []  # empties current world data
                world = reset_level(level)  # resets level data
                game_over = 0  # resets players states
                game_over2 = 0
                score = 0  # resets score

        if game_over == 1 and game_over2 == 1:
            if type(level) != int:
                draw_text("YOU WIN!", font, blue, (screen_width // 2) - 80, screen_height // 2)
                run = False
            else:
                level += 1
                if add:
                    total_score += score
                if level <= max_levels:
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    game_over2 = 0
                    score = 0
                else:
                    draw_text("YOU WIN!", font, blue, (screen_width // 2) - 80, screen_height // 2)
                    add = False
                    if restart_button.draw():
                        level = 0
                        world_data = []
                        world = reset_level(level)
                        game_over = 0
                        game_over2 = 0
                        score = 0
                        total_score = 0
                        save_counter = 0
                    if type(level) == int and save_counter == 0:
                        if save_button.draw():
                            f = open("score_data", "rb")  # picks which level to read
                            data = f.read()
                            data2 = pickle.loads(data)
                            f.close()
                            pickle_out = open("score_data", "wb")
                            SCORE_INP = simpledialog.askstring(title="Save score", prompt="Enter name to save score")
                            data2.append([SCORE_INP, total_score])
                            pickle.dump(data2, pickle_out)
                            pickle_out.close()
                            print(total_score)
                            save_counter += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()
pygame.quit()
