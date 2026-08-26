from image_loader import ImageLoader
from palette_extractor import PaletteExtractor
from matcher import ColorMatcher

# this class is like Facade

class StylistService:

    def __init__(self, repository, n_colors: int = 5):
        self.repository = repository
        self.extractor = PaletteExtractor(n_colors=n_colors)
        self.matcher = ColorMatcher()

    def _prepare_image(self, image_path: str):
        """Load and preprocess an image for palette extraction."""
        loader = ImageLoader(image_path)
        image = loader.load()
        image = loader.to_rgb(image)
        image = loader.resize(image)
        return loader.crop_center(image)

    def recommend(self, image_path: str, source_category: str) -> dict:
        items = self.repository.get_all()

        image = self._prepare_image(image_path)
        palette = self.extractor.extract(image)
        dominant = palette[0][0]

        outfit = self.matcher.build_outfit(dominant, items, source_category)

        candidates = [i for i in items if i.category != source_category]
        ranked = [(i, self.matcher.score_palette(palette, i)) for i in candidates]
        ranked.sort(key=lambda pair: pair[1], reverse=True)

        return {
            "palette": palette,
            "dominant": dominant,
            "outfit": outfit,
            "ranked": ranked,
        }