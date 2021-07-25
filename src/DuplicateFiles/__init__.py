import sys
import os
from pathlib import Path
from from_root import from_root
import pandas as pd
from copy import deepcopy
import pickle

sys.path.append(os.getcwd())
from src.utils.SingletonMeta import SingletonMeta
from src.ReadCatalog import CatalogReader
from src.utils.TimeExecution import time_exec

SKIP_SEARCH = False
PRINT_PATHS = False
EXCLUDED_PATHS = [
    r"$RECYCLE.BIN",
    r"System Volume Information",
    r"DoNotUse/Music Performances",
    r"Samsung T5/repeated shows",
]


class DuplicateFiles(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.catalog = deepcopy(CatalogReader().drive_descriptors)
        self.drives = tuple(self.catalog.keys())
        self.exclude = EXCLUDED_PATHS
        self.min_size_in_bytes = 100 * 1024 * 1024
        self.duplicate_items = list()
        if not SKIP_SEARCH:
            self.reduce_catalog_based_on_min_filesize()
            self.cast_paths_to_path_object()
        self.paths_compared = 0
        self.space_savings = 0
        self.a_list, self.b_list = list(), list()

    def reduce_catalog_based_on_min_filesize(self):
        for drive in self.catalog.keys():
            self.catalog[drive]["paths_and_stats"] = self.reduce_descriptors(
                self.catalog[drive]["paths_and_stats"]
            )

    def cast_paths_to_path_object(self):
        for drive in self.catalog.keys():
            for descriptor in self.catalog[drive]["paths_and_stats"]:
                descriptor["path"] = Path(descriptor["path"])
                descriptor["pathname"] = descriptor["path"].name

    def is_not_excluded_file(self, path_a, path_b):
        for item in self.exclude:
            if item in str(path_a) or item in str(path_b):
                return False
        return True

    def is_duplicate(
        self,
        drive_a: str,
        drive_b: str,
        dict_a: dict,
        path_a: str,
        dict_b: dict,
        path_b: str,
    ):
        if (
            (drive_a == drive_b)
            and dict_a["path_size"] == dict_b["path_size"]
            and (path_a == path_b)
        ):
            return False

        return (
            dict_a["path_size"] == dict_b["path_size"]
            and dict_a["pathname"] == dict_b["pathname"]
            and self.is_not_excluded_file(
                (Path(drive_a) / path_a), (Path(drive_b) / path_b)
            )
        )

    @time_exec
    def reduce_descriptors(self, descriptor):
        reduced_descriptor = tuple(
            [item for item in descriptor if item["path_size"] > self.min_size_in_bytes]
        )
        return reduced_descriptor

    def bytes_to_gb(self, bytes_):
        return bytes_ / 1024 / 1024 / 1024

    def compare_paths_across_two_drives(self, drive_a, drive_b):
        if drive_a != drive_b:
            print(f"\nWorking on {drive_a} and {drive_b}")
        else:
            print(f"\nWorking on {drive_a}")
        drive_a_paths_descriptors = self.catalog[drive_a]["paths_and_stats"]
        drive_b_paths_descriptors = self.catalog[drive_b]["paths_and_stats"]
        duplicate_items = list()
        for dict_a in drive_a_paths_descriptors:
            path_a = dict_a["path"]
            for dict_b in drive_b_paths_descriptors:
                self.paths_compared += 1
                path_b = dict_b["path"]
                if self.is_duplicate(drive_a, drive_b, dict_a, path_a, dict_b, path_b):
                    entry = (
                        f"{drive_a}/{path_a}",
                        f"{drive_b}/{path_b}",
                        f"{self.bytes_to_gb(dict_a['path_size'])}",
                    )
                    if drive_a == drive_b:
                        complement_entry = (
                            f"{drive_b}/{path_b}",
                            f"{drive_a}/{path_a}",
                            f"{self.bytes_to_gb(dict_a['path_size'])}",
                        )
                        if complement_entry in duplicate_items:
                            continue
                    duplicate_items.append(entry)
                    if PRINT_PATHS:
                        print(f"\n\n{drive_a}/{path_a}")
                        print(f"{drive_b}/{path_b}\n\n")
        print(f"{self.paths_compared} paths compared")
        self.duplicate_items.extend(duplicate_items)

    def compare_all_drives(self):
        if SKIP_SEARCH:
            print("Skipping search".upper())
            with open("duplicate_items.json", "rb") as fp:
                self.duplicate_items = pickle.load(fp)
            return
        num_drives = len(self.drives)
        for source_drive_idx in range(num_drives):
            for best_drive_idx in range(source_drive_idx, num_drives):
                drive_a = self.drives[source_drive_idx]
                drive_b = self.drives[best_drive_idx]
                self.compare_paths_across_two_drives(drive_a, drive_b)
        with open("duplicate_items.json", "wb") as fp:
            pickle.dump(self.duplicate_items, fp, protocol=pickle.HIGHEST_PROTOCOL)

    def find_potential_errors(self):
        original_list = list()
        flip_list = list()
        error_items = list()
        for item in self.duplicate_items:
            original_list.append((item[0], item[1]))
            flip_list.append((item[1], item[0]))
        for item in tuple(original_list):
            if item in tuple(flip_list):
                error_items.append(item)
        return error_items

    def correct_potential_errors(self, error_items: list):
        print(f"Attempting to correct {len(error_items)} errors")

        def remove_duplicates(item):
            for error_item in tuple(error_items):
                if error_item[0] == item[0] and error_item[1] == item[1]:
                    error_items.remove(error_item)
                    return False
            return True

        self.duplicate_items = tuple(filter(remove_duplicates, self.duplicate_items))

    @time_exec
    def sanity_check(self):
        error_items = self.find_potential_errors()
        print(f"\n{len(error_items)} wrong paths detected!")
        if not error_items:
            return
        self.correct_potential_errors(error_items)
        error_items = self.find_potential_errors()
        print(f"{len(error_items)} wrong paths detected!")
        if error_items:
            raise RuntimeError("Exiting due to duplicate search failure")

    def determine_space_savings(self):
        for item in self.duplicate_items:
            self.space_savings += float(item[2])
        space_savings_in_gb = self.space_savings
        print(f"\nSpace savings possible: {space_savings_in_gb:.1f}GB")

    def generate_report_output(self):
        df = pd.DataFrame(
            self.duplicate_items, columns=("File A", "File B", "size in GB")
        )
        df.to_csv(from_root(".") / "duplicates.csv")
        df.to_html(from_root(".") / "duplicates.html")

    @time_exec
    def compare_all_paths(self):
        self.compare_all_drives()
        self.sanity_check()
        self.determine_space_savings()
        self.generate_report_output()


if __name__ == "__main__":
    DuplicateFiles().compare_all_paths()
