import cv2 as cv
import numpy as np

class Filter:
    """A collection of image processing filters using OpenCV."""

    # Constants
    GAUSSIAN_KSIZE = (15, 15)
    GAUSSIAN_SIGMA_X = 0
    MEDIAN_KSIZE = 5
    BILATERAL_D = 9
    BILATERAL_SIGMA_COLOR = 75
    BILATERAL_SIGMA_SPACE = 75

    SHARPEN_KERNEL = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ])

    CANNY_LOW_THRESHOLD = 100
    CANNY_HIGH_THRESHOLD = 200

    SOBEL_KSIZE = 3
    SOBEL_DDEPTH = cv.CV_64F
    SOBEL_DX = 1
    SOBEL_DY = 1
    SOBEL_ZERO = 0

    LAPLACIAN_DDEPTH = cv.CV_64F

    def __init__(self):
        """Initializes the filter settings and kernel parameters."""
        # Blur settings
        self.gaussian_ksize = self.GAUSSIAN_KSIZE
        self.gaussian_sigmaX = self.GAUSSIAN_SIGMA_X
        self.median_ksize = self.MEDIAN_KSIZE
        self.bilateral_d = self.BILATERAL_D
        self.bilateral_sigmaColor = self.BILATERAL_SIGMA_COLOR
        self.bilateral_sigmaSpace = self.BILATERAL_SIGMA_SPACE

        # Sharpening kernel
        self.sharpen_kernel = self.SHARPEN_KERNEL

        # Edge detection thresholds
        self.canny_low = self.CANNY_LOW_THRESHOLD
        self.canny_high = self.CANNY_HIGH_THRESHOLD

        # Sobel settings
        self.sobel_ksize = self.SOBEL_KSIZE
        self.sobel_ddepth = self.SOBEL_DDEPTH
        self.sobel_dx = self.SOBEL_DX
        self.sobel_dy = self.SOBEL_DY
        self.sobel_zero = self.SOBEL_ZERO

        # Laplacian setting
        self.laplacian_ddepth = self.LAPLACIAN_DDEPTH

    def apply_gaussian_blur(self, frame):
        """Applies Gaussian Blur to the input frame."""
        return cv.GaussianBlur(
            frame,
            self.gaussian_ksize,
            self.gaussian_sigmaX
        )

    def apply_median_blur(self, frame):
        """Applies Median Blur to reduce noise."""
        return cv.medianBlur(frame, self.median_ksize)

    def apply_bilateral_filter(self, frame):
        """Applies Bilateral Filtering to smooth image and keep edges."""
        return cv.bilateralFilter(
            frame,
            self.bilateral_d,
            self.bilateral_sigmaColor,
            self.bilateral_sigmaSpace
        )

    def apply_sharpening(self, frame):
        """Applies a sharpening filter using a convolution kernel."""
        return cv.filter2D(frame, -1, self.sharpen_kernel)

    def apply_edge_detection(self, frame):
        """Applies Canny edge detection and converts result to BGR."""
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        edges = cv.Canny(gray, self.canny_low, self.canny_high)
        return cv.cvtColor(edges, cv.COLOR_GRAY2BGR)

    def apply_laplacian(self, frame):
        """Applies the Laplacian operator for edge detection."""
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        lap = cv.Laplacian(gray, self.laplacian_ddepth)
        lap = cv.convertScaleAbs(lap)
        return cv.cvtColor(lap, cv.COLOR_GRAY2BGR)

    def apply_sobel(self, frame):
        """Applies Sobel edge detection and returns combined magnitude."""
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        sobel_x = cv.Sobel(
            gray,
            self.sobel_ddepth,
            self.sobel_dx,
            self.sobel_zero,
            ksize=self.sobel_ksize
        )

        sobel_y = cv.Sobel(
            gray,
            self.sobel_ddepth,
            self.sobel_zero,
            self.sobel_dy,
            ksize=self.sobel_ksize
        )

        magnitude = cv.magnitude(sobel_x, sobel_y)
        magnitude = cv.convertScaleAbs(magnitude)
        return cv.cvtColor(magnitude, cv.COLOR_GRAY2BGR)