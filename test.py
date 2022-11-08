from p5 import *


def draw():
    background(51)
    translate(mouse_x, mouse_y)
    fill(255)
    stroke(255)
    stroke_weight(2)
    begin_shape()
    vertex(0, -50)
    vertex(14, -20)
    vertex(47, -15)
    vertex(23, 7)
    vertex(29, 40)
    vertex(0, 25)
    vertex(-29, 40)
    vertex(-23, 7)
    vertex(-47, -15)
    vertex(-14, -20)
    end_shape("CLOSE")


run()
