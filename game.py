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

        self.dummy_animation = MySprite("./img/mage/idle", 10)
        self.dummy_group = pygame.sprite.Group(self.dummy_animation)

        self.entity = Entity([30,30])
        self.entity.add_animation(self.dummy_animation, "idle")

        self.start()


    def start(self):
        while True:
            # repaint background
            self.screen.fill(self.bkg_color)

            self.dummy_group.update()
            self.dummy_group.draw(self.screen)
            self.entity.update()

            # update loop
            self.update_fps(display=True)
            pygame.display.update()
            self.clock.tick(60)

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
