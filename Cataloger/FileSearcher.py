from icecream import ic
from SingletonMeta import SingletonMeta
from ReadCatalog import CatalogReader
from fuzzywuzzy import process


class FileSearcher(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.drive_descriptors: dict = CatalogReader().drive_descriptors

    def count_paths(self):
        for drive, descriptor in self.drive_descriptors.items():
            paths = descriptor["paths"]
            print(f"{drive}: ", len(paths), "paths")

    def _match_to_search_term(self, search_term, strings_to_search):
        matches_and_scores = process.extractBests(
            search_term, strings_to_search, score_cutoff=80, limit=50
        )
        return matches_and_scores

    def search(self, search_term):
        print("\n")
        drive_scores = []
        for drive, descriptor in self.drive_descriptors.items():
            catalogued_date = self._get_drive_last_catalogued_date(descriptor)
            paths = self._get_paths_from_drive_descriptor(descriptor)
            self._print_drive_info(drive, catalogued_date)
            matches_and_scores = self._match_to_search_term(search_term, paths)
            matches, scores = [], []
            [
                (matches.append(match_), scores.append(score))
                for match_, score in matches_and_scores
            ]

            self._print_matches(matches_and_scores)
            drive_score = self._score_drive(scores)
            drive_scores.append((drive, drive_score))

        self._guess_most_likely_drive(drive_scores)
        print("Search finished!")

    def _score_drive(self, scores):
        # matches_cutoff = 2
        # if len(scores) >= matches_cutoff:
        #     top_2_scores_in_drive_match = scores[:matches_cutoff]
        #     return sum(top_2_scores_in_drive_match)
        # if len(scores) == 1:
        #     return scores[0] * 1.5
        # return 0
        return sum(scores)

    def _guess_most_likely_drive(self, drive_scores):
        sorted_drive_scores = sorted(drive_scores, key=lambda x: x[1], reverse=True)

        print("Most likely drives:")
        [print(f"{drive}: {score}") for drive, score in sorted_drive_scores]

    def _get_drive_last_catalogued_date(self, descriptor):
        catalogued_date = descriptor["catalogued_date"]
        return catalogued_date

    def _get_paths_from_drive_descriptor(self, descriptor):
        paths = descriptor["paths"]
        return paths

    def _print_matches(self, matches_and_scores):
        ic(matches_and_scores)

    def _print_drive_info(self, drive, catalogued_date):
        print(f"{drive}")
        print("Drive last catalogued at:", catalogued_date)


if __name__ == "__main__":
    FileSearcher().count_paths()

    search_string = input("What would you like to search for?: ")
    FileSearcher().search(search_string)