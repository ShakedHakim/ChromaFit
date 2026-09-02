from dataclasses import dataclass


@dataclass(frozen=True)
class NamedColor:
    name: str
    rgb: tuple[int, int, int]

    def to_hex(self) -> str:
        """Convert the RGB color to a hexadecimal string."""
        r, g, b = self.rgb
        return f"#{r:02X}{g:02X}{b:02X}"