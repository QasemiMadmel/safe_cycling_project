# filename_handler.py

import datetime
import os

def get_common_suffix():
    return input("choose filename: ")

def create_filename(base_dir, base_name, suffix):
    date_str = datetime.datetime.now().strftime("%d%m%Y")
    filename = f"{date_str}_{base_name}_{suffix}.csv"
    return os.path.join(base_dir, "measurements", filename)
