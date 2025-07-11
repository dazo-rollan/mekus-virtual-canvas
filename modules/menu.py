import cv2
import numpy as np
from modules.drawing import (
    COLORS,
    WHITE,
    LIGHT_GRAY,
    DARK_GRAY,
    DARKER_GRAY,
    MID_GRAY,
    RED,
)

# UI Constants
BUTTON_RADIUS = 25
TOGGLE_RADIUS = 30
BUTTON_SPACING = 75
MAX_COLORS = 8
PEN_SIZE_MIN = 5
PEN_SIZE_MAX = 30
PEN_SIZE_STEP = 5
OVERLAY_ALPHA = 0.5
SHAPE_BUTTON_ALPHA = 0.4

# Text Constants
FONT = cv2.FONT_HERSHEY_SIMPLEX
TEXT_SCALE = 0.6
TEXT_THICKNESS = 1
LABEL_MARGIN = 10
LABEL_OFFSET_Y = 25


class CircleButton:
    """Represents a circular UI button."""

    def __init__(
        self, center_x, center_y, radius, color, label="", is_pen=False
    ):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.color = color
        self.label = label
        self.is_pen = is_pen
        self.alpha = OVERLAY_ALPHA

    def draw(self, frame):
        """Draw the button on the frame."""
        overlay = frame.copy()
        center = (self.center_x, self.center_y)

        cv2.circle(overlay, center, self.radius, self.color, -1)
        cv2.addWeighted(overlay, self.alpha, frame, 1 - self.alpha, 0, frame)

        if self.label:
            text_size = cv2.getTextSize(
                self.label, FONT, TEXT_SCALE, TEXT_THICKNESS
            )[0]
            text_x = self.center_x - text_size[0] // 2
            text_y = self.center_y + self.radius + text_size[1] + LABEL_MARGIN

            cv2.putText(
                frame,
                self.label,
                (text_x, text_y),
                FONT,
                TEXT_SCALE,
                WHITE,
                TEXT_THICKNESS,
            )

    def is_over(self, x, y):
        """Check if point (x,y) is inside the button."""
        return (x - self.center_x) ** 2 + (
            y - self.center_y
        ) ** 2 < self.radius**2


class Menu:
    """Manages the UI menu for the virtual canvas."""

    def __init__(self, board_toggle_pos, pen_toggle_pos):
        self.board_toggle_pos = board_toggle_pos
        self.pen_toggle_pos = pen_toggle_pos

        # Button positions
        self.clear_button_pos = (pen_toggle_pos[0] - 80, pen_toggle_pos[1])
        self.eraser_button_pos = (
            self.clear_button_pos[0] - 80,
            pen_toggle_pos[1],
        )
        self.color_toggle_pos = (
            self.eraser_button_pos[0] - 80,
            pen_toggle_pos[1],
        )

        # Button collections
        self.color_buttons = []
        self.pen_size_buttons = []
        self.shape_buttons = []
        self.clear_button = None
        self.current_hover = None

        self.create_buttons()

    def create_buttons(self):
        """Create all UI buttons."""
        self.create_color_buttons()
        self.create_pen_size_buttons()
        self.create_shape_buttons()
        self.create_clear_button()
        self.create_toggle_buttons()

    def create_color_buttons(self):
        """Create color selection buttons."""
        self.color_buttons = [
            CircleButton(
                self.color_toggle_pos[0]
                - BUTTON_SPACING
                - index * BUTTON_SPACING,
                self.color_toggle_pos[1],
                BUTTON_RADIUS,
                color,
            )
            for index, color in enumerate(COLORS[:MAX_COLORS])
        ]

    def create_pen_size_buttons(self):
        """Create pen size selection buttons."""
        self.pen_size_buttons = [
            CircleButton(
                self.pen_toggle_pos[0],
                self.pen_toggle_pos[1]
                + BUTTON_SPACING
                + index * BUTTON_SPACING,
                size,
                MID_GRAY,
                is_pen=True,
            )
            for index, size in enumerate(
                range(PEN_SIZE_MIN, PEN_SIZE_MAX, PEN_SIZE_STEP)
            )
        ]

    def create_shape_buttons(self):
        """Create shape selection buttons."""
        self.shape_buttons = [
            CircleButton(
                self.board_toggle_pos[0] + 60,
                self.board_toggle_pos[1],
                BUTTON_RADIUS,
                DARK_GRAY,
                "Free Draw",
            )
        ]

    def create_clear_button(self):
        """Create clear canvas button."""
        self.clear_button = CircleButton(
            *self.clear_button_pos, BUTTON_RADIUS, DARKER_GRAY, "Clear"
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
        """Draw the entire UI on the frame."""

        self.board_toggle.draw(frame)

        # Draw buttons if visible
        if app.show_canvas:
            print("Drawing canvas buttons")
            self.clear_button.draw(frame)
            self.pen_toggle.draw(frame)
            self.color_toggle.draw(frame)
            self.eraser_toggle.draw(frame)

            if app.show_colors:
                print("Drawing color buttons")
                for button in self.color_buttons:
                    button.draw(frame)

            if app.show_brush_sizes:
                print("Drawing pen size buttons")
                for button in self.pen_size_buttons:
                    # Draw white outline for pen size buttons
                    cv2.circle(
                        frame,
                        (button.center_x, button.center_y),
                        button.radius + 4,
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

            for button in self.shape_buttons:
                button.alpha = SHAPE_BUTTON_ALPHA
                button.draw(frame)

    def draw(self, frame):
        """Draw the button on the frame."""
        # Create overlay for transparency effect
        overlay = frame.copy()
        center = (self.center_x, self.center_y)

        # Draw button
        cv2.circle(overlay, center, self.radius, self.color, -1)

        # Apply transparency
        cv2.addWeighted(overlay, self.alpha, frame, 1 - self.alpha, 0, frame)

        # Draw label if exists
        if self.label:
            text_size = cv2.getTextSize(
                self.label, FONT, TEXT_SCALE, TEXT_THICKNESS
            )[0]
            text_x = self.center_x - text_size[0] // 2
            text_y = self.center_y + self.radius + text_size[1] + LABEL_MARGIN

            cv2.putText(
                frame,
                self.label,
                (text_x, text_y),
                FONT,
                TEXT_SCALE,
                WHITE,
                TEXT_THICKNESS,
            )

    def handle_interaction(self, finger_pos, is_clicking):
        """Handle button interactions."""
        if finger_pos is None:
            self.current_hover = None
            return None

        for button in self.get_all_buttons():
            if button.is_over(finger_pos[0], finger_pos[1]):
                self.current_hover = button
                return button if is_clicking else None

        self.current_hover = None
        return None

    def get_all_buttons(self):
        """Get all buttons for interaction checking."""
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
