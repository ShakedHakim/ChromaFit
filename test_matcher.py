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
        self.dark_brown = (80, 50, 45)                       # H = 4, S = 112, V = 80 (earthy)
        self.teal = NamedColor("teal", (0, 128, 128))        # H = 90, near-complementary to brown
        self.tan = NamedColor("tan", (210, 180, 140))        # H = 17, muted and light
        self.cocoa = NamedColor("cocoa", (135, 95, 66))               # H = 13, earth tone, deeper
        self.papayawhip = NamedColor("papayawhip", (255, 239, 213))   # H = 19, muted, very pale

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

    def test_score_earthy_source_prefers_muted_warm_over_complementary(self):
        """For a brown source, a muted warm tan beats the near-complementary teal."""
        warm = self.matcher.score(self.dark_brown, self.tan, "bottom")
        complementary = self.matcher.score(self.dark_brown, self.teal, "bottom")
        self.assertGreater(warm, complementary)

    def test_score_earthy_source_shoes_prefer_deeper_tones(self):
        """For shoes, a deeper muted candidate beats a very pale one."""
        self.assertGreater(self.matcher.score(self.dark_brown, self.cocoa, "shoes"),
                           self.matcher.score(self.dark_brown, self.papayawhip, "shoes"))

    def test_recommend_colors_earthy_source_differs_for_shoes_and_bottom(self):
        candidates = [self.cocoa, self.papayawhip, self.tan, self.teal, self.white]
        result = self.matcher.recommend_colors([(self.dark_brown, 1.0)], candidates,
                                               ["bottom", "shoes"], top_n=2)
        names = {category: [c.name for c, _ in scored] for category, scored in result.items()}
        self.assertNotEqual(names["bottom"], names["shoes"])

    def test_score_non_earthy_source_uses_hue_distance_strategy(self):
        """A saturated (non-earthy) source is still scored purely by the hue-distance strategy."""
        dist = ColorUtils.hue_distance(ColorUtils.rgb_to_hsv(self.orange)[0],
                                       ColorUtils.rgb_to_hsv(self.cyan.rgb)[0])
        expected = self.matcher.strategy.score_hue_distance(dist)

        actual = self.matcher.score(self.orange, self.cyan, "bottom")

        self.assertAlmostEqual(actual, expected)

    # --- recommend_colors ---

    def test_recommend_colors_returns_every_requested_category(self):
        self.assertEqual(set(self.recommendations.keys()), set(self.targets))

    def test_recommend_colors_includes_neutral_for_saturated_source(self):
        """A saturated source still gets a neutral, and a dark colored item doesn't take that slot."""
        candidates = [NamedColor("yellow", (255, 255, 0)), NamedColor("orange", (255, 165, 0)),
                      NamedColor("lime", (0, 255, 0)), self.white, NamedColor("black", (0, 0, 0)),
                      NamedColor("dark green", (3, 53, 0))]
        picks = self.matcher.recommend_colors([(self.blue, 1.0)], candidates, ["top"], top_n=4)["top"]
        names = [c.name for c, _ in picks]
        self.assertTrue({"white", "black"} & set(names))
        self.assertNotIn("dark green", names)

    def test_recommend_colors_picks_are_visibly_different(self):
        candidates = [NamedColor("yellow", (255, 255, 0)), NamedColor("yellow 2", (250, 250, 10)),
                      NamedColor("yellow 3", (255, 250, 5)), NamedColor("orange", (255, 165, 0)),
                      NamedColor("lime", (0, 255, 0)), self.white]
        picks = self.matcher.recommend_colors([(self.blue, 1.0)], candidates, ["top"], top_n=4)["top"]
        for i, (a, _) in enumerate(picks):
            for b, _ in picks[i + 1:]:
                with self.subTest(pair=(a.name, b.name)):
                    self.assertGreaterEqual(ColorUtils.rgb_distance(a.rgb, b.rgb),
                                            ColorMatcher.MIN_PICK_DISTANCE)

    def test_recommend_colors_reserves_at_most_half_the_slots_for_neutrals(self):
        """With better-scoring hued candidates available, neutrals fill only the reserved slots."""
        candidates = [NamedColor("yellow", (255, 255, 0)), NamedColor("orange", (255, 165, 0)),
                      NamedColor("lime", (0, 255, 0)), self.white, NamedColor("black", (0, 0, 0)),
                      NamedColor("grey", (128, 128, 128))]
        for top_n in (1, 3):
            picks = self.matcher.recommend_colors([(self.blue, 1.0)], candidates, ["top"], top_n=top_n)["top"]
            neutrals = [c for c, _ in picks if c.name in {"white", "black", "grey"}]
            with self.subTest(top_n=top_n):
                self.assertEqual(len(picks), top_n)
                self.assertLessEqual(len(neutrals), top_n // 2)

    def test_recommend_colors_each_category_sorted_descending(self):
        for category, scored in self.recommendations.items():
            scores = [s for _, s in scored]
            with self.subTest(category=category):
                self.assertEqual(scores, sorted(scores, reverse=True))


if __name__ == "__main__":
    unittest.main()
