import math
import sys

import neat
import pygame

print(pygame.ver)

screen_width = 1500
screen_height = 800
generation = 1

# Variables
fast_method = True
car_speed = 40


class Car:
    def __init__(self):
        self.surface = pygame.image.load('car.png')
        self.surface = pygame.transform.scale(self.surface, (100, 100))
        self.rotate_surface = self.surface
        self.position = [700, 650]
        self.angle = 0
        self.speed = 0

        self.center = self.surface.get_rect().center
        # self.center = [self.position[0] + 50, self.position[1] + 50]
        self.radars = []
        self.radars_for_draw = []

        self.alive = True
        self.goal = False

        self.distance = 0
        self.time_spent = 0

    def draw(self, screen):
        screen.blit(self.rotate_surface, self.position)

        for radar in self.radars:
            pos, dist = radar
            # pygame.draw.circle(screen, (255, 0, 0), pos, dist)
            pygame.draw.line(screen, (0, 255, 0), self.center, pos, 1)
            pygame.draw.circle(screen, (0, 255, 0), pos, 5)

    def rotate_image_from_center(self, image, angle):
        original_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = original_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image

    def check_collisions(self, map):
        self.alive = True
        for p in self.four_points:
            if map.get_at((int(p[0]), int(p[1]))) == (255, 255, 255, 255):
                self.alive = False
                break

    def check_radar(self, degree, map):
        len = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)

        while not map.get_at((x, y)) == (255, 255, 255, 255) and len < 300:
            len = len + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)

        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])

    def get_data(self):
        radars = self.radars
        ret = [0, 0, 0, 0, 0]
        for i, r in enumerate(radars):
            ret[i] = int(r[1] / 30)

        return ret

    def get_alive(self):
        return self.alive

    def get_reward(self):
        if fast_method:
            return self.distance / self.time_spent
        else:
            return self.distance / 50.0

    def update(self, map):
        # self.speed = self.speed + dt * self.speed * 0.1
        self.speed = car_speed

        self.rotate_surface = self.rotate_image_from_center(self.surface, self.angle)
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        if self.position[0] < 20:
            self.position[0] = 20
        elif self.position[0] > screen_width - 120:
            self.position[0] = screen_width - 120

        self.distance += self.speed
        self.time_spent += 1
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        if self.position[1] < 20:
            self.position[1] = 20
        elif self.position[1] > screen_height - 120:
            self.position[1] = screen_height - 120

        # calculate 4 collision points
        self.center = [int(self.position[0]) + 50, int(self.position[1]) + 50]
        len = 40
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * len,
                    self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * len]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * len,
                     self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * len]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * len,
                       self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * len]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * len,
                        self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * len]
        self.four_points = [left_top, right_top, left_bottom, right_bottom]

        self.check_collisions(map)
        self.radars.clear()
        for d in range(-90, 120, 45):
            self.check_radar(d, map)

    """
    def update(self, dt):
        #self.speed = self.speed + dt * self.speed * 0.1
        self.angle += self.speed * dt
        self.rotate_surface = pygame.transform.rotate(self.surface, self.angle)
        self.center = self.rotate_surface.get_rect().center
        self.position[0] += math.cos(math.radians(self.angle)) * self.speed * dt
        self.position[1] += math.sin(math.radians(self.angle)) * self.speed * dt

        for radar in self.radars:
            pos, dist = radar
            pos[0] += math.cos(math.radians(self.angle)) * self.speed * dt
            pos[1] += math.sin(math.radians(self.angle)) * self.speed * dt

        self.radars_for_draw = self.radars.copy()
        self.radars_for_draw.append(self.center)
        self.radars_for_draw.append(self.position)

        if self.position[0] < 0 or self.position[0] > screen_width or self.position[1] < 0 or self.position[1] > screen_height:
            self.alive = False
            self.goal = False
            self.distance = 0
            self.time_spent = 0

    def get_inputs(self):
        inputs = []
        for radar in self.radars_for_draw:
            inputs.append(radar[0] / screen_width)
            inputs.append(radar[1] / screen_height)
        return inputs

    def get_outputs(self):
        outputs = []
        outputs.append(self.speed / 10)
        outputs.append(self.angle / 360)
        return outputs

    def get_distance(self):
        return self.distance

    def get_time_spent(self):
        return self.time_spent
    
    def get_fitness(self):
        return self.distance / self.time_spent
    
    def get_alive(self):
        return self.alive
    
    def get_goal(self):
        return self.goal
    
    def set_goal(self):
        self.goal = True
        
    def set_distance(self, distance):
        self.distance = distance
        
    def set_time_spent(self, time_spent):
        self.time_spent = time_spent
        
    def set_alive(self, alive):
        self.alive = alive
        
    def set_fitness(self, fitness):
        self.fitness = fitness
        
    def set_angle(self, angle):
        self.angle = angle
        
    def set_speed(self, speed):
        self.speed = speed
        
    def set_radars(self, radars):
        self.radars = radars
        
    def set_radars_for_draw(self, radars_for_draw):
        self.radars_for_draw = radars_for_draw
        
    def set_position(self, position):
        self.position = position
        
    def set_center(self, center):
        
        self.center = center
        
    def set_rotate_surface(self, rotate_surface):
        self.rotate_surface = rotate_surface
        
    def set_surface(self, surface):
        self.surface = surface
        
    def set_angle(self, angle):
        self.angle = angle
        
    def set_speed(self, speed):
        self.speed = speed
        
    def set_radars(self, radars):
        self.radars = radars
    """


def run_car(genomes, config):
    # Init NEAT
    nets = []
    cars = []

    # Init pygame
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    map = pygame.image.load("map.png")
    map = pygame.transform.scale(map, (screen_width, screen_height))
    generation_font = pygame.font.SysFont("Arial", 50)
    # generation_text = generation_font.render("Generation: 0", True, (255, 255, 255))
    font = pygame.font.SysFont("Arial", 30)

    # Init cars
    for _, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

        cars.append(Car())

    # Main Loop
    global generation
    generation += 1
    """
    global best_distance
    global best_time
    global best_fitness
    global best_car
    global best_car_genome
    global best_car_id
    global best_car_genome_id
    global best_car_generation
    global best_car_generation_id
    """
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

        # Input car data and get outputs
        for index, car in enumerate(cars):
            output = nets[index].activate(car.get_data())
            out = output.index(max(output))
            if out == 0:
                car.angle += 20
            elif out == 1:
                car.angle -= 20
            # Get output from NEAT
            # output = nets[i].activate((car.x, car.y, car.angle, car.speed))
            # Update car
            # car.update(output[0], output[1])

        # update car and fitness
        remaining_cars = 0
        for i, car in enumerate(cars):
            if car.get_alive():
                remaining_cars += 1
                car.update(map)
                genomes[i][1].fitness += car.get_reward()

        # Break if Remaining cars is 0
        if remaining_cars == 0:
            break

        # Draw map
        screen.blit(map, (0, 0))

        # Draw cars
        for car in cars:
            if car.get_alive():
                car.draw(screen)

        # Draw generation
        text = generation_font.render("Generation : " + str(generation), True, (255, 255, 0))
        text_rect = text.get_rect()
        text_rect.center = (screen_width / 2, 100)
        screen.blit(text, text_rect)

        # Draw remaining cars
        text = font.render("remain cars : " + str(remaining_cars), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (screen_width / 2, 200)
        screen.blit(text, text_rect)

        # Update screen
        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    # Config File
    config_path = "config-feedforward.txt"
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Create population
    pop = neat.Population(config)

    # Add reporter
    pop.add_reporter(neat.StdOutReporter())
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    # Run for 100 generations (Eval function = run_car)
    winner = pop.run(run_car, 100)
