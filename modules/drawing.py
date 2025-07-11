import cv2

# Color Constants
RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
YELLOW = (0, 255, 255)
PURPLE = (255, 0, 255)
CYAN = (255, 255, 0)
WHITE = (255, 255, 255)
LIGHT_GRAY = (211, 211, 211)
MID_GRAY = (169, 169, 169)
DARKER_GRAY = (70, 70, 70)
BLACK = (0, 0, 0)
ORANGE = (0, 165, 255)
PINK = (203, 192, 255)
INDIGO = (130, 0, 75)
VIOLET = (238, 130, 238)

# Mapping from color tuples to readable names
COLOR_NAMES = {
    RED: "Red",
    GREEN: "Green",
    BLUE: "Blue",
    YELLOW: "Yellow",
    PURPLE: "Purple",
    CYAN: "Cyan",
    WHITE: "White",
    BLACK: "Black",
    ORANGE: "Orange",
    PINK: "Pink",
    INDIGO: "Indigo",
    VIOLET: "Violet",
}

# Available drawing shapes
FREE_DRAW = "Free Draw"
SHAPES = [FREE_DRAW]

# Common color list used in UI
COLORS = [
    RED, GREEN, BLUE, YELLOW, PURPLE, CYAN,
    WHITE, BLACK, ORANGE, PINK, INDIGO, VIOLET
]


class Shape:
    """Abstract shape class with color and thickness."""
    def __init__(self, color, thickness):
        self.color = color
        self.thickness = thickness

    def draw(self, canvas):
        raise NotImplementedError("Draw method must be implemented by subclass")


class Rectangle(Shape):
    """Draws a rectangle on the canvas."""
    def __init__(self, start_point, end_point, color, thickness):
        super().__init__(color, thickness)
        self.start_point = start_point
        self.end_point = end_point

    def draw(self, canvas):
        cv2.rectangle(canvas, self.start_point, self.end_point, self.color, self.thickness)


class Circle(Shape):
    """Draws a circle on the canvas."""
    def __init__(self, center, radius, color, thickness):
        super().__init__(color, thickness)
        self.center = center
        self.radius = radius

    def draw(self, canvas):
        cv2.circle(canvas, self.center, self.radius, self.color, self.thickness)


class Line(Shape):
    """Draws a line on the canvas."""
    def __init__(self, start_point, end_point, color, thickness):
        super().__init__(color, thickness)
        self.start_point = start_point
        self.end_point = end_point

    def draw(self, canvas):
        cv2.line(canvas, self.start_point, self.end_point, self.color, self.thickness)