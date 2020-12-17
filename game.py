import pygame
import os
import random
import math

globl_draw_boxes = True
 
 
SIZE = WIDTH, HEIGHT = 1280, 720 #the width and height of our screen
BACKGROUND_COLOR = pygame.Color('white') #The background colod of our window
FPS = 10 #Frames per second

class Chunk():
    def __init__(self, size=100):
        self.size = size

        self.heights = []
        self.textures = []

        self.entities = []

    def add_entity(self, entity):
        self.entities.append(entity)


class Map():
    def __init__(self, size=[20, 20]):
        self.size = size

        self.chunks = [[], []]
        self.chunk_size = 100


    def load_chunk(self, pos):
        pass

    def create_chunk(self, pos):
        pass
        


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
        
        self.pos = pygame.Vector2(0, 0)
    
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
        self.pos = pygame.Vector2(0, 0)
        self.size = [self.scale*16, self.scale*16]
        self.animation_idle_right = MySprite("img/mage/idle/", scale=self.scale)
        self.animation_idle_left = MySprite("img/mage/idle/", scale=self.scale, flip=True)
        self.animation_walk_right = MySprite("img/mage/walk/", scale=self.scale)
        self.animation_walk_left = MySprite("img/mage/walk/", scale=self.scale, flip=True)
        self.group = pygame.sprite.Group(self.animation_idle_right)

        self.c = 0
        self.speed = 2
        self.acceleration = 2
        self.move_dir = pygame.Vector2(0, 0)

        self.bord_box = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        self.coll_box = pygame.Rect(self.pos[0]+(self.size[0]*(1/8)), self.pos[1]+(self.size[1]*(2/3)), self.size[0]*(6/8), self.size[1]*(1/3))
        self.pre_coll_box = self.coll_box.inflate(self.scale*self.speed*2, self.scale*self.speed*2)



    def interaction(self, collisions, keys=[]):
        # set speed via shift-key
        if keys[pygame.K_LSHIFT]:
            self.speed = 3
        elif keys[pygame.K_LCTRL]:
            self.speed = 1
        else:
            self.speed = 2

        # get blocked directions
        blocked_directions = []
        for obj in collisions:
            blocked_directions.append(pygame.Vector2(self.pre_coll_box.center[0] - obj.coll_box.center[0], self.pre_coll_box.center[1] - obj.coll_box.center[1]))
        
        # move
        if keys[pygame.K_RIGHT] or keys[pygame.K_LEFT] or keys[pygame.K_DOWN] or keys[pygame.K_UP]:
            # parse keyboard inputs
            if keys[pygame.K_RIGHT]:
                self.move_dir[0] += self.speed / self.acceleration
            if keys[pygame.K_LEFT]:
                self.move_dir[0] -= self.speed / self.acceleration
            if keys[pygame.K_DOWN]:
                self.move_dir[1] += self.speed / self.acceleration
            if keys[pygame.K_UP]:
                self.move_dir[1] -= self.speed / self.acceleration

            # set speed to self.speed independent to direction (possible with vec.scale_to_length)
            if self.move_dir.length() > self.speed:
                self.move_dir = self.move_dir.normalize() * self.speed

            # state machine for collisions
            blocked = False
            #TODO fix algorithm
            for vec in blocked_directions:
                res = vec + self.move_dir*0.8
                #print(res, vec)
                if res.length() < vec.length():
                    #blocked = True
                    if math.sqrt(vec[0]*vec[0] + self.move_dir[0]*self.move_dir[0]) > math.sqrt(vec[1]*vec[1] + self.move_dir[1]*self.move_dir[1]):
                        self.move_dir[0] = 0.0
                    if math.sqrt(vec[1]*vec[1] + self.move_dir[1]*self.move_dir[1]) > math.sqrt(vec[0]*vec[0] + self.move_dir[0]*self.move_dir[0]):
                        self.move_dir[1] = 0.0

            # add vectors
            if not blocked:
                self.pos += self.move_dir

            #set facing direction
            if self.move_dir[0] >= 0:
                self.group = pygame.sprite.Group(self.animation_walk_right)
            else:
                self.group = pygame.sprite.Group(self.animation_walk_left)
        else:
            self.move_dir /= self.acceleration
            self.idle()


    def idle(self):
        if self.move_dir[0] >= 0:
            self.group = pygame.sprite.Group(self.animation_idle_right)
        else:
            self.group = pygame.sprite.Group(self.animation_idle_left)

    def update(self, screen):
        self.c += 1
        self.animation_idle_right.pos = self.pos
        self.animation_idle_left.pos = self.pos
        self.animation_walk_right.pos = self.pos
        self.animation_walk_left.pos = self.pos
        self.animation_idle_right.update_position()
        self.animation_idle_left.update_position()
        self.animation_walk_right.update_position()
        self.animation_walk_left.update_position()

        self.bord_box = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        self.coll_box = pygame.Rect(self.pos[0]+(self.size[0]*(1/6)), self.pos[1]+(self.size[1]*(4/5)), self.size[0]*(4/6), self.size[1]*(1/5))
        self.pre_coll_box = self.coll_box.inflate(self.scale*self.speed*2, self.scale*self.speed*2)

        if self.c%int(20/self.speed) == 0:
            self.group.update()

        self.group.draw(screen)


class Entity():
    def __init__(self, image_path, pos, scale=1):
        self.image_path = image_path        
        self.pos = pos
        self.scale = scale

        img_size = pygame.image.load(self.image_path).get_size()
        self.size = [img_size[0]*self.scale, img_size[1]*self.scale]
        self.image = pygame.transform.scale(pygame.image.load(self.image_path), (img_size[0]*scale,img_size[1]*scale))

        self.update()

    def get_pos(self):
        return (self.pos)
    
    def update(self):
        self.bord_box = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        self.coll_box = pygame.Rect(self.pos[0]+(self.size[0]*(3/12)), self.pos[1]+(self.size[1]*(5/6)), self.size[0]*(6/12), self.size[1]*(1/5))


def main():

    global globl_draw_boxes

    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    clock = pygame.time.Clock()
 
    curr_chunk = Chunk(800)

    mage = Character("Dude", scale=4)
    mage.pos.xy = (WIDTH/2 - mage.size[0]), (HEIGHT/2 - mage.size[1]/2)

    #TODO add all elements to the chunk model
    trees = []
    for i in range(6):
        trees.append(Entity("./img/tree/tree_0.png", [random.randint(0, curr_chunk.size), random.randint(0, curr_chunk.size)], scale=6))
        trees.append(Entity("./img/pine/pine_0.png", [random.randint(0, curr_chunk.size), random.randint(0, curr_chunk.size)], scale=6))

    collision_boxes = []
    border_boxes = []
    for tree in trees:
        collision_boxes.append(tree.coll_box)
        border_boxes.append(tree.bord_box)


    # add trees to current chunk
    for tree in trees:
        curr_chunk.add_entity(tree)

    c = 0 
    while True:
        c += 1

        # get collisions
        collisions = pygame.Rect.collidelistall(mage.coll_box, collision_boxes)
        layer_collisions = pygame.Rect.collidelistall(mage.coll_box, border_boxes)
        pre_collisions = pygame.Rect.collidelistall(mage.pre_coll_box, collision_boxes)

        # get objects of collisions
        collision_objects = []
        for collision in pre_collisions:
            collision_objects.append(trees[i])

        # get pressed keyboard keys
        keys = pygame.key.get_pressed()

        if keys[pygame.K_b]:
            globl_draw_boxes = not globl_draw_boxes

        # move player
        mage.interaction(collision_objects, keys=keys)
        
        # draw the background
        screen.fill(pygame.Color(78, 86, 82))

        # # draw trees
        # for tree in trees:
            # screen.blit(tree.image, tree.get_pos())

        # draw trees from current chunk
        for entity in curr_chunk.entities:
            screen.blit(entity.image, entity.get_pos())

        # draw mage
        mage.update(screen)

        # draw collision and borderboxes
        if globl_draw_boxes:
            # tree boxes
            for i in range(len(trees)):
                if len(collisions) > 0:
                    if i in collisions:
                        pygame.draw.rect(screen, (255, 0, 0), trees[i].coll_box, 1)
                    else:
                        pygame.draw.rect(screen, (255, 255, 0), trees[i].coll_box, 1)
                else:
                    pygame.draw.rect(screen, (255, 255, 0), trees[i].coll_box, 1)
                pygame.draw.rect(screen, (0, 255, 0), trees[i].bord_box, 1)
            # mage box
            pygame.draw.rect(screen, (0, 255, 0), mage.bord_box, 1)
            if len(collisions) > 0:
                pygame.draw.rect(screen, (255, 0, 0), mage.coll_box, 1)
                pygame.draw.rect(screen, (255, 0, 0), mage.pre_coll_box, 1)
            else:
                pygame.draw.rect(screen, (255, 255, 0), mage.coll_box, 1)
                pygame.draw.rect(screen, (255, 255, 0), mage.pre_coll_box, 1)

        # draw trees infront of player if necessary
        if len(layer_collisions) > 0:
            for i in layer_collisions:
                screen.blit(trees[i].image, trees[i].get_pos())

        # update loop
        pygame.display.update()
        clock.tick(100)

        # check for quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
 
if __name__ == '__main__':
    main()