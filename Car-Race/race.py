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
        self.angle = 0
        self.speed = 0

        self.center = self.surface.get_rect().center
        #self.center = [self.position[0] + 50, self.position[1] + 50]
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
            #pygame.draw.circle(screen, (255, 0, 0), pos, dist)
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
        for wall in map.walls:
            if wall[0] < self.position[0] + self.center[0] < wall[1]:
                if wall[2] < self.position[1] + self.center[1] < wall[3]:
                    self.alive = False
                    break

    def check_radar(self, degree, map):
        len = 0
        x = int(self.center[0] + math.cos(math.radians(degree)) * len)
        y = int(self.center[1] + math.sin(math.radians(degree)) * len)

        while not map.get_at((x, y)) == (0, 0, 0):
            len += 1
            x = int(self.center[0] + math.cos(math.radians(degree)) * len)
            y = int(self.center[1] + math.sin(math.radians(degree)) * len)

        dist = int(len * math.cos(math.radians(degree)))
        self.radars.append(((x, y), dist))

    def update(self, map, dt):
        #self.speed = self.speed + dt * self.speed * 0.1
        self.speed = 30

        self.rotate_surface = self.rotate_image_from_center(self.surface, self.angle)
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

        # caculate 4 collision points
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