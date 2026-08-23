from abc import ABC, abstractmethod
from models import ClothingItem


class ItemRepository(ABC):

    @abstractmethod
    def get_all(self) -> list[ClothingItem]:
        pass

    @abstractmethod
    def find_by_category(self, category: str) -> list[ClothingItem]:
        pass


class MockItemRepository(ItemRepository):

    def __init__(self):
        self._items = [
            ClothingItem("חולצה לבנה", (255, 255, 255), "top"),
            ClothingItem("חולצת פסים כחולה", (60, 90, 160), "top"),
            ClothingItem("סוודר בורדו", (128, 32, 48), "top"),
            ClothingItem("ג'ינס כהה", (40, 55, 90), "bottom"),
            ClothingItem("מכנסי חאקי", (190, 175, 130), "bottom"),
            ClothingItem("חצאית שחורה", (25, 25, 25), "bottom"),
            ClothingItem("סניקרס לבנות", (245, 245, 240), "shoes"),
            ClothingItem("מגפי עור חום", (95, 60, 35), "shoes"),
        ]

    def get_all(self) -> list[ClothingItem]:
        return list(self._items)

    def find_by_category(self, category: str) -> list[ClothingItem]:
        return [item for item in self._items if item.category == category]