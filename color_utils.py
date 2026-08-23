# this class is for color utilities
import cv2
import numpy as np

class ColorUtils:
    @staticmethod
    def rgb_to_hsv(rgb: tuple) -> tuple:
    #convert RGB to HSV. H: 0-179, S: 0-255, V: 0-255.
        pixel = np.uint8([[list(rgb)]])
        hsv = cv2.cvtColor(pixel, cv2.COLOR_RGB2HSV)
        return tuple(int(c) for c in hsv[0][0])

    @staticmethod
    def hue_distance(h1: int, h2: int) -> int:
    #find the shortest distance between two hues on the color wheel
        diff = abs(h1 - h2)
        distance = min(diff, 180 - diff)
        return distance

    @staticmethod
    def is_neutral(hsv: tuple) -> bool:
        #True for blacks, whites, greys and other low-saturation colors.
        h, s, v = hsv
        if s < 40:  # אפור, לבן, דהוי — הגוון חסר משמעות
            return True
        if v < 40:  # כמעט שחור — הגוון לא נראה בכלל
            return True
        return False