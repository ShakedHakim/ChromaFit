# this class is for color utilities
from operator import truediv

import cv2
import numpy as np

class ColorUtils:
    @staticmethod
    def rgb_to_hsv(rgb: tuple) -> tuple:
        """Convert RGB to HSV. H: 0-179, S: 0-255, V: 0-255."""
        pixel = np.uint8([[list(rgb)]])
        hsv = cv2.cvtColor(pixel, cv2.COLOR_RGB2HSV)
        return tuple(int(c) for c in hsv[0][0])

    @staticmethod
    def hue_distance(h1: int, h2: int) -> int:
        """Find the shortest distance between two hues on the color wheel."""
        diff = abs(h1 - h2)
        distance = min(diff, 180 - diff)
        return distance

    @staticmethod
    def is_neutral(hsv: tuple, sat_tol: int = 40, dark_tol: int = 60) -> bool:
        """True for blacks, whites, greys and other low-saturation colors."""
        h, s, v = hsv

        if s < sat_tol:
            return True
        if v < dark_tol:      # dark enough that hue is unreliable
            return True
        return False

    @staticmethod
    def are_similar(hsv1: tuple, hsv2: tuple, hue_tol: int = 10, sat_tol: int = 40, val_tol: int = 40) -> bool:
        """True if two HSV colors are within the hue, saturation and value tolerances."""
        h1, s1, v1 = hsv1
        h2, s2, v2 = hsv2

        return (ColorUtils.hue_distance(h1, h2) < hue_tol
                and abs(s1 - s2) < sat_tol
                and abs(v1 - v2) < val_tol)

    @staticmethod
    def vividness(hsv: tuple) -> float:
        """How loud a color is, in [0, 1]: saturation times brightness (neon colors are close to 1)."""
        return (hsv[1] / 255) * (hsv[2] / 255)

    @staticmethod
    def is_earthy_tone(hsv: tuple, hue_max: int = 25, hue_min_wrap: int = 170,
                       sat_range: tuple = (60, 200), val_range: tuple = (40, 140)) -> bool:
        """True for muted, darker reds/oranges (browns, rust) that is_neutral() doesn't catch."""
        h, s, v = hsv
        return ((h <= hue_max or h >= hue_min_wrap)
                and sat_range[0] <= s <= sat_range[1]
                and val_range[0] <= v <= val_range[1])

    @staticmethod
    def rgb_distance(rgb1: tuple, rgb2: tuple) -> float:
        """Normalized Euclidean distance between two RGB colors, in [0, 1]."""
        squared_diff = sum((a - b) ** 2 for a, b in zip(rgb1, rgb2))
        max_squared_diff = 3 * (255 ** 2)
        return (squared_diff / max_squared_diff) ** 0.5
