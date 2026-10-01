import logging

from image_loader import ImageLoader
from palette_extractor import PaletteExtractor
from palette_cleaner import PaletteCleaner
from matcher import ColorMatcher
from scoring_strategy import ContinuousScoring

logger = logging.getLogger(__name__)


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
        """Run the full pipeline on an image and return its palette, dominant color and recommendations."""
        colors = self.repository.get_all()
        logger.debug("Loaded %d candidate colors from repository", len(colors))

        logger.info("Loading and preprocessing image: %s", image_path)
        image = self._prepare_image(image_path)

        logger.info("Extracting palette with %d clusters", self.extractor.n_colors)
        palette = self.extractor.extract(image)
        logger.debug("Extracted palette with %d colors", len(palette))

        logger.info("Cleaning palette of %d colors", len(palette))
        palette = self.cleaner.clean(palette)
        logger.debug("Cleaned palette has %d colors", len(palette))
        dominant = palette[0][0]

        logger.info("Scoring candidates for categories: %s (top %d)", targets, top_n)
        recommendations = self.matcher.recommend_colors(
            palette, colors, targets, top_n
        )

        return {
            "palette": palette,
            "dominant": dominant,
            "recommendations": recommendations,
        }