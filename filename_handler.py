# filename_handler.py

import datetime
import os

def get_common_suffix():
    
    # get the suffix from user input
    return input("choose filename: ")

def create_filename(base_dir, base_name, suffix):
    
    # create the date and format
    date_str = datetime.datetime.now().strftime("%d%m%Y")
    
    # combine the filename
    filename = f"{date_str}_{base_name}_{suffix}.csv"
    
    # return the full path for the file 
    return os.path.join(base_dir, "measurements", filename)
