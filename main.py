from repository import MockItemRepository
from color_utils import ColorUtils
from image_loader import ImageLoader
from palette_extractor import PaletteExtractor
from matcher import ColorMatcher


def main():
    repo = MockItemRepository()

    print("--- כל הפריטים ---")
    for item in repo.get_all():
        print(f"{item.name:<20} {item.to_hex()}  ({item.category})")

    print("\n--- רק חולצות ---")
    for item in repo.find_by_category("top"):
        print(f"{item.name:<20} {item.to_hex()}")

    loader = ImageLoader("shirt.jpg")
    image = loader.load()
    image = loader.to_rgb(image)
    image = loader.resize(image)
    image = loader.crop_center(image)

    extractor = PaletteExtractor(n_colors=5)
    palette = extractor.extract(image)

    print("\n--- פלטת הצבעים ---")
    for color, pct in palette:
        print(f"{color}  {pct:.1%}")

    print("\n--- בדיקת ColorUtils ---")
    print(ColorUtils.rgb_to_hsv((234, 84, 0)))
    print(ColorUtils.rgb_to_hsv((255, 255, 255)))
    print(ColorUtils.hue_distance(5, 175))
    print(ColorUtils.is_neutral((0, 0, 255)))

    matcher = ColorMatcher()
    dominant = palette[0][0]

    print(f"\n--- התאמות ל-{dominant} ---")
    for item, s in matcher.find_matches(dominant, repo.get_all()):
        print(f"{item.name:<20} {item.to_hex()}  {s:.2f}")

    print(ColorUtils.rgb_to_hsv((60, 90, 160)))  # הכחול
    print(ColorUtils.rgb_to_hsv((128, 32, 48)))  # הבורדו

if __name__ == "__main__":
    main()