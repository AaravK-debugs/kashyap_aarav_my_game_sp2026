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


class Wall(Sprite):

    def __init__(self, game, x, y):
        # add wall to sprite groups
        self.groups = game.all_sprites, game.all_walls
        Sprite.__init__(self, self.groups)

        # draw wall as a colored tile
        self.image = game.wall_img
        self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE


class Coin(Sprite):

    def __init__(self, game, x, y):
        # add coin to sprite groups
        self.groups = game.all_sprites, game.all_coins
        Sprite.__init__(self, self.groups)

        # draw coin as a small yellow circle
        self.image = pg.Surface((TILESIZE, TILESIZE), pg.SRCALPHA)
        pg.draw.circle(self.image, YELLOW, (TILESIZE // 2, TILESIZE // 2), TILESIZE // 4)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE


class Guard(Sprite):

    def __init__(self, game, x, y):
        # add guard to sprite groups
        self.groups = game.all_sprites, game.all_mobs
        Sprite.__init__(self, self.groups)

        self.game = game

        # draw guard as a red square
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(GUARD_COLOR)
        self.rect = self.image.get_rect()

        # guard position as a vector
        self.pos = vec(x, y) * TILESIZE
        self.vel = vec(0, 0)

        # hitbox for collisions
        self.hit_rect = GUARD_HIT_RECT.copy()

        # patrol between start point and a point to the right
        self.patrol_start = vec(x, y) * TILESIZE
        self.patrol_end = vec(x + 3, y) * TILESIZE
        # which patrol point the guard is moving toward
        self.patrol_target = self.patrol_end

        # the direction the guard is currently facing (starts facing right)
        self.facing = vec(1, 0)

        # set up guard state machine
        self.state_machine = StateMachine()
        self.states = [
            GuardPatrolState(self),
            GuardAlertState(self)
        ]
        self.state_machine.start_machine(self.states)

    # move the guard toward its current patrol target
    def move_toward_target(self):
        direction = self.patrol_target - self.pos

        # if close enough to target, switch to the other patrol point
        if direction.length() < 4:
            if self.patrol_target == self.patrol_end:
                self.patrol_target = self.patrol_start
            else:
                self.patrol_target = self.patrol_end

        # move toward target at guard speed
        if direction.length() > 0:
            self.vel = direction.normalize() * GUARD_SPEED
            # update facing here so it always matches the drawn cone
            self.facing = direction.normalize()

    # calculates the three cone points — shared by detection AND drawing
    # this guarantees what you see is exactly what detects you
    def get_cone_points(self):
        half_angle = GUARD_FOV_ANGLE / 2
        left_edge = self.facing.rotate(-half_angle).normalize() * GUARD_VISION_RANGE
        right_edge = self.facing.rotate(half_angle).normalize() * GUARD_VISION_RANGE
        center = vec(self.pos.x, self.pos.y)
        tip_left = self.pos + left_edge
        tip_right = self.pos + right_edge
        return center, tip_left, tip_right

    # checks if point P is inside triangle A B C using cross product signs
    def point_in_triangle(self, p, a, b, c):
        def sign(p1, p2, p3):
            return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)
        d1 = sign(p, a, b)
        d2 = sign(p, b, c)
        d3 = sign(p, c, a)
        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
        return not (has_neg and has_pos)

    # steps along a ray checking if any wall blocks the view
    def wall_between(self, start, end):
        direction = end - start
        distance = direction.length()
        if distance == 0:
            return False
        step = direction.normalize()
        for i in range(0, int(distance), 8):
            point = start + step * i
            for wall in self.game.all_walls:
                if wall.rect.collidepoint(point.x, point.y):
                    return True
        return False

    # detection uses the exact same triangle as draw_fov — no mismatch possible
    def can_see_player(self):
        if self.facing.length() == 0:
            return False
        center, tip_left, tip_right = self.get_cone_points()
        player_pos = self.game.player.pos
        # player must be inside the visible triangle
        if not self.point_in_triangle(player_pos, center, tip_left, tip_right):
            return False
        # and no wall blocking the line of sight
        return not self.wall_between(self.pos, player_pos)

    # draws the cone using the exact same points used in detection
    def draw_fov(self, screen):
        if self.facing.length() == 0:
            return
        center, tip_left, tip_right = self.get_cone_points()
        # yellow normally, red when player is caught
        if self.game.player_caught:
            cone_color = (255, 0, 0, 80)
        else:
            cone_color = (255, 255, 0, 60)
        cone_surface = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        pg.draw.polygon(cone_surface, cone_color, [
            (int(center.x), int(center.y)),
            (int(tip_left.x), int(tip_left.y)),
            (int(tip_right.x), int(tip_right.y))
        ])
        screen.blit(cone_surface, (0, 0))

    def update(self):
        # update state machine each frame
        self.state_machine.update()

        # track which direction the guard is facing based on movement
        if self.vel.length() > 0:
            self.facing = self.vel.normalize()

        # move guard
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        self.hit_rect.center = self.pos

        # stop guard velocity after applying it
        self.vel = vec(0, 0)


class Projectile(Sprite):

    def __init__(self, game, x, y):
        # add projectile to sprite groups
        self.groups = game.all_sprites, game.all_projectiles
        Sprite.__init__(self, self.groups)

        # draw projectile as a small white square
        self.image = pg.Surface((8, 8))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()

        self.pos = vec(x, y)
        self.vel = vec(PLAYER_SPEED * 2, 0)

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos

        # remove projectile if it goes off screen
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()


class Mob(Sprite):

    def __init__(self, game, x, y):
        # add mob to sprite groups
        self.groups = game.all_sprites, game.all_mobs
        Sprite.__init__(self, self.groups)

        # draw mob as a blue square
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def update(self):
        pass