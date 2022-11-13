#!/bin/python3

import pyglet

from math import sin, cos, acos, atan, pi
from random import randint

G = 6.67408 * 10**-11

SOLAR_MASS = 2 * 10**30
EARTH_MASS = 5.9 * 10**24
MOON_MASS = 7.3 * 10**22

def gravity_force(m1, m2, r): 
    if not r:
        return 0
    return (5*m1*m2)/(r**2)


class Vec2:
    def __init__(self, *args, **kwargs):
        
        if len(args) == 1:
            self.x = args[0]
            self.y = args[0]

        elif ('x' in kwargs and 'y' in kwargs):
            self.x: float = kwargs['x']
            self.y: float = kwargs['y']        
            
        elif ('mag' in kwargs and 'arg' in kwargs):
            self.x: float = cos(kwargs['arg']) * kwargs['mag']
            self.y: float = sin(kwargs['arg']) * kwargs['mag']

    def __add__(self, term):
        return Vec2(x=self.x + term.x, y=self.y + term.y)

    def __sub__(self, term):
        return Vec2(x=self.x - term.x, y=self.y - term.y)
    
    def __mul__(self, factor):
        return Vec2(x=self.x*factor, y=self.y*factor)

    def rotate(self, theta):
        return Vec2(
            x=self.x*cos(theta) - self.y*sin(theta),
            y=self.x*sin(theta) + self.y*cos(theta)
        )

    def normalize(self):
        length = self.length
        if not length:
            return Vec2(0)
        return Vec2(x=self.x/length, y=self.y/length)

    @property
    def length(self) -> float:
        return (self.x**2 + self.y**2) ** 0.5

    def __str__(self):
        return f"x={self.x:.4f}, y={self.y:.4f}"


class Entity:
    def __init__(self, batch: pyglet.graphics.Batch, mass: float, radius: float = 0, position: Vec2 = Vec2(0), velocity: Vec2 = Vec2(0)):
        self.mass: float = mass
        
        self.force: Vec2 = Vec2(0)
        self.acceleration: Vec2 = Vec2(0)
        self.velocity: Vec2 = velocity
        self.position: Vec2 = position

        self.radius = mass * 2 if not radius else radius
        self.color = randint(0, 255), randint(0, 255), randint(0, 255)
        self.shape = pyglet.shapes.Circle(
            self.position.x, self.position.y, radius=self.radius, color=self.color, batch=batch
        )

    def move(self, bounds: Vec2, *entities):
        self.acceleration = Vec2(
            x=self.force.x / self.mass, y=self.force.y / self.mass
        )

        self.velocity += self.acceleration
        self.position += self.velocity

        self.shape.x, self.shape.y = self.position.x, self.position.y

        if (self.position.x < 0 or self.position.x > bounds.x):
            self.velocity.x *= -1        
        if (self.position.y < 0 or self.position.y > bounds.y):
            self.velocity.y *= -1


class Body(Entity):
    def __init__(self, batch: pyglet.graphics.Batch, mass: float, radius: float = 0, position: Vec2 = Vec2(0), velocity: Vec2 = Vec2(0)):
        super().__init__(batch, mass=mass, radius=radius, position=position, velocity=velocity)

    def get_forces(self, *bodies):
        self.force = Vec2(0)
        for body in bodies:
            if body is not self:
                distance = (self.position - body.position).length
                if distance > self.radius + body.radius:
                    force = gravity_force(
                        self.mass, body.mass, 
                        distance
                    )
                    direction = (body.position - self.position).normalize()

                    self.force += Vec2(
                        x=force*direction.x, y=force*direction.y
                    )
                    # self.collided, body.collided = False, False
                elif distance < self.radius + body.radius:
                    self.collide(body)

    def collide(self, body):
        
        if ((self.position + self.velocity) - (body.position + body.velocity)).length > self.radius + body.radius:
            return  # they are not moving closer to each other

        elasticity = 1.0

        dp = body.position - self.position
        the1 = atan(dp.y / dp.x)

        tv1 = self.velocity.rotate(-the1)
        tv2 = body.velocity.rotate(-the1)
        
        tv1.x, tv2.x = \
            elasticity*(tv1.x*(self.mass - body.mass) + tv2.x*2*body.mass)/(self.mass + body.mass), \
            elasticity*(tv1.x*2*self.mass + tv2.x*(body.mass - self.mass))/(self.mass + body.mass)

        self.velocity = tv1.rotate(the1)
        body.velocity = tv2.rotate(the1)


class Window(pyglet.window.Window):
    def __init__(self, width, height, caption):
        super(Window, self).__init__(width=width, height=height, caption=caption)
        self.fps_display = pyglet.window.FPSDisplay(self)

        self.to_draw = []
        self.entities = []

    def track(self, *entities):
        for entity in entities:
            if isinstance(entity, pyglet.graphics.Batch):
                self.to_draw.append(entity)
            if isinstance(entity, Entity):
                self.entities.append(entity)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self.close()

    def on_key_release(self, symbol, modifiers):
        pass
            
    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_draw(self):
        self.clear()

        for entity in self.to_draw:
            entity.draw()

        self.fps_display.draw()

    def update(self, dt):
        for entity in self.entities:
            if isinstance(entity, Body):
                entity.get_forces(*self.entities)
            entity.move(Vec2(x=self.width, y=self.height), *self.entities)

    def start(self):
        pyglet.clock.schedule_interval(self.update, 1/120)
        pyglet.app.run()


def main():

    window = Window(900, 900, "gravity")

    bodies_batch = pyglet.graphics.Batch()
    bodies = [
        Body(batch=bodies_batch, mass=10, radius=20, position=Vec2(x=450, y=450), velocity=Vec2(x=-0.0, y=-0.0)),
        Body(batch=bodies_batch, mass=10, radius=20, position=Vec2(x=50, y=50), velocity=Vec2(x=0.1, y=0.1)),
        Body(batch=bodies_batch, mass=1, radius=5, position=Vec2(x=400, y=12), velocity=Vec2(x=0, y=0)),
        Body(batch=bodies_batch, mass=10, radius=20, position=Vec2(x=23, y=400), velocity=Vec2(x=-0, y=-0.5)),
        Body(batch=bodies_batch, mass=10, radius=20, position=Vec2(x=900, y=800), velocity=Vec2(x=-0.2, y=-0.1)),
        Body(batch=bodies_batch, mass=1, radius=5, position=Vec2(x=750, y=250), velocity=Vec2(x=-0, y=0)),
    ]

    window.track(bodies_batch, *bodies)
    
    window.start()


if __name__ == '__main__':
    main()
