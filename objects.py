import pygame
import os

class Entity1(pygame.sprite.Sprite):
    def __init__(self, pos, name=None, size=[16,16], update_rate=1):
        super(Entity1, self).__init__()
        self.pos = pygame.Vector2(pos)
        self.size = size

        # sprite rect -> correct position of image
        self.rect = pygame.Rect(self.pos[0] + int(self.size[0]/2), self.pos[1] + int(self.size[1]), self.size[0], self.size[1])

        self.animations = {}
        self.update_rates = {}
        self.animation = "idle"
        self.image = None
        self.update_rate = update_rate
        self.counter = 0
        self.index = 0

    def update(self, pos=None):
        # update position
        if pos:
            self.pos = pygame.Vector2(pos)
            self.rect = pygame.Rect(self.pos[0] + int(self.size[0]/2), self.pos[1] + int(self.size[1]), self.size[0], self.size[1])
           
        # update image
        self.counter+=1
        if self.counter%int(self.update_rates[self.animation]*self.update_rate) == 0:
            self.index += 1
        if self.index >= len(self.animations[self.animation]):
            self.index = 0
    
        self.image = self.animations[self.animation][self.index]

    def add_animation(self, path, name, flip=False, update_rate=1):
        self.animations[name] = self.load_images(path, flip=flip)
        self.update_rates[name] = update_rate
        #ToDo add some kind of update range per animation

    def set_animation(self, name):
        self.animation = name

    def load_images(self, path, flip):
        images = []
        if path.endswith(".png"):
            images.append(pygame.image.load(path))
        else:
            for filename in sorted(os.listdir(path)):
                if filename.endswith(".png"):
                    images.append(pygame.image.load(os.path.join(path, filename)))
        # resize all images
        images = self.resize_images(images, self.size)
        images = self.flip_images(images, flip)
        return images

    def resize_images(self, images, size):
        ret_images = []
        for i in range(len(images)):
            ret_images.append(pygame.transform.scale(images[i], (size[0], size[1])))
        return ret_images

    def flip_images(self, images, flip):
        ret_images = []
        for i in range(len(images)):
            ret_images.append(pygame.transform.flip(images[i], flip, 0))
        return ret_images
