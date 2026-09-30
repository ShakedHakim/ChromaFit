import unittest

from color_utils import ColorUtils
from matcher import ColorMatcher
from models import NamedColor
from repository import MockColorRepository


class TestColorMatcher(unittest.TestCase):

    def setUp(self):
        self.matcher = ColorMatcher()
        self.red = (255, 0, 0)                               # H = 0
        self.cyan = NamedColor("cyan", (0, 255, 255))        # H = 90
        self.chartreuse = NamedColor("chartreuse", (128, 255, 0))  # H = 45
        self.orange = (234, 84, 0)                           # H = 11, S = 255
        self.white = NamedColor("white", (255, 255, 255))
        self.saturated_orange = NamedColor("orange", self.orange)
        self.blue = (0, 0, 200)                              # H = 120

        self.targets = ["bottom", "shoes", "outerwear"]
        self.recommendations = self.matcher.recommend_colors(
            [(self.orange, 0.7), ((255, 255, 255), 0.3)],
            MockColorRepository().get_all(),
            self.targets)

    # --- score ---

    def test_score_complementary_pair_beats_clashing_pair(self):
        complementary = self.matcher.score(self.red, self.cyan, "bottom")
        clashing = self.matcher.score(self.red, self.chartreuse, "bottom")
        self.assertGreater(complementary, clashing)

    def test_score_neutral_candidate_uses_base_plus_contrast(self):
        """A neutral candidate bypasses hue distance: NEUTRAL_BASE + contrast bonus."""
        contrast = ColorUtils.rgb_distance(self.orange, self.white.rgb)
        expected = (ColorMatcher.NEUTRAL_BASE
                    + contrast * ColorMatcher.NEUTRAL_CONTRAST_BONUS)

        actual = self.matcher.score(self.orange, self.white, "bottom")

        self.assertAlmostEqual(actual, expected)

    def test_score_saturated_candidate_penalized_for_shoes(self):
        """Candidates above SHOE_MAX_SATURATION score lower for shoes than for bottoms."""
        as_shoes = self.matcher.score(self.blue, self.saturated_orange, "shoes")
        as_bottom = self.matcher.score(self.blue, self.saturated_orange, "bottom")
        self.assertLess(as_shoes, as_bottom)

    # --- recommend_colors ---

    def test_recommend_colors_returns_every_requested_category(self):
        self.assertEqual(set(self.recommendations.keys()), set(self.targets))

    def test_recommend_colors_each_category_sorted_descending(self):
        for category, scored in self.recommendations.items():
            scores = [s for _, s in scored]
            with self.subTest(category=category):
                self.assertEqual(scores, sorted(scores, reverse=True))


if __name__ == "__main__":
    unittest.main()
