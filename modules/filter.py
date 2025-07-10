import cv2 as cv
import numpy as np

class Filter:
    """A collection of image processing filters using OpenCV."""

    # Blur constants
    GAUSSIAN_KSIZE = (15, 15)
    GAUSSIAN_SIGMA_X = 0
    MEDIAN_KSIZE = 5
    BILATERAL_D = 9
    BILATERAL_SIGMA_COLOR = 75
    BILATERAL_SIGMA_SPACE = 75

    # Sharpening kernel
    SHARPEN_KERNEL = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ])

    # Canny thresholds
    CANNY_LOW_THRESHOLD = 100
    CANNY_HIGH_THRESHOLD = 200

    # Sobel constants
    SOBEL_KSIZE = 3
    SOBEL_DDEPTH = cv.CV_64F
    SOBEL_DX = 1
    SOBEL_DY = 1
    SOBEL_ZERO = 0

    # Laplacian
    LAPLACIAN_DDEPTH = cv.CV_64F

    def apply_gaussian_blur(self, frame):
        """Applies Gaussian Blur to the input frame."""
        return cv.GaussianBlur(
            frame,
            self.GAUSSIAN_KSIZE,
            self.GAUSSIAN_SIGMA_X
        )

    def apply_median_blur(self, frame):
        """Applies Median Blur to reduce noise."""
        return cv.medianBlur(frame, self.MEDIAN_KSIZE)

    def apply_bilateral_filter(self, frame):
        """Applies Bilateral Filtering to smooth image and keep edges."""
        return cv.bilateralFilter(
            frame,
            self.BILATERAL_D,
            self.BILATERAL_SIGMA_COLOR,
            self.BILATERAL_SIGMA_SPACE
        )

    def apply_sharpening(self, frame):
        """Applies a sharpening filter using a convolution kernel."""
        return cv.filter2D(frame, -1, self.SHARPEN_KERNEL)

    def apply_edge_detection(self, frame):
        """Applies Canny edge detection and converts result to BGR."""
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        edges = cv.Canny(
            gray,
            self.CANNY_LOW_THRESHOLD,
            self.CANNY_HIGH_THRESHOLD
        )
        return cv.cvtColor(edges, cv.COLOR_GRAY2BGR)

    def apply_laplacian(self, frame):
        """Applies the Laplacian operator for edge detection."""
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        lap = cv.Laplacian(gray, self.LAPLACIAN_DDEPTH)
        lap = cv.convertScaleAbs(lap)
        return cv.cvtColor(lap, cv.COLOR_GRAY2BGR)

    def apply_sobel(self, frame):
        """Applies Sobel edge detection and returns combined magnitude."""
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        sobel_x = cv.Sobel(
            gray,
            self.SOBEL_DDEPTH,
            self.SOBEL_DX,
            self.SOBEL_ZERO,
            ksize=self.SOBEL_KSIZE
        )

        sobel_y = cv.Sobel(
            gray,
            self.SOBEL_DDEPTH,
            self.SOBEL_ZERO,
            self.SOBEL_DY,
            ksize=self.SOBEL_KSIZE
        )

        magnitude = cv.magnitude(sobel_x, sobel_y)
        magnitude = cv.convertScaleAbs(magnitude)
        return cv.cvtColor(magnitude, cv.COLOR_GRAY2BGR)