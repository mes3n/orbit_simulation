#/bin/python

import pyglet

from math import sin, cos, acos, pi


G = 6.67408 * 10**-11

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

    def multiply(self, vector) -> float:
        return self.x * vector.x + self.y * vector.y

    def mirror(self, normal):
        normal = normal.normalize()
        # print(self.dot_product(normal))
        return self - normal*self.dot_product(normal)*2

    def dot_product(self, vector) -> float:
        if not self.length or not vector.length:
            return 0
        return acos(
            round(self.multiply(vector), 4) / round(self.length*vector.length, 4)
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
        return f"{self.x}, {self.y}"


class Entity:
    def __init__(self, mass: float, position: Vec2 = Vec2(0)):
        self.mass: float = mass
        
        self.force: Vec2 = Vec2(0)
        self.acceleration: Vec2 = Vec2(0)
        self.velocity: Vec2 = Vec2(0)
        self.position: Vec2 = position

        self.radius = self.mass * 2
        self.shape = pyglet.shapes.Circle(
            self.position.x, self.position.y, radius=self.radius, color=(175, 30, 200)
        )

    def move(self, *entities):
        self.acceleration = Vec2(
            x=self.force.x / self.mass, y=self.force.y / self.mass
        )
        self.velocity += self.acceleration

        for entity in entities:
            if entity is not self:
                future_distance = ((self.position + self.velocity) - (entity.position + entity.velocity)).length
                if future_distance < self.radius + entity.radius:  # collision
                    
                    new_velocity_len = (self.mass - entity.mass)*self.velocity.length/(self.mass + entity.mass) \
                                + 2*entity.mass*entity.velocity.length/(self.mass + entity.mass)

                    self.velocity = self.velocity.mirror(((entity.position + entity.velocity) - (self.position + self.velocity))).normalize() * new_velocity_len
                    # self.velocity = Vec2(0) - self.velocity
                    print("bounce", self.mass)

        self.position += self.velocity

        self.shape.x, self.shape.y = self.position.x, self.position.y
        self.force = Vec2(0)

    @property
    def momentum(self):
        return self.mass * self.velocity.length

    @property
    def kinetic_energy(self):
        return self.mass * (self.velocity.length**2) * 0.5


class Body(Entity):
    def __init__(self, mass: float, position: Vec2 = Vec2(0)):
        super().__init__(mass=mass, position=position)

    def get_forces(self, *bodies):
        for body in bodies:
            if body is not self:
                distance = (self.position - body.position).length
                if distance > self.radius + body.radius:
                    force = gravity_force(
                        self.mass, body.mass, 
                        (self.position - body.position).length
                    )
                    direction = (body.position - self.position).normalize()

                    self.force += Vec2(
                        x=force*direction.x, y=force*direction.y
                    )

        # return

        for body in bodies:
            if body is not self:
                if (body.position - self.position).length <= self.radius + body.radius:  # collision
                    normal = self.position - body.position

                    total_momentum = self.momentum + body.momentum
                    kinetic_energy = self.kinetic_energy + body.kinetic_energy

                    self.velocity

                    # self.force = self.velocity.mirror(normal).normalize() * self.force.length
                    # self.velocity = Vec2(0)

                    # theta = self.force.dot_product(normal)  # angle from force to normal
                    # print(theta)
                    # length_of_new = self.force.length * sin(theta)

                    # alpha = normal.dot_product(Vec2(x=1, y=0))  # angle to x axis

                    # self.force = Vec2(mag=length_of_new, arg=alpha + pi*0.5)
                    # self.velocity = Vec2(0)


class Window(pyglet.window.Window):
    def __init__(self):
        super(Window, self).__init__(width=900, height=900, caption="Gravity")
        self.fps_display = pyglet.window.FPSDisplay(self)

        self.entities = []
        self.bodies = []

    def track(self, *entities):
        for entity in entities:
            self.entities.append(entity)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self.close()

    # def on_key_release(self, symbol, modifiers):
    #     if symbol == pyglet.window.key.ESCAPE:
    #         self.close()    
            
    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_draw(self):
        self.update()

        self.clear()

        for entity in self.entities:
            entity.shape.draw()

        self.fps_display.draw()

    def update(self):
        for entity in self.entities:
            if isinstance(entity, Body):
                entity.get_forces(*self.entities)
            entity.move(*self.entities)


def main():

    window = Window()

    bodies = [
        Body(mass=10, position=Vec2(x=370, y=370)),
        Body(mass=4, position=Vec2(x=400, y=400)),

        Body(mass=10, position=Vec2(x=23, y=324)),
        Body(mass=12, position=Vec2(x=800, y=227)),
        Body(mass=8, position=Vec2(x=22, y=645)),
        Body(mass=4, position=Vec2(x=766, y=11)),
        Body(mass=4, position=Vec2(x=243, y=11)),
        Body(mass=4, position=Vec2(x=22, y=11)),
        Body(mass=4, position=Vec2(x=414, y=11)),
        Body(mass=4, position=Vec2(x=882, y=11)),
    ]
    entities = [
        Body(mass=1, position=Vec2(x=450, y=450))
    ]
    window.track(*bodies)
    
    pyglet.app.run()


if __name__ == '__main__':
    main()

    # v1 = Vec2(x=3, y=5)
    # v2 = Vec2(x=-4, y=-2).normalize()

    # print(f"{v1.x}, {v1.y}")
    # print(f"{v2.x}, {v2.y}")

    # for i in range(4):
    #     v1 += v2
    #     print(f"{v1.x}, {v1.y}")

