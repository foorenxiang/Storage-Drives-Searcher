from icecream import ic
import sys
import os
from fuzzywuzzy import process as fwprocess
from multiprocessing import Process, Queue

sys.path.append(os.getcwd())
from SingletonMeta import SingletonMeta
from ReadCatalog import CatalogReader

from pathlib import Path

sys.path.append(os.getcwd())
from Cataloger.DriveDisplay import IMAGE_STORE, display_drive_image


def take_cli_input():
    return " ".join(sys.argv[1:])


class FileSearcher(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.drive_descriptors: dict = CatalogReader().drive_descriptors

    def print_title(self, title):
        SEPARATOR_CHAR = "#"
        separator = "".join([SEPARATOR_CHAR for _ in title])
        separator_template = f"\n{separator}\n" f"{title}" f"\n{separator}\n"
        print(separator_template)

    def count_paths(self):
        for drive, descriptor in self.drive_descriptors.items():
            paths = descriptor["paths"]
            print(f"{drive}: ", len(paths), "paths")
        print("\n")

    def match_to_search_term(self, search_term, strings_to_search):
        matches_and_scores = fwprocess.extractBests(
            search_term, strings_to_search, score_cutoff=80, limit=50
        )
        return matches_and_scores

    def score_drive(self, scores):
        # matches_cutoff = 2
        # if len(scores) >= matches_cutoff:
        #     top_2_scores_in_drive_match = scores[:matches_cutoff]
        #     return sum(top_2_scores_in_drive_match)
        # if len(scores) == 1:
        #     return scores[0] * 1.5
        # return 0
        return sum(scores)

    def guess_most_likely_drive(self, drive_scores):
        self.sorted_drive_scores = sorted(
            drive_scores, key=lambda x: x[1], reverse=True
        )
        self.print_title("Most likely drives:")
        [print(f"{drive}: {score}") for drive, score in self.sorted_drive_scores]

    def _show_top_n_drive_images(self, n=3):
        display_selection = self.sorted_drive_scores[:n]
        for index, drive_name in enumerate(display_selection):
            rank = index + 1
            image_path_of_drive = Path(IMAGE_STORE) / f"{drive_name}.HEIC"
            if image_path_of_drive.exists():
                display_drive_image(image_path_of_drive, rank)
                continue
            print(f"Could not find image for {drive_name}")

    def get_drive_last_catalogued_date(self, descriptor):
        catalogued_date = descriptor["catalogued_date"]
        return catalogued_date

    def get_paths_from_drive_descriptor(self, descriptor):
        paths = descriptor["paths"]
        return paths

    def print_matches_in_drive(self, drive, matches_and_scores):
        self.print_title(f"{drive.upper()}")
        if matches_and_scores:
            [print(match, score) for match, score in matches_and_scores]
            return
        print("No matches found")

    def search_all_drives(self, search_term):
        queue = Queue()
        processes = [
            Process(
                target=FileSearcher().search_individual_drive,
                args=(search_term, drive, descriptor, queue),
            )
            for drive, descriptor in self.drive_descriptors.items()
        ]
        [process.start() for process in processes]
        [process.join() for process in processes]
        process_results = [queue.get() for _ in processes]
        drive_scores = list()
        for result in process_results:
            drive, drive_score, matches_and_scores = result
            FileSearcher().print_matches_in_drive(drive, matches_and_scores)
            drive_scores.append((drive, drive_score))
        FileSearcher().guess_most_likely_drive(drive_scores)
        print("Search finished!")

    @staticmethod
    def search_individual_drive(search_term, drive, descriptor, queue):
        catalogued_date = FileSearcher().get_drive_last_catalogued_date(descriptor)
        print(f"Searching {drive} last catalogued on {catalogued_date}")
        paths = FileSearcher().get_paths_from_drive_descriptor(descriptor)
        matches_and_scores = FileSearcher().match_to_search_term(search_term, paths)
        matches, scores = [], []
        [
            (matches.append(match_), scores.append(score))
            for match_, score in matches_and_scores
        ]
        drive_score = FileSearcher().score_drive(scores)
        queue.put((drive, drive_score, matches_and_scores))


if __name__ == "__main__":
    search_term = take_cli_input() or input("What would you like to search for?: ")
    print(f"Searching for {search_term}\n")
    FileSearcher().count_paths()
    FileSearcher().search_all_drives(search_term)
    FileSearcher()._show_top_n_drive_images()
