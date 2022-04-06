def level_editor():
    import pygame
    import pickle
    import time
    from os import path
    import tkinter as tk
    from tkinter import simpledialog

    pygame.init()

    ROOT = tk.Tk()
    ROOT.withdraw()

    clock = pygame.time.Clock()
    fps = 60

    screen_width = 600
    screen_height = 600

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Level editor")

    # Game variables
    tile_size = 30

    white = (255, 255, 255)
    blue = (0, 0, 255)

    # Load and scale images
    bg_img = pygame.image.load("bg image.webp")
    bg_img = pygame.transform.scale(bg_img, (600, 600))


    class World:
        def __init__(self, data):
            self.tile_list = []

            dirt_img = pygame.image.load("dirt.png")
            grass_img = pygame.image.load("grass.png")

            row_count = 0
            for row in data:
                col_count = 0
                for tile in row:
                    if tile == 1:           # dirt block
                        img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                        img_rect = img.get_rect()
                        img_rect.x = col_count*tile_size
                        img_rect.y = row_count*tile_size
                        tile = (img, img_rect)
                        self.tile_list.append(tile)
                    if tile == 2:           # grass block
                        img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                        img_rect = img.get_rect()
                        img_rect.x = col_count*tile_size
                        img_rect.y = row_count*tile_size
                        tile = (img, img_rect)
                        self.tile_list.append(tile)
                    if tile == 3:           # enemy
                        blob = Enemy(col_count*tile_size, row_count*tile_size)
                        blob_group.add(blob)
                    if tile == 4:           # horizontal moving platform
                        platform = Platform(col_count*tile_size, row_count*tile_size, 1, 0)
                        platform_group.add(platform)
                    if tile == 5:           # vertical moving platform
                        platform = Platform(col_count*tile_size, row_count*tile_size, 0, 1)
                        platform_group.add(platform)
                    if tile == 6:           # lava
                        lava = Lava(col_count*tile_size, row_count*tile_size + (tile_size // 2))
                        lava_group.add(lava)
                    if tile == 7:           # coin
                        coin = Coin(col_count*tile_size + (tile_size // 2), row_count*tile_size + (tile_size // 2))
                        coin_group.add(coin)
                    if tile == 8:           # end door
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


    class Platform(pygame.sprite.Sprite):
        def __init__(self, x, y, move_x, move_y):
            pygame.sprite.Sprite.__init__(self)
            platform_img = pygame.image.load("platform.png")
            self.image = pygame.transform.scale(platform_img, (tile_size, tile_size // 2))
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y


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


    def draw_grid():
        for c in range(21):
            # vertical lines
            pygame.draw.line(screen, white, (c * tile_size, 0), (c * tile_size, screen_height))
            # horizontal lines
            pygame.draw.line(screen, white, (0, c * tile_size), (screen_width, c * tile_size))


    blob_group = pygame.sprite.Group()
    platform_group = pygame.sprite.Group()
    lava_group = pygame.sprite.Group()
    end_group = pygame.sprite.Group()
    coin_group = pygame.sprite.Group()

    pickle_in = open(f"level11_data", "rb")
    world_data = pickle.load(pickle_in)

    tk.messagebox.showinfo(title="Info", message="Press S to save the level, click on tiles to change them",)

    run = True         # game loop
    while run:
        clock.tick(fps)
        screen.blit(bg_img, (0, 0))

        blob_group.empty()
        platform_group.empty()  # empties all sprite groups
        lava_group.empty()
        end_group.empty()
        coin_group.empty()

        world = World(world_data)
        world.draw()

        blob_group.draw(screen)
        platform_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        end_group.draw(screen)

        draw_grid()

        key = pygame.key.get_pressed()

        if pygame.mouse.get_pressed()[0] == 1:
            pos = pygame.mouse.get_pos()
            x1 = pos[0]//30
            y1 = pos[1]//30
            if 0 < x1 < 19 and 0 < y1 < 19:
                world_data[y1][x1] = (world_data[y1][x1] + 1) % 9
                pygame.display.update()
                time.sleep(0.3)

        if key[pygame.K_s]:
            USER_INP = simpledialog.askstring(title="Level Name", prompt="What do you want the level to be called?")
            pickle_out = open(f"level{USER_INP}_data", "wb")
            pickle.dump(world_data, pickle_out)
            pickle_out.close()
            tk.messagebox.showinfo(title="Saved", message="Level saved successfully", )
            run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        pygame.display.update()

