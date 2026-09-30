from image_loader import ImageLoader
from palette_extractor import PaletteExtractor
from palette_cleaner import PaletteCleaner
from matcher import ColorMatcher
from scoring_strategy import ContinuousScoring


class StylistService:
    # Orchestrates the full color recommendation pipeline.
    def __init__(self, repository, n_colors: int = 5):
        self.repository = repository
        self.extractor = PaletteExtractor(n_colors=n_colors)
        self.cleaner = PaletteCleaner()
        self.matcher = ColorMatcher(ContinuousScoring())

    def _prepare_image(self, image_path: str):
        #Load and preprocess an image for palette extraction.
        loader = ImageLoader(image_path)
        image = loader.load()
        image = loader.to_rgb(image)
        image = loader.resize(image)
        return loader.crop_center(image)

    def recommend(self, image_path: str, targets: list, top_n: int = 3) -> dict:
        colors = self.repository.get_all()

        image = self._prepare_image(image_path)
        palette = self.extractor.extract(image)
        palette = self.cleaner.clean(palette)
        dominant = palette[0][0]

        recommendations = self.matcher.recommend_colors(
            palette, colors, targets, top_n
        )

        return {
            "palette": palette,
            "dominant": dominant,
            "recommendations": recommendations,
        }