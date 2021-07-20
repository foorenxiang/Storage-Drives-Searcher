from from_root import from_root
import json
from icecream import ic
import sys
import os

sys.path.append(os.getcwd())
from src.utils.SingletonMeta import SingletonMeta
from src.Cataloger.Initializer import Initializer
from src.FileSearcher import FileSearcher

CATALOG_FILE_LOCATION = from_root("catalog.json")


# TODO: RX: break into smaller single responsibility classes
class CatalogReader(metaclass=SingletonMeta):
    def __init__(self):
        self.catalogs_path = Initializer(catalog_drives=False).catalogs_path
        self.drive_descriptors = dict()
        self._read_catalog_files()

    def utility(self):
        self._enumerate_drives()
        self._count_catalogued_files()
        self._print_stats()
        self._print_options()
        self._get_selected_drive_descriptor()
        self._print_selected_drive_descriptor()

    def _print_selected_drive_descriptor(self):
        try:
            print("Loading...")
            ic(self.drive_descriptors[self._selected_drive_name])
        except IndexError:
            print("Invalid selection!")

    def _get_selected_drive_descriptor(self):
        self._selected_drive_name_index = 1
        self._selected_drive_name = self.enumerated_drives[
            int(self.selected_drive_index) - self.enumeration_offset
        ][self._selected_drive_name_index]

    def _print_options(self):
        [print(f"{drive_name}:", enum) for enum, drive_name in self.enumerated_drives]
        self.selected_drive_index = input("\nSelect drive index to show manifest for: ")

    def _print_stats(self):
        print("\nFiles catalogued:", self.items_catalogued)
        print("\nDrives catalogued:")

    def _count_catalogued_files(self):
        self.items_catalogued = 0
        for descriptor in self.drive_descriptors.values():
            self.items_catalogued = len(
                FileSearcher().get_paths_from_drive_descriptor(descriptor)
            )

    def _enumerate_drives(self):
        self.drives_catalogued = self.drive_descriptors.keys()
        self.enumeration_offset = 1
        self.enumerated_drives = tuple(
            enumerate(self.drives_catalogued, self.enumeration_offset)
        )

    def _read_catalog_files(self):
        for catalog_path in self.catalogs_path.glob("*.json"):
            drivename = catalog_path.stem
            with open(catalog_path, "r") as fp:
                self.drive_descriptors[drivename] = json.load(fp)


if __name__ == ("__main__"):
    CatalogReader().utility()
