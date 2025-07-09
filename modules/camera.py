import cv2
import threading


class Camera:
    """
    Camera class for initialization, frame handling, and cleanup.
    Supports optional background frame capture using threading.
    """

    DEFAULT_CAMERA_INDEX = 0
    DEFAULT_WIDTH = 640
    DEFAULT_HEIGHT = 480

    def __init__(
        self,
        camera_index=DEFAULT_CAMERA_INDEX,
        width=DEFAULT_WIDTH,
        height=DEFAULT_HEIGHT
    ):
        """
        Initialize the camera with specified parameters.

        Args:
            camera_index (int): Index of the camera (default: 0).
            width (int): Desired frame width in pixels (default: 640).
            height (int): Desired frame height in pixels (default: 480).
        """
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap = None

        # Threading-related attributes
        self._latest_frame = None
        self._is_running = False
        self._capture_thread = None
        self._frame_lock = threading.Lock()

    def open(self):
        """Open the camera and set frame properties.

        Raises:
            RuntimeError: If camera cannot be opened.
        """
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera with index {self.camera_index}")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

    def _update_frame(self):
        """Continuously capture frames in a background thread."""
        while self._is_running:
            if self.cap is None or not self.cap.isOpened():
                continue

            ret, frame = self.cap.read()
            if not ret:
                continue

            with self._frame_lock:
                self._latest_frame = frame

    def start(self):
        """Start background frame capture."""
        self.open()
        self._is_running = True
        self._capture_thread = threading.Thread(
            target=self._update_frame,
            daemon=True
        )
        self._capture_thread.start()

    def get_frame(self):
        """
        Get the latest frame captured by the background thread if running,
        otherwise capture a single frame.

        Returns:
            numpy.ndarray: The captured frame.

        Raises:
            RuntimeError: If camera is not opened or frame cannot be read.
        """
        if self._is_running:
            with self._frame_lock:
                if self._latest_frame is None:
                    raise RuntimeError("No frame available yet.")
                return self._latest_frame.copy()

        if self.cap is None or not self.cap.isOpened():
            raise RuntimeError("Camera is not opened.")

        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Failed to read frame from camera.")

        return frame

    def stop(self):
        """Stop background frame capture and release resources."""
        if not self._is_running:
            return

        self._is_running = False
        
        if self._capture_thread is not None:
            self._capture_thread.join()
            self._capture_thread = None
            
        self.release()

    def release(self):
        """Release the camera resources."""
        if self.cap is None:
            return

        self.cap.release()
        self.cap = None

    def __enter__(self):
        """Context manager entry point.

        Returns:
            Camera: The initialized camera object.
        """
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point.

        Args:
            exc_type: Exception type if any occurred.
            exc_val: Exception value if any occurred.
            exc_tb: Exception traceback if any occurred.

        Returns:
            bool: False to propagate exceptions.
        """
        self.release()
        if exc_type is not None:
            print(f"An error occurred: {exc_val}")
        return False