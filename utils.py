import pygame as pg
from settings import *


class Map:
    def __init__(self, filename):
        # read the level text file line by line into a list of strings
        self.data = []
        with open(filename, 'rt') as f:
            for line in f:
                self.data.append(line.strip())

        # derive map size in tiles and in pixels from the loaded data
        self.tilewidth  = len(self.data[0])
        self.tileheight = len(self.data)
        self.width  = self.tilewidth  * TILESIZE
        self.height = self.tileheight * TILESIZE


class Spritesheet:
    def __init__(self, filename):
        # load the full sprite sheet image once; individual frames are cut from it
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        # cut a single frame out of the sheet at position (x, y) with given size
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        new_image = pg.transform.scale(image, (width, height))
        return new_image


class Cooldown:
    """Tracks whether enough time has passed since the cooldown was started."""

    def __init__(self, time):
        self.start_time = 0
        self.time = time  # duration in milliseconds

    def start(self):
        # record the moment the cooldown begins
        self.start_time = pg.time.get_ticks()

    def ready(self):
        # returns True once `time` ms have elapsed since start()
        current_time = pg.time.get_ticks()
        return current_time - self.start_time >= self.time


class Camera:
    def __init__(self, width, height):
        # offset is added to every sprite's position when drawing
        self.offset = pg.math.Vector2(0, 0)
        self.width  = width
        self.height = height

    def apply(self, sprite):
        # return a shifted rect so the sprite draws at the correct screen position
        return sprite.rect.move(self.offset.x, self.offset.y)

    def update(self, target):
        # center the camera on the target, then clamp so it never shows outside the map
        self.offset.x = -target.rect.centerx + WIDTH  // 2
        self.offset.y = -target.rect.centery + HEIGHT // 2

        # clamp horizontally
        self.offset.x = min(0, self.offset.x)
        self.offset.x = max(-(self.width - WIDTH), self.offset.x)

        # clamp vertically
        self.offset.y = min(0, self.offset.y)
        self.offset.y = max(-(self.height - HEIGHT), self.offset.y)