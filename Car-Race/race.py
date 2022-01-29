import pygame
import math
import sys
import neat

print(pygame.ver)

screen_width = 1500
screen_height = 800
generation = 1

class Car:
    def __init__(self):
        self.surface = pygame.image.load('car.png')
        self.surface = pygame.transform.scale(self.surface, (100, 100))
        self.rotate_surface = self.surface
        self.position = [700, 650]

    def draw(self, screen):
        screen.blit(self.rotate_surface, self.position)


def run_car():
    # Init NEAT
    nets = []
    cars = []

    # Init pygame
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    map = pygame.image.load("map.png")

    # Main Loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

        # Draw map
        screen.blit(map, (0, 0))

        car = Car()
        car.draw(screen)

        # Draw cars
        for i, car in enumerate(cars):
            car.draw(screen)
            # Get output from NEAT
            #output = nets[i].activate((car.x, car.y, car.angle, car.speed))
            # Update car
            #car.update(output[0], output[1])

        # Update screen
        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    run_car()