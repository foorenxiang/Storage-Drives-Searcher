from pathlib import Path
import sys
import os
import json
from icecream import ic

json_path = Path(os.getcwd()) / "catalog.json"
with open(json_path, "r") as fp:
    catalog = json.load(fp)
drive = "Samsung T5"
path_stats = tuple(catalog[drive]["paths_and_stats"])
BIG_FILE_THRESHOLD_IN_MB = 300
megabytes_to_bytes = lambda megabytes: megabytes * (1024 ** 2)
big_file_threshold = megabytes_to_bytes(BIG_FILE_THRESHOLD_IN_MB)
big_files = tuple(
    [stat for stat in path_stats if stat["path_size"] > big_file_threshold]
)
ic(big_files)
repr_ = repr(json_path.stat())

stat_types = [
    "st_mode",
    "st_ino",
    "st_dev",
    "st_nlink",
    "st_uid",
    "st_gid",
    "st_size",
    "st_atime",
    "st_mtime",
    "st_ctime",
]


def stat_value_getter(repr_, stat_item):
    stat_value = repr_.split(stat_item)[1].split(",")[0][1:]
    if stat_value[-1] == ")":
        stat_value = stat_value[:-1]
    return stat_value


stats = {stat_type: stat_value_getter(repr_, stat_type) for stat_type in stat_types}

print(stats)
