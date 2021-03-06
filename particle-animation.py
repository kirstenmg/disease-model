# import the modules we'll need:
import pygame #to draw window, particles
import random #to determine random movement
import math   #to use math functions
import time   #to keep track of infection time
import matplotlib.pyplot as plt #to create a graph

# constants for setup
RADIUS    = 15
(WIDTH, HEIGHT) = (500, 500) #height excludes text box
TEXT_BOX_HEIGHT = 100 # height of box with text at bottom of screen
SPEED           = 2
RECOVERY        = 10 #seconds

WINDOW_COLOR    = (255, 255, 255)
WINDOW_TITLE    = "Particles"

NUM_PARTICLES   = 50

# constants for infection, recovery, symptomatic rates
INFECTION_MIN   = 0.9
INFECTION_MAX   = 1
RECOVERY_MAX    = 1
RECOVERY_MIN    = 0.9
SYMPTOMATIC_MIN = 0.75
SYMPTOMATIC_MAX = 0.5

# activate pygame library
pygame.init()

# create pygame window object and display it
screen = pygame.display.set_mode((WIDTH, HEIGHT + TEXT_BOX_HEIGHT))
pygame.display.set_caption(WINDOW_TITLE)
screen.fill(WINDOW_COLOR)


#represents a particle
class Particle:
    def __init__(self, x, y, angle):
        
        self.angle = angle
        self.speed = random.random() # a characteristic of the Particle
        self.current_speed = self.speed # actual speed, adjusted after collisions
        self.collision_time = 0 # time since latest collision
        self.collided = False        

        self.x = x
        self.y = y
        self.radius = RADIUS
        self.color = (0, 0, 255)        
        
        self.status = "healthy"
        self.onset = 0 # this doesn't become relevant until infection

        # rates
        self.recovery_probability    = random.uniform(RECOVERY_MIN,\
                                                      RECOVERY_MAX)
        self.symptomatic_probability = random.uniform(SYMPTOMATIC_MIN,\
                                                      SYMPTOMATIC_MAX)
        self.infection_probability   = random.uniform(INFECTION_MIN,\
                                                      INFECTION_MAX)

    # draw particle on screen
    def display(self):
        pygame.draw.circle(screen, self.color, (int(self.x),
                           int(self.y)), self.radius)

    # update x and y position of particle
    def move(self):
        self.x += math.cos(self.angle) * self.current_speed * SPEED
        self.y += -math.sin(self.angle) * self.current_speed * SPEED

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
                    self.color  = (255, 0, 0)
                self.status = "infected"
                self.onset  = time.time()

    # check if the particle should recover, if so, recover
    def recover(self):
        if self.status == "infected" and\
           time.time() - self.onset > RECOVERY:
            num = random.random()
            if num < self.recovery_probability:
                self.color  = (0, 255, 0)
                self.status = "recovered"
                self.infection_probability = random.uniform(0, 0.01)
            else:
                self.status = "dead"
                

# adjust direction if centers of any two particles are too close
# param particles is a list of all particles in the window
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

                if (target.status == "infected"\
                    or other.status == "infected"):                    
                    target.infect()
                    other.infect()

                # adjust target x and y to be next to other
                if distance != 0:
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

    # initialize status counts
    healthy = 0
    infected = 1
    recovered = 0
    dead = 0

    #create array to store healthy counts
    healthy_counts = []
    infected_counts = []
    recovered_counts = []
    death_counts = []

    # make screen persist until user closes it
    running = True
    while running:
        # pause the program for 20 ms
        pygame.time.delay(10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit() # we could also set running = False

                  
        # check if particles run into each other
        collide(particles)

        #reset particle status counts
        healthy = 0
        infected = 0
        recovered = 0     


        # update each particle in our list and the display
        for p in particles:
            p.move()
            p.bounce()
            p.recover()
            p.display()

            if p.status == "healthy":
                healthy += 1
            elif p.status == "infected":
                infected += 1
            elif p.status == "recovered":
                recovered += 1
            elif p.status == "dead":
                dead += 1
                particles.remove(p)

        # add counts at this point in time, for graphing later
        healthy_counts.append(healthy)
        infected_counts.append(infected)
        recovered_counts.append(recovered)
        death_counts.append(dead)
            
        # create font object
        font = pygame.font.Font(pygame.font.get_default_font(), 15)        

        # create Surfaces with text and combine it with the screen
        # surface to display status counts
        text = font.render("healthy: " + str(healthy), True, (0, 0, 0))
        screen.blit(text, (10, HEIGHT))
        text = font.render("infected: " + str(infected), True, (0, 0, 0))
        screen.blit(text, (10, HEIGHT + 20))
        text = font.render("recovered: " + str(recovered), True, (0, 0, 0))
        screen.blit(text, (10, HEIGHT + 40))
        text = font.render("dead: " + str(dead), True, (0, 0, 0))
        screen.blit(text, (10, HEIGHT + 60))

        # update the display
        pygame.display.update()
        screen.fill(WINDOW_COLOR)

        # once no particles are infected, stop running and display graph
        if (infected == 0 and (recovered > 1 or dead > 1)):
            running = False

            # plot infections over time
            plt.plot(infected_counts)
            plt.xlabel("time")
            plt.ylabel("number of infected particles")
            plt.title("Infection counts over time")
            plt.show()
        
main()
