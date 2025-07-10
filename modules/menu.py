import cv2
from drawing import COLORS, SHAPES, ERASER, CLEAR_DRAWING

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
LINE_THICKNESS = 2
FILLED = -1


class CircleButton:
    """
    Represents a circular UI button.
    """

    def __init__(self, center_x, center_y, radius, color,
                 label='', is_pen=False):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.color = color
        self.label = label
        self.is_pen = is_pen
        self.alpha = OVERLAY_ALPHA

    def draw(self, image):
        """
        Draw the circular button with optional label.
        """
        overlay = image.copy()
        center = (self.center_x, self.center_y)
        cv2.circle(overlay, center, self.radius, self.color, FILLED)
        cv2.addWeighted(overlay, self.alpha, image,
                        1 - self.alpha, 0, image)

        if self.label:
            text_size = cv2.getTextSize(
                self.label, TEXT_FONT, TEXT_SCALE, TEXT_THICKNESS
            )[0]
            text_x = self.center_x - text_size[0] // 2
            text_y = self.center_y + self.radius + \
                     text_size[1] + LABEL_MARGIN

            cv2.putText(image, self.label, (text_x, text_y),
                        TEXT_FONT, TEXT_SCALE, WHITE, TEXT_THICKNESS)

    def is_over(self, mouse_x, mouse_y):
        """
        Check if a point is over the button.
        """
        dx = mouse_x - self.center_x
        dy = mouse_y - self.center_y
        return (dx ** 2 + dy ** 2) < self.radius ** 2


class Menu:
    """
    Manages the whiteboard tool menu and its UI buttons.
    """

    def __init__(self, board_toggle_pos, pen_toggle_pos):
        self.board_toggle_pos = board_toggle_pos
        self.pen_toggle_pos = pen_toggle_pos
        self.clear_button = None

        # Derive positions for other buttons relative to toggles
        self.clear_button_pos = (
            self.pen_toggle_pos[0] - BUTTON_GAP,
            self.pen_toggle_pos[1]
        )
        self.eraser_button_pos = (
            self.clear_button_pos[0] - BUTTON_GAP,
            self.pen_toggle_pos[1]
        )
        self.color_toggle_pos = (
            self.eraser_button_pos[0] - BUTTON_GAP,
            self.pen_toggle_pos[1]
        )

        self.color_buttons = []
        self.pen_size_buttons = []
        self.shape_buttons = []

    def create_buttons(self):
        """
        Create color, pen size, shape, and clear buttons.
        """
        self.color_buttons = [
            CircleButton(
                self.color_toggle_pos[0] - COLOR_TOGGLE_OFFSET -
                color_index * COLOR_BUTTON_SPACING,
                self.color_toggle_pos[1],
                COLOR_BUTTON_RADIUS,
                color
            )
            for color_index, color in
            enumerate(COLORS[:COLOR_BUTTON_MAX])
        ]

        self.pen_size_buttons = [
            CircleButton(
                self.pen_toggle_pos[0],
                self.pen_toggle_pos[1] +
                PEN_BUTTON_OFFSET_Y +
                size_index * PEN_BUTTON_VERTICAL_SPACING,
                pen_size,
                MID_GRAY,
                is_pen=True
            )
            for size_index, pen_size in
            enumerate(range(PEN_SIZE_MIN, PEN_SIZE_MAX, PEN_SIZE_STEP))
        ]

        self.shape_buttons = [
            CircleButton(
                self.board_toggle_pos[0] + TOGGLE_RADIUS +
                SHAPE_BUTTON_OFFSET_X +
                shape_index * SHAPE_BUTTON_SPACING,
                self.board_toggle_pos[1],
                SHAPE_BUTTON_RADIUS,
                DARK_GRAY,
                shape
            )
            for shape_index, shape in
            enumerate(SHAPES[:SHAPE_COUNT])
        ]

        self.clear_button = CircleButton(
            self.clear_button_pos[0],
            self.clear_button_pos[1],
            CLEAR_BUTTON_RADIUS,
            DARKER_GRAY,
            CLEAR_DRAWING
        )

    def draw_toggle(self, frame, toggle_center_x, toggle_center_y,
                    toggle_radius, is_toggle_on):
        """
        Draws a circular toggle button. If `is_toggle_on` is True,
        a red 'X' mark is drawn to indicate active state.

        Parameters:
        - frame: The image/frame where the toggle will be drawn.
        - toggle_center_x: X-coordinate of the toggle's center.
        - toggle_center_y: Y-coordinate of the toggle's center.
        - toggle_radius: Radius of the toggle circle.
        - is_toggle_on: Whether the toggle is active (adds 'X' mark).
        """
        toggle_center = (toggle_center_x, toggle_center_y)

        # Draw filled white toggle background
        cv2.circle(frame, toggle_center, toggle_radius, WHITE, FILLED)

        # Draw gray toggle outline
        cv2.circle(frame, toggle_center, toggle_radius,
                   LIGHT_GRAY, LINE_THICKNESS)

        # Draw red 'X' if toggle is on
        if is_toggle_on:
            offset = TOGGLE_CROSS_OFFSET
            cv2.line(frame,
                     (toggle_center_x - offset, toggle_center_y - offset),
                     (toggle_center_x + offset, toggle_center_y + offset),
                     RED, LINE_THICKNESS)
            cv2.line(frame,
                     (toggle_center_x + offset, toggle_center_y - offset),
                     (toggle_center_x - offset, toggle_center_y + offset),
                     RED, LINE_THICKNESS)

    def draw_ui(self, app):
        """
        Draw the entire UI overlay on the app frame.

        Parameters:
        - app: The main whiteboard application instance. Expected to have:
            - app.canvas: The drawing layer with alpha channel.
            - app.preview_canvas: The shape preview layer (semi-transparent).
            - app.frame: The frame/image where all layers and UI will be drawn.
            - app.is_board_hidden: Flag to show/hide the board UI.
            - app.are_colors_hidden: Flag to show/hide the color palette.
            - app.are_pen_sizes_hidden: Flag to show/hide pen size options.
            - app.is_using_eraser: Flag to indicate eraser tool is active.
        """

        # === Blend canvas with alpha onto the main frame ===
        alpha = app.canvas[..., 3:] / MAX_ALPHA_VALUE
        app.frame[:] = (app.frame * (1 - alpha) +
                        app.canvas[..., :3] * alpha).astype("uint8")

        # === Blend preview canvas (e.g. shapes) onto frame ===
        preview_alpha = app.preview_canvas[..., 3:] / MAX_ALPHA_VALUE
        app.frame[:] = (app.frame * (1 - preview_alpha) +
                        app.preview_canvas[..., :3] *
                        preview_alpha).astype("uint8")

        # === Draw toggle to show/hide the board, with label ===
        self.draw_toggle(app.frame, *self.board_toggle_pos,
                        TOGGLE_RADIUS, not app.is_board_hidden)

        cv2.putText(app.frame, "Board",
                    (self.board_toggle_pos[0] - BOARD_LABEL_OFFSET_X,
                    self.board_toggle_pos[1] +
                    TOGGLE_RADIUS + LABEL_OFFSET_Y),
                    TEXT_FONT, TEXT_SCALE, WHITE, TEXT_THICKNESS)

        # === Skip drawing if board UI is hidden ===
        if app.is_board_hidden:
            return

        # === Draw toggles for pen sizes, colors, eraser ===
        self.draw_toggle(app.frame, *self.pen_toggle_pos,
                        TOGGLE_RADIUS, not app.are_pen_sizes_hidden)

        self.draw_toggle(app.frame, *self.color_toggle_pos,
                        TOGGLE_RADIUS, not app.are_colors_hidden)

        self.draw_toggle(app.frame, *self.eraser_button_pos,
                        TOGGLE_RADIUS, app.is_using_eraser)

        # === Draw labels under the toggles ===
        cv2.putText(app.frame, "Colors",
                    (self.color_toggle_pos[0] - COLOR_LABEL_OFFSET_X,
                    self.color_toggle_pos[1] +
                    TOGGLE_RADIUS + LABEL_OFFSET_Y),
                    TEXT_FONT, TEXT_SCALE, WHITE, TEXT_THICKNESS)

        cv2.putText(app.frame, "Thickness",
                    (self.pen_toggle_pos[0] - THICKNESS_LABEL_OFFSET_X,
                    self.pen_toggle_pos[1] +
                    TOGGLE_RADIUS + LABEL_OFFSET_Y),
                    TEXT_FONT, TEXT_SCALE, WHITE, TEXT_THICKNESS)

        cv2.putText(app.frame, "Eraser",
                    (self.eraser_button_pos[0] - ERASER_LABEL_OFFSET_X,
                    self.eraser_button_pos[1] +
                    TOGGLE_RADIUS + LABEL_OFFSET_Y),
                    TEXT_FONT, TEXT_SCALE, WHITE, TEXT_THICKNESS)

        # === Draw the clear canvas button ===
        self.clear_button.draw(app.frame)

        # === Draw color selection buttons if visible ===
        if not app.are_colors_hidden:
            for color_button in self.color_buttons:
                color_button.draw(app.frame)

        # === Draw pen size selection buttons if visible ===
        if not app.are_pen_sizes_hidden:
            for pen_button in self.pen_size_buttons:
                # Draw white outline around the size circle
                cv2.circle(app.frame,
                        (pen_button.center_x, pen_button.center_y),
                        pen_button.radius + PEN_BUTTON_OUTLINE,
                        WHITE, FILLED)

                # Draw actual size circle (darker fill)
                cv2.circle(app.frame,
                        (pen_button.center_x, pen_button.center_y),
                        pen_button.radius,
                        pen_button.color, FILLED)

        # === Draw shape tool selection buttons ===
        for shape_button in self.shape_buttons:
            shape_button.alpha = SHAPE_BUTTON_ALPHA
            shape_button.draw(app.frame)