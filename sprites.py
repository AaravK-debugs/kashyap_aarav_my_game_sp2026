from ctypes import Array

import pygame as pg
from pygame.sprite import Sprite
from player_states import *
from settings import *
from utils import *
from  os import path
from state_machine import *

# shorthand for pygame vector class
vec = pg.math.Vector2


# custom collision function that uses the sprite's hitbox
# instead of the default rect for collision detection
def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)


# this function handles player collision with walls
# it checks x and y directions separately to avoid getting stuck in walls
def collide_with_walls(sprite, group, dir):

    # check horizontal collision
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)

        if hits:
            # if the wall is to the right of the player
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                # move player to the left side of the wall
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2

            # if the wall is to the left of the player
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                # move player to the right side of the wall
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2

            # stop horizontal velocity
            sprite.vel.x = 0

            # update hitbox position
            sprite.hit_rect.centerx = sprite.pos.x

    # check vertical collision
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)

        if hits:
            # if wall is below player
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2

            # if wall is above player
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2

            # stop vertical velocity
            sprite.vel.y = 0

            # update hitbox position
            sprite.hit_rect.centery = sprite.pos.y


class Player(Sprite):

    def __init__(self, game, x, y):

        # add player to sprite groups
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)

        self.game = game

        # load the sprite sheet containing animation frames
        self.spritesheet = Spritesheet(path.join(self.game.img_dir, "sprite_sheet.png"))

        # load animation frames
        self.load_images()

        # create player image
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image = self.spritesheet.get_image(0,0,TILESIZE,TILESIZE)

        # make black transparent
        self.image.set_colorkey(BLACK)

        # rectangle used for drawing the sprite
        self.rect = self.image.get_rect()

        # player velocity vector
        self.vel = vec(0,0)

        # player position stored as a vector for smoother movement
        self.pos = vec(x,y) * TILESIZE

        # separate hitbox used for collisions
        self.hit_rect = PLAYER_HIT_RECT

        # state flags
        self.jumping = False
        self.moving = False

        # animation tracking variables
        self.last_update = 0
        self.current_frame = 0

        # create state machine for player behavior
        self.state_machine = StateMachine()

        # define possible player states
        self.states: Array[State] = [
            PlayerIdleState(self),
            PlayerMoveState(self)
        ]

        # start state machine
        self.state_machine.start_machine(self.states)


    # checks keyboard input and updates velocity
    def get_keys(self):

        # reset velocity every frame
        self.vel = vec(0,0)

        keys = pg.key.get_pressed()

        # fire projectile
        if keys[pg.K_f]:
            print(' fired a projectile')
            p = Projectile(self.game, self.rect.x, self.rect.y)

        # movement controls
        if keys[pg.K_a]:
            self.vel.x = -PLAYER_SPEED

        if keys[pg.K_d]:
            self.vel.x = PLAYER_SPEED

        if keys[pg.K_w]:
            self.vel.y = -PLAYER_SPEED

        if keys[pg.K_s]:
            self.vel.y = PLAYER_SPEED

        # normalize diagonal movement so it isn't faster
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071


    # loads animation frames from the sprite sheet
    def load_images(self):

        # frames used when standing still
        self.standing_frames = [
            self.spritesheet.get_image(0,0,TILESIZE, TILESIZE), 
            self.spritesheet.get_image(TILESIZE,0,TILESIZE, TILESIZE)
        ]

        # frames used when moving
        self.moving_frames = [
            self.spritesheet.get_image(TILESIZE*2,0,TILESIZE, TILESIZE), 
            self.spritesheet.get_image(TILESIZE*3,0,TILESIZE, TILESIZE)
        ]

        # make black transparent
        for frame in self.standing_frames:
            frame.set_colorkey(BLACK)

        for frame in self.moving_frames:
            frame.set_colorkey(BLACK)


    # handles switching animation frames
    def animate(self):

        now = pg.time.get_ticks()

        # idle animation
        if not self.jumping and not self.moving:

            if now - self.last_update > 350:

                self.last_update = now

                # cycle through frames
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)

                bottom = self.rect.bottom

                # update sprite image
                self.image = self.standing_frames[self.current_frame]

                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        # movement animation
        elif self.moving:

            if now - self.last_update > 350:

                self.last_update = now

                self.current_frame = (self.current_frame + 1) % len(self.moving_frames)

                bottom = self.rect.bottom

                self.image = self.moving_frames[self.current_frame]

                self.rect = self.image.get_rect()
                self.rect.bottom = bottom


    # determines which player state should be active
    def state_check(self):

        # if player is moving
        if self.vel != vec(0,0):

            self.state_machine.transition("move")
            self.moving = True

        # otherwise player is idle
        else:
            self.state_machine.transition("idle")
            self.moving = False


    # called every frame
    def update(self):

        # update current state
        self.state_machine.update()

        # read keyboard input
        self.get_keys()

        # check for state transitions
        self.state_check()

        # update animation
        self.animate()

        # update position
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt

        # handle x-axis collisions
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.all_walls, 'x')

        # handle y-axis collisions
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.all_walls, 'y')

        # sync visual rect with hitbox
        self.rect.center = self.hit_rect.center