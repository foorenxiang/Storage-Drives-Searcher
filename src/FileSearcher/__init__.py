import sys
import os
from fuzzywuzzy import process as fwprocess
from multiprocessing import Process, Queue
from pathlib import Path

sys.path.append(os.getcwd())
from src.Cataloger.CatalogHandler import CatalogHandler
from src.utils.SingletonMeta import SingletonMeta
from src.utils.TimeExecution import time_exec
from src.DriveDisplay import IMAGE_STORE, display_drive_image


def take_cli_input():
    cli_input = " ".join(sys.argv[1:])
    if cli_input:
        print("CLI inputs has been deprecated. Please enter search term here instead:")


class FileSearcher(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.drive_descriptors = CatalogHandler().read_catalogs()

    def print_title(self, title):
        SEPARATOR_CHAR = "#"
        separator = "".join([SEPARATOR_CHAR for _ in title])
        separator_template = f"\n{separator}\n" f"{title}" f"\n{separator}\n"
        print(separator_template)

    def count_paths(self):
        for drive, descriptor in self.drive_descriptors.items():
            catalogued_date = FileSearcher().get_drive_last_catalogued_date(descriptor)
            paths = FileSearcher().get_paths_from_drive_descriptor(descriptor)
            print(
                f"{drive} last catalogued on {catalogued_date} with {len(paths)} paths"
            )
        print()

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
        [
            print(f"{drive}: {score}")
            for drive, score in self.sorted_drive_scores
            if score > 10
        ]

    def _show_top_n_drive_images(self, n=3):
        display_selection = self.sorted_drive_scores[:n][::-1]
        for index, (drive_name, _) in enumerate(display_selection):
            rank = index + 1
            image_path_of_drive = Path(IMAGE_STORE) / f"{drive_name}.HEIC"
            print(image_path_of_drive)
            if image_path_of_drive.exists():
                display_drive_image(image_path_of_drive, rank)
                continue
            print(f"Could not find image for {drive_name}")

    def get_drive_last_catalogued_date(self, descriptor):
        catalogued_date = descriptor["catalogued_date"]
        return catalogued_date

    def get_paths_from_drive_descriptor(self, descriptor):
        paths_and_stats = descriptor["paths_and_stats"]
        paths = [path_and_stat["path"] for path_and_stat in paths_and_stats]
        return paths

    def print_matches_in_drive(self, drive, matches_and_scores):
        if matches_and_scores:
            self.print_title(f"{drive.upper()}")
            [print(match, score) for match, score in matches_and_scores]

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
        self.print_title("Search finished!")

    @staticmethod
    def search_individual_drive(search_term, drive, descriptor, queue):
        paths = FileSearcher().get_paths_from_drive_descriptor(descriptor)
        matches_and_scores = FileSearcher().match_to_search_term(search_term, paths)
        matches, scores = [], []
        [
            (matches.append(match_), scores.append(score))
            for match_, score in matches_and_scores
        ]
        drive_score = FileSearcher().score_drive(scores)
        queue.put((drive, drive_score, matches_and_scores))


@time_exec
def run_search():
    take_cli_input()
    search_term = input("What would you like to search for?: ")
    FileSearcher().print_title(f"Searching for {search_term}\n")
    FileSearcher().count_paths()
    FileSearcher().search_all_drives(search_term)
    FileSearcher()._show_top_n_drive_images()


if __name__ == "__main__":
    run_search()
