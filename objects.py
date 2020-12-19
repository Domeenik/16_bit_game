import pygame
import os

class MySprite(pygame.sprite.Sprite):
    def __init__(self, path, update_rate=1):
        super(MySprite, self).__init__()
        self.path = path
        self.images = []
        self.flip = True
        self.scale = 1

        self.update_rate = update_rate
        self.counter = 0

        self.load_images()

    def load_images(self):
        if self.path.endswith(".png"):
            self.images.append(pygame.image.load(self.path))
        else:
            for filename in sorted(os.listdir(self.path)):
                if filename.endswith(".png"):
                    self.images.append(pygame.image.load(os.path.join(self.path, filename)))
        self.index = 0
        self.image = self.images[self.index]

        self.pos = pygame.Vector2(0, 0)
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.scale*2, self.scale*2)

    def flip(self, flip):
        self.flip = flip
        if self.flip:
            for image in self.images:
                image = pygame.transform.flip(IMAGE, 1, 0)

    def set_scale(self, scale):
        self.scale = scale

    def update(self, pos=None):
        # update position
        if pos:
            self.pos = pos
            self.rect = pygame.Rect(self.pos[0], self.pos[1], 150, 198)

        # update image
        self.counter+=1
        if self.counter%self.update_rate == 0:
            self.index += 1
        if self.index >= len(self.images):
            self.index = 0
    
        self.image = self.images[self.index]

class Entity(object):
    def __init__(self, pos, size=[16, 16]):
        self.size = size
        self.pos = pygame.Vector2(pos)

        self.animations = {}

        self.static = False

    def set_size(self, size):
        self.size = size

    def add_animation(self, sprite, name):
        self.animations[name] = sprite
        self.set_animation(name)

    def set_animation(self, name):
        self.animation = self.animations[name]

    def update(self):
        self.animation.update()