import time
from threading import Thread

import cv2 as cv
import numpy as np

from modules.camera import Camera
from modules.hand_tracker import HandTracker
from modules.menu import Menu
from modules.drawing import COLORS, SHAPES, ERASER, CLEAR_DRAWING

class MekusVirtualCanvas:

    EXIT_KEY = 27  # ESC key to exit
    WAIT_KEY_DELAY = 1  # Delay for key press detection

    MAX_ALPHA = 255  # Maximum opacity for the canvas
    ALPHA_INDEX = 3

    def __init__(self):
        """Iniitalize the Mekus Virtual Canvas."""
        self.cap = Camera()
        self.tracker = HandTracker()

        self.canvas = None
        self.preview_canvas = None
        self.frame = None

        self.prev_finger_pos = ()
        self.tracker.toggle_drawing_mode()
        self.brush_color = (0, 0, 255)  # Red color for drawing
        self.brush_size = 10  # Default brush size

    def setup_menu(self):
        """Setup the menu for the Mekus Virtual Canvas."""
        # Initialize menu items, colors, shapes, etc.
        # This can be extended to include more features like color selection,
        # shape drawing, etc.
        HORIZONTAL_MARGIN_RATIO = 0.1  # 10% of width
        VERTICAL_MARGIN_RATIO = 0.05  # 5% of height
        BUTTON_SPACING_RATIO = 0.05  # 5% of height

        board_toggle_pos = (
            self.cap.width - int(self.cap.width * HORIZONTAL_MARGIN_RATIO),
            int(self.cap.height * VERTICAL_MARGIN_RATIO),
        )
        pen_toggle_pos = (
            self.cap.width - int(self.cap.width * HORIZONTAL_MARGIN_RATIO),
            int(
                self.cap.height * (VERTICAL_MARGIN_RATIO + BUTTON_SPACING_RATIO)
            ),
        )

        self.menu = Menu(
            board_toggle_pos=board_toggle_pos,
            pen_toggle_pos=pen_toggle_pos,
        )
        self.menu.create_buttons()

        self.is_canvas_hidden = False
        self.are_colors_hidden = False
        self.are_pen_sizes_hidden = False
        self.is_using_eraser = False

        self.current_tool = SHAPES[0]  # Default to free draw

    def run(self):
        """Run the Mekus Virtual Canvas application."""
        self.cap.start()
        self.start_live_camera()
        self.stop()

    def start_live_camera(self):
        """Start the live camera feed and process frames."""
        self.init_camera()

        while self.cap.is_running:
            try:
                frame = self.cap.get_frame()
            except RuntimeError as e:
                print(f"Error capturing frame: {e}")
                break

            processed_frame = self.process_frame(frame)

            if self.tracker.detect_click():
                finger_pos = self.tracker.get_hand_position(processed_frame)
                index_finger_pos = finger_pos.get(
                    self.tracker.INDEX_FINGER_KEY, None
                )
                clicked_button = self.menu.handle_interaction(
                    finger_pos=index_finger_pos, is_clicking=True
                )
                if clicked_button:
                    print(f"Clicked button: {clicked_button}")

            if self.tracker.is_drawing_mode:
                processed_frame = self.draw_on_canvas(processed_frame)

            self.frame = processed_frame.copy()
            self.menu.draw_ui(self)

            self.show_frame()

            if cv.waitKey(self.WAIT_KEY_DELAY) == self.EXIT_KEY:
                break

    def init_camera(self):
        """Initialize the camera and wait for the first frame."""
        TIMEOUT = 5  # seconds to wait for the camera to start
        start_time = time.time()

        print("\n\nInitializing camera...\n\n")
        while (
            self.cap.latest_frame is None
            and (time.time() - start_time) < TIMEOUT
        ):
            time.sleep(0.05)

        height, width = self.cap.latest_frame.shape[:2]

        self.canvas = np.zeros((height, width, 4), dtype=np.uint8)
        self.preview_canvas = np.zeros((height, width, 4), dtype=np.uint8)
        self.frame = np.zeros((height, width, 3), dtype=np.uint8)

        self.setup_menu()

    def process_frame(self, frame):
        """Process frame and draw hand landmarks."""
        frame = cv.flip(
            frame, 1
        )  # Flip the frame horizontally for mirror effect

        processed_frame = self.tracker.process_frame(frame)

        display_frame = processed_frame.copy()

        if not self.is_canvas_hidden:
            # Get alpha channel and reshape for broadcasting
            alpha_channel = self.canvas[
                :, :, self.ALPHA_INDEX
            ]  # Correctly extracts alpha channel
            alpha_channel = alpha_channel[
                ..., np.newaxis
            ]  # Reshape to (H, W, 1)

            # Convert to float for blending
            display_frame = display_frame.astype(float)
            canvas_rgb = cv.cvtColor(self.canvas, cv.COLOR_BGRA2BGR).astype(
                float
            )

            # Normalize alpha
            alpha_normalized = alpha_channel / self.MAX_ALPHA

            # Perform blending
            blended = (
                display_frame * (1 - alpha_normalized)
                + canvas_rgb * alpha_normalized
            )
            display_frame = blended.astype(np.uint8)

        self.menu.draw_ui(self)
        return display_frame

    def draw_on_canvas(self, frame: np.ndarray):
        """
        Combine drawing canvas with camera frame using proper alpha blending.
        """
        # Ensure canvas has content
        if not self.has_drawing_content():
            return frame

        # Convert canvas to 3-channel if needed
        canvas_rgb = self.prepare_canvas_for_blending()

        # Perform alpha blending
        return self.alpha_blend(
            foreground=canvas_rgb,
            background=frame,
            alpha=self.get_canvas_alpha(),
        )

    def has_drawing_content(self):
        """Check if canvas contains visible drawings"""
        return np.any(self.canvas[self.ALPHA_INDEX] > 0)  # Check alpha channel

    def prepare_canvas_for_blending(self):
        """Convert BGRA canvas to BGR by stripping alpha channel"""
        return cv.cvtColor(self.canvas, cv.COLOR_BGRA2BGR)

    def get_canvas_alpha(self):
        """Extract and normalize alpha channel [0,1]"""
        alpha = self.canvas[self.ALPHA_INDEX]  # Extract alpha channel
        return (alpha / self.MAX_ALPHA)[
            ..., None
        ]  # Normalize and add channel dim

    def alpha_blend(self, foreground, background, alpha):
        """Alpha blend two images (foreground over background)"""
        return (background * (1 - alpha) + foreground * alpha).astype(np.uint8)

    def get_hand_draw_mode(self):
        """Get the current hand draw mode."""
        if self.tracker.draw_modes:
            return self.tracker.draw_modes[self.tracker.SELECTED_HAND_INDEX]

        return False

    def show_frame(self):
        """Display the frame in a window."""
        cv.imshow("Mekus Virtual Canvas", self.frame)

    def stop(self):
        """Stop the Mekus Virtual Canvas."""
        self.cap.stop()
        cv.destroyAllWindows()


if __name__ == "__main__":
    # Initialize and run the Mekus Virtual Canvas application
    mekus = MekusVirtualCanvas()
    mekus.run()