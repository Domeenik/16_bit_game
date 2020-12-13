import pygame
import os
 
 
SIZE = WIDTH, HEIGHT = 600, 400 #the width and height of our screen
BACKGROUND_COLOR = pygame.Color('white') #The background colod of our window
FPS = 10 #Frames per second
 
class MySprite(pygame.sprite.Sprite):
    def __init__(self, path, scale=1):
        super(MySprite, self).__init__()
 
        self.images = []
        
        for filename in os.listdir(path):
            if filename.endswith(".png"):
                img_size = pygame.image.load(os.path.join(path, filename)).get_size()
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
        
 
def main():
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    mage_walk = MySprite("img/mage/walk/", scale=6)
    mage_idle = MySprite("img/mage/idle/", scale=6)

    my_group = pygame.sprite.Group(mage_idle)
    clock = pygame.time.Clock()
 
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
                mage_idle.pos[0] += 2
            if keys[pygame.K_LEFT]:
                mage_idle.pos[0] -= 2
            if keys[pygame.K_DOWN]:
                mage_idle.pos[1] += 2
            if keys[pygame.K_UP]:
                mage_idle.pos[1] -= 2
            my_group = pygame.sprite.Group(mage_walk)
        else:
            mage_idle.pos = mage_walk.pos
            my_group = pygame.sprite.Group(mage_idle)
            mage_idle.update_position()
                    
        
        if c%10 == 0:
        
            my_group.update()
        mage_walk.update_position()
        screen.fill(BACKGROUND_COLOR)
        my_group.draw(screen)
        pygame.display.update()
        clock.tick(100)
 
if __name__ == '__main__':
    main()