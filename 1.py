import math
from math import radians

class Shape:
    def get_perimeter(self):
        raise EOFError
    def get_area(self):
        raise EOFError

    @property
    def perimeter(self):
        return self.get_perimeter()

    @property
    def area(self):
        return self.get_area()


class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    def get_perimeter(self):
        return 2 * 3.14 * self.radius
    def get_area(self):
        return 3.14 * self.radius * self.radius


class Square(Shape):
    def __init__(self, side):
        self.side = side
    def get_perimeter(self):
        return self.side * 4
    def get_area(self):
        return self.side * self.side


class Triangle(Shape):
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c
    def get_area(self):
        p = self.a + self.b + self.c
        return math.sqrt(p * (p - self.a) * (p - self.b) * (p - self.c))
    def get_perimeter(self):
        return self.a + self.b + self.c

Test = [Triangle(2, 2, 2), Square(2), Triangle(1, 2, 3)]
for i in Test:
    print(f"{i.area:.1f}")