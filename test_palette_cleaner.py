import unittest

from palette_cleaner import PaletteCleaner


class TestPaletteCleaner(unittest.TestCase):

    def setUp(self):
        palette = [((234, 84, 0), 0.6), ((230, 83, 1), 0.3)]
        self.cleaned = PaletteCleaner().clean(palette)

    def test_clean_merges_near_identical_colors_into_one_entry(self):
        self.assertEqual(len(self.cleaned), 1)

    def test_clean_merged_entry_has_summed_weight(self):
        _, weight = self.cleaned[0]
        self.assertAlmostEqual(weight, 0.9)


if __name__ == "__main__":
    unittest.main()
