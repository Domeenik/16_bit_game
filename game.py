import pygame
import os
import random
import math
import time
import operator

# self written
from complementary import *
from objects import *

class Game():
    def __init__(self, width=None, height=None):
        # general setup
        self.settings = ConfigHandler("settings.json")
        self.size = [width, height]
        self.bkg_color = pygame.Color(78, 86, 82)
        if not width: self.size = self.settings.get("general", "size")

        # pygame objects
        pygame.init()
        self.screen = pygame.display.set_mode(self.size, flags=pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(self.settings.get("cosmetics", "font"), 25)
        self.clock = pygame.time.Clock()

        # map
        map_size = self.settings.get("map", "size")
        chunk_size = self.settings.get("map", "chunk_size")
        self.map = Map(size=map_size, display_size=self.size)
        self.map_size = [map_size[0]*chunk_size[0], map_size[1]*chunk_size[1]]
        self.camera = Camera(self.size)

        # game settings
        self.render_lights = self.settings.get("graphics", "render_lights")

        self.add_objects()
        self.start()

    def add_objects(self):
        self.all_sprites = pygame.sprite.Group()
        self.lights = pygame.sprite.Group()

        self.spawn = pygame.Vector2(self.map_size[0]/2, self.map_size[1]/2)
        
        # add player
        self.player = Player([self.spawn[0],self.spawn[1]], name="player", size=[32,32])
        self.player.add_animation("./img/mage/idle", "idle", update_rate=9)
        self.player.add_animation("./img/mage/idle", "idle_right", update_rate=9)
        self.player.add_animation("./img/mage/idle", "idle_left", update_rate=9, flip=True)
        self.player.add_animation("./img/mage/walk", "walk_right", update_rate=10)
        self.player.add_animation("./img/mage/walk", "walk_left", update_rate=10, flip=True)
        self.all_sprites.add(self.player)

        # add companion
        self.companion = Companion(self.player, [self.spawn[0]+100,self.spawn[1]], name="player", size=[24,24])
        self.companion.add_animation("./img/cat/cat_0.png", "idle_right", update_rate=9, flip=True)
        self.companion.add_animation("./img/cat/cat_0.png", "idle_left", update_rate=9)
        self.companion.add_animation("./img/cat/walk", "walk_right", update_rate=9, flip=True)
        self.companion.add_animation("./img/cat/walk", "walk_left", update_rate=9)
        self.all_sprites.add(self.companion)

        # campfire
        self.campfire = DynamicEntity((self.spawn[0]-200,self.spawn[1]), name="campfire", size=[32,32])
        self.campfire.add_animation("./img/fire/campfire_on", "fire_on", update_rate=10)
        self.campfire.add_animation("./img/fire/campfire_off", "fire_off", update_rate=10)
        self.campfire.set_animation("fire_on")

        # hovers
        self.hover = Hover("./img/hover/msg", update_rate=100)

        # light
        self.light = Light(self.campfire.pos, size=[512,512])
        self.light.add_animation("./img/light/circle.png")

        self.player.set_hover(self.hover)

    def user_input(self, keys):
        # update player
        self.player.interaction(keys)

        # close the game via escape
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            quit()

        # choose not to render lights for performance boost
        if keys[pygame.K_l]:
            self.render_lights = not self.render_lights
            time.sleep(0.2)

    def start(self):
        c = 0
        while True:
            # repaint background
            self.screen.fill(self.bkg_color)
            
            # get pressed keys for control
            self.user_input(pygame.key.get_pressed())
            #ToDo implement collisions

            # add sprites from loaded chunks
            #self.all_sprites = pygame.sprite.Group(self.map.chunks[self.map.current_chunk].sprites)
            self.all_sprites = pygame.sprite.Group(self.map.get_sprites(self.camera))
            self.all_sprites.add(self.player)
            #self.all_sprites.add(self.player.hover)
            self.all_sprites.add(self.companion)
            self.all_sprites.add(self.campfire)
            #self.map.update(self.player.pos)

            # lights
            self.light.follow_target(self.campfire, (0,0))
            self.lights.add(self.light)
            
            # draw entities
            self.all_sprites.update()
            self.all_sprites = pygame.sprite.Group(sorted(self.all_sprites, key=lambda x: x.pos[1])) # prints '(0, 100)'
            self.lights.update()
            
            #ToDo update only changes
            # get camera position and translate sprites
            self.camera.update(self.player)
            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, self.camera.apply(sprite))
            
            # render lights
            if self.render_lights:
                for light in self.lights:
                    self.screen.blit(light.image, self.camera.apply(light))

            #ToDo reimplement
            # draw current chunk
            #pygame.draw.rect(self.screen, (0, 255, 255), self.camera.apply(self.map.chunks[self.map.current_chunk]), 1)

            # update loop
            self.update_fps(display=True)
            pygame.display.update()
            self.clock.tick(60)
            c += 1


            # check for quit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

    def update_fps(self, display=False):
        self.fps = str(int(self.clock.get_fps()))
        self.fps_text = self.font.render(self.fps, 1, pygame.Color("coral"))
        if self.settings.get("debugging", "display_fps"): 
            self.screen.blit(self.fps_text, (self.size[0] - 25, 5))




def main():
    game = Game()

if __name__ == "__main__":
    main()
