from repository import MockItemRepository


def main():
    repo = MockItemRepository()

    print("--- כל הפריטים ---")
    for item in repo.get_all():
        print(f"{item.name:<20} {item.to_hex()}  ({item.category})")

    print("\n--- רק חולצות ---")
    for item in repo.find_by_category("top"):
        print(f"{item.name:<20} {item.to_hex()}")

    from ImageLoader import ImageLoader

    loader = ImageLoader("shirt.jpg")

    image = loader.load()
    image = loader.to_rgb(image)
    image = loader.resize(image)
    image = loader.crop_center(image)  # ← השלב החדש


    print(image.shape)
    print(image[0, 0])

    from palette_extractor import PaletteExtractor

    extractor = PaletteExtractor(n_colors=5)
    palette = extractor.extract(image)

    for color, pct in palette:
        print(f"{color}  {pct:.1%}")

if __name__ == "__main__":
    main()