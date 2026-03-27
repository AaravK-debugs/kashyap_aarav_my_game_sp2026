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
    return one.hit_rect.colliderect(two.rect)


def collide_with_walls(sprite, group, dir):

    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x

    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
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

        self.spritesheet = Spritesheet(path.join(self.game.img_dir, "sprite_sheet.png"))
        self.load_images()

        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image = self.spritesheet.get_image(0, 0, TILESIZE, TILESIZE)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()

        self.vel = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE
        self.hit_rect = PLAYER_HIT_RECT.copy()
        self.hit_rect.center = self.pos

        self.jumping = False
        self.moving = False
        self.last_update = 0
        self.current_frame = 0

        self.state_machine = StateMachine()
        self.states = [PlayerIdleState(self), PlayerMoveState(self)]
        self.state_machine.start_machine(self.states)

    def get_keys(self):
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()

        if keys[pg.K_f]:
            Projectile(self.game, self.rect.x, self.rect.y)

        if keys[pg.K_a]:
            self.vel.x = -PLAYER_SPEED
        if keys[pg.K_d]:
            self.vel.x = PLAYER_SPEED
        if keys[pg.K_w]:
            self.vel.y = -PLAYER_SPEED
        if keys[pg.K_s]:
            self.vel.y = PLAYER_SPEED

        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071

    def load_images(self):
        self.standing_frames = [
            self.spritesheet.get_image(0, 0, TILESIZE, TILESIZE),
            self.spritesheet.get_image(TILESIZE, 0, TILESIZE, TILESIZE)
        ]
        self.moving_frames = [
            self.spritesheet.get_image(TILESIZE * 2, 0, TILESIZE, TILESIZE),
            self.spritesheet.get_image(TILESIZE * 3, 0, TILESIZE, TILESIZE)
        ]
        for frame in self.standing_frames + self.moving_frames:
            frame.set_colorkey(BLACK)

    def animate(self):
        now = pg.time.get_ticks()
        frames = self.moving_frames if self.moving else self.standing_frames
        if now - self.last_update > 350:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(frames)
            bottom = self.rect.bottom
            self.image = frames[self.current_frame]
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom

    def state_check(self):
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

        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt

        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.all_walls, 'x')

        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.all_walls, 'y')

        self.rect.center = self.hit_rect.center


class Wall(Sprite):

    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_walls
        Sprite.__init__(self, self.groups)

        # draw wall as a solid colored tile — no image needed
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(WALL_COLOR)

        # add a subtle 1px darker border so walls have definition
        pg.draw.rect(self.image, (30, 34, 60), self.image.get_rect(), 1)

        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE


class Coin(Sprite):

    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_coins
        Sprite.__init__(self, self.groups)

        # draw coin as a glowing gold circle
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

        # draw guard as a colored square
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(GUARD_COLOR)

        self.rect = self.image.get_rect()
        self.pos = vec(x, y) * TILESIZE
        self.vel = vec(0, 0)
        self.hit_rect = GUARD_HIT_RECT.copy()

        # patrol 2 tiles left and right from spawn
        self.patrol_start = vec(x - 2, y) * TILESIZE
        self.patrol_end   = vec(x + 2, y) * TILESIZE
        self.patrol_target = self.patrol_end

        # start facing right
        self.facing = vec(1, 0)

        # position rect immediately so guard is visible on frame 1
        self.rect.center = self.pos
        self.hit_rect.center = self.pos

        self.state_machine = StateMachine()
        self.states = [GuardPatrolState(self), GuardAlertState(self)]
        self.state_machine.start_machine(self.states)

    def move_toward_target(self):
        direction = self.patrol_target - self.pos

        # flip patrol direction when close enough to target
        if direction.length() < 4:
            if self.patrol_target == self.patrol_end:
                self.patrol_target = self.patrol_start
            else:
                self.patrol_target = self.patrol_end

        if direction.length() > 0:
            self.vel = direction.normalize() * GUARD_SPEED
            self.facing = direction.normalize()

    # single source of truth for the cone shape — used by both detection and drawing
    def get_cone_points(self):
        half_angle = GUARD_FOV_ANGLE / 2
        left_edge  = self.facing.rotate(-half_angle).normalize() * GUARD_VISION_RANGE
        right_edge = self.facing.rotate( half_angle).normalize() * GUARD_VISION_RANGE
        center    = vec(self.pos.x, self.pos.y)
        tip_left  = self.pos + left_edge
        tip_right = self.pos + right_edge
        return center, tip_left, tip_right

    def point_in_triangle(self, p, a, b, c):
        def sign(p1, p2, p3):
            return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)
        d1, d2, d3 = sign(p, a, b), sign(p, b, c), sign(p, c, a)
        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
        return not (has_neg and has_pos)

    def wall_between(self, start, end):
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
        if self.facing.length() == 0:
            return False
        center, tip_left, tip_right = self.get_cone_points()
        player_pos = self.game.player.pos
        if not self.point_in_triangle(player_pos, center, tip_left, tip_right):
            return False
        return not self.wall_between(self.pos, player_pos)

    def draw_fov(self, screen):
        if self.facing.length() == 0:
            return
        center, tip_left, tip_right = self.get_cone_points()
        # red cone when alert, soft yellow otherwise
        cone_color = (220, 60, 60, 80) if self.game.player_caught else (255, 230, 80, 45)
        cone_surf = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        pg.draw.polygon(cone_surf, cone_color, [
            (int(center.x),    int(center.y)),
            (int(tip_left.x),  int(tip_left.y)),
            (int(tip_right.x), int(tip_right.y))
        ])
        screen.blit(cone_surf, (0, 0))

    def update(self):
        self.state_machine.update()

        if self.vel.length() > 0:
            self.facing = self.vel.normalize()

        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        self.hit_rect.center = self.pos
        self.vel = vec(0, 0)


class Projectile(Sprite):

    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_projectiles
        Sprite.__init__(self, self.groups)

        self.image = pg.Surface((8, 8))
        self.image.fill(ACCENT_COLOR)
        self.rect = self.image.get_rect()

        self.pos = vec(x, y)
        self.vel = vec(PLAYER_SPEED * 2, 0)
        self.game = game

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()


class Mob(Sprite):

    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_mobs
        Sprite.__init__(self, self.groups)

        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(GUARD_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def update(self):
        pass