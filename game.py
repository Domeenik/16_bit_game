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
        self.screen = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(self.settings.get("cosmetics", "font"), 25)
        self.clock = pygame.time.Clock()

        self.add_objects()
        self.start()

    def add_objects(self):
        self.player = Entity1([40,40], name="player", size=[64,64])
        self.player.add_animation("./img/mage/idle", "idle", update_rate=9)
        self.player.add_animation("./img/mage/walk", "walk", update_rate=20)
        self.player.update([10,10])

        self.all_sprites = pygame.sprite.Group(self.player)


    def start(self):
        c = 0
        while True:
            # repaint background
            self.screen.fill(self.bkg_color)
            
            # draw entities
            self.all_sprites.update()
            self.all_sprites.draw(self.screen)

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
