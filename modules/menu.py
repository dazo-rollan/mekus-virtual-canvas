import cv2
import numpy as np
from modules.drawing import (
    COLORS, 
    WHITE, 
    LIGHT_GRAY, 
    MID_GRAY, 
    COLOR_NAMES
)

# UI Button Constants
BUTTON_RADIUS = 25
TOGGLE_RADIUS = 30
BUTTON_SPACING = 75
PEN_SIZE_OFFSET_Y = 65
MAX_COLORS = 8
PEN_SIZE_MIN = 5
PEN_SIZE_MAX = 30
PEN_SIZE_STEP = 5
OVERLAY_ALPHA = 0.8

# Text Display Constants
FONT = cv2.FONT_HERSHEY_SIMPLEX
TEXT_SCALE = 0.6
TEXT_THICKNESS = 1
LABEL_MARGIN = 10
LABEL_BOTTOM_MARGIN = 20
LABEL_OUTLINE_WIDTH = 4

# Button Position Offsets
CLEAR_OFFSET_X = 80
ERASER_OFFSET_X = 80
COLOR_OFFSET_X = 80


class CircleButton:
    """Represents a circular button element in the UI."""

    def __init__(self, center_x, center_y, radius, color,
                 label="", is_pen=False, value=None):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.color = color
        self.label = label
        self.is_pen = is_pen
        self.value = value
        self.alpha = OVERLAY_ALPHA

    def draw(self, frame):
        """Render the circular button with optional label."""
        overlay = frame.copy()
        center = (self.center_x, self.center_y)
        cv2.circle(overlay, center, self.radius, self.color, -1)
        cv2.addWeighted(overlay, self.alpha, frame, 1 - self.alpha, 0, frame)

        if not self.label:
            return
        text_size = cv2.getTextSize(
            self.label, FONT, TEXT_SCALE, TEXT_THICKNESS
        )[0]
        text_x = self.center_x - text_size[0] // 2
        text_y = self.center_y + self.radius + text_size[1] + LABEL_MARGIN
        cv2.putText(frame, self.label, (text_x, text_y),
                    FONT, TEXT_SCALE, WHITE, TEXT_THICKNESS)

    def is_over(self, x, y):
        """Return True if (x, y) is inside the button area."""
        return (x - self.center_x) ** 2 + (y - self.center_y) ** 2 \
            < self.radius ** 2


class Menu:
    """UI Manager for all on-screen buttons in the drawing app."""

    def __init__(self, board_toggle_pos, pen_toggle_pos):
        self.board_toggle_pos = board_toggle_pos
        self.pen_toggle_pos = pen_toggle_pos
        self.last_message = ""

        self.clear_button_pos = (
            pen_toggle_pos[0] - CLEAR_OFFSET_X, pen_toggle_pos[1]
        )
        self.eraser_button_pos = (
            self.clear_button_pos[0] - ERASER_OFFSET_X, pen_toggle_pos[1]
        )
        self.color_toggle_pos = (
            self.eraser_button_pos[0] - COLOR_OFFSET_X, pen_toggle_pos[1]
        )

        self.color_buttons = []
        self.pen_size_buttons = []
        self.shape_buttons = []
        self.clear_button = None
        self.current_hover = None
        self.create_buttons()

    def create_buttons(self):
        self.create_color_buttons()
        self.create_pen_size_buttons()
        self.create_shape_buttons()
        self.create_clear_button()
        self.create_toggle_buttons()

    def create_color_buttons(self):
        self.color_buttons = [
            CircleButton(
                self.color_toggle_pos[0] - BUTTON_SPACING - index * BUTTON_SPACING,
                self.color_toggle_pos[1],
                BUTTON_RADIUS,
                color,
            )
            for index, color in enumerate(
                [c for c in COLORS if c != WHITE][:MAX_COLORS]
            )
        ]

    def create_pen_size_buttons(self):
        sizes = list(range(PEN_SIZE_MIN, PEN_SIZE_MAX + 1, PEN_SIZE_STEP))
        base_y = self.pen_toggle_pos[1] + PEN_SIZE_OFFSET_Y
        self.pen_size_buttons = [
            CircleButton(
                self.pen_toggle_pos[0],
                base_y + index * BUTTON_SPACING,
                BUTTON_RADIUS,
                MID_GRAY,
                label=str(size),
                is_pen=True,
                value=size
            )
            for index, size in enumerate(sizes)
        ]

    def create_shape_buttons(self):
        self.shape_buttons = []

    def create_clear_button(self):
        self.clear_button = CircleButton(
            *self.clear_button_pos, TOGGLE_RADIUS, LIGHT_GRAY, "Clear"
        )

    def create_toggle_buttons(self):
        self.board_toggle = CircleButton(
            *self.board_toggle_pos, TOGGLE_RADIUS, LIGHT_GRAY, "Board"
        )
        self.pen_toggle = CircleButton(
            *self.pen_toggle_pos, TOGGLE_RADIUS, LIGHT_GRAY, "Size"
        )
        self.color_toggle = CircleButton(
            *self.color_toggle_pos, TOGGLE_RADIUS, LIGHT_GRAY, "Colors"
        )
        self.eraser_toggle = CircleButton(
            *self.eraser_button_pos, TOGGLE_RADIUS, LIGHT_GRAY, "Eraser"
        )

    def draw_ui(self, app, frame):
        self.board_toggle.draw(frame)
        if not app.show_canvas:
            return

        self.clear_button.draw(frame)
        self.pen_toggle.draw(frame)
        self.color_toggle.draw(frame)
        self.eraser_toggle.draw(frame)

        if app.show_colors:
            for button in self.color_buttons:
                button.draw(frame)

        if app.show_brush_sizes:
            for button in self.pen_size_buttons:
                cv2.circle(
                    frame,
                    (button.center_x, button.center_y),
                    button.radius + LABEL_OUTLINE_WIDTH,
                    WHITE,
                    -1,
                )
                cv2.circle(
                    frame,
                    (button.center_x, button.center_y),
                    button.radius,
                    button.color,
                    -1,
                )
                if not button.label:
                    continue
                text_size = cv2.getTextSize(
                    button.label, FONT, TEXT_SCALE, TEXT_THICKNESS
                )[0]
                text_x = button.center_x - text_size[0] // 2
                text_y = button.center_y + text_size[1] // 2
                cv2.putText(frame, button.label, (text_x, text_y),
                            FONT, TEXT_SCALE, WHITE,
                            TEXT_THICKNESS, cv2.LINE_AA)

        if not self.last_message:
            return

        text_size = cv2.getTextSize(
            self.last_message, FONT, TEXT_SCALE, TEXT_THICKNESS
        )[0]
        text_x = frame.shape[1] - text_size[0] - LABEL_BOTTOM_MARGIN
        text_y = frame.shape[0] - LABEL_BOTTOM_MARGIN
        cv2.putText(frame, self.last_message, (text_x, text_y),
                    FONT, TEXT_SCALE, WHITE,
                    TEXT_THICKNESS, cv2.LINE_AA)

    def handle_interaction(self, finger_pos, is_clicking):
        if finger_pos is None:
            self.current_hover = None
            return None

        for button in self.get_all_buttons():
            if not button.is_over(finger_pos[0], finger_pos[1]):
                continue

            self.current_hover = button
            if not is_clicking:
                return None

            if button in self.color_buttons:
                name = COLOR_NAMES.get(tuple(button.color), str(button.color))
                self.last_message = f"Selected Color: {name}"
            elif button in self.pen_size_buttons:
                self.last_message = f"Pen Thickness: {button.value}"
            elif button == self.eraser_toggle:
                self.last_message = "Eraser Selected"
            else:
                self.last_message = ""
            return button

        self.current_hover = None
        return None

    def get_all_buttons(self):
        return [
            self.clear_button,
            *self.color_buttons,
            *self.pen_size_buttons,
            *self.shape_buttons,
            self.board_toggle,
            self.pen_toggle,
            self.color_toggle,
            self.eraser_toggle,
        ]
