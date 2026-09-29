from color_utils import ColorUtils
from models import NamedColor
from scoring_strategy import ScoringStrategy, DiscreteScoring

class ColorMatcher:

    def __init__(self, strategy: ScoringStrategy = None):
        self.strategy = strategy or DiscreteScoring()

    NEUTRAL_BASE = 0.7
    NEUTRAL_CONTRAST_BONUS = 0.2
    SHOE_MAX_SATURATION = 180
    SHOE_PENALTY = 0.6

    def score(self, color_rgb: tuple, candidate: NamedColor,
              target_category: str) -> float:
        source_hsv = ColorUtils.rgb_to_hsv(color_rgb)
        candidate_hsv = ColorUtils.rgb_to_hsv(candidate.rgb)

        if ColorUtils.is_neutral(source_hsv) or ColorUtils.is_neutral(candidate_hsv):
            contrast = abs(source_hsv[2] - candidate_hsv[2]) / 255
            result = self.NEUTRAL_BASE + contrast * self.NEUTRAL_CONTRAST_BONUS
        else:
            dist = ColorUtils.hue_distance(source_hsv[0], candidate_hsv[0])
            result = self.strategy.score_hue_distance(dist)

        return self._apply_category_adjustment(result, candidate_hsv, target_category)

    def _apply_category_adjustment(self, base_score: float, candidate_hsv: tuple,
                                   target_category: str) -> float:
        """Penalize highly saturated candidates for shoes, which lean toward muted colors."""
        if target_category == "shoes" and candidate_hsv[1] > self.SHOE_MAX_SATURATION:
            return base_score * self.SHOE_PENALTY
        return base_score

    def score_palette(self, palette: list, candidate: NamedColor,
                      target_category: str) -> float:
        total = 0.0
        for color, weight in palette:
            total += self.score(color, candidate, target_category) * weight
        return total

    def recommend_colors(self, palette: list, colors: list,
                         targets: list, top_n: int = 3) -> dict:
        result = {}

        for category in targets:
            scored = []
            for candidate in colors:
                s = self.score_palette(palette, candidate, category)
                scored.append((candidate, s))

            scored.sort(key=lambda pair: pair[1], reverse=True)
            result[category] = scored[:top_n]

        return result