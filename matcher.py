from color_utils import ColorUtils
from models import NamedColor
from scoring_strategy import ScoringStrategy, DiscreteScoring

class ColorMatcher:

    def __init__(self, strategy: ScoringStrategy = None):
        self.strategy = strategy or DiscreteScoring()

    NEUTRAL_BASE = 0.7
    NEUTRAL_CONTRAST_BONUS = 0.2
    # Shoes lean toward muted, wearable colors. The penalty uses vividness (S*V) rather than saturation
    # alone: dark saturated colors such as navy, brown, olive and burgundy (vividness <= 0.4) are fine
    # for shoes, while bright loud ones such as lemon or violet pink (0.6+) are not.
    SHOE_MAX_VIVIDNESS = 0.5
    SHOE_PENALTY = 0.6
    # A photographed black garment often comes out as a dark, slightly tinted grey that is_neutral()
    # misses (V >= 60, S >= 40). Scoring it by hue would recommend its neon complement, so sources
    # darker and less saturated than these limits are scored like neutral sources instead.
    NEAR_BLACK_MAX_VALUE = 80
    NEAR_BLACK_MAX_SATURATION = 120
    # In the neutral path, contrast against a dark source always means "light", which pushes shoes to
    # pastels. For shoes, this share of the contrast bonus rewards depth (darker = better) instead.
    SHOE_DEPTH_WEIGHT = 0.5
    EARTHY_BASE = 0.6
    EARTHY_HUE_WEIGHT = 0.15
    EARTHY_PROFILE_WEIGHT = 0.15
    EARTHY_VALUE_WEIGHT = 0.10
    EARTH_HUE_BAND = (6, 25)       # OpenCV hue: rust / terracotta / brown / camel / tan
    EARTH_HUE_SOFTNESS = 10
    EARTH_SAT_BAND = (80, 220)
    EARTH_VAL_BAND = (90, 220)
    EARTH_BAND_SOFTNESS = 60
    EARTHY_CONTRAST_CAP = 80       # a brightness gap of 80+ counts as full contrast
    BAND_EDGE_SCORE = 0.8
    NEUTRAL_SLOTS = 2              # reserved, but never more than half of top_n
    MIN_PICK_DISTANCE = 0.12       # normalized RGB distance (about 53 of 441) between any two picks
    NEUTRAL_MIN_DISTANCE = 0.5     # reserved neutrals must differ clearly (e.g. a light and a dark one)

    def score(self, color_rgb: tuple, candidate: NamedColor,
              target_category: str) -> float:
        """Score how well a candidate color pairs with a single source color."""
        source_hsv = ColorUtils.rgb_to_hsv(color_rgb)
        candidate_hsv = ColorUtils.rgb_to_hsv(candidate.rgb)

        if (ColorUtils.is_neutral(source_hsv) or ColorUtils.is_neutral(candidate_hsv)
                or self._is_near_black(source_hsv)):
            result = self._score_neutral(color_rgb, candidate, candidate_hsv, target_category)
        elif ColorUtils.is_earthy_tone(source_hsv):
            result = self._score_earthy(source_hsv, candidate_hsv, target_category)
        else:
            dist = ColorUtils.hue_distance(source_hsv[0], candidate_hsv[0])
            result = self.strategy.score_hue_distance(dist)

        return self._apply_category_adjustment(result, candidate_hsv, target_category)

    def _is_near_black(self, source_hsv: tuple) -> bool:
        """True for dark, slightly tinted sources that is_neutral() misses; earth tones keep their own path."""
        return (source_hsv[2] < self.NEAR_BLACK_MAX_VALUE
                and source_hsv[1] < self.NEAR_BLACK_MAX_SATURATION
                and not ColorUtils.is_earthy_tone(source_hsv))

    def _score_neutral(self, color_rgb: tuple, candidate: NamedColor, candidate_hsv: tuple,
                       target_category: str) -> float:
        """Base plus contrast bonus; for shoes part of the bonus rewards depth instead of contrast."""
        contrast = ColorUtils.rgb_distance(color_rgb, candidate.rgb)
        if target_category == "shoes":
            depth = 1 - candidate_hsv[2] / 255
            contrast = (1 - self.SHOE_DEPTH_WEIGHT) * contrast + self.SHOE_DEPTH_WEIGHT * depth
        return self.NEUTRAL_BASE + contrast * self.NEUTRAL_CONTRAST_BONUS

    def _score_earthy(self, source_hsv: tuple, candidate_hsv: tuple,
                      target_category: str) -> float:
        """Favour candidates with an earth-tone hue, saturation and brightness; shoes favour deeper tones."""
        hue, saturation, value = candidate_hsv
        if hue >= 150:
            hue -= 180                 # pinks/magentas sit just below 0 on the hue wheel
        hue_part = self._band_score(hue, *self.EARTH_HUE_BAND, self.EARTH_HUE_SOFTNESS)
        profile_part = (self._band_score(saturation, *self.EARTH_SAT_BAND, self.EARTH_BAND_SOFTNESS)
                        * self._band_score(value, *self.EARTH_VAL_BAND, self.EARTH_BAND_SOFTNESS))
        if target_category == "shoes":
            value_part = 1 - value / 255
        else:
            value_part = min(abs(source_hsv[2] - value), self.EARTHY_CONTRAST_CAP) / self.EARTHY_CONTRAST_CAP
        return (self.EARTHY_BASE + self.EARTHY_HUE_WEIGHT * hue_part
                + self.EARTHY_PROFILE_WEIGHT * profile_part + self.EARTHY_VALUE_WEIGHT * value_part)

    def _band_score(self, x: float, low: float, high: float, softness: float) -> float:
        """1.0 at the middle of [low, high], BAND_EDGE_SCORE at its edges, fading to 0 over softness outside it."""
        if x < low:
            return max(0.0, 1 - (low - x) / softness) * self.BAND_EDGE_SCORE
        if x > high:
            return max(0.0, 1 - (x - high) / softness) * self.BAND_EDGE_SCORE
        middle, half_width = (low + high) / 2, (high - low) / 2
        return self.BAND_EDGE_SCORE + (1 - self.BAND_EDGE_SCORE) * (1 - abs(x - middle) / half_width)

    def _apply_category_adjustment(self, base_score: float, candidate_hsv: tuple,
                                   target_category: str) -> float:
        """Penalize vivid (bright and saturated) candidates for shoes, which lean toward muted colors."""
        if target_category == "shoes" and ColorUtils.vividness(candidate_hsv) > self.SHOE_MAX_VIVIDNESS:
            return base_score * self.SHOE_PENALTY
        return base_score

    def score_palette(self, palette: list, candidate: NamedColor,
                      target_category: str) -> float:
        """Score a candidate against a whole palette, weighting each color by its share."""
        total = 0.0
        for color, weight in palette:
            total += self.score(color, candidate, target_category) * weight
        return total

    def recommend_colors(self, palette: list, colors: list,
                         targets: list, top_n: int = 3) -> dict:
        """Return the top_n candidates per category: reserved neutral slots, no near-duplicates."""
        result = {}

        for category in targets:
            scored = []
            for candidate in colors:
                s = self.score_palette(palette, candidate, category)
                scored.append((candidate, s))

            scored.sort(key=lambda pair: pair[1], reverse=True)
            result[category] = self._pick_diverse(scored, top_n)

        return result

    def _pick_diverse(self, ranked: list, top_n: int) -> list:
        """Fill the reserved neutral slots first, then the best remaining candidates, skipping near-duplicates."""
        picks = []

        def fits(candidate: NamedColor, minimum: float) -> bool:
            return all(ColorUtils.rgb_distance(candidate.rgb, p.rgb) >= minimum for p, _ in picks)

        neutral_slots = min(self.NEUTRAL_SLOTS, top_n // 2)
        for candidate, s in ranked:
            if len(picks) == neutral_slots:
                break
            if self._is_reserved_neutral(candidate) and fits(candidate, self.NEUTRAL_MIN_DISTANCE):
                picks.append((candidate, s))

        for candidate, s in ranked:
            if len(picks) == top_n:
                break
            if all(candidate is not p for p, _ in picks) and fits(candidate, self.MIN_PICK_DISTANCE):
                picks.append((candidate, s))

        return sorted(picks, key=lambda pair: pair[1], reverse=True)

    @staticmethod
    def _is_reserved_neutral(candidate: NamedColor) -> bool:
        """Neutral by low saturation only, so very dark colored items (dark green, navy) can't take a neutral slot."""
        return ColorUtils.is_neutral(ColorUtils.rgb_to_hsv(candidate.rgb), dark_tol=0)