import numpy as np
from sklearn.cluster import KMeans
from color_utils import ColorUtils


class PaletteExtractor:
    def __init__(self, n_colors: int = 5):
        self.n_colors = n_colors

    def extract(self, image):
        pixels = image.reshape(-1, 3)

        kmeans = KMeans(n_clusters=self.n_colors, n_init=10)
        kmeans.fit(pixels)

        centers = kmeans.cluster_centers_.astype(int)
        labels, counts = np.unique(kmeans.labels_, return_counts=True)
        total = len(kmeans.labels_)

        order = np.argsort(counts)[::-1]

        result = []
        for i in order:
            color = tuple(int(c) for c in centers[i])
            weight = counts[i] / total
            result.append((color, weight))

        return self._merge_similar(result)

    def _merge_similar(self, palette: list) -> list:
        #Merge perceptually similar colors, summing their weights.
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



