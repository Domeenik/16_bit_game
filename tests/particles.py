from perlin_noise import PerlinNoise
import pygame
import random

class Particle():
    def __init__(self, pos=(0,0), size=(10), color=(50,50,50)):
        self.pos = pos
        self.size = size
        self.color = color
        self.acc = (0, 0)

    def update(self, pos=None):
        if pos:
            self.pos = pos
        self.pos = (self.pos[0] + self.acc[0], self.pos[1] + self.acc[1])

    def apply_force(self, vec):
        self.acc = (self.acc[0] + vec[0], self.acc[1] + vec[1])

    def set_acceleration(self, acc):
        self.acc = acc

class FireParticle(Particle):
    def __init__(self, pos, size, color):
        new_pos = (pos[0] + random.randint(-size*2, size*2), pos[1] + random.randint(-size*3, size))
        super(FireParticle, self).__init__(new_pos, size, color)
        self.noise = PerlinNoise()
        self.start_size = size + random.randint(-10, 10)/2
        self.lifespan = 1
        self.set_acceleration((0, -1))

    def update(self):
        self.lifespan -= 0.005
        self.pos = (self.pos[0] + self.noise(self.pos[1]/100)*2, self.pos[1])
        self.apply_force((0, +0.0001))
        self.color = (self.color[0] * 0.99, self.color[1] * 0.99, self.color[2] * 0.99)
        self.size = self.start_size * 0.99 * self.lifespan + self.noise(self.lifespan)
        super().update()

pygame.init()
flags = pygame.DOUBLEBUF | pygame.NOFRAME | pygame.HWSURFACE
screen = pygame.display.set_mode((600,600), flags=flags)
clock = pygame.time.Clock()

particles = []

c = 0
rect_surf = pygame.Surface((6,6))
pygame.draw.rect(rect_surf, (200, 150, 0), pygame.Rect(0,0,6,6))

while True:
    screen.fill((0, 0, 0))

    c += 1

    rand = random.randint(-100, 100)
    if len(particles) < 200 and c%6 == 0:
        particles.append(FireParticle(pygame.mouse.get_pos(), 8, (200 + rand * 0.5, 150 + rand * 0.4, 0, 0.1)))

    for particle in particles:
        particle.update()

        #pygame.draw.circle(screen, particle.color, particle.pos, int(particle.size))
        pygame.draw.rect(screen, particle.color, pygame.Rect(particle.pos[0], particle.pos[1], particle.size*2, particle.size*2))
        #pygame.draw.rect(screen, (particle.color[0], particle.color[1]*1.2, particle.color[2]), pygame.Rect(particle.pos[0] + particle.size/2, particle.pos[1] + particle.size, particle.size, particle.size))
        #screen.blit(rect_surf, particle.pos)

    for particle in particles:
        if particle.lifespan < 0.01:
            particles.remove(particle)

    clock.tick(6000)
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()