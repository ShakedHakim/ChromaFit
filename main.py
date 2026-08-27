from repository import MockItemRepository
from stylist_service import StylistService

IMAGES = ["shirt.jpg", "blue.jpg", "green.jpg", "black.jpg", "white.jpg"]


def main():
    service = StylistService(MockItemRepository())

    for path in IMAGES:
        print(f"\n{'=' * 50}")
        print(f"IMAGE: {path}")
        print('=' * 50)

        result = service.recommend(path, source_category="top")

        print("Palette:")
        for color, pct in result["palette"]:
            print(f"  {color}  {pct:.1%}")

        print("Outfit:")
        for category, (item, score) in result["outfit"].items():
            print(f"  {category:<8} {item.name:<20} {score:.2f}")


if __name__ == "__main__":
    main()