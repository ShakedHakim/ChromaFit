from color_utils import ColorUtils


class PaletteCleaner:
    """Cleans an extracted palette by merging perceptually similar colors."""

    def clean(self, palette: list) -> list:
        """Merge perceptually similar colors, summing their weights."""
        merged = []

        for color, weight in palette:
            hsv = ColorUtils.rgb_to_hsv(color)

            for i in range(len(merged)):
                existing_hsv = ColorUtils.rgb_to_hsv(merged[i][0])
                if ColorUtils.are_similar(hsv, existing_hsv):
                    merged[i] = (merged[i][0], merged[i][1] + weight)
                    break
            else:
                merged.append((color, weight))

        return merged
