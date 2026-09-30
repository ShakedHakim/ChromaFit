import unittest

from color_utils import ColorUtils


class TestColorUtils(unittest.TestCase):

    # --- hue_distance ---

    def test_hue_distance_same_hue_is_zero(self):
        self.assertEqual(ColorUtils.hue_distance(42, 42), 0)

    def test_hue_distance_wraps_around_circular_hue(self):
        """Hue is circular (0-179), so 5 and 175 are 10 apart, not 170."""
        self.assertEqual(ColorUtils.hue_distance(5, 175), 10)

    def test_hue_distance_maximum_is_ninety(self):
        self.assertEqual(ColorUtils.hue_distance(0, 90), 90)

    # --- is_neutral ---

    def test_is_neutral_white(self):
        white = ColorUtils.rgb_to_hsv((255, 255, 255))
        self.assertTrue(ColorUtils.is_neutral(white))

    def test_is_neutral_black(self):
        black = ColorUtils.rgb_to_hsv((0, 0, 0))
        self.assertTrue(ColorUtils.is_neutral(black))

    def test_is_neutral_rejects_bright_saturated_orange(self):
        """Regression: a high-V saturated color must not be treated as neutral.

        An earlier version flagged any color with v > 220 as neutral, which
        misclassified bright saturated colors like this orange.
        """
        orange = ColorUtils.rgb_to_hsv((234, 84, 0))
        self.assertFalse(ColorUtils.is_neutral(orange))

    # --- are_similar ---

    def test_are_similar_near_identical_colors(self):
        self.assertTrue(ColorUtils.are_similar((11, 255, 234), (12, 250, 230)))

    def test_are_similar_rejects_warm_vs_cool_hues(self):
        warm_orange = (11, 255, 234)
        cool_blue = (120, 255, 200)
        self.assertFalse(ColorUtils.are_similar(warm_orange, cool_blue))

    # --- rgb_distance ---

    def test_rgb_distance_identical_colors_is_zero(self):
        self.assertEqual(ColorUtils.rgb_distance((234, 84, 0), (234, 84, 0)), 0.0)

    def test_rgb_distance_black_to_white_is_one(self):
        self.assertAlmostEqual(ColorUtils.rgb_distance((0, 0, 0), (255, 255, 255)), 1.0)

    def test_rgb_distance_single_channel_difference(self):
        """Black vs pure red differs by 255 in one channel: sqrt(1/3) ≈ 0.57735."""
        self.assertAlmostEqual(ColorUtils.rgb_distance((0, 0, 0), (255, 0, 0)), 0.57735, places=5)


if __name__ == "__main__":
    unittest.main()
