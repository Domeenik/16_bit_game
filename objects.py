import pygame
import os
import random
import math
from perlin_noise import PerlinNoise
import time

#ToDo function for generating random coords in rect

class Camera():
    def __init__(self, size=[600,400], max_size=[1000,1000]):
        self.size = size
        self.camera = pygame.Rect(0, 0, size[0], size[1])
        self.max_size = max_size

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = - target.rect.x + self.size[0]/2
        y = - target.rect.y + self.size[1]/2

        # limit to borders
        x = min(0, x)
        y = min(0, y)
        #x = max(-(self.size[0] - self.max_size[0]), x)
        #y = max(-(self.size[1] - self.max_size[1]), y)
    
        # recalculate camera rect
        self.camera = pygame.Rect(x, y, self.size[0], self.size[1])

class Map():
    def __init__(self, display_size=[600,400], size=[10,10], chunk_size=[500,500]):
        self.size = size
        self.chunk_size = chunk_size
        self.display_size = display_size

        # storing the Chunk-element
        self.chunks = []
        self.current_chunks = []
        self.current_chunk = 0

        self.generate_chunks()

        self.rect_list = []
        for chunk in self.chunks:
            self.rect_list.append(chunk.rect)

    def generate_chunks(self):
        #ToDo add external map generation -> 1. height, 2. structs, 3. keep-out, 4. forest 
        for j in range(self.size[0]):
            for k in range(self.size[1]):
                self.chunks.append(Chunk((j, k), self.chunk_size))


    def get_sprites(self, camera):
        # get collided rects
        camera_rect = pygame.Rect(- camera.camera.x, - camera.camera.y, camera.camera.width, camera.camera.height)
        collide_rects = camera_rect.collidelistall(self.rect_list)

        ret_sprites = []
        self.current_chunks = []
        for index in collide_rects:
            ret_sprites.append(self.chunks[index].sprites)
            self.current_chunks.append(self.chunks)
        
        return ret_sprites
    
    def update(self):
        for chunk in self.current_chunks:
            chunk.update()


class Chunk():
    def __init__(self, pos, size=[100, 100]):
        self.pos = pygame.Vector2(pos[1]*size[0], pos[0]*size[1])        
        self.size = size
        self.rect = pygame.Rect(pos[1]*size[0], pos[0]*size[1], size[0], size[1])

        self.sprites = pygame.sprite.Group()
        self.generate_terrain()

    def generate_terrain(self):
        trees = []
        amount = random.randint(0, 50)
        for i in range(amount):
            #trees.append(StaticEntity([random.randint(self.pos[0], self.pos[0] + self.size[0]), random.randint(self.pos[1], self.pos[1] + self.size[1])], size=[64, 64]))
            trees.append(StaticEntity([random.randint(self.rect.x, self.rect.x + self.size[0]), random.randint(self.rect.y, self.rect.y + self.size[1])], size=[64, 64]))
            if i >= random.randint(0,amount):
                trees[i].add_animation("./img/trees/pine_0.png", "idle")
            else:
                trees[i].add_animation("./img/trees/tree_0.png", "idle")
            #trees[i].update()
            self.sprites.add(trees[i])

    def update(self):
        pass
    

class Light(pygame.sprite.Sprite):
    def __init__(self, pos, size=[16,16], transparency=128, update_rate=1):
        super(Light, self).__init__()
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        self.size = size
        self.update_rate = update_rate
        self.alpha = transparency

        self.images = []
        self.image = None

        self.counter = 0
        self.index = 0

        self.noise = PerlinNoise(octaves=30, seed=777)

    def follow_target(self, target, offset):
        self.target = target
        self.offset = pygame.Vector2(offset)
        self.rect = pygame.Rect(target.rect.topleft, self.size)

    def update(self):        
        # update position
        x = self.target.pos[0] - int(self.rect.width/2)
        y = self.target.pos[1] - int(self.rect.height/2) - int(self.target.size[1]*4/3)
        self.rect = pygame.Rect(x, y, self.rect.width, self.rect.height)
        self.pos = self.rect.topleft
           
        # update image
        self.counter+=1
        if self.counter%int(self.update_rate) == 0:
            self.index += 1
        if self.index >= len(self.images):
            self.index = 0
    
        self.image = self.images[self.index]

        # try flickering
        self.image.set_alpha(80+(self.noise(self.counter/1000))*80)


    def add_animation(self, path, flip=False):
        self.images = self.load_images(path, flip=flip)

    def load_images(self, path, flip):
        images = []
        if path.endswith(".png"):
            images.append(pygame.image.load(path).convert_alpha())
        else:
            for filename in sorted(os.listdir(path)):
                if filename.endswith(".png"):
                    images.append(pygame.image.load(os.path.join(path, filename)).convert_alpha())
        # resize all images
        images = self.resize_images(images, self.size)
        images = self.flip_images(images, flip)
        images = self.set_alpha(images, self.alpha)
        return images

    def set_alpha(self, images, alpha):
        ret_images = []
        for i in range(len(images)):
            ret_img = images[i]
            ret_img.set_alpha(alpha)
            ret_images.append(ret_img)
        return ret_images

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


class Entity(pygame.sprite.Sprite):
    def __init__(self, pos, name=None, size=[16,16], update_rate=1):
        super(Entity, self).__init__()
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

        # interactions
        self.actions = []

        #Todo: add hover animation
        self.hover = None

    def add_action(self, action):
        self.actions.append(action)

    def set_hover(self, hover):
        self.hover = hover

    def update(self, pos=None):
        # update position
        if pos:
            self.pos = pygame.Vector2(pos)
        self.rect = pygame.Rect(self.pos[0] - int(self.size[0]/2), self.pos[1] - int(self.size[1]), self.size[0], self.size[1])
           
        # update image
        self.counter+=1
        if self.counter%int(self.update_rates[self.animation]*self.update_rate) == 0:
            self.index += 1
        if self.index >= len(self.animations[self.animation]):
            self.index = 0
    
        self.image = self.animations[self.animation][self.index]

        # update hover
        if not self.hover == None:
            self.hover.update(self)

    def add_animation(self, path, name, flip=False, update_rate=1):
        self.animations[name] = self.load_images(path, flip=flip)
        self.update_rates[name] = update_rate

    def correct_position(self, pos):
        self.offset = pos

    def set_animation(self, name):
        self.animation = name

    def load_images(self, path, flip):
        images = []
        if path.endswith(".png"):
            images.append(pygame.image.load(path).convert_alpha())
        else:
            for filename in sorted(os.listdir(path)):
                if filename.endswith(".png"):
                    images.append(pygame.image.load(os.path.join(path, filename)).convert_alpha())
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


#ToDo transfer dynamic animations to dynamicEntity
class DynamicEntity(Entity):
    def __init__(self, pos, name=None, size=[16,16], update_rate=1):
        super(DynamicEntity, self).__init__(pos, name, size, update_rate)
        
        self.speed = 1
        self.move_dir = pygame.Vector2(0, 0)

    def set_offset(self, offset):
        self.pos += offset

class StaticEntity(Entity):
    def __init__(self, pos, name=None, size=[16,16], update_rate=1):
        super(StaticEntity, self).__init__(pos, name, size, update_rate)
        
    def update(self, pos=None):
        # update position
        if pos:
            self.pos = pygame.Vector2(pos)
        self.rect = pygame.Rect(self.pos[0] - int(self.size[0]/2), self.pos[1] - int(self.size[1]), self.size[0], self.size[1])
           
        # update image
        self.image = self.animations[self.animation][self.index]


class Companion(DynamicEntity):
    def __init__(self, master, pos, name=None, size=[16,16], update_rate=1):
        super(Companion, self).__init__(pos, name, size, update_rate)

        self.master = master
        self.poi_rad = self.size[0]*10
        self.new_pos = pygame.Vector2(0,0)
        self.set_animation("idle_right")

    #ToDo: think about a structure
    def update(self):
        # decrease movement
        self.move_dir /= 1.5

        # update speed depending on master
        self.speed = self.master.speed/2

        # get point of interest
        self.poi = self.master.pos

        # get distance to poi
        distance = self.poi - self.pos

        # calculate a new position
        if distance.length() >= self.poi_rad - 10 or random.randint(0,1000) > 995:
            self.new_pos = self.poi + 0.5*self.poi_rad*pygame.Vector2(random.randint(-100,100)/100, random.randint(-100, 100)/100)

        # move to new position
        if not pygame.Vector2(self.new_pos - self.pos).length() < 10:
            self.move_dir -= (self.pos - self.new_pos).normalize()

            # normalize vector to length of speed
            if self.move_dir.length() > self.speed:
                self.move_dir = self.move_dir.normalize() * self.speed
        
            # add move-vetor to position
            self.pos += self.move_dir

        # if no movement reset animation and reset move vector
        if self.move_dir.length() < 0.1:
            if self.move_dir[0] > 0:
                self.set_animation("idle_right")
            elif self.move_dir[0] < 0:
                self.set_animation("idle_left")
            self.move_dir = pygame.Vector2(0,0)
        else:
            if self.move_dir[0] > 0:
                self.set_animation("walk_right")
            elif self.move_dir[0] < 0:
                self.set_animation("walk_left")

            
        super().update()

class Action():
    #ToDo restruct -> no need for key?
    def __init__(self, name, key):
        self.name = name
        self.key = key


class Player(DynamicEntity):
    def __init__(self, pos, name=None, size=[16,16], update_rate=1):
        super(Player, self).__init__(pos, name, size, update_rate)
        self.radius = 100

    def interaction(self, keys):
        # decrease movement
        self.move_dir /= 1.5

        #ToDo better way to call?
        if keys[pygame.K_e]:
            for action in self.available_actions:
                action[0].action(Action("use", "e"))
            time.sleep(0.2)

        # if no movement reset animation and reset move vector
        if self.move_dir.length() < 0.1:
            if self.move_dir[0] > 0:
                self.set_animation("idle_right")
            elif self.move_dir[0] < 0:
                self.set_animation("idle_left")
            self.move_dir = pygame.Vector2(0,0)

        # set different speeds by shift and ctrl keys
        if keys[pygame.K_LSHIFT]:
            self.speed = 3
        elif keys[pygame.K_LCTRL]:
            self.speed = 1
        else:
            self.speed = 2

        # add movement
        if keys[pygame.K_RIGHT]:
            self.move_dir[0] += self.speed
            self.set_animation("walk_right")
        if keys[pygame.K_LEFT]:
            self.move_dir[0] -= self.speed
            self.set_animation("walk_left")
        if keys[pygame.K_UP]:
            self.move_dir[1] -= self.speed
        if keys[pygame.K_DOWN]:
            self.move_dir[1] += self.speed

        # regulate to max speed
        if self.move_dir.length() > self.speed:
            self.move_dir = self.move_dir.normalize() * self.speed
        
        # add move vetor to position
        self.pos += self.move_dir

    def get_objects_in_range(self, entities):
        self.entities_in_range = []
        self.available_actions = []
        for entity in entities:
            if (self.pos - entity.pos).length() < self.radius:
                self.entities_in_range.append(entity)
                if len(entity.actions):
                    for action in entity.actions:
                        self.available_actions.append([entity, action])
        print(self.available_actions)



class Campfire(DynamicEntity):
    def __init__(self, pos, name=None, size=[16,16], update_rate=1):
        super(Campfire, self).__init__(pos, name, size, update_rate)
        self.state = True

    def toggle(self, state=True):
        self.state = state
        if self.state:
            self.set_animation("fire_on")
        else:
            self.set_animation("fire_off")

    def action(self, action):
        #ToDo shift to entity -> some general functions
        if action.name == "use":
            self.toggle(not self.state)
            