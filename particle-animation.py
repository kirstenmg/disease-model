# import the modules we'll need:
import pygame #to draw window, particles
import random #to determine random movement
import math   #to use math functions
import time   #to keep track of infection time


"""
To do:
 - maintaining speed
 - recovery rate
 - amount of time sick - correlates with recovery rate
 - walls
 - phases:
     - walled in, with doors
         - doors close
     - boxes open up, dots enter center
 - aisles
     - movement angles
 - add counts for different groups

"""


# constants
RADIUS    = 10
(WIDTH, HEIGHT) = (400, 400)
SPEED           = 1
COLLIDED_SPEED  = 0.5

DEFAULT_COLOR   = (0, 0, 255)
INFECTED_COLOR  = (255, 0, 0)
RECOVERED_COLOR = (0, 255, 0)

RECOVERY        = 10 #seconds

WINDOW_COLOR    = (255, 255, 255)
WINDOW_TITLE    = "Particles"

NUM_PARTICLES   = 50


# activate pygame library
pygame.init()

# create pygame window object and display it
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(WINDOW_TITLE)
screen.fill(WINDOW_COLOR)


#represents a particle
class Particle:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.radius = RADIUS
        self.thickness = 1
        self.speed = random.random() # a characteristic of the Particle
        self.current_speed = self.speed # actual speed, adjusted after collisions
        self.collision_time = 0 # time since latest collision
        self.collided = False
        self.color = (0, 0, 100 + self.speed * 155)
        self.angle = angle
        self.status = "healthy"
        self.onset = 0 # this doesn't become relevant until infection

        self.recovery_probability  = random.uniform(0.9, 1)
        self.symptomatic_probability = random.uniform(0.5, 0.75)
        self.infection_probability = random.uniform(0.9, 1) # not realistic?

    # draw particle on screen
    def display(self):
        pygame.draw.circle(screen, self.color, ((int)(self.x),
                           (int)(self.y)), self.radius)

    # update x and y position of particle
    def move(self):
        # check if speed should be reset - it is averaged, then restored to the
        # particle's original speed
##        if (self.collided and time.time() - self.collision_time >= 0.5):
##            self.current_speed = self.speed
##            self.collided = False
##        elif (self.collided and time.time() - self.collision_time >= 0.25):
##            self.current_speed = (self.current_speed + self.speed) / 2

        # update position
        self.x += math.cos(self.angle) * self.current_speed
        self.y += -math.sin(self.angle) * self.current_speed

    # check if particle needs to bounce off the wall
    def bounce(self):
        if self.x > WIDTH - self.radius:
            self.x = 2 * (WIDTH - self.radius) - self.x
            self.angle = math.pi - self.angle
            
        elif self.x < self.radius:
            self.x = 2 * self.radius - self.x
            self.angle = math.pi - self.angle
            
        if self.y > HEIGHT - self.radius:
            self.y = 2 * (HEIGHT - self.radius) - self.y
            self.angle =  - self.angle
            
        elif self.y < self.radius:
            self.y = 2 * self.radius - self.y
            self.angle = - self.angle

    # infect this particle, if it is not already
    def infect(self):        
        if self.status != "infected":
            num = random.random()
            if num <= self.infection_probability:
                num = random.random()
                if num <= self.symptomatic_probability:
                    self.color  = (100 * self.speed + 155, 0, 0)
                self.status = "infected"
                self.onset  = time.time()

    # check if the particle should recover, if so, recover
    def recover(self):
        if self.status == "infected" and time.time() - self.onset > RECOVERY:
            self.color  = RECOVERED_COLOR
            self.status = "recovered"
            self.infection_probability = random.uniform(0, 0.01)
            

# adjust direction if centers of any two particles are closer than twice
# the radius
# parameter is list of all particles in the window
def collide(particles):
    for i in range(0, len(particles) - 1):
        target = particles[i]
        
        for j in range(i + 1, len(particles)):
            other = particles[j]
            diff_x = target.x - other.x
            diff_y = target.y - other.y
            distance = math.sqrt(diff_x**2 + diff_y**2)
            
            if distance < RADIUS * 2:

                # adjust directions (switch velocities)
                temp_angle              = target.angle
                temp_speed              = target.current_speed
                target.angle            = other.angle
                target.current_speed    = other.current_speed
                other.angle             = temp_angle
                other.current_speed     = temp_speed
                target.collision_time   = time.time()
                other.collision_time    = time.time()
                target.collided = True
                other.collided  = True

                if (target.status == "infected" or other.status == "infected"):
                    target.infect()
                    other.infect()

                # adjust target x and y to be next to other
                target.x = other.x + diff_x / distance * 2 * RADIUS
                target.y = other.y + diff_y / distance * 2 * RADIUS

def main():
    particles = []

    for i in range(NUM_PARTICLES):
        x = random.randint(RADIUS, WIDTH - RADIUS)
        y = random.randint(RADIUS, HEIGHT - RADIUS)
        angle = random.uniform(0, 2 * math.pi)

        particles.append(Particle(x, y, angle))

    particles[0].infect()

    # make screen persist until user closes it
    running = True
    while running:
        # pause the program for 20 ms
        pygame.time.delay(10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit() # we could also set running = False

        # update each particle in our list and the display
        for p in particles:
            p.move()
            p.bounce()
            p.display()
            p.recover()
        
        collide(particles)
        pygame.display.update()
        screen.fill(WINDOW_COLOR)

main()
