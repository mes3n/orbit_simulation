from operator import sub
import os
from typing import List
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from math import cos, sin, atan, pi
from random import randint

import pygame
pygame.init()


WIDTH, HEIGHT = 600, 600

window = pygame.display.set_mode((WIDTH, HEIGHT))  # create window
pygame.display.set_caption("Physics Simulation")

COLORS = [(115, 92, 176), (0,164,239), (106,180,62), (232, 157, 65), (253, 64,132)]

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

G = 6.674*(10**-11)  # gravitational constant

SOLAR_MASS = 2.0*(10**30)
EARTH_MASS = 5.97219*(10**24)

SOLAR_RADIUS = 6.9634*(10**8)
EARTH_RADIUS = 6.371*(10**6)

E_S_DISTANCE = 1.5*(10**8)

DISTANCE_SCALE = 5*(10**-7)
RADIUS_SCALE = 5**(10**-29)


def distance_between_points(pos1, pos2):
    return ((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)**(1/2)

def angle_to_point(pos1, pos2):
    Dx = pos2[0] - pos1[0]
    Dy = pos2[1] - pos1[1]

    if (Dx) == 0:
        if Dy >= 0:
            return pi/2
        elif Dy < 0:
            return -pi/2
    else:
        if Dx >= 0 and Dy >= 0:
            return atan((Dy)/(Dx))
        elif Dx < 0 and Dy < 0:
            return atan((Dy)/(Dx)) - pi
        elif Dx >= 0 and Dy <= 0:
            return atan((Dy)/(Dx))
        elif Dx < 0 and Dy > 0:
            return atan((Dy)/(Dx)) - pi


class Vector2(list):
    def __init__(self, args):
        super().__init__(args)

    def add_vector(self, vector):
        self[0] += vector[0]
        self[1] += vector[1]

    def set_vector(self, vector):
        self[0] = vector[0]
        self[1] = vector[1]


class Body():
    def __init__(self, center=[WIDTH/2, WIDTH/2], radius=1, mass=1, color=WHITE):
        self.center = Vector2(center)
        self.radius = radius
        self.mass = mass

        self.color = color

class Satellite(Body):
    def __init__(self, velocity=[0, 0], center=[WIDTH/2, HEIGHT/2], radius=1, mass=1, color=WHITE):
        super().__init__(center=center, radius=radius, mass=mass, color=color)
        self.velocity = Vector2(velocity)

    def move(self):
        dis = distance_between_points(self.center, primary_body.center)
        acc = (self.mass*primary_body.mass)/(self.mass*dis*dis)

        theta = angle_to_point(self.center, primary_body.center)

        self.velocity.add_vector([cos(theta)*acc, sin(theta)*acc])
        self.center.add_vector(self.velocity)

    def contact(self):
        if distance_between_points(self.center, primary_body.center) < self.radius + primary_body.radius:
            return True
        return False


def update():
    window.fill(BLACK)

    pygame.draw.circle(window, primary_body.color, primary_body.center, primary_body.radius)
    pygame.draw.circle(window, satellite.color, satellite.center, satellite.radius)

    pygame.display.update()


def events():

    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # closing window
            pygame.quit()
            quit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            satellite.center.set_vector(pygame.mouse.get_pos())
            update()

            while True:
                for sub_event in pygame.event.get():
                    if sub_event.type == pygame.QUIT:  # closing window
                        pygame.quit()
                        quit()
                    
                    if sub_event.type == pygame.MOUSEBUTTONUP:
                        scale = 0.05
                        mouse_pos = pygame.mouse.get_pos()
                        satellite.velocity.set_vector([scale*(satellite.center[0] - mouse_pos[0]), scale*(satellite.center[1] - mouse_pos[1])])
                        return

                    # draw arrows for forces

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # ESC to quit
                pygame.quit()
                quit()


def main():
    clock = pygame.time.Clock()

    while True:
        
        dt = clock.tick(60)

        events()

        if not satellite.contact():
            satellite.move()

        update()


if __name__ == '__main__':
    primary_body = Body(radius=100, mass=400, color=COLORS[3])
    satellite = Satellite(center=[WIDTH/2, 50], velocity=[0, 0], radius=20, mass=10, color=COLORS[1])

    main()
