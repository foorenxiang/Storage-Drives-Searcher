import sys
import os
from pathlib import Path
from from_root import from_root
import pandas as pd
from copy import deepcopy

sys.path.append(os.getcwd())
from src.utils.SingletonMeta import SingletonMeta
from src.ReadCatalog import CatalogReader
from src.utils.TimeExecution import time_exec


# logging.basicConfig(
#     filename="duplicates.csv", filemode="w", level=logging.INFO, format="%(message)s"
# )
# logger = logging.getLogger()


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
        self.initial_path_count = 0
        self.duplicate_items = list()
        self.reduce_catalog_based_on_min_filesize()
        self.cast_paths_to_path_object()
        self.paths_compared = 0
        self.space_savings = 0
        # logger.info("File A, File B, size in GB")

    def reduce_catalog_based_on_min_filesize(self):
        for drive in self.catalog.keys():
            self.initial_path_count += len(self.catalog[drive]["paths_and_stats"])
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

    @time_exec
    def compare_all_paths(self):
        print(f"{self.initial_path_count} paths to compare")
        num_drives = len(self.drives)
        for source_drive_idx in range(num_drives):
            for best_drive_idx in range(source_drive_idx, num_drives):
                drive_a = self.drives[source_drive_idx]
                drive_b = self.drives[best_drive_idx]

                self.compare_drive_paths(drive_a, drive_b)
        space_savings_in_gb = self.space_savings / 1024 / 1024 / 1024
        print(f"\nSpace savings possible: {space_savings_in_gb:.1f}GB")
        print(f"Utility finished with {self.paths_compared} paths compared")
        df = pd.DataFrame(
            self.duplicate_items, columns=("File A", "File B", "size in GB")
        )
        print(df)
        df.to_csv(from_root(".") / "duplicates.csv")
        df.to_html(from_root(".") / "duplicates.html")

    # TODO: fix only adjacent comparisons
    def compare_drive_paths(self, drive_a, drive_b):
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
                    # logger.info(
                    #     f"{drive_a}/{path_a},{drive_b}/{path_b},{bytes_to_gb(dict_a['path_size'])}"
                    # ) if dict_a["path_modified_time"] >= dict_b[
                    #     "path_modified_time"
                    # ] else logger.info(
                    #     f"{drive_b}/{path_b},{drive_a}/{path_a}{bytes_to_gb(dict_a['path_size'])}"
                    # )

                    self.duplicate_items.append(
                        [
                            f"{drive_a}/{path_a}",
                            f"{drive_b}/{path_b}",
                            f"{bytes_to_gb(dict_a['path_size'])}",
                        ]
                    ) if dict_a["path_modified_time"] >= dict_b[
                        "path_modified_time"
                    ] else self.duplicate_items.append(
                        [
                            f"{drive_b}/{path_b}",
                            f"{drive_a}/{path_a}",
                            f"{bytes_to_gb(dict_a['path_size'])}",
                        ]
                    )

                    print(f"\n\n{drive_a}/{path_a}")
                    print(f"{drive_b}/{path_b}\n\n")
                    self.space_savings += dict_a["path_size"]


if __name__ == "__main__":
    DuplicateFiles().compare_all_paths()
