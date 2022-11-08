import random
from p5 import *
from math import pi

brush_list = []


def setup():
    size(500, 500)
    background(255)
    for i in range(50):
        brush_list.append(Brush())


def draw():
    for brush in brush_list:
        brush.paint()


class Brush:
    def __init__(self):
        self.angle = 0
        self.components = []
        self.color = None
        self.angle = random.random() * 2 * pi
        self.x = random.random() * 500
        self.y = random.random() * 500
        self.R, self.G, self.B = random.random() * 255, random.random() * 255, random.random() * 255

        for i in range(4):
            self.components.append(random.randint(1, 4))

    def paint(self):
        # a = 0
        r = 50
        # u = random.random() * 0.5 + 0.5
        velocity = random.random() * 0.15 + 1.5

        fill(self.R, self.G, self.B, 10)
        no_stroke()

        # begin_shape()
        # while a < 2 * pi:
        #     vertex(x1, y1)
        #     v = random.random() * 0.15 + 0.85
        #     x1 = self.x + r * cos(self.angle + a) * u * v
        #     y1 = self.y + r * sin(self.angle + a) * u * v
        #     a += pi / 180
        #     for i in range(2):
        #         r += sin(a * self.components[i])
        #
        # end_shape(CLOSE)
        ellipse(self.x, self.y, r, r)

        self.x += velocity * cos(self.angle)
        self.y += velocity * sin(self.angle)
        self.angle += random.random() * 2 * pi / 180

        if self.x - r < 0 or self.x + r > 500 or self.y - r < 0 or self.y + r > 500:
            self.angle += pi / 2


run()
