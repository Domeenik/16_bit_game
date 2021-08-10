
class Hover(pygame.sprite.Sprite):
    def __init__(self, path, size=[16,16], flip=False, update_rate=1):
        super(Hover, self).__init__()
        self.size = size
        self.update_rate = update_rate
        self.rect = pygame.Rect(0,0,0,0)#pygame.Rect(target.pos[0], target.pos[1] - target.size[1], self.size[0], self.size[1])
        self.pos = self.rect.topleft

        self.images = []
        self.image = None
        self.counter = 0
        self.index = 0

        self.images = self.load_images(path, flip)

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

    def update(self, target):
        self.target = target
        
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
