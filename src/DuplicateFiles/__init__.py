import sys
import os
from pathlib import Path
from from_root import from_root
from numpy import shares_memory
import pandas as pd
from copy import deepcopy
import pickle
from collections import defaultdict

sys.path.append(os.getcwd())
from src.utils.SingletonMeta import SingletonMeta
from src.ReadCatalog import CatalogReader
from src.utils.TimeExecution import time_exec

PATH_TO_DUMP_DUPLICATES = "Duplicate Items"
MIN_SIZE_IN_MB = 100
SKIP_SEARCH = False
PRINT_PATHS = False
EXCLUDED_PATHS = [
    r"$RECYCLE.BIN",
    r"System Volume Information",
]


class DuplicateFiles(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.catalog = deepcopy(CatalogReader().drive_descriptors)
        self.drives = tuple(self.catalog.keys())
        self.exclude = EXCLUDED_PATHS
        self.min_size_in_bytes = MIN_SIZE_IN_MB * 1024 * 1024
        self.duplicate_items = tuple()
        if not SKIP_SEARCH:
            self.optimise_descriptors()
        self.paths_compared = 0
        self.space_savings = 0
        from_root(PATH_TO_DUMP_DUPLICATES).mkdir(exist_ok=True)

    def reduce_descriptor_based_on_min_filesize(self, drive):
        descriptor = self.catalog[drive]["paths_and_stats"]
        reduced_descriptor = tuple(
            [item for item in descriptor if item["path_size"] > self.min_size_in_bytes]
        )
        self.catalog[drive]["paths_and_stats"] = reduced_descriptor

    def cast_paths_to_path_object(self, drive):
        for descriptor in self.catalog[drive]["paths_and_stats"]:
            descriptor["path"] = Path(descriptor["path"])
            descriptor["pathname"] = descriptor["path"].name

    def optimise_descriptors(self):
        for drive in self.catalog.keys():
            self.reduce_descriptor_based_on_min_filesize(drive)
            self.cast_paths_to_path_object(drive)

    def is_not_excluded_file(self, path_a, path_b):
        for item in self.exclude:
            if item in str(path_a) or item in str(path_b):
                return False
        return True

    def bytes_to_gb(self, bytes_):
        return bytes_ / 1024 / 1024 / 1024

    def compare_paths_across_two_drives(self, drive_a, drive_b):
        drive_a_paths_descriptors = self.catalog[drive_a]["paths_and_stats"]
        if drive_a == drive_b:
            print(f"\nWorking on {drive_a}")
            self.compare_paths_in_same_drive(drive_a, drive_a_paths_descriptors)
            return

        drive_b_paths_descriptors = self.catalog[drive_b]["paths_and_stats"]
        print(f"\nWorking on {drive_a} and {drive_b}")
        self.compare_paths_across_two_different_drives(
            drive_a, drive_b, drive_a_paths_descriptors, drive_b_paths_descriptors
        )

    def print_paths_compared(self):
        print(f"{self.paths_compared} paths compared")

    def compare_paths_across_two_different_drives(
        self, drive_a, drive_b, drive_a_paths_descriptors, drive_b_paths_descriptors
    ):
        def is_duplicate():
            return (
                dict_a["path_size"] == dict_b["path_size"]
                and dict_a["pathname"] == dict_b["pathname"]
                and self.is_not_excluded_file(
                    (Path(drive_a) / path_a), (Path(drive_b) / path_b)
                )
            )

        duplicate_items = tuple()

        for dict_a in drive_a_paths_descriptors:
            path_a = dict_a["path"]
            for dict_b in drive_b_paths_descriptors:
                self.paths_compared += 1
                path_b = dict_b["path"]
                if is_duplicate():
                    entry = (
                        f"{drive_a}/{path_a}",
                        f"{drive_b}/{path_b}",
                        f"{self.bytes_to_gb(dict_a['path_size'])}",
                    )
                    duplicate_items += (entry,)
                    if PRINT_PATHS:
                        print(f"\n\n{drive_a}/{path_a}")
                        print(f"{drive_b}/{path_b}\n\n")
        self.print_paths_compared()
        self.duplicate_items += duplicate_items

    def compare_paths_in_same_drive(self, drive_a, drive_a_paths_descriptors):
        def is_duplicate():
            return (
                dict_a["path_size"] == dict_b["path_size"]
                and dict_a["pathname"] == dict_b["pathname"]
                and path_a != path_b
                and self.is_not_excluded_file(
                    (Path(drive_a) / path_a), (Path(drive_a) / path_b)
                )
            )

        duplicate_items = tuple()

        for dict_a in drive_a_paths_descriptors:
            path_a = dict_a["path"]
            for dict_b in drive_a_paths_descriptors:
                self.paths_compared += 1
                path_b = dict_b["path"]
                if is_duplicate():
                    entry = (
                        f"{drive_a}/{path_a}",
                        f"{drive_a}/{path_b}",
                        f"{self.bytes_to_gb(dict_a['path_size'])}",
                    )
                    complement_entry = (
                        f"{drive_a}/{path_b}",
                        f"{drive_a}/{path_a}",
                        f"{self.bytes_to_gb(dict_a['path_size'])}",
                    )
                    if complement_entry in duplicate_items:
                        continue
                    duplicate_items += (entry,)
                    if PRINT_PATHS:
                        print(f"\n\n{drive_a}/{path_a}")
                        print(f"{drive_a}/{path_b}\n\n")
        self.print_paths_compared()
        self.duplicate_items += duplicate_items

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

    def verification(self):
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
        df.to_csv(str(from_root(PATH_TO_DUMP_DUPLICATES) / "duplicates.csv"))
        df.to_html(str(from_root(PATH_TO_DUMP_DUPLICATES) / "duplicates.html"))

    def generate_paths_to_delete(self):
        paths_to_delete = tuple(sorted([item[1] for item in self.duplicate_items]))
        file_definitions = defaultdict(list)
        [
            file_definitions[str(tuple(Path(pathstring).parents)[-2])].append(
                pathstring
            )
            for pathstring in paths_to_delete
        ]

        for drive in file_definitions.keys():
            with open(from_root(PATH_TO_DUMP_DUPLICATES) / f"{drive}.txt", "w") as fp:
                [fp.write(f"{item}\n") for item in file_definitions[drive]]

    @time_exec
    def compare_all_paths(self):
        self.compare_all_drives()
        self.verification()
        self.determine_space_savings()
        self.generate_report_output()
        self.generate_paths_to_delete()


if __name__ == "__main__":
    DuplicateFiles().compare_all_paths()
