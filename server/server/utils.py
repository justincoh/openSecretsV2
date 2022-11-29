from pathlib import Path


def list_files_in_dir(dir=""):
    """
    takes in a path string e.g. "./data/states/" and
    returns the names of all files in that directory
    """
    file_names = []
    for f in Path(dir).iterdir():
        file_names.append(f.name)

    return file_names
