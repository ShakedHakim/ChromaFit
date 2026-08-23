import cv2


class ImageLoader:
    def __init__(self, path: str):
        self.path = path

    def load(self):
        return cv2.imread(self.path)

    def to_rgb(self, image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    def resize(self, image, width: int = 200, height: int = 200):
        return cv2.resize(image, (width, height))


    def crop_center(self, image, ratio: float = 0.5):
        h, w, _ = image.shape
        new_h, new_w = int(h * ratio), int(w * ratio)
        start_h, start_w = (h - new_h) // 2, (w - new_w) // 2

        return image[start_h:start_h + new_h, start_w:start_w + new_w]