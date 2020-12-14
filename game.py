import pygame
import os
import random
 
 
SIZE = WIDTH, HEIGHT = 1280, 720 #the width and height of our screen
BACKGROUND_COLOR = pygame.Color('white') #The background colod of our window
FPS = 10 #Frames per second
 
class MySprite(pygame.sprite.Sprite):
    def __init__(self, path, scale=1, flip=False):
        super(MySprite, self).__init__()
 
        self.images = []
        
        for filename in os.listdir(path):
            if filename.endswith(".png"):
                img_size = pygame.image.load(os.path.join(path, filename)).get_size()
                if flip:
                    self.images.append(pygame.transform.flip(pygame.transform.scale(pygame.image.load(os.path.join(path, filename)), (img_size[0]*scale,img_size[1]*scale)), 1, 0))
                else:
                    self.images.append(pygame.transform.scale(pygame.image.load(os.path.join(path, filename)), (img_size[0]*scale,img_size[1]*scale)))
                # print(os.path.join(path, filename))
            else:
                continue
 
        self.index = 0
 
        self.image = self.images[self.index]
        
        self.pos = [0,0]
    
        self.rect = pygame.Rect(self.pos[0], self.pos[1], 150, 198)
 
    def update(self):
        self.index += 1
 
        if self.index >= len(self.images):
            self.index = 0
        
        self.image = self.images[self.index]
        
    def update_position(self):
        self.rect = pygame.Rect(self.pos[0], self.pos[1], 150, 198)
        
        self.image = self.images[self.index]
        

class Character():
    def __init__(self, name, scale=1):
        self.name = name
        self.scale = scale
        self.position = [0, 0]


        self.animation_idle_right = MySprite("img/mage/idle/", scale=self.scale)
        self.animation_idle_left = MySprite("img/mage/idle/", scale=self.scale, flip=True)
        self.animation_walk_right = MySprite("img/mage/walk/", scale=self.scale)
        self.animation_walk_left = MySprite("img/mage/walk/", scale=self.scale, flip=True)

        self.group = pygame.sprite.Group(self.animation_idle_right)

        self.c = 0
        
        self.orientation = 0

    def walk(self, speed, orientation):
        self.orientation = orientation
        if orientation == 0:
            self.position[0] += speed
            self.group = pygame.sprite.Group(self.animation_walk_right)
        elif orientation == 1:
            self.position[0] -= speed
            self.group = pygame.sprite.Group(self.animation_walk_left)
        elif orientation == 2:
            self.position[1] += speed
        elif orientation == 3:
            self.position[1] -= speed


    def idle(self):
        if self.orientation == 0:
            self.group = pygame.sprite.Group(self.animation_idle_right)
        elif self.orientation == 1:
            self.group = pygame.sprite.Group(self.animation_idle_left)

    def update(self, screen):
        self.c += 1
        self.animation_idle_right.pos = self.position
        self.animation_idle_left.pos = self.position
        self.animation_walk_right.pos = self.position
        self.animation_walk_left.pos = self.position
        self.animation_idle_right.update_position()
        self.animation_idle_left.update_position()
        self.animation_walk_right.update_position()
        self.animation_walk_left.update_position()

        if self.c%10 == 0:
            self.group.update()

        self.group.draw(screen)


class Entity():
    def __init__(self, image_path, pos, scale=1):
        self.image_path = image_path        
        self.pos = pos
        self.scale = scale

        img_size = pygame.image.load(self.image_path).get_size()
        self.image = pygame.transform.scale(pygame.image.load(self.image_path), (img_size[0]*scale,img_size[1]*scale))

    def get_pos(self):
        return (self.pos)

def main():
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    clock = pygame.time.Clock()
 
    mage = Character("Dude", scale=4)

    trees = []
    for i in range(6):
        trees.append(Entity("./img/tree/tree_0.png", [random.randint(0, WIDTH), random.randint(0, HEIGHT)], scale=6))
        trees.append(Entity("./img/pine/pine_0.png", [random.randint(0, WIDTH), random.randint(0, HEIGHT)], scale=6))

    c = 0
 
    while True:
        c += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_RIGHT] or keys[pygame.K_LEFT] or keys[pygame.K_DOWN] or keys[pygame.K_UP]:
            if keys[pygame.K_RIGHT]:
                mage.walk(2, 0)
            if keys[pygame.K_LEFT]:
                mage.walk(2, 1)
            if keys[pygame.K_DOWN]:
                mage.walk(2, 2)
            if keys[pygame.K_UP]:
                mage.walk(2, 3)
        else:
            mage.idle()
                    
        screen.fill(pygame.Color(78, 86, 82))
        
        for tree in trees:
            screen.blit(tree.image, tree.get_pos())
        mage.update(screen)

        pygame.display.update()
        clock.tick(100)
 
if __name__ == '__main__':
    main()