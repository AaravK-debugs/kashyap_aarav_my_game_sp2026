# game engine using template from Chris Bradfield's "Making Games with Python & Pygame"
'''
Main file responsible for game loop including input, update, and draw methods.
'''

import pygame as pg
import sys
from os import path
from settings import *
from sprites import *
from utils import *
vec = pg.math.Vector2


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.current_level = 1
        print('game instantiated...')

    def load_data(self):
        self.game_dir = path.dirname(__file__)
        self.img_dir = path.join(self.game_dir, 'images')
        # load the map for the current level
        map_file = path.join(self.game_dir, f'level{self.current_level}.txt')
        self.map = Map(map_file)
        print('data is loaded')

    def new(self):
        self.load_data()
        self.all_sprites    = pg.sprite.Group()
        self.all_walls      = pg.sprite.Group()
        self.all_mobs       = pg.sprite.Group()
        self.all_projectiles = pg.sprite.Group()
        self.all_coins      = pg.sprite.Group()

        # game state flags
        self.player_caught  = False
        self.coins_collected = 0

        # read the map and spawn sprites
        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                if tile == '1':
                    Wall(self, col, row)
                if tile == 'P':
                    self.player = Player(self, col, row)
                if tile == 'M':
                    Mob(self, col, row)
                if tile == 'G':
                    Guard(self, col, row)
                if tile == 'C':
                    Coin(self, col, row)

        # store total coins so win condition works correctly
        self.total_coins = len(self.all_coins)
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
                self.running = False
                pg.quit()
                sys.exit()

    def update(self):
        self.all_sprites.update()

        # collect coins on touch
        coin_hits = pg.sprite.spritecollide(self.player, self.all_coins, True)
        for coin in coin_hits:
            self.coins_collected += 1

        # check win: all coins collected
        if self.total_coins > 0 and self.coins_collected >= self.total_coins:
            self.show_win_screen()

        # check lose: guard spotted player
        if self.player_caught:
            self.show_game_over_screen()

    def draw(self):
        # fill background with dark color
        self.screen.fill(DARK_BG)
        self.all_sprites.draw(self.screen)

        # draw each guard's vision cone on top
        for mob in self.all_mobs:
            if isinstance(mob, Guard):
                mob.draw_fov(self.screen)

        # coin counter top center
        self.draw_text(f"Coins: {self.coins_collected} / {self.total_coins}", 22, TEXT_COLOR, WIDTH // 2, 10)

        pg.display.flip()

    # --- screen helpers ---

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(pg.font.match_font('arial'), size)
        surf = font.render(text, True, color)
        rect = surf.get_rect()
        rect.midtop = (x, y)
        self.screen.blit(surf, rect)

    def draw_overlay(self, alpha=180):
        # semi-transparent dark overlay for screens
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((10, 10, 20, alpha))
        self.screen.blit(overlay, (0, 0))

    def wait_for_choice(self, option_a_key, option_b_key):
        # waits for the player to press one of two keys, returns 'a' or 'b'
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == option_a_key:
                        return 'a'
                    if event.key == option_b_key:
                        return 'b'

    def show_game_over_screen(self):
        # draw the current frame then overlay the game over screen
        self.draw()
        self.draw_overlay()
        self.draw_text("SPOTTED!", 64, DANGER_COLOR, WIDTH // 2, HEIGHT // 2 - 80)
        self.draw_text("The guard saw you...", 28, TEXT_COLOR, WIDTH // 2, HEIGHT // 2)
        self.draw_text("R  — Retry level", 26, ACCENT_COLOR, WIDTH // 2, HEIGHT // 2 + 60)
        self.draw_text("Q  — Quit", 26, TEXT_COLOR, WIDTH // 2, HEIGHT // 2 + 100)
        pg.display.flip()

        choice = self.wait_for_choice(pg.K_r, pg.K_q)
        if choice == 'a':
            # restart the current level
            self.running = True
            self.player_caught = False
            self.new()
        else:
            pg.quit()
            sys.exit()

    def show_win_screen(self):
        self.draw()
        self.draw_overlay()
        self.draw_text("LEVEL COMPLETE!", 56, ACCENT_COLOR, WIDTH // 2, HEIGHT // 2 - 90)
        self.draw_text(f"Coins collected: {self.coins_collected}", 28, COIN_COLOR, WIDTH // 2, HEIGHT // 2 - 20)

        # check if a next level file exists
        next_level_file = path.join(path.dirname(__file__), f'level{self.current_level + 1}.txt')
        has_next = path.exists(next_level_file)

        if has_next:
            self.draw_text("N  — Next Level", 26, ACCENT_COLOR, WIDTH // 2, HEIGHT // 2 + 50)
            self.draw_text("R  — Retry this level", 26, TEXT_COLOR, WIDTH // 2, HEIGHT // 2 + 90)
            pg.display.flip()
            choice = self.wait_for_choice(pg.K_r, pg.K_n)
            if choice == 'b':
                self.current_level += 1
        else:
            self.draw_text("You completed all levels!", 26, TEXT_COLOR, WIDTH // 2, HEIGHT // 2 + 50)
            self.draw_text("R  — Play again", 26, ACCENT_COLOR, WIDTH // 2, HEIGHT // 2 + 90)
            pg.display.flip()
            self.wait_for_choice(pg.K_r, pg.K_r)

        # restart into new (or same) level
        self.running = True
        self.new()


if __name__ == "__main__":
    g = Game()

while g.running:
    g.new()

pg.quit()