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

SKIP_SEARCH = True


class DuplicateFiles(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.catalog = deepcopy(CatalogReader().drive_descriptors)
        self.drives = tuple(self.catalog.keys())
        self.exclude = [
            r"$RECYCLE.BIN",
            r"System Volume Information",
            r"DoNotUse/Music Performances",
            r"Samsung T5/repeated shows",
        ]
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

    def is_duplicate(self, drive_a, drive_b, dict_a, path_a, dict_b, path_b):
        if (
            (drive_a == drive_b)
            and dict_a["path_size"] == dict_b["path_size"]
            and (path_a == path_b)
        ):
            return False

        return (
            dict_a["path_size"] == dict_b["path_size"]
            and dict_a["pathname"] == dict_b["pathname"]
            and not (
                any(
                    [
                        item
                        for item in self.exclude
                        if item in str(Path(drive_a) / path_a)
                    ]
                    + [
                        item
                        for item in self.exclude
                        if item in str(Path(drive_b) / path_b)
                    ]
                )
            )
        )

    @time_exec
    def reduce_descriptors(self, descriptor):
        reduced_descriptor = tuple(
            [item for item in descriptor if item["path_size"] > self.min_size_in_bytes]
        )
        return reduced_descriptor

    def compare_paths_across_two_drives(self, drive_a, drive_b):
        print(f"\nWorking on {drive_a} and {drive_b}")
        drive_a_paths_descriptors = self.catalog[drive_a]["paths_and_stats"]
        drive_b_paths_descriptors = self.catalog[drive_b]["paths_and_stats"]
        for dict_a in drive_a_paths_descriptors:
            print(f"\r{self.paths_compared} paths compared", end="", flush=True)
            self.paths_compared += 1
            path_a = dict_a["path"]
            for dict_b in drive_b_paths_descriptors:
                self.paths_compared += 1
                path_b = dict_b["path"]
                if self.is_duplicate(drive_a, drive_b, dict_a, path_a, dict_b, path_b):
                    bytes_to_gb = lambda bytes_: bytes_ / 1024 / 1024 / 1024

                    self.duplicate_items.append(
                        (
                            f"{drive_a}/{path_a}",
                            f"{drive_b}/{path_b}",
                            f"{bytes_to_gb(dict_a['path_size'])}",
                        )
                    ) if dict_a["path_modified_time"] >= dict_b[
                        "path_modified_time"
                    ] else self.duplicate_items.append(
                        (
                            f"{drive_b}/{path_b}",
                            f"{drive_a}/{path_a}",
                            f"{bytes_to_gb(dict_a['path_size'])}",
                        )
                    )

                    print(f"\n\n{drive_a}/{path_a}")
                    print(f"{drive_b}/{path_b}\n\n")

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

        self.error_items = error_items
        print(f"{len(self.error_items)} wrong paths detected!")

    def correct_potential_errors(self):
        print(f"Attempting to correct {len(self.error_items)} errors")

        def remove_duplicates(item):
            for error_item in tuple(self.error_items):
                if error_item[0] == item[0] and error_item[1] == item[1]:
                    self.error_items.remove(error_item)
                    return False
            return True

        self.duplicate_items = tuple(filter(remove_duplicates, self.duplicate_items))

    def final_printout(self):
        for item in self.duplicate_items:
            self.space_savings += float(item[2])
        space_savings_in_gb = self.space_savings
        print(f"\nSpace savings possible: {space_savings_in_gb:.1f}GB")
        print(f"{len(self.error_items)} wrong paths detected!")
        print(f"Utility finished with {self.paths_compared} paths compared")

    def generate_report_output(self):
        df = pd.DataFrame(
            self.duplicate_items, columns=("File A", "File B", "size in GB")
        )
        df.to_csv(from_root(".") / "duplicates.csv")
        df.to_html(from_root(".") / "duplicates.html")

    @time_exec
    def sanity_check(self):
        self.find_potential_errors()
        self.correct_potential_errors()
        self.find_potential_errors()

    @time_exec
    def compare_all_paths(self):
        self.compare_all_drives()
        self.generate_report_output()
        self.sanity_check()
        self.final_printout()


if __name__ == "__main__":
    DuplicateFiles().compare_all_paths()
