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
        flags = pygame.DOUBLEBUF | pygame.NOFRAME
        self.screen = pygame.display.set_mode(self.size, flags=flags)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(self.settings.get("cosmetics", "font"), 25)
        self.clock = pygame.time.Clock()

        # map
        map_size = self.settings.get("map", "size")
        chunk_size = self.settings.get("map", "chunk_size")
        self.map = Map(size=map_size, display_size=self.size)
        self.map_size = [map_size[0]*chunk_size[0], map_size[1]*chunk_size[1]]
        self.camera = Camera(self.size)

        # world settings
        self.day_cycling = self.settings.get("world", "day_cycling")
        self.cycle = 0

        # game settings
        self.render_lights = self.settings.get("graphics", "render_lights")
        self.fps_cap = self.settings.get("graphics", "fps_cap")

        self.add_objects()
        self.start()

    def add_objects(self):
        #ToDo planned: structure like:
        #self.map = pygame.sprite.Group(self.map.get_sprites())
        #self.actions = self.map.get_interactions()

        self.backgrounds = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.lights = pygame.sprite.Group()
        self.overlay_sprites = pygame.sprite.Group()

        self.spawn = pygame.Vector2(self.map_size[0]/2, self.map_size[1]/2)
        
        # actions
        self.use = Action("use", pygame.K_e)

        # add player
        self.player = Mage([self.spawn[0],self.spawn[1]], name="player", size=[32,32])
        self.all_sprites.add(self.player)

        # add companion
        self.companion = Cat(self.player, [self.spawn[0]+100,self.spawn[1]], name="friend", size=[24,24])
        self.all_sprites.add(self.companion)

        # campfire
        self.campfire = Campfire((self.spawn[0]-200,self.spawn[1]), name="campfire", size=[32,32])
        self.campfire.add_action(self.use)

        # struct
        self.struct = Structure((self.spawn[0], self.spawn[1]))
        self.struct.add_entity(self.campfire, (10,100))

        # overlay
        self.overlay = Overlay()
        self.overlay_sprites.add(self.overlay.sprites)

        # map generation
        self.draw_background = True

        # testing background
        self.bkg = Bkg()

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
        if keys[pygame.K_c]:
            self.day_cycling = not self.day_cycling
            time.sleep(0.2)

        # performance mode
        if keys[pygame.K_p]:
            self.fps_cap = not self.fps_cap
            time.sleep(0.2)

        # debug player health
        if keys[pygame.K_PLUS]:
            self.player.health += 1
            time.sleep(0.2)
        if keys[pygame.K_MINUS]:
            self.player.health -= 1
            time.sleep(0.2)
        
        # debug background
        if keys[pygame.K_b]:
            self.draw_background = not self.draw_background
            time.sleep(0.2)

    def start(self):
        c = 0
        while True:
            
            # get pressed keys for control
            #ToDo implement collisions

            # add sprites from loaded chunks
            self.all_sprites = pygame.sprite.Group(self.map.get_sprites(self.camera))
            self.all_sprites.add(self.companion)
            #self.all_sprites.add(self.campfire)

            # add structs
            for sprite in self.struct.sprites:
                self.all_sprites.add(sprite)

            # update player
            self.all_sprites.add(self.player)
            self.player.get_objects_in_range(self.all_sprites)
            self.user_input(pygame.key.get_pressed())

            # draw entities
            self.all_sprites.update()
            self.all_sprites = pygame.sprite.Group(sorted(self.all_sprites, key=lambda x: x.pos[1])) # prints '(0, 100)'
            
            # get camera position
            self.camera.update(self.player)

            # render background
            if self.draw_background:
                #m_pos = pygame.mouse.get_pos()
                #print(m_pos)
                #clr = pygame.Color(m_pos[0], m_pos[1], 82)
                self.screen.fill(pygame.Color(71, 127, 82))
                self.backgrounds = pygame.sprite.Group(self.map.get_backgrounds(self.camera))
                self.backgrounds.update()
                for background in self.backgrounds:
                    self.screen.blit(background.image, self.camera.apply(background))
            else:
                self.screen.fill(self.bkg_color)
                #self.screen.blit(self.bkg.image, self.camera.apply(self.bkg))

            #ToDo update only changes
            # render sprites
            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, self.camera.apply(sprite))
            
            # render lights
            if self.render_lights:
                for sprite in self.all_sprites:
                    if not sprite.light == None:
                        self.lights.add(sprite.light)
                        
                self.lights.update()
                self.light_surf = pygame.Surface(self.size, flags=pygame.HWSURFACE)
                if self.day_cycling:
                    self.cycle = int((1+math.sin(c/400))*170/2)
                else: 
                    self.cycle = 0
                self.clr = (80 + self.cycle, 60 + self.cycle, 80 + self.cycle)
                self.light_surf.fill(self.clr)
                #pygame.draw.circle(self.light_surf, (200,250,250), (500,500), 100)
                for light in self.lights:                        
                    if light.is_active:
                        self.light_surf.blit(light.image, self.camera.apply(light))
                self.screen.blit(self.light_surf, (0,0), special_flags=pygame.BLEND_MULT)
                
            # display overlay
            self.overlay.life_bar.update_health(self.player.health)
            self.overlay_sprites.update()
            for sprite in self.overlay_sprites:
                self.screen.blit(sprite.image, sprite.rect.topleft)

            #ToDo reimplement
            # draw current chunk
            #pygame.draw.rect(self.screen, (0, 255, 255), self.camera.apply(self.map.chunks[self.map.current_chunk]), 1)

            # update loop
            self.update_fps(display=True)
            pygame.display.update()
            c += 1
            if self.fps_cap:
                self.clock.tick(60)
            else:
                self.clock.tick(1000)

            # clean up
            for sprite in self.all_sprites:
                sprite.remove()

            # check for quit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

    def update_fps(self, display=False):
        self.fps = str(int(self.clock.get_fps()))
        self.fps_text = self.font.render(self.fps, 1, pygame.Color("coral"))
        offset = self.fps_text.get_rect().width
        if self.settings.get("debugging", "display_fps"): 
            self.screen.blit(self.fps_text, (self.size[0] - 8 - offset, 8))


def main():
    game = Game()

if __name__ == "__main__":
    main()
