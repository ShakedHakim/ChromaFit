from repository_factory import RepositoryFactory
from stylist_service import StylistService

CATEGORIES = ["top", "bottom", "shoes"]


def show_menu():
    for i, category in enumerate(CATEGORIES, start=1):
        print(f"  {i}. {category}")


def ask_single(prompt: str) -> str:
    print(prompt)
    show_menu()
    choice = int(input("> "))
    return CATEGORIES[choice - 1]


def ask_multiple(prompt: str) -> list:
    print(prompt)
    show_menu()

    while True:
        answer = input("> ")
        try:
            result = []
            for part in answer.split(","):
                choice = int(part.strip())
                result.append(CATEGORIES[choice - 1])
            return result
        except (ValueError, IndexError):
            print("Invalid input. Enter numbers separated by commas, e.g. 2,3")


def main():
    print("=== ChromaFit ===\n")

    source = ask_single("What are you matching?")
    targets = ask_multiple("\nWhat do you need colors for? (e.g. 2,3)")
    image_path = input("\nImage path: ")

    service = StylistService(RepositoryFactory.create("sqlite"))
    result = service.recommend(image_path, targets=targets)

    print(f"\nDetected color: {result['dominant']}")

    for category, matches in result["recommendations"].items():
        print(f"\nFor {category}:")
        for color, score in matches:
            print(f"  {color.name:<20} {color.to_hex()}  {score:.2f}")


if __name__ == "__main__":
    main()