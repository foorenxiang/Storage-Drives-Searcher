# https://stackoverflow.com/questions/54395735/how-to-work-with-heic-image-file-types-in-python
import whatimage
import pyheif
from PIL import Image
from pathlib import Path
from from_root import from_root

APP_FOLDER = Path.home() / ".Storage Drive Searcher"
IMAGE_STORE = APP_FOLDER / "drive_images"


def display_drive_image(filepath, index=None):
    with open(filepath, "rb") as f:
        data = f.read()
        fmt = whatimage.identify_image(data)
        if fmt not in ["heic", "avif"]:
            return
    heif_file = pyheif.read(filepath)
    image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )
    image.show(title=(f"Rank {index}" if index else None))


if __name__ == "__main__":
    for index, file in enumerate(Path(IMAGE_STORE).glob("*.HEIC")):
        display_drive_image(str(file.resolve()), index)
