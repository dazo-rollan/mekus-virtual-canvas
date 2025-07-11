import time
import cv2 as cv
import numpy as np
from modules.camera import Camera
from modules.hand_tracker import HandTracker
from modules.menu import Menu
from modules.drawing import (
    COLORS,
    WHITE,
    FREE_DRAW,
)


class VirtualCanvas:
    ESC_KEY = 27
    FRAME_DELAY = 1

    def __init__(self):
        self.camera = Camera(height=720, width=1280)
        self.tracker = HandTracker()
        self.menu = None

        # Canvas properties
        self.canvas = None
        self.canvas_size = None
        self.canvas_origin = None

        # Drawing state
        self.current_color = COLORS[0]  # Start with red
        self.brush_size = 10
        self.current_tool = FREE_DRAW
        self.is_drawing = False
        self.prev_pos = None

        # UI state
        self.show_canvas = False
        self.show_colors = False
        self.show_brush_sizes = False
        self.is_eraser = False

    def initialize(self):
        """Initialize camera and UI components."""
        self.camera.start()
        self.wait_for_camera()

        try:
            self.wait_for_camera()
        except RuntimeError as e:
            print(f"Error: {e}")
            return

        self.setup_menu()
        self.setup_canvas()

    def wait_for_camera(self):
        """Wait until the camera is ready."""
        TIMEOUT = 5  # seconds
        start_time = time.time()

        print("Waiting for camera to initialize...")
        while (
            self.camera.get_immediate_frame() is None
            and (time.time() - start_time) < TIMEOUT
        ):
            time.sleep(0.1)

        if self.camera.get_immediate_frame() is None:
            raise RuntimeError("Camera initialization timed out.")

    def setup_canvas(self):
        """Initialize the drawing canvas."""
        self.canvas_size = (
            int(self.camera.height - (self.camera.height * 0.20)),
            int(self.camera.width - (self.camera.width * 0.20)),
        )
        self.canvas_origin = (
            int(self.camera.height * 0.20),  # 20% from top
            int(self.camera.width * 0.05),  # 5% from left
        )

        height, width = self.canvas_size
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)
        self.canvas[:] = WHITE  # White background

    def setup_menu(self):
        """Initialize the menu with proper positioning."""
        # Calculate menu positions based on frame dimensions
        frame_width = self.camera.width
        frame_height = self.camera.height

        # Position toggles on the right side
        board_toggle_pos = (
            int(frame_width * 0.1),  # 1% from left
            int(frame_height * 0.1),  # 10% from top
        )
        pen_toggle_pos = (
            int(frame_width * 0.9),
            board_toggle_pos[1],  # Spaced vertically
        )

        self.menu = Menu(board_toggle_pos, pen_toggle_pos)
        self.menu.create_buttons()

    def process_frame(self):
        """Process each frame for drawing and UI interaction."""
        frame = self.camera.get_frame()
        if frame is None:
            return False

        # Flip frame horizontally for mirror effect
        frame = cv.flip(frame, 1)

        # Process hand tracking
        processed_frame = self.tracker.process_frame(frame)

        # Get finger position
        finger_pos = self.tracker.get_hand_position(processed_frame)
        index_pos = finger_pos.get(self.tracker.INDEX_FINGER_KEY, None)

        hand_draw_modes = self.tracker.draw_modes
        will_draw = False
        if hand_draw_modes:
            will_draw = hand_draw_modes[0]

        if not will_draw:
            self.prev_pos = None

        # Handle drawing if canvas is visible
        if self.tracker.is_drawing_mode and will_draw:
            self.handle_drawing(index_pos, processed_frame)

        # Handle UI interactions
        self.handle_ui_interaction(index_pos, processed_frame)

        canvas_y, canvas_x = self.canvas_origin
        height, width = self.canvas_size

        if self.show_canvas:
            frame_region = processed_frame[
                canvas_y : canvas_y + height, canvas_x : canvas_x + width
            ]
            blended = cv.addWeighted(frame_region, 0.5, self.canvas, 0.5, 0)
            processed_frame[
                canvas_y : canvas_y + height, canvas_x : canvas_x + width
            ] = blended

        # Display the frame
        cv.imshow("Virtual Canvas", processed_frame)

        return cv.waitKey(self.FRAME_DELAY) != self.ESC_KEY

    def handle_drawing(self, finger_pos, frame):
        """Handle drawing operations on the canvas."""
        if not self.show_canvas or not finger_pos:
            return

        # Convert finger position to canvas coordinates
        canvas_x = finger_pos[0] - self.canvas_origin[1]
        canvas_y = finger_pos[1] - self.canvas_origin[0]

        # Check if finger is within canvas bounds
        if not (
            0 <= canvas_x < self.canvas_size[1]
            and 0 <= canvas_y < self.canvas_size[0]
        ):
            self.prev_pos = None
            return

        if not self.prev_pos:
            self.prev_pos = (canvas_x, canvas_y)

        # Handle eraser or drawing tool
        if self.is_eraser:
            cv.circle(
                self.canvas,
                (canvas_x, canvas_y),
                self.brush_size * 2,  # Make eraser larger
                WHITE,
                -1,
            )

        if not self.is_eraser:
            if self.prev_pos:
                cv.line(
                    self.canvas,
                    self.prev_pos,
                    (canvas_x, canvas_y),
                    self.current_color,
                    self.brush_size,
                )

        # previous position
        self.prev_pos = (canvas_x, canvas_y)

    def handle_ui_interaction(self, finger_pos, frame):
        """Handle interactions with UI buttons."""
        if finger_pos is None:
            return

        # Check for button clicks
        clicked_button = self.menu.handle_interaction(
            finger_pos=finger_pos, is_clicking=self.tracker.detect_click()
        )

        print(f"Clicked button: {clicked_button}")

        if clicked_button:
            self.handle_button_action(clicked_button)

        # Draw UI elements
        self.menu.draw_ui(self, frame)

    def handle_button_action(self, button):
        """Execute actions based on button clicks."""
        if button.label == "Board":
            self.tracker.toggle_drawing_mode()
            self.show_canvas = not self.show_canvas

        if button.label == "Colors":
            self.show_colors = not self.show_colors

        if button.label == "Size":
            self.show_brush_sizes = not self.show_brush_sizes

        if button.label == "Eraser":
            self.is_eraser = not self.is_eraser

        if button in self.menu.color_buttons:
            self.current_color = button.color
            self.is_eraser = False

        if button in self.menu.pen_size_buttons:
            self.brush_size = button.radius

        if button == self.menu.clear_button:
            self.canvas[:] = WHITE

        if button in self.menu.shape_buttons:
            self.current_tool = button.label
            self.is_eraser = False

    def run(self):
        """Main application loop."""
        self.initialize()

        while self.process_frame():
            pass

        self.camera.stop()
        cv.destroyAllWindows()


if __name__ == "__main__":
    app = VirtualCanvas()
    app.run()
