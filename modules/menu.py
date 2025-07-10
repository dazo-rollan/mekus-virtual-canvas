# Imports OpenCV and NumPy for image handling and UI components
import cv2
import numpy as np

# Imports constants from drawing.py like color options and shape modes
from drawing import (
    COLORS, CLEAR, ERASER, WHITE,
    SHAPES, FREE_DRAW, SHAPE_CIRCLE,
    SHAPE_RECTANGLE, SHAPE_LINE
)

# Global states and drawing settings
canvas, preview_canvas, frame = None, None, None
drawing = False
start_x = start_y = x = y = -1
current_color = COLORS[0]
brush_size = 5
eraser_size = 30
using_eraser = False
current_shape = FREE_DRAW

# UI visibility flags
hide_board = True
hide_colors = True
hide_pen_sizes = True

# Toggle positions
toggle_radius = 30
board_toggle_x, board_toggle_y = 80, 50
pen_toggle_x, pen_toggle_y = 1170, 50
clear_x = pen_toggle_x - 80
eraser_x = clear_x - 80
color_toggle_x = eraser_x - 80
eraser_y = color_toggle_y = clear_y = pen_toggle_y

# UI elements
color_buttons, pen_buttons, shape_buttons = [], [], []
clear_button = None


class CircleButton:
    """
    Represents a circular UI button for color, pen size, shape, or clear
    action.

    Attributes:
        cx (int): X-coordinate of button center.
        cy (int): Y-coordinate of button center.
        radius (int): Radius of the button.
        color (tuple): BGR color of the button.
        label (str): Optional text label (e.g., 'CLEAR' or shape type).
        is_pen (bool): True if this button is for selecting pen size.
    """
    def __init__(self, cx, cy, radius, color, label='', is_pen=False):
        self.cx = cx
        self.cy = cy
        self.radius = radius
        self.color = color
        self.label = label
        self.is_pen = is_pen
        self.alpha = 0.5

    def draw(self, img):
        """
        Draws the button on a given image.

        Args:
            img (ndarray): The image (usually frame) to draw the button on.
        """
        overlay = img.copy()
        cv2.circle(overlay, (self.cx, self.cy), self.radius,
                   self.color, -1)
        cv2.addWeighted(overlay, self.alpha, img, 1 - self.alpha,
                        0, img)
        if not self.label:
            return
        font = cv2.FONT_HERSHEY_SIMPLEX
        size = cv2.getTextSize(self.label, font, 0.6, 1)[0]
        pos = (self.cx - size[0] // 2,
               self.cy + self.radius + size[1] + 10)
        cv2.putText(img, self.label, pos, font, 0.6,
                    (255, 255, 255), 1)

    def is_over(self, x, y):
        """
        Checks if a given point (x, y) is inside the button's area.

        Args:
            x (int): X-coordinate of the point.
            y (int): Y-coordinate of the point.

        Returns:
            bool: True if the point is inside the button.
        """
        return (x - self.cx) ** 2 + (y - self.cy) ** 2 < self.radius ** 2


def create_buttons():
    """
    Initializes color, pen size, shape, and clear action buttons.

    This populates global lists: color_buttons, pen_buttons, and
    shape_buttons. It also initializes the clear_button object.
    """
    global color_buttons, pen_buttons, shape_buttons, clear_button

    color_buttons = [
        CircleButton(color_toggle_x - 50 - i * 55, color_toggle_y,
                     25, c) for i, c in enumerate(COLORS[:8])
    ]

    pen_buttons = [
        CircleButton(pen_toggle_x, pen_toggle_y + 60 + i * 50,
                     size, (80, 80, 80), is_pen=True)
        for i, size in enumerate(range(5, 30, 5))
    ]

    shape_buttons = [
        CircleButton(board_toggle_x + toggle_radius + 60 + i * 80,
                     board_toggle_y, 25, (60, 60, 60), shape)
        for i, shape in enumerate(SHAPES[:3])  # LINE, RECTANGLE, CIRCLE
    ]

    clear_button = CircleButton(clear_x, clear_y, 30,
                                (100, 100, 100), CLEAR)


def draw_toggle(x, y, r, is_on):
    """
    Draws a toggle UI element at (x, y) with given radius and state.

    Args:
        x (int): X-coordinate of the toggle center.
        y (int): Y-coordinate of the toggle center.
        r (int): Radius of the toggle button.
        is_on (bool): If True, draws a red "X" to show it's active.
    """
    cv2.circle(frame, (x, y), r, (255, 255, 255), -1)
    cv2.circle(frame, (x, y), r, (200, 200, 200), 2)
    if not is_on:
        return
    offset = 8
    cv2.line(frame, (x - offset, y - offset),
             (x + offset, y + offset), (0, 0, 255), 2)
    cv2.line(frame, (x + offset, y - offset),
             (x - offset, y + offset), (0, 0, 255), 2)


def is_inside_whiteboard(x, y):
    """
    Checks if a point (x, y) is within the drawable whiteboard area.

    Args:
        x (int): X-coordinate of the point.
        y (int): Y-coordinate of the point.

    Returns:
        bool: True if the point is within the whiteboard bounds.
    """
    return 50 < x < 1070 and 120 < y < 700


def draw_ui():
    """
    Renders all UI elements including:
    - Blending the canvas and preview layers with the live frame
    - Drawing toggles for UI options
    - Displaying color, pen, shape, and clear buttons
    """
    alpha = canvas[..., 3:] / 255.0
    frame[:] = (frame * (1 - alpha) +
                canvas[..., :3] * alpha).astype(np.uint8)

    preview_alpha = preview_canvas[..., 3:] / 255.0
    frame[:] = (frame * (1 - preview_alpha) +
                preview_canvas[..., :3] * preview_alpha).astype(np.uint8)

    draw_toggle(board_toggle_x, board_toggle_y,
                toggle_radius, not hide_board)
    cv2.putText(frame, "Board", (board_toggle_x - 30,
                board_toggle_y + toggle_radius + 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    if hide_board:
        return

    draw_toggle(pen_toggle_x, pen_toggle_y,
                toggle_radius, not hide_pen_sizes)
    draw_toggle(color_toggle_x, color_toggle_y,
                toggle_radius, not hide_colors)
    draw_toggle(eraser_x, eraser_y,
                toggle_radius, using_eraser)

    cv2.putText(frame, "Colors", (color_toggle_x - 30,
                color_toggle_y + toggle_radius + 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(frame, "Thickness", (pen_toggle_x - 40,
                pen_toggle_y + toggle_radius + 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(frame, "Eraser", (eraser_x - 30,
                eraser_y + toggle_radius + 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    clear_button.draw(frame)

    if not hide_colors:
        for c in color_buttons:
            c.draw(frame)

    if not hide_pen_sizes:
        for p in pen_buttons:
            cv2.circle(frame, (p.cx, p.cy), p.radius + 4,
                       (255, 255, 255), -1)
            cv2.circle(frame, (p.cx, p.cy), p.radius, p.color, -1)

    for s in shape_buttons:
        s.alpha = 0.4
        s.draw(frame)


def handle_mouse(event, mx, my, *_):
    """
    Handles mouse interactions like clicking, drawing, erasing, and
    selecting UI options.

    Args:
        event (int): OpenCV mouse event type.
        mx (int): X-coordinate of the mouse event.
        my (int): Y-coordinate of the mouse event.
    """
    global drawing, start_x, start_y, x, y
    global current_color, brush_size, using_eraser
    global hide_board, hide_colors, hide_pen_sizes, current_shape

    x, y = mx, my

    if event == cv2.EVENT_LBUTTONDOWN:
        start_x, start_y = mx, my
        drawing = True

        if (mx - board_toggle_x) ** 2 + (my - board_toggle_y) ** 2 < \
                toggle_radius ** 2:
            hide_board = not hide_board
            return

        if hide_board:
            return

        if (mx - pen_toggle_x) ** 2 + (my - pen_toggle_y) ** 2 < \
                toggle_radius ** 2:
            hide_pen_sizes = not hide_pen_sizes

        if (mx - color_toggle_x) ** 2 + (my - color_toggle_y) ** 2 < \
                toggle_radius ** 2:
            hide_colors = not hide_colors

        if (mx - eraser_x) ** 2 + (my - eraser_y) ** 2 < \
                toggle_radius ** 2:
            using_eraser = not using_eraser

        if clear_button.is_over(mx, my):
            canvas[:] = 0
            canvas[..., :3] = WHITE
            canvas[..., 3] = 0
            return

        for c in color_buttons:
            if c.is_over(mx, my):
                current_color = c.color
                using_eraser = False
                return

        for p in pen_buttons:
            if p.is_over(mx, my):
                brush_size = p.radius
                return

        for s in shape_buttons:
            if s.is_over(mx, my):
                current_shape = s.label
                return

    if event == cv2.EVENT_MOUSEMOVE:
        if not drawing or hide_board:
            return

        if not is_inside_whiteboard(mx, my):
            return

        if using_eraser:
            mask = np.zeros_like(canvas[..., 0])
            cv2.circle(mask, (mx, my), eraser_size, 255, -1)
            canvas[mask == 255] = [255, 255, 255, 0]
            return

        if current_shape != FREE_DRAW:
            return

        b, g, r = current_color
        cv2.line(canvas, (start_x, start_y), (mx, my),
                 (b, g, r, 255), brush_size)
        start_x, start_y = mx, my

    if event == cv2.EVENT_LBUTTONUP:
        drawing = False

        if hide_board or using_eraser:
            return

        if current_shape not in [SHAPE_LINE, SHAPE_RECTANGLE, SHAPE_CIRCLE]:
            return

        if not is_inside_whiteboard(mx, my):
            return

        if current_shape == SHAPE_LINE:
            cv2.line(canvas, (start_x, start_y), (mx, my),
                     current_color + (255,), brush_size)
        elif current_shape == SHAPE_RECTANGLE:
            cv2.rectangle(canvas, (start_x, start_y), (mx, my),
                          current_color + (255,), brush_size)
        elif current_shape == SHAPE_CIRCLE:
            cx = (start_x + mx) // 2
            cy = (start_y + my) // 2
            radius = int(((mx - start_x) ** 2 + (my - start_y) ** 2) ** 0.5 / 2)
            cv2.circle(canvas, (cx, cy), radius,
                       current_color + (255,), brush_size)


def setup():
    """
    Initializes the whiteboard environment including:
    - Transparent canvas
    - Preview canvas
    - UI buttons setup
    """
    global canvas, preview_canvas
    canvas = np.zeros((720, 1280, 4), np.uint8)
    canvas[..., :3] = WHITE
    canvas[..., 3] = 0
    preview_canvas = np.zeros_like(canvas)
    create_buttons()


def run_whiteboard():
    """
    Main application loop:
    - Captures webcam frames
    - Handles drawing and UI interactions
    - Displays blended frame output in a window

    Press 'q' to exit the application.
    """
    global frame

    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    cv2.namedWindow("video")
    cv2.setMouseCallback("video", handle_mouse)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        preview_canvas[:] = 0

        if drawing and not hide_board and not using_eraser and \
                is_inside_whiteboard(start_x, start_y) and \
                is_inside_whiteboard(x, y):

            if current_shape == SHAPE_LINE:
                cv2.line(preview_canvas, (start_x, start_y), (x, y),
                         current_color + (255,), brush_size)
            elif current_shape == SHAPE_RECTANGLE:
                cv2.rectangle(preview_canvas, (start_x, start_y), (x, y),
                              current_color + (255,), brush_size)
            elif current_shape == SHAPE_CIRCLE:
                cx = (start_x + x) // 2
                cy = (start_y + y) // 2
                radius = int(((x - start_x) ** 2 + (y - start_y) ** 2) ** 0.5 / 2)
                cv2.circle(preview_canvas, (cx, cy), radius,
                           current_color + (255,), brush_size)

        draw_ui()
        cv2.imshow("video", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    setup()
    run_whiteboard()