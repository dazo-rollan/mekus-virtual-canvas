import cv2 as cv
import mediapipe as mp

class HandTracker:
    """Track hand landmarks and detect raised fingers using MediaPipe Hands."""

    # Drawing constants
    CIRCLE_TIP_RADIUS = 5
    INNER_CIRCLE_TIP_COLOR = (75, 75, 75)
    OUTER_CIRCLE_TIP_COLOR = (200, 200, 200)
    INNER_CIRCLE_TIP_FILL = cv.FILLED
    OUTER_CIRCLE_TIP_THICKNESS = 2

    INDEX_FINGER_KEY = "INDEX_FINGER"
    MIDDLE_FINGER_KEY = "MIDDLE_FINGER"

    # Finger landmark indices
    # These indices correspond to the MediaPipe Hands landmark model
    # https://chuoling.github.io/mediapipe/solutions/hands.html
    FINGER_LANDMARKS = {
        INDEX_FINGER_KEY: {"MCP": 5, "PIP": 6, "DIP": 7, "TIP": 8},
        MIDDLE_FINGER_KEY: {"MCP": 9, "PIP": 10, "DIP": 11, "TIP": 12},
    }

    def __init__(
        self,
        use_static_image_mode=False,
        max_num_hands=10,
        detection_conf=0.8,
        tracking_conf=0.85,
    ):
        """Initialize the hand tracker with MediaPipe Hands settings."""
        self.hand_detector = mp.solutions.hands.Hands(
            static_image_mode=use_static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=detection_conf,
            min_tracking_confidence=tracking_conf,
        )

        self.hand_landmarks = None

        self.is_drawing_mode = False
        self.draw_modes = []

    def process_frame(self, image_bgr):
        """Process a frame and return it with drawn landmarks."""
        self.update_landmarks(image_bgr)
        if self.hand_landmarks and self.hand_landmarks.multi_hand_landmarks:
            self.draw_raised_fingers(image_bgr)

        return image_bgr

    def get_finger_positions(self):
        """Get current finger positions for all hands."""
        if not self.has_landmarks():
            return {}

        positions = {}
        for hand in self.hand_landmarks.multi_hand_landmarks:
            for finger_name, joint_names in self.FINGER_LANDMARKS.items():
                tip = hand.landmark[joint_names["TIP"]]
                positions[finger_name] = self.normalize_coordinates(tip)

        return positions

    def update_landmarks(self, image_bgr):
        """Update hand landmarks from the current frame."""
        image_rgb = cv.cvtColor(image_bgr, cv.COLOR_BGR2RGB)
        self.hand_landmarks = self.hand_detector.process(image_rgb)

    def has_landmarks(self):
        """Check if valid landmarks exist."""
        return self.hand_landmarks and self.hand_landmarks.multi_hand_landmarks

    def draw_raised_fingers(self, image_bgr):
        """Draw circles on raised fingers for all hands."""
        raised_fingers = self.detect_raised_fingers()

        self.update_drawing_mode(raised_fingers)

        for index, landmark in enumerate(
            self.hand_landmarks.multi_hand_landmarks,
        ):
            self.draw_finger_tips(
                image_bgr,
                landmark,
                raised_fingers[index],
                self.draw_modes[index],
            )

    def update_drawing_mode(self, raised_fingers):
        """Check if the drawing mode is active based on raised fingers."""
        self.draw_modes = [False] * len(raised_fingers)

        if not self.is_drawing_mode:
            return

        for fingers in raised_fingers:
            is_drawing = fingers.get("INDEX_FINGER") and not fingers.get(
                "MIDDLE_FINGER"
            )
            self.draw_modes.append(is_drawing)

    def draw_finger_tips(self, image_bgr, landmark, raised_fingers, draw_mode):
        """Draw tips for raised fingers of a single hand."""
        for finger_name, joint_names in self.FINGER_LANDMARKS.items():
            if raised_fingers.get(finger_name):
                tip = landmark.landmark[joint_names["TIP"]]
                x_coord, y_coord = self.normalize_coordinates(
                    tip, image_bgr.shape
                )
                self.draw_finger_tip(
                    image_bgr, finger_name, (x_coord, y_coord), draw_mode
                )

    def draw_finger_tip(self, image_bgr, finger_name, coord, draw_mode):
        """Draw a single finger tip marker based on its hand's draw mode."""
        cv.circle(
            image_bgr,
            coord,
            self.CIRCLE_TIP_RADIUS,
            self.OUTER_CIRCLE_TIP_COLOR,
            self.OUTER_CIRCLE_TIP_THICKNESS,
        )

        # Draw inner circle only if not in drawing mode and not the index finger
        if not (draw_mode and finger_name == "INDEX_FINGER"):
            cv.circle(
                image_bgr,
                coord,
                self.CIRCLE_TIP_RADIUS,
                self.INNER_CIRCLE_TIP_COLOR,
                self.INNER_CIRCLE_TIP_FILL,
            )

    def detect_raised_fingers(self):
        """Detect raised fingers for all hands."""
        if not self.has_landmarks():
            return []

        return [
            self.check_hand_fingers(hand)
            for hand in self.hand_landmarks.multi_hand_landmarks
        ]

    def check_hand_fingers(self, hand_landmark):
        """Check which fingers are raised for a single hand."""
        return {
            finger_name: self.is_finger_raised(hand_landmark, joints)
            for finger_name, joints in self.FINGER_LANDMARKS.items()
        }

    def is_finger_raised(self, hand_landmark, joints):
        """Check if a single finger is raised."""
        y_coords = {
            key: hand_landmark.landmark[joints[key]].y
            for key in ["TIP", "DIP", "PIP", "MCP"]
        }

        return (
            y_coords["TIP"]
            < y_coords["DIP"]
            < y_coords["PIP"]
            < y_coords["MCP"]
        )

    def normalize_coordinates(self, landmark, image_shape=None):
        """Convert normalized coordinates to pixel coordinates."""
        if image_shape is None:
            return (landmark.x, landmark.y)

        image_height, image_width, _ = image_shape

        return (
            int(landmark.x * image_height),
            int(landmark.y * image_width),
        )

    def toggle_drawing_mode(self, is_drawing_mode):
        self.is_drawing_mode = is_drawing_mode