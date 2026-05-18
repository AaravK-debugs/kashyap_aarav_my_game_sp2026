from ctypes import Array

import pygame as pg
from pygame.sprite import Sprite
from player_states import *
from settings import *
from utils import *
from os import path
from state_machine import *

vec = pg.math.Vector2


def collide_hit_rect(one, two):
    # custom collision test that uses hit_rect instead of the full image rect
    return one.hit_rect.colliderect(two.rect)


def collide_with_walls(sprite, group, dir):
    """Push a sprite out of any walls it overlaps, one axis at a time."""

    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            # push left or right depending on which side the wall is on
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x

    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            # push up or down depending on which side the wall is on
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y


class Player(Sprite):

    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game

        # load sprite sheet and grab animation frames from it
        self.spritesheet = Spritesheet(path.join(self.game.img_dir, "sprite_sheet.png"))
        self.load_images()

        # start with the first standing frame
        self.image = self.spritesheet.get_image(0, 0, TILESIZE, TILESIZE)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()

        self.vel = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE        # world position in pixels
        self.hit_rect = PLAYER_HIT_RECT.copy() # smaller rect used for wall collision
        self.hit_rect.center = self.pos

        # animation tracking
        self.jumping      = False
        self.moving       = False
        self.last_update  = 0
        self.current_frame = 0

        # set up state machine with idle and move states
        self.state_machine = StateMachine()
        self.states = [PlayerIdleState(self), PlayerMoveState(self)]
        self.state_machine.start_machine(self.states)

    def get_keys(self):
        # reset velocity each frame, then apply direction from held keys
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()

        if keys[pg.K_f]:
            Projectile(self.game, self.rect.x, self.rect.y)

        if keys[pg.K_a]: self.vel.x = -PLAYER_SPEED
        if keys[pg.K_d]: self.vel.x =  PLAYER_SPEED
        if keys[pg.K_w]: self.vel.y = -PLAYER_SPEED
        if keys[pg.K_s]: self.vel.y =  PLAYER_SPEED

        # diagonal movement: scale down so speed is consistent in all directions
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071

    def load_images(self):
        # slice standing and moving frames out of the sprite sheet
        self.standing_frames = [
            self.spritesheet.get_image(0,            0, TILESIZE, TILESIZE),
            self.spritesheet.get_image(TILESIZE,     0, TILESIZE, TILESIZE),
        ]
        self.moving_frames = [
            self.spritesheet.get_image(TILESIZE * 2, 0, TILESIZE, TILESIZE),
            self.spritesheet.get_image(TILESIZE * 3, 0, TILESIZE, TILESIZE),
        ]
        for frame in self.standing_frames + self.moving_frames:
            frame.set_colorkey(BLACK)

    def animate(self):
        # flip frames every 350 ms; pick the right set based on whether player is moving
        now = pg.time.get_ticks()
        frames = self.moving_frames if self.moving else self.standing_frames
        if now - self.last_update > 350:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(frames)
            bottom = self.rect.bottom
            self.image = frames[self.current_frame]
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom  # keep feet on the ground after frame swap

    def state_check(self):
        # tell the state machine which state the player should be in this frame
        if self.vel != vec(0, 0):
            self.state_machine.transition("move")
            self.moving = True
        else:
            self.state_machine.transition("idle")
            self.moving = False

    def update(self):
        self.state_machine.update()
        self.get_keys()
        self.state_check()
        self.animate()

        # move on x axis, resolve wall collisions, then repeat for y
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt

        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.all_walls, 'x')

        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.all_walls, 'y')

        # sync the visible rect to the (possibly corrected) hit_rect
        self.rect.center = self.hit_rect.center


class Wall(Sprite):

    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_walls
        Sprite.__init__(self, self.groups)

        # draw wall as a solid colored tile
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(WALL_COLOR)

        # subtle 1px border so adjacent walls have visible edges
        pg.draw.rect(self.image, (30, 34, 60), self.image.get_rect(), 1)

        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE


class Coin(Sprite):

    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_coins
        Sprite.__init__(self, self.groups)

        # draw coin as a gold circle on a transparent surface
        self.image = pg.Surface((TILESIZE, TILESIZE), pg.SRCALPHA)
        pg.draw.circle(self.image, COIN_COLOR, (TILESIZE // 2, TILESIZE // 2), TILESIZE // 4)

        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE


class Guard(Sprite):

    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_mobs
        Sprite.__init__(self, self.groups)
        self.game = game

        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(GUARD_COLOR)

        self.rect     = self.image.get_rect()
        self.pos      = vec(x, y) * TILESIZE
        self.vel      = vec(0, 0)
        self.hit_rect = GUARD_HIT_RECT.copy()

        # patrol between 2 tiles left and 2 tiles right of spawn
        self.patrol_start  = vec(x - 2, y) * TILESIZE
        self.patrol_end    = vec(x + 2, y) * TILESIZE
        self.patrol_target = self.patrol_end  # start by moving right

        self.facing = vec(1, 0)  # unit vector indicating look direction

        # sync rects immediately so guard appears correctly on frame 1
        self.rect.center     = self.pos
        self.hit_rect.center = self.pos

        # state machine with patrol and alert states
        self.state_machine = StateMachine()
        self.states = [GuardPatrolState(self), GuardAlertState(self)]
        self.state_machine.start_machine(self.states)

    def move_toward_target(self):
        direction = self.patrol_target - self.pos

        # flip waypoint when close enough to the current one
        if direction.length() < 4:
            if self.patrol_target == self.patrol_end:
                self.patrol_target = self.patrol_start
            else:
                self.patrol_target = self.patrol_end

        if direction.length() > 0:
            self.vel    = direction.normalize() * GUARD_SPEED
            self.facing = direction.normalize()

    def get_cone_points(self):
        """Return the three vertices of the vision cone triangle."""
        half_angle  = GUARD_FOV_ANGLE / 2
        left_edge   = self.facing.rotate(-half_angle).normalize() * GUARD_VISION_RANGE
        right_edge  = self.facing.rotate( half_angle).normalize() * GUARD_VISION_RANGE
        center      = vec(self.pos.x, self.pos.y)
        tip_left    = self.pos + left_edge
        tip_right   = self.pos + right_edge
        return center, tip_left, tip_right

    def point_in_triangle(self, p, a, b, c):
        """Returns True if point p is inside triangle (a, b, c)."""
        def sign(p1, p2, p3):
            return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)
        d1, d2, d3 = sign(p, a, b), sign(p, b, c), sign(p, c, a)
        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
        return not (has_neg and has_pos)

    def wall_between(self, start, end):
        """
        Raycasting check: walk from start to end in 8px steps and return True
        if any step lands inside a wall rect. Prevents seeing through walls.
        """
        direction = end - start
        distance  = direction.length()
        if distance == 0:
            return False
        step = direction.normalize()
        for i in range(0, int(distance), 8):
            point = start + step * i
            for wall in self.game.all_walls:
                if wall.rect.collidepoint(point.x, point.y):
                    return True
        return False

    def can_see_player(self):
        """Two-part check: player must be in the cone AND have no wall in between."""
        if self.facing.length() == 0:
            return False
        center, tip_left, tip_right = self.get_cone_points()
        player_pos = self.game.player.pos
        # step 1: is the player inside the triangular vision cone?
        if not self.point_in_triangle(player_pos, center, tip_left, tip_right):
            return False
        # step 2: is there an unobstructed line of sight?
        return not self.wall_between(self.pos, player_pos)

    def draw_fov(self, screen, offset):
        """Draw the vision cone polygon, shifted by the camera offset."""
        if self.facing.length() == 0:
            return
        center, tip_left, tip_right = self.get_cone_points()

        # shift all three cone points by the camera offset
        cx = int(center.x    + offset.x);  cy = int(center.y    + offset.y)
        lx = int(tip_left.x  + offset.x);  ly = int(tip_left.y  + offset.y)
        rx = int(tip_right.x + offset.x);  ry = int(tip_right.y + offset.y)

        # red cone when alert, yellow when patrolling
        cone_color = (220, 60, 60, 80) if self.game.player_caught else (255, 230, 80, 45)
        cone_surf  = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        pg.draw.polygon(cone_surf, cone_color, [(cx, cy), (lx, ly), (rx, ry)])
        screen.blit(cone_surf, (0, 0))

    def update(self):
        self.state_machine.update()

        # keep facing direction in sync with velocity
        if self.vel.length() > 0:
            self.facing = self.vel.normalize()

        self.pos += self.vel * self.game.dt
        self.rect.center     = self.pos
        self.hit_rect.center = self.pos
        self.vel = vec(0, 0)  # velocity is reapplied each frame by the state


class Projectile(Sprite):

    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_projectiles
        Sprite.__init__(self, self.groups)

        self.image = pg.Surface((8, 8))
        self.image.fill(ACCENT_COLOR)
        self.rect = self.image.get_rect()

        self.pos  = vec(x, y)
        self.vel  = vec(PLAYER_SPEED * 2, 0)  # always fires to the right for now
        self.game = game

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        # destroy the projectile once it leaves the screen
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()


class Mob(Sprite):
    """Placeholder mob — currently has no behavior."""

    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_mobs
        Sprite.__init__(self, self.groups)

        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(GUARD_COLOR)
        self.rect   = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def update(self):
        pass