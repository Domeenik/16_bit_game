import pygame
import os
import random
import math
import time
import operator

globl_draw_boxes = False
 
 
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
        
        if path.endswith(".png"):
            img_size = pygame.image.load(path).get_size()
            if flip:
                self.images.append(pygame.transform.flip(pygame.transform.scale(pygame.image.load(path), (img_size[0]*scale,img_size[1]*scale)), 1, 0))
            else:
                self.images.append(pygame.transform.scale(pygame.image.load(path), (img_size[0]*scale,img_size[1]*scale)))
        else:
            for filename in sorted(os.listdir(path)):
                if filename.endswith(".png"):
                    img_size = pygame.image.load(os.path.join(path, filename)).get_size()
                    if flip:
                        self.images.append(pygame.transform.flip(pygame.transform.scale(pygame.image.load(os.path.join(path, filename)), (img_size[0]*scale,img_size[1]*scale)), 1, 0))
                    else:
                        self.images.append(pygame.transform.scale(pygame.image.load(os.path.join(path, filename)), (img_size[0]*scale,img_size[1]*scale)))
                    # print(os.path.join(path, filename))
                else:
                    continue

        # load config
        # if path.endswith(".png"):
        #     self.config = ConfigHandler(path.replace(".png", ".json"))
        # else:
        #     self.config = ConfigHandler()
 
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

        # hover animation
        self.hover = False
        self.animation_hover = MySprite("img/hover/msg/", scale=int(self.scale/2))
        self.group_hover = pygame.sprite.Group(self.animation_hover)

        self.c = 0
        self.speed = 2
        self.acceleration = 2
        self.move_dir = pygame.Vector2(0, 0)

        self.bord_box = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        self.coll_box = pygame.Rect(self.pos[0]+(self.size[0]*(1/8)), self.pos[1]+(self.size[1]*(2/3)), self.size[0]*(6/8), self.size[1]*(1/3))
        self.pre_coll_box = self.coll_box.inflate(self.scale*self.speed*2, self.scale*self.speed*2)



    def interaction(self, collisions, keys=[]):
        # hover animation
        if keys[pygame.K_h]:
            self.hover = not self.hover
            time.sleep(0.2)

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

        if self.hover:
            self.animation_hover.pos = pygame.Vector2(self.pos[0] + self.size[0]*2/5, self.pos[1] - self.size[1]/2)
            self.animation_hover.pos[1] -= (self.size[1]/16) * math.sin(self.c*self.speed/200.0)
            self.animation_hover.update_position()
            if self.c%int(30/self.speed) == 0:
                self.group_hover.update()
            self.group_hover.draw(screen)


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


class Companion():
    def __init__(self, name, scale=1):
        self.name = name
        self.scale = scale
        self.pos = pygame.Vector2(0, 0)
        self.size = [self.scale*16, self.scale*16]
        self.animation_idle_right = MySprite("img/cat/cat_0.png", scale=self.scale, flip=True)
        self.animation_idle_left = MySprite("img/cat/cat_0.png", scale=self.scale)
        self.animation_walk_right = MySprite("img/cat/walk/", scale=self.scale, flip=True)
        self.animation_walk_left = MySprite("img/cat/walk/", scale=self.scale)
        self.group = pygame.sprite.Group(self.animation_idle_right)

        # hover animation
        self.hover = False
        self.animation_hover = MySprite("img/hover/msg/", scale=int(self.scale/2))
        self.group_hover = pygame.sprite.Group(self.animation_hover)

        self.c = 0
        self.speed = 0.1
        self.acceleration = 10
        self.move_dir = pygame.Vector2(0, 0)
        self.new_pos = self.pos

        self.bord_box = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        self.coll_box = pygame.Rect(self.pos[0]+(self.size[0]*(1/8)), self.pos[1]+(self.size[1]*(2/3)), self.size[0]*(6/8), self.size[1]*(1/3))
        self.pre_coll_box = self.coll_box.inflate(self.scale*self.speed*2, self.scale*self.speed*2)

    def idle(self):
        if self.move_dir[0] >= 0:
            self.group = pygame.sprite.Group(self.animation_idle_right)
        else:
            self.group = pygame.sprite.Group(self.animation_idle_left)

    def interaction(self, poi, collisions, keys=[]):
        self.poi = poi
        # hover animation
        if keys[pygame.K_j]:
            self.hover = not self.hover
            time.sleep(0.2)

        # set speed via shift-key
        if keys[pygame.K_LSHIFT]:
            self.speed = 2
        elif keys[pygame.K_LCTRL]:
            self.speed = 0.5
        else:
            self.speed = 1

        # get blocked directions
        blocked_directions = []
        for obj in collisions:
            blocked_directions.append(pygame.Vector2(self.pre_coll_box.center[0] - obj.coll_box.center[0], self.pre_coll_box.center[1] - obj.coll_box.center[1]))


        distance = poi - self.pos
        self.poi_rad = 200

        if distance.length() >= self.poi_rad - 10 or random.randint(0,1000) > 995:
            self.new_pos = poi + 0.5*self.poi_rad*pygame.Vector2(random.randint(-1,1), random.randint(-1, 1))

        if not pygame.Vector2(self.new_pos - self.pos).length() < 10:
            # move
            self.move_dir -= (self.pos - self.new_pos).normalize() / self.acceleration
            #print(self.move_dir)

            # # move
            # if keys[pygame.K_RIGHT] or keys[pygame.K_LEFT] or keys[pygame.K_DOWN] or keys[pygame.K_UP]:
            #     # parse keyboard inputs
            #     if keys[pygame.K_RIGHT]:
            #         self.move_dir[0] += self.speed / self.acceleration
            #     if keys[pygame.K_LEFT]:
            #         self.move_dir[0] -= self.speed / self.acceleration
            #     if keys[pygame.K_DOWN]:
            #         self.move_dir[1] += self.speed / self.acceleration
            #     if keys[pygame.K_UP]:
            #         self.move_dir[1] -= self.speed / self.acceleration

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
        self.pre_coll_box = self.coll_box.inflate(self.scale*self.speed*4, self.scale*self.speed*10)

        if self.c%int(20/self.speed) == 0:
            self.group.update()
        self.group.draw(screen)

        if self.hover:
            self.animation_hover.pos = pygame.Vector2(self.pos[0] + self.size[0]*2/5, self.pos[1] - self.size[1]/2)
            self.animation_hover.pos[1] -= (self.size[1]/16) * math.sin(self.c*self.speed/200.0)
            self.animation_hover.update_position()
            if self.c%int(30/self.speed) == 0:
                self.group_hover.update()
            self.group_hover.draw(screen)

def main():

    global globl_draw_boxes

    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    clock = pygame.time.Clock()
 
    curr_chunk = Chunk(800)

    mage = Character("Dude", scale=4)
    mage.pos.xy = (WIDTH/2 - mage.size[0]), (HEIGHT/2 - mage.size[1]/2)

    companion = Companion("little friend", scale=2)
    companion.pos.xy = (WIDTH/2), (HEIGHT/2)

    #TODO add all elements to the chunk model
    entities = []
    for i in range(6):
        entities.append(Entity("./img/trees/tree_0.png", pygame.Vector2(random.randint(0, curr_chunk.size), random.randint(0, curr_chunk.size)), scale=6))
        entities.append(Entity("./img/trees/pine_0.png", pygame.Vector2(random.randint(0, curr_chunk.size), random.randint(0, curr_chunk.size)), scale=6))
        entities.append(Entity("./img/rocks/rock_0.png", pygame.Vector2(random.randint(0, curr_chunk.size), random.randint(0, curr_chunk.size)), scale=3))

    # sort entities by y pos for correct placement
    entities = sorted(entities, key=operator.attrgetter('pos.y'))

    collision_boxes = []
    border_boxes = []
    for entity in entities:
        collision_boxes.append(entity.coll_box)
        border_boxes.append(entity.bord_box)


    # add entities to current chunk
    for entity in entities:
        curr_chunk.add_entity(entity)

    c = 0 
    while True:
        c += 1

        # get collisions
        collisions = pygame.Rect.collidelistall(mage.coll_box, collision_boxes)
        layer_collisions = pygame.Rect.collidelistall(mage.coll_box, border_boxes)
        pre_collisions = pygame.Rect.collidelistall(mage.pre_coll_box, collision_boxes)

        # get companion collisions
        comp_collisions = pygame.Rect.collidelistall(companion.coll_box, collision_boxes)
        comp_layer_collisions = pygame.Rect.collidelistall(companion.coll_box, border_boxes)
        comp_pre_collisions = pygame.Rect.collidelistall(companion.pre_coll_box, collision_boxes)

        # get objects of collisions
        collision_objects = []
        for collision in pre_collisions:
            collision_objects.append(entities[i])

        # get objects of companion collisions
        comp_collision_objects = []
        for collision in comp_pre_collisions:
            comp_collision_objects.append(entities[i])

        # get pressed keyboard keys
        keys = pygame.key.get_pressed()

        if keys[pygame.K_b]:
            globl_draw_boxes = not globl_draw_boxes

        # move player and companion
        mage.interaction(collision_objects, keys=keys)
        companion.interaction(mage.pos, comp_collision_objects, keys=keys)
        
        # draw the background
        screen.fill(pygame.Color(78, 86, 82))

        # # draw entities
        # for entity in entities:
            # screen.blit(entity.image, entity.get_pos())

        # draw entities from current chunk
        for entity in curr_chunk.entities:
            screen.blit(entity.image, entity.get_pos())

        # draw mage & companion
        # player companion collision
        if pygame.Rect.colliderect(mage.pre_coll_box, companion.pre_coll_box):
            if mage.pre_coll_box.center[1] > companion.pre_coll_box.center[1]:
                companion.update(screen)
                mage.update(screen)
            else:
                mage.update(screen)
                companion.update(screen)
        else:
            companion.update(screen)
            mage.update(screen)


        # draw collision and borderboxes
        if globl_draw_boxes:
            # entity boxes
            for i in range(len(entities)):
                if len(collisions) > 0:
                    if i in collisions:
                        pygame.draw.rect(screen, (255, 0, 0), entities[i].coll_box, 1)
                    else:
                        pygame.draw.rect(screen, (255, 255, 0), entities[i].coll_box, 1)
                else:
                    pygame.draw.rect(screen, (255, 255, 0), entities[i].coll_box, 1)
                pygame.draw.rect(screen, (0, 255, 0), entities[i].bord_box, 1)
            # mage box
            pygame.draw.rect(screen, (0, 255, 0), mage.bord_box, 1)
            if len(collisions) > 0:
                pygame.draw.rect(screen, (255, 0, 0), mage.coll_box, 1)
                pygame.draw.rect(screen, (255, 0, 0), mage.pre_coll_box, 1)
            else:
                pygame.draw.rect(screen, (255, 255, 0), mage.coll_box, 1)
                pygame.draw.rect(screen, (255, 255, 0), mage.pre_coll_box, 1)
            pygame.draw.rect(screen, (255, 255, 0), companion.coll_box, 1)
            pygame.draw.rect(screen, (255, 255, 0), companion.pre_coll_box, 1)

        # draw entities infront of player if necessary
        if len(layer_collisions) > 0:
            for i in layer_collisions:
                screen.blit(entities[i].image, entities[i].get_pos())
        
        # draw entities infront of companion if necessary
        if len(comp_layer_collisions) > 0:
            for i in comp_layer_collisions:
                screen.blit(entities[i].image, entities[i].get_pos())

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