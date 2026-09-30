import unittest

import numpy as np

from palette_extractor import PaletteExtractor


class TestPaletteExtractor(unittest.TestCase):

    def setUp(self):
        """Build a 100x100 image: top 70 rows orange, bottom 30 rows blue, with noise."""
        self.orange = np.array([234, 84, 0])
        self.blue = np.array([20, 40, 200])

        rng = np.random.default_rng(0)
        image = np.zeros((100, 100, 3), dtype=np.int16)
        image[:70] = self.orange
        image[70:] = self.blue
        image += rng.integers(-10, 11, size=image.shape, dtype=np.int16)
        self.image = np.clip(image, 0, 255).astype(np.uint8)

        self.palette = PaletteExtractor(n_colors=2).extract(self.image)

    def test_extract_weights_sum_to_one(self):
        total = sum(weight for _, weight in self.palette)
        self.assertAlmostEqual(total, 1.0, places=6)

    def test_extract_dominant_color_matches_larger_region(self):
        dominant_color, _ = self.palette[0]
        for actual, expected in zip(dominant_color, self.orange):
            self.assertLessEqual(abs(actual - int(expected)), 10)


if __name__ == "__main__":
    unittest.main()
