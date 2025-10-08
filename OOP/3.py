import math
import tkinter as tk
from tkinter import Canvas


class Shape:
    def get_perimeter(self):
        raise NotImplementedError("Метод должен быть реализован в подклассе")

    def get_area(self):
        raise NotImplementedError("Метод должен быть реализован в подклассе")

    @property
    def perimeter(self):
        return self.get_perimeter()

    @property
    def area(self):
        return self.get_area()


class Point(Shape):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_perimeter(self):
        return 0

    def get_area(self):
        return 0

    def draw(self, canvas):
        canvas.create_oval(self.x - 2, self.y - 2, self.x + 2, self.y + 2, fill="black", outline="black")
        canvas.create_text(self.x, self.y - 10)


class Line(Shape):
    def __init__(self, x1, y1, x2, y2):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.length = self._distance(x1, y1, x2, y2)

    def _distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def get_perimeter(self):
        return self.length

    def get_area(self):
        return 0

    def draw(self, canvas):
        canvas.create_line(self.x1, self.y1, self.x2, self.y2, fill="purple", width=2)


        mid_x = (self.x1 + self.x2) / 2
        mid_y = (self.y1 + self.y2) / 2
        canvas.create_text(mid_x, mid_y - 15)


class Circle(Shape):
    def __init__(self, center_x, center_y, radius):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius

    def get_perimeter(self):
        return 2 * math.pi * self.radius

    def get_area(self):
        return math.pi * self.radius * self.radius

    def draw(self, canvas):
        canvas.create_oval(
            self.center_x - self.radius,
            self.center_y - self.radius,
            self.center_x + self.radius,
            self.center_y + self.radius,
            outline="blue"
        )
        canvas.create_text(self.center_x, self.center_y)


class Square(Shape):
    def __init__(self, x1, y1, x2, y2, x3, y3, x4, y4):

        self.points = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
        self.side = self._distance(x1, y1, x2, y2)

    def _distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def get_perimeter(self):
        return self.side * 4

    def get_area(self):
        return self.side * self.side

    def draw(self, canvas):

        points_flat = [coord for point in self.points for coord in point]
        canvas.create_polygon(points_flat, outline="red", fill="")


        center_x = sum(point[0] for point in self.points) / 4
        center_y = sum(point[1] for point in self.points) / 4
        canvas.create_text(center_x, center_y)


class Triangle(Shape):
    def __init__(self, x1, y1, x2, y2, x3, y3):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.x3, self.y3 = x3, y3


        self.a = self._distance(x1, y1, x2, y2)
        self.b = self._distance(x2, y2, x3, y3)
        self.c = self._distance(x3, y3, x1, y1)

    def _distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def get_area(self):

        return abs((self.x1 * (self.y2 - self.y3) +
                    self.x2 * (self.y3 - self.y1) +
                    self.x3 * (self.y1 - self.y2)) / 2)

    def get_perimeter(self):
        return self.a + self.b + self.c

    def draw(self, canvas):
        points = [self.x1, self.y1, self.x2, self.y2, self.x3, self.y3]
        canvas.create_polygon(points, outline="green", fill="")


        center_x = (self.x1 + self.x2 + self.x3) / 3
        center_y = (self.y1 + self.y2 + self.y3) / 3
        canvas.create_text(center_x, center_y)


def create_square_from_top_left(x, y, side):

    return Square(x, y, x + side, y, x + side, y + side, x, y + side)


def main():
    try:
        root = tk.Tk()
        root.title("Фигуры по координатам")

        canvas = Canvas(root, width=500, height=400, bg="white")
        canvas.pack()


        shapes = [
            Point(50, 50),
            Line(80, 80, 150, 150),
            Triangle(200, 50, 150, 150, 250, 150),
            create_square_from_top_left(300, 50, 80),
            Circle(450, 120, 40)
        ]

        for shape in shapes:
            shape.draw(canvas)
            print(f"{shape.__class__.__name__}: Area = {shape.area:.1f}, Perimeter = {shape.perimeter:.1f}")

        btn = tk.Button(root, text="Close", command=root.quit)
        btn.pack(pady=5)

        root.mainloop()

    except tk.TclError as e:
        print(f"Tkinter error: {e}" )


if __name__ == "__main__":
    main()