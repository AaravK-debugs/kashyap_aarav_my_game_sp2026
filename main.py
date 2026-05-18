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

# shorthand for 2D vectors used throughout the game
vec = pg.math.Vector2


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.current_level = 1
        # lives persist across levels — only reset on full game over or completing all levels
        self.starting_lives = 3
        self.lives = self.starting_lives

    def load_data(self):
        self.game_dir = path.dirname(__file__)
        self.img_dir = path.join(self.game_dir, 'images')
        # build path to current level's text file and parse it into a Map
        map_file = path.join(self.game_dir, f'level{self.current_level}.txt')
        self.map = Map(map_file)

    def new(self):
        self.load_data()

        # sprite groups — each group holds a specific type of sprite
        self.all_sprites     = pg.sprite.Group()
        self.all_walls       = pg.sprite.Group()
        self.all_mobs        = pg.sprite.Group()
        self.all_projectiles = pg.sprite.Group()
        self.all_coins       = pg.sprite.Group()

        # reset per-level state flags
        self.player_caught   = False
        self.coins_collected = 0

        # walk every tile in the map and spawn the right sprite for each character
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

        # snapshot total coins now so the win check works even after coins are removed
        self.total_coins = len(self.all_coins)

        # camera sized to the full map so it can scroll
        self.camera = Camera(self.map.width, self.map.height)

        self.run()

    def run(self):
        # core game loop: cap framerate, then process input -> update -> draw
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000  # dt in seconds for frame-rate-independent movement
            self.events()
            self.update()
            self.draw()

    def events(self):
        # handle OS-level events (window close button)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
                pg.quit()
                sys.exit()

    def update(self):
        # update all sprites (movement, animation, AI, etc.)
        self.all_sprites.update()

        # keep camera centered on the player
        self.camera.update(self.player)

        # remove any coin the player is touching and count it
        coin_hits = pg.sprite.spritecollide(self.player, self.all_coins, True)
        for coin in coin_hits:
            self.coins_collected += 1

        # win condition: all coins picked up
        if self.total_coins > 0 and self.coins_collected >= self.total_coins:
            self.show_win_screen()

        # lose condition: a guard set the caught flag
        if self.player_caught:
            self.show_game_over_screen()

    def draw(self):
        # clear screen each frame
        self.screen.fill(DARK_BG)

        # draw every sprite offset by the camera so the world scrolls
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))

        # draw vision cones on top of sprites (guards only)
        for mob in self.all_mobs:
            if isinstance(mob, Guard):
                mob.draw_fov(self.screen, self.camera.offset)

        # HUD: coin counter centered at top
        self.draw_text(f"Coins: {self.coins_collected} / {self.total_coins}", 22, TEXT_COLOR, WIDTH // 2, 10)

        # HUD: lives counter top left
        self.draw_text(f"Lives: {self.lives}", 22, DANGER_COLOR, 60, 10)

        pg.display.flip()

    # --- screen helpers ---

    def draw_text(self, text, size, color, x, y):
        # render a string to the screen centered horizontally at (x, y)
        font = pg.font.Font(pg.font.match_font('arial'), size)
        surf = font.render(text, True, color)
        rect = surf.get_rect()
        rect.midtop = (x, y)
        self.screen.blit(surf, rect)

    def draw_overlay(self, alpha=180):
        # paint a semi-transparent dark layer over the game frame for menu screens
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((10, 10, 20, alpha))
        self.screen.blit(overlay, (0, 0))

    def wait_for_choice(self, option_a_key, option_b_key):
        # block until the player presses one of two keys; returns 'a' or 'b'
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
        # deduct a life each time the player is caught
        self.lives -= 1

        # no lives left -> hard game over screen
        if self.lives <= 0:
            self.show_no_lives_screen()
            return

        # still have lives -> show spotted screen and let player retry the level
        self.draw()
        self.draw_overlay()
        self.draw_text("SPOTTED!", 64, DANGER_COLOR, WIDTH // 2, HEIGHT // 2 - 100)
        self.draw_text("The guard saw you...", 28, TEXT_COLOR, WIDTH // 2, HEIGHT // 2 - 40)
        self.draw_text(f"Lives remaining: {self.lives}", 28, DANGER_COLOR, WIDTH // 2, HEIGHT // 2)
        self.draw_text("R  - Retry level", 26, ACCENT_COLOR, WIDTH // 2, HEIGHT // 2 + 60)
        self.draw_text("Q  - Quit", 26, TEXT_COLOR, WIDTH // 2, HEIGHT // 2 + 100)
        pg.display.flip()

        choice = self.wait_for_choice(pg.K_r, pg.K_q)
        if choice == 'a':
            # reload the same level; lives carry over
            self.running = True
            self.player_caught = False
            self.new()
        else:
            pg.quit()
            sys.exit()

    def show_no_lives_screen(self):
        # true game over — player burned all 3 lives
        self.draw()
        self.draw_overlay()
        self.draw_text("GAME OVER", 64, DANGER_COLOR, WIDTH // 2, HEIGHT // 2 - 100)
        self.draw_text("You're out of lives.", 28, TEXT_COLOR, WIDTH // 2, HEIGHT // 2 - 30)
        self.draw_text("R  - Restart from Level 1", 26, ACCENT_COLOR, WIDTH // 2, HEIGHT // 2 + 40)
        self.draw_text("Q  - Quit", 26, TEXT_COLOR, WIDTH // 2, HEIGHT // 2 + 80)
        pg.display.flip()

        choice = self.wait_for_choice(pg.K_r, pg.K_q)
        if choice == 'a':
            # full reset: back to level 1 with a fresh set of lives
            self.lives = self.starting_lives
            self.current_level = 1
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

        # check disk for the next level file to decide which options to show
        next_level_file = path.join(path.dirname(__file__), f'level{self.current_level + 1}.txt')
        has_next = path.exists(next_level_file)

        if has_next:
            # more levels available: offer N to advance or R to replay
            self.draw_text("N  - Next Level", 26, ACCENT_COLOR, WIDTH // 2, HEIGHT // 2 + 50)
            self.draw_text("R  - Retry this level", 26, TEXT_COLOR, WIDTH // 2, HEIGHT // 2 + 90)
            pg.display.flip()
            choice = self.wait_for_choice(pg.K_r, pg.K_n)
            if choice == 'b':  # 'b' maps to the second key passed in (K_n)
                self.current_level += 1
        else:
            # all levels done — full reset so a replay starts from the beginning
            self.draw_text("You completed all levels!", 26, TEXT_COLOR, WIDTH // 2, HEIGHT // 2 + 50)
            self.draw_text("R  - Play again", 26, ACCENT_COLOR, WIDTH // 2, HEIGHT // 2 + 90)
            pg.display.flip()
            self.wait_for_choice(pg.K_r, pg.K_r)
            self.current_level = 1
            self.lives = self.starting_lives

        # launch the next (or same) level
        self.running = True
        self.new()


if __name__ == "__main__":
    g = Game()

while g.running:
    g.new()

pg.quit()