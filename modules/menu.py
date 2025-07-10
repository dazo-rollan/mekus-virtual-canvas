import cv2
from modules.drawing import COLORS, SHAPES, ERASER, CLEAR_DRAWING

# === UI Constants ===
COLOR_BUTTON_RADIUS = 25
COLOR_BUTTON_SPACING = 55
COLOR_BUTTON_MAX = 8
COLOR_TOGGLE_OFFSET = 50

PEN_SIZE_MIN = 5
PEN_SIZE_MAX = 30
PEN_SIZE_STEP = 5
PEN_BUTTON_VERTICAL_SPACING = 50
PEN_BUTTON_OFFSET_Y = 60

SHAPE_BUTTON_SPACING = 80
SHAPE_BUTTON_RADIUS = 25
SHAPE_BUTTON_OFFSET_X = 60
SHAPE_COUNT = 4
SHAPE_BUTTON_ALPHA = 0.4

CLEAR_BUTTON_RADIUS = 30
TOGGLE_RADIUS = 30
OVERLAY_ALPHA = 0.5

TEXT_FONT = cv2.FONT_HERSHEY_SIMPLEX
TEXT_SCALE = 0.6
TEXT_THICKNESS = 1
LABEL_MARGIN = 10

LABEL_OFFSET_Y = 25
ERASER_LABEL_OFFSET_X = 30
THICKNESS_LABEL_OFFSET_X = 40
COLOR_LABEL_OFFSET_X = 30
BOARD_LABEL_OFFSET_X = 30

TOGGLE_CROSS_OFFSET = 8
PEN_BUTTON_OUTLINE = 4
BUTTON_GAP = 80

# === Color Constants ===
WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (60, 60, 60)
DARKER_GRAY = (100, 100, 100)
MID_GRAY = (80, 80, 80)
RED = (0, 0, 255)

# === Other Constants ===
MAX_ALPHA_VALUE = 255
BACKGROUND_WEIGHT_NORMED = 1
LINE_THICKNESS = 2
FILLED = -1


class CircleButton:
    """Represents a circular UI button with optional label."""

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

    def draw(self, image):
        """Draw the circular button with optional label."""
        overlay = image.copy()
        center = (self.center_x, self.center_y)
        cv2.circle(overlay, center, self.radius, self.color, FILLED)
        cv2.addWeighted(overlay, self.alpha, image, 1 - self.alpha, 0, image)

        if not self.label:
            return

        text_size = cv2.getTextSize(
            self.label, TEXT_FONT, TEXT_SCALE, TEXT_THICKNESS
        )[0]
        text_x = self.center_x - text_size[0] // 2
        text_y = self.center_y + self.radius + text_size[1] + LABEL_MARGIN

        cv2.putText(
            image,
            self.label,
            (text_x, text_y),
            TEXT_FONT,
            TEXT_SCALE,
            WHITE,
            TEXT_THICKNESS,
        )

    def is_over(self, cursor_x, cursor_y):
        """Check if cursor position is over the button."""
        dx = cursor_x - self.center_x
        dy = cursor_y - self.center_y
        return (dx**2 + dy**2) < self.radius**2


class Menu:
    """Manages the whiteboard tool menu and its UI buttons."""

    def __init__(self, board_toggle_pos, pen_toggle_pos):
        self.board_toggle_pos = board_toggle_pos
        self.pen_toggle_pos = pen_toggle_pos
        self.clear_button = None
        self.color_buttons = []
        self.pen_size_buttons = []
        self.shape_buttons = []
        self.current_hover = None

        self.initialize_button_positions()

    def initialize_button_positions(self):
        """Initialize positions for all UI buttons relative to toggles."""
        self.clear_button_pos = (
            self.pen_toggle_pos[0] - BUTTON_GAP,
            self.pen_toggle_pos[1],
        )
        self.eraser_button_pos = (
            self.clear_button_pos[0] - BUTTON_GAP,
            self.pen_toggle_pos[1],
        )
        self.color_toggle_pos = (
            self.eraser_button_pos[0] - BUTTON_GAP,
            self.pen_toggle_pos[1],
        )

    def create_buttons(self):
        """Create all UI buttons including color, pen size, shape, and clear buttons."""
        self.create_color_buttons()
        self.create_pen_size_buttons()
        self.create_shape_buttons()
        self.create_clear_button()

    def create_color_buttons(self):
        """Create color selection buttons."""
        self.color_buttons = [
            CircleButton(
                self.color_toggle_pos[0]
                - COLOR_TOGGLE_OFFSET
                - color_index * COLOR_BUTTON_SPACING,
                self.color_toggle_pos[1],
                COLOR_BUTTON_RADIUS,
                color,
            )
            for color_index, color in enumerate(COLORS[:COLOR_BUTTON_MAX])
        ]

    def create_pen_size_buttons(self):
        """Create pen size selection buttons."""
        self.pen_size_buttons = [
            CircleButton(
                self.pen_toggle_pos[0],
                self.pen_toggle_pos[1]
                + PEN_BUTTON_OFFSET_Y
                + size_index * PEN_BUTTON_VERTICAL_SPACING,
                pen_size,
                MID_GRAY,
                is_pen=True,
            )
            for size_index, pen_size in enumerate(
                range(PEN_SIZE_MIN, PEN_SIZE_MAX, PEN_SIZE_STEP)
            )
        ]

    def create_shape_buttons(self):
        """Create shape selection buttons."""
        self.shape_buttons = [
            CircleButton(
                self.board_toggle_pos[0]
                + TOGGLE_RADIUS
                + SHAPE_BUTTON_OFFSET_X
                + shape_index * SHAPE_BUTTON_SPACING,
                self.board_toggle_pos[1],
                SHAPE_BUTTON_RADIUS,
                DARK_GRAY,
                shape,
            )
            for shape_index, shape in enumerate(SHAPES[:SHAPE_COUNT])
        ]

    def create_clear_button(self):
        """Create clear canvas button."""
        self.clear_button = CircleButton(
            self.clear_button_pos[0],
            self.clear_button_pos[1],
            CLEAR_BUTTON_RADIUS,
            DARKER_GRAY,
            CLEAR_DRAWING,
        )

    def draw_toggle(
        self,
        frame,
        toggle_center_x,
        toggle_center_y,
        toggle_radius,
        is_toggle_on,
    ):
        """Draw a circular toggle button with optional 'X' mark when active."""
        toggle_center = (toggle_center_x, toggle_center_y)
        cv2.circle(frame, toggle_center, toggle_radius, WHITE, FILLED)
        cv2.circle(
            frame, toggle_center, toggle_radius, LIGHT_GRAY, LINE_THICKNESS
        )

        if not is_toggle_on:
            return

        offset = TOGGLE_CROSS_OFFSET
        cv2.line(
            frame,
            (toggle_center_x - offset, toggle_center_y - offset),
            (toggle_center_x + offset, toggle_center_y + offset),
            RED,
            LINE_THICKNESS,
        )
        cv2.line(
            frame,
            (toggle_center_x + offset, toggle_center_y - offset),
            (toggle_center_x - offset, toggle_center_y + offset),
            RED,
            LINE_THICKNESS,
        )

    def blend_canvas_with_frame(self, app):
        """Blend canvas and preview canvas with alpha onto the main frame."""
        alpha = app.canvas[..., 3:] / MAX_ALPHA_VALUE
        app.frame = (
            app.frame * (BACKGROUND_WEIGHT_NORMED - alpha)
            + app.canvas[..., :3] * alpha
        ).astype("uint8")

        preview_alpha = app.preview_canvas[..., 3:] / MAX_ALPHA_VALUE
        app.frame = (
            app.frame * (BACKGROUND_WEIGHT_NORMED - preview_alpha)
            + app.preview_canvas[..., :3] * preview_alpha
        ).astype("uint8")

    def draw_toggle_labels(self, app):
        """Draw labels for all toggle buttons."""
        self.draw_label(
            app, "Board", self.board_toggle_pos, BOARD_LABEL_OFFSET_X
        )
        self.draw_label(
            app, "Colors", self.color_toggle_pos, COLOR_LABEL_OFFSET_X
        )
        self.draw_label(
            app, "Thickness", self.pen_toggle_pos, THICKNESS_LABEL_OFFSET_X
        )
        self.draw_label(
            app, "Eraser", self.eraser_button_pos, ERASER_LABEL_OFFSET_X
        )

    def draw_label(self, app, text, position, offset_x):
        """Draw a single label under a toggle button."""
        cv2.putText(
            app.frame,
            text,
            (
                position[0] - offset_x,
                position[1] + TOGGLE_RADIUS + LABEL_OFFSET_Y,
            ),
            TEXT_FONT,
            TEXT_SCALE,
            WHITE,
            TEXT_THICKNESS,
        )

    def draw_toggles(self, app):
        """Draw all toggle buttons."""
        self.draw_toggle(
            app.frame,
            *self.board_toggle_pos,
            TOGGLE_RADIUS,
            not app.is_canvas_hidden,
        )
        self.draw_toggle(
            app.frame,
            *self.pen_toggle_pos,
            TOGGLE_RADIUS,
            not app.are_pen_sizes_hidden,
        )
        self.draw_toggle(
            app.frame,
            *self.color_toggle_pos,
            TOGGLE_RADIUS,
            not app.are_colors_hidden,
        )
        self.draw_toggle(
            app.frame,
            *self.eraser_button_pos,
            TOGGLE_RADIUS,
            app.is_using_eraser,
        )

    def draw_pen_size_buttons(self, app):
        """Draw pen size selection buttons with white outlines."""
        for pen_button in self.pen_size_buttons:
            cv2.circle(
                app.frame,
                (pen_button.center_x, pen_button.center_y),
                pen_button.radius + PEN_BUTTON_OUTLINE,
                WHITE,
                FILLED,
            )
            cv2.circle(
                app.frame,
                (pen_button.center_x, pen_button.center_y),
                pen_button.radius,
                pen_button.color,
                FILLED,
            )

    def draw_ui(self, app):
        """Draw the entire UI overlay on the app frame."""
        self.blend_canvas_with_frame(app)
        self.draw_toggles(app)
        self.draw_toggle_labels(app)

        if app.is_canvas_hidden:
            return

        self.clear_button.draw(app.frame)

        if not app.are_colors_hidden:
            for color_button in self.color_buttons:
                color_button.draw(app.frame)

        if not app.are_pen_sizes_hidden:
            self.draw_pen_size_buttons(app)

        for shape_button in self.shape_buttons:
            shape_button.alpha = SHAPE_BUTTON_ALPHA
            shape_button.draw(app.frame)

    def handle_interaction(self, finger_pos, is_clicking):
        """Handle finger position and click state with all buttons."""
        if finger_pos is None:
            self.current_hover = None
            return None

        for button in self.get_all_buttons():
            if not button.is_over(finger_pos[0], finger_pos[1]):
                continue

            self.current_hover = button
            return button if is_clicking else None

        self.current_hover = None
        return None

    def get_all_buttons(self):
        """Return a combined list of all buttons for interaction checking."""
        return (
            [self.clear_button]
            + self.color_buttons
            + self.pen_size_buttons
            + self.shape_buttons
        )
