from abc import ABC, abstractmethod


class ScoringStrategy(ABC):

    @abstractmethod
    def score_hue_distance(self, dist: int) -> float:
        pass


class DiscreteScoring(ScoringStrategy):
    # The original scoring rules — four fixed steps.

    def score_hue_distance(self, dist: int) -> float:
        if dist < 10:
            return 0.75
        elif dist < 30:
            return 0.85
        elif dist < 75:
            return 0.35
        else:
            return 1.0

class ContinuousScoring(ScoringStrategy):
    # A smooth scoring curve — no two distances give the exact same score.

    def score_hue_distance(self, dist: int) -> float:
        if dist <= 30:
            return 0.5 + (dist / 30) * 0.35
        else:
            return 0.85 + ((dist - 30) / 60) * 0.15