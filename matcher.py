from color_utils import ColorUtils


class ColorMatcher:
#Scores items based on their color similarity to a given color.

    NEUTRAL_SCORE = 0.7

    def score(self, color_rgb: tuple, item) -> float:
        # Convert both colors to HSV
        color_hsv = ColorUtils.rgb_to_hsv(color_rgb)
        item_hsv = ColorUtils.rgb_to_hsv(item.rgb_color)

        if ColorUtils.is_neutral(color_hsv) or ColorUtils.is_neutral(item_hsv):
            return self.NEUTRAL_SCORE

        dist = ColorUtils.hue_distance(color_hsv[0], item_hsv[0])

        if dist < 10:
            return 0.75  # אותו גוון
        elif dist < 30:
            return 0.85  # שכנים
        elif dist < 75:
            return 0.35  # לא קרוב אך לא מנוגד
        else:
            return 1.0  # משלים


    def find_matches(self, color_rgb: tuple, items: list, top_n: int = 3) -> list:
        scored = [(item, self.score(color_rgb, item)) for item in items]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:top_n]