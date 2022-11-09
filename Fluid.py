import random
from p5 import *
from math import pi

brush_list = []


def setup():
    size(200, 200)
    background(255)
    for i in range(10):
        brush_list.append(Brush())


def draw():
    for brush in brush_list:
        brush.paint()


def polygon(x, y, radius, npoints):
    angle = TWO_PI / npoints

    begin_shape()
    a = 0
    while a < TWO_PI:
        sx = x + cos(a) * radius
        sy = y + sin(a) * radius
        vertex(sx, sy)

        a = a + angle

    end_shape()


class Brush:
    def __init__(self):
        self.angle = 0
        self.angle = random.random() * 2 * pi
        self.x = random.random() * 200
        self.y = random.random() * 200
        self.R, self.G, self.B = random.random() * 450, random.random() * 450, random.random() * 450

    def paint(self):
        # a = 0
        r = 50
        delta_r = 10
        # u = random.random() * 0.5 + 0.5
        delta_v = 0.5
        velocity = random.random() * 0.15 + 1.5

        fill(self.R, self.G, self.B, 5)
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
        polygon(self.x, self.y, r, 15)

        self.x += velocity * cos(self.angle)
        self.y += velocity * sin(self.angle)
        self.angle += random.random() * pi / 180
        r += random.random() * delta_r - delta_r / 2
        velocity += random.random() * delta_v - delta_v / 2

        if self.x < 0 or self.x > 200 or self.y < 0 or self.y > 200:
            self.angle += pi


run()
