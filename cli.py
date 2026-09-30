from pathlib import Path

from image_loader import ImageLoader
from repository_factory import RepositoryFactory
from stylist_service import StylistService

CATEGORIES = ["top", "bottom", "shoes"]


def show_menu() -> None:
    """Print the numbered category menu."""
    for i, category in enumerate(CATEGORIES, start=1):
        print(f"  {i}. {category}")


def parse_choice(text: str) -> str | None:
    """Return the category for a menu number, or None if the input is not a valid choice."""
    try:
        choice = int(text.strip())
    except ValueError:
        return None
    if 1 <= choice <= len(CATEGORIES):
        return CATEGORIES[choice - 1]
    return None


def ask_single(prompt: str) -> str:
    """Ask for one category, re-prompting until the input is valid."""
    print(prompt)
    show_menu()

    while True:
        category = parse_choice(input("> "))
        if category is not None:
            return category
        print(f"Invalid input. Enter a single number from 1 to {len(CATEGORIES)}.")


def ask_multiple(prompt: str) -> list[str]:
    """Ask for one or more comma-separated categories, rejecting the entry if any part is invalid."""
    print(prompt)
    show_menu()

    while True:
        categories = [parse_choice(part) for part in input("> ").split(",")]
        if None not in categories:
            return list(dict.fromkeys(categories))
        print(f"Invalid input. Enter numbers from 1 to {len(CATEGORIES)} "
              f"separated by commas, e.g. 2,3")


def ask_image_path(prompt: str) -> str:
    """Ask for an image path, re-prompting until it points to a readable image file."""
    while True:
        path = input(prompt).strip().strip('"')
        if not Path(path).is_file():
            print(f"File not found: '{path}'. Please enter a valid image path.")
            continue
        try:
            ImageLoader(path).load()
        except ValueError as error:
            print(error)
            continue
        return path


def main() -> None:
    """Run the interactive ChromaFit command-line session."""
    print("=== ChromaFit ===\n")

    source = ask_single("What are you matching?")
    targets = ask_multiple("\nWhat do you need colors for? (e.g. 2,3)")
    image_path = ask_image_path("\nImage path: ")

    service = StylistService(RepositoryFactory.create("sqlite"))
    result = service.recommend(image_path, targets=targets)

    print(f"\nMatching your {source}:")
    print(f"Detected color: {result['dominant']}")

    for category, matches in result["recommendations"].items():
        print(f"\nFor {category}:")
        for color, score in matches:
            print(f"  {color.name:<20} {color.to_hex()}  {score:.2f}")


if __name__ == "__main__":
    main()
