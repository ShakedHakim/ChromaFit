import numpy as np
from sklearn.cluster import KMeans


class PaletteExtractor:
    def __init__(self, n_colors: int = 5, random_state: int = 42):
        self.n_colors = n_colors
        self.random_state = random_state

    def extract(self, image):
        """Cluster the image's pixels and return (color, weight) pairs sorted by weight."""
        pixels = image.reshape(-1, 3)

        kmeans = KMeans(n_clusters=self.n_colors, n_init=10,
                        random_state=self.random_state)
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

        return result



