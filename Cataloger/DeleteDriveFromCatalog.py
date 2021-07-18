from pathlib import Path
import os
import json

CATALOG_PATH = Path(os.getcwd()) / "catalog.json"


def read_catalog(catalog_path):
    with open(catalog_path, "r") as fp:
        catalog = json.load(fp)
    return catalog


def prompt_for_drive_to_purge(catalog):
    drives = tuple(catalog.keys())
    drives_enumerated = enumerate(drives)
    [print(f"{idx}:", drive) for idx, drive in enumerate(drives)]
    selected_drive_index = int(
        input("Type number of drive to be removed from catalog ")
    )
    selected_drive_key = drives[selected_drive_index]
    return selected_drive_key


def purge_drive_from_catalog(catalog_path, catalog, selected_drive_key):
    confirmed = input(f"Delete {selected_drive_key} from catalog? (y) ") == "y"
    if confirmed:
        del catalog[selected_drive_key]

    with open(catalog_path, "w") as fp:
        json.dump(catalog, fp)


if __name__ == "__main__":
    catalog = read_catalog(CATALOG_PATH)
    selected_drive_key = prompt_for_drive_to_purge(catalog)
    purge_drive_from_catalog(CATALOG_PATH, catalog, selected_drive_key)
