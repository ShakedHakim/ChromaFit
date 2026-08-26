from repository import MockItemRepository
from stylist_service import StylistService

SOURCE_IMAGE = "shirt.jpg"
SOURCE_CATEGORY = "top"


def main():
    service = StylistService(MockItemRepository())
    result = service.recommend(SOURCE_IMAGE, source_category=SOURCE_CATEGORY)

    print("--- Color palette ---")
    for color, pct in result["palette"]:
        print(f"{color}  {pct:.1%}")

    print("\n--- Recommended outfit ---")
    for category, (item, score) in result["outfit"].items():
        print(f"{category:<8} {item.name:<20} {item.to_hex()}  {score:.2f}")

    print("\n--- Full ranking ---")
    for item, score in result["ranked"]:
        print(f"{item.name:<20} {item.to_hex()}  {score:.2f}")


if __name__ == "__main__":
    main()