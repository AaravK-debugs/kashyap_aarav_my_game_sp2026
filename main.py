# game engine using template from Chris Bradfield's "Making Games with Python & Pygame"
# I can push from vs code...
# I can push more code from vs code to github
'''
Main file responsible for game loop including input, update, and draw methods.

Tools for game development.

# creating pixel art:
https://www.piskelapp.com/

# free game assets:
https://opengameart.org/

# free sprite sheets:
https://www.kenney.nl/assets

# sound effects:
https://www.bfxr.net/
# music:
https://incompetech.com/music/royalty-free/


'''

import pygame as pg
import sys
from os import path
from settings import *
from sprites import *
from utils import *
vec = pg.math.Vector2

# import settings


# the game class that will be instantiated in order to run the game...
class Game:
    def __init__(self):
        pg.init()
        # setting up pygame screen using tuple value for width height
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)

        self.clock = pg.time.Clock()
        self.running = True
        self.playing = True
        self.game_cooldown = Cooldown(5000)
        print('game instantiated...')
        
    
    # a method is a function tied to a Class

    def load_data(self):
        self.game_dir = path.dirname(__file__)
        self.img_dir = path.join(self.game_dir, 'images')
        self.wall_img = pg.image.load(path.join(self.img_dir, 'wall_art.png')).convert_alpha()
        self.map = Map(path.join(self.game_dir, 'level1.txt'))
        print('data is loaded')

    def new(self):
        self.load_data()
        self.all_sprites = pg.sprite.Group()
        self.all_walls = pg.sprite.Group()
        self.all_mobs = pg.sprite.Group()
        self.all_projectiles = pg.sprite.Group()
        self.all_coins = pg.sprite.Group()

        # flags for game state
        self.player_caught = False
        self.coins_collected = 0
        # self.player = Player(self, 15, 15)
        # self.mob = Mob(self, 4, 4) 
        # self.wall = Wall(self, WIDTH/2/TILESIZE, HEIGHT/2/TILESIZE)
        for row, tiles in enumerate(self.map.data):
            for col, tile, in enumerate(tiles):
                if tile == '1':
                    # call class constructor without assigning variable...when
                    Wall(self, col, row)
                if tile == 'P':
                    self.player = Player(self, col, row)
                if tile == 'M':
                    Mob(self, col, row)
                if tile == 'G':
                    # spawn a guard at this map position
                    Guard(self, col, row)
                if tile == 'C':
                    Coin(self, col, row)
        self.run()

    def run(self):
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.MOUSEBUTTONUP:
                print("i can get mouse input")
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_k:
                    print("i can determine when keys are pressed")

            if event.type == pg.KEYUP:
                if event.key == pg.K_k:
                    print("i can determine when keys are released")
    


    def quit(self):
        pass

    def update(self):
        self.all_sprites.update()

        # check if player touched a coin — remove it and increase counter
        coin_hits = pg.sprite.spritecollide(self.player, self.all_coins, True)
        for coin in coin_hits:
            self.coins_collected += 1

        # stop the game loop if a guard caught the player
        if self.player_caught:
            self.draw()
            pg.time.wait(2000)
            self.running = False

    
    def draw(self):
        self.screen.fill(BLUE)
        self.all_sprites.draw(self.screen)

        # draw each guard's vision cone on top of sprites
        for guard in self.all_mobs:
            if isinstance(guard, Guard):
                guard.draw_fov(self.screen)

        # show coin counter in top left
        self.draw_text("Coins: " + str(self.coins_collected), 24, WHITE, WIDTH / 2, TILESIZE)

        # show game over if caught
        if self.player_caught:
            self.draw_text("GAME OVER - You were spotted!", 36, RED, WIDTH / 2, HEIGHT / 2)

        # show win message if all coins collected
        if len(self.all_coins) == 0 and self.coins_collected > 0:
            self.draw_text("YOU WIN! All coins collected!", 36, YELLOW, WIDTH / 2, HEIGHT / 2)

        pg.display.flip()

    def draw_text(self, text, size, color, x, y):
        font_name = pg.font.match_font('arial')
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x,y)
        self.screen.blit(text_surface, text_rect)

if __name__ == "__main__":
    g = Game()

while g.running:
    g.new()


pg.quit()