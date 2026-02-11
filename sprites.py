import pygame as pg
from pygame.sprite import Sprite
from settings import *

vec = pg.math.Vector2  # vector shortcut

class Player(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites # add to sprite group
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE)) # player image
        self.image.fill(WHITE)
        self.rect = self.image.get_rect() # hitbox
        self.vel = vec(0,0)
        self.pos = vec(x,y) * TILESIZE # position in pixels
    def get_keys(self):
        self.vel = vec(0,0)  # reset movement
        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            self.vel.x = -PLAYER_SPEED
        if keys[pg.K_d]:
            self.vel.x = PLAYER_SPEED
        if keys[pg.K_w]:
            self.vel.y = -PLAYER_SPEED
        if keys[pg.K_s]:
            self.vel.y = PLAYER_SPEED
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071 # slow diagonal movement

    def update(self):
        # print("player updating")
        self.get_keys() # read input
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt  # move player


class Mob(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites # add to sprite group
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE)) # mob image
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.vel = vec(1,0) # move direction
        self.pos = vec(x,y) * TILESIZE
        self.speed = 10  # movement speed
    def update(self):
        hits = pg.sprite.spritecollide(self, self.game.all_walls, True) #check wall hit
        if hits:
            print("collided")
            self.speed = 100 # change speed on hit
        
        if self.rect.x > WIDTH or self.rect.x < 0: 
            self.speed *= -1 # reverse direction
            self.pos.y += TILESIZE # move down
        self.pos += self.speed * self.vel
        self.rect.center = self.pos


class Wall(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_walls  # add to groups
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))  # wall image
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.vel = vec(0,0) # no movement
        self.pos = vec(x,y) * TILESIZE
        self.rect.center = self.pos  # place wall
    def update(self):
        pass  # walls don’t move


class Coin(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites # add to sprite group    
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))  # coin image
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.vel = vec(0,0) # no movement
        self.pos = vec(x,y) * TILESIZE
    def update(self):
        pass # coin doesn’t move