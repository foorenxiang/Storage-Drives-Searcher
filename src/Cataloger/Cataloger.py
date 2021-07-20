import logging
from pathlib import Path
import os
import sys
import glob

sys.path.append(os.getcwd())


logger = logging.getLogger(__name__)


class Cataloger:
    @staticmethod
    def catalog_files(drivepath) -> tuple:
        print(f"Cataloging {drivepath.stem}!")
        paths_and_stats = tuple()
        for path in glob.glob(f"{drivepath}/**/*", recursive=True):
            if Path(path).is_file:
                path_string = str(Path(path).relative_to(drivepath))
                path = Path(drivepath) / path_string
                file_stat = {
                    "path": path_string,
                    "path_size": path.stat().st_size,
                    "path_modified_time": path.stat().st_mtime,
                    "path_accessed_time": path.stat().st_atime,
                }
                paths_and_stats += (file_stat,)
        if not paths_and_stats:
            logger.error("Failed to find files on drive, is it plugged in?")
            sys.exit()
        return paths_and_stats
