from dataclasses import dataclass


@dataclass(frozen=True)
class ClothingItem:
    name: str
    rgb_color: tuple[int, int, int]
    category: str  # "top" / "bottom" / "shoes"

    def to_hex(self) -> str:
        """Convert the RGB color to a hexadecimal string."""
        r, g, b = self.rgb_color
        return f"#{r:02X}{g:02X}{b:02X}"