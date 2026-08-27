from color_utils import ColorUtils


class ColorMatcher:
#Scores items based on their color similarity to a given color.

    NEUTRAL_BASE = 0.7
    NEUTRAL_CONTRAST_BONUS = 0.2
    CATEGORIES = ("top", "bottom", "shoes")

    def score(self, color_rgb: tuple, item) -> float:
        # Convert both colors to HSV
        color_hsv = ColorUtils.rgb_to_hsv(color_rgb)
        item_hsv = ColorUtils.rgb_to_hsv(item.rgb_color)

        if ColorUtils.is_neutral(color_hsv) or ColorUtils.is_neutral(item_hsv):
            contrast = abs(color_hsv[2] - item_hsv[2]) / 255
            return self.NEUTRAL_BASE + contrast * self.NEUTRAL_CONTRAST_BONUS

        dist = ColorUtils.hue_distance(color_hsv[0], item_hsv[0])

        if dist < 10:
            return 0.75  # same hue
        elif dist < 30:
            return 0.85  # neibhboring hue
        elif dist < 75:
            return 0.35  # not close- but contrast
        else:
            return 1.0  # opposite hue


    def find_matches(self, color_rgb: tuple, items: list, top_n: int = 3, exclude_category: str = None) -> list:
        if exclude_category is not None:
            items = [item for item in items if item.category != exclude_category]
        scored = [(item, self.score(color_rgb, item)) for item in items]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:top_n]


    def build_outfit(self, color_rgb: tuple, items: list, source_category: str) -> dict:
        outfit = {}

        for category in self.CATEGORIES:
            if category == source_category:
                continue

            in_category = [i for i in items if i.category == category]
            matches = self.find_matches(color_rgb, in_category, top_n=1)

            if matches:
                outfit[category] = matches[0]

        return outfit

    def score_palette(self, palette: list, item) -> dict:
        total = 0.0
        for c, w in palette:
            total += self.score(c, item) * w
        return total