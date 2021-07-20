import sys
import os

sys.path.append(os.getcwd())
from src.Cataloger.Initializer import Initializer

CATALOGS_PATH = Initializer(catalog_drives=False).catalogs_path


def prompt_for_drive_to_purge():
    drives = tuple(path.stem for path in (CATALOGS_PATH.glob("*.json")))
    [print(f"{idx}:", drive) for idx, drive in enumerate(drives)]
    selected_drive_index = int(
        input("Type number of drive to be removed from catalog ")
    )
    selected_drive_key = drives[selected_drive_index]
    return selected_drive_key


def purge_drive_from_catalog(selected_drive_key: str):
    confirmed = input(f"Delete {selected_drive_key} from catalog? (y) ") == "y"
    if confirmed:
        (CATALOGS_PATH / f"{selected_drive_key}.json").unlink()


if __name__ == "__main__":
    selected_drive_key = prompt_for_drive_to_purge()
    purge_drive_from_catalog(selected_drive_key)
