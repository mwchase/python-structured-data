import os.path
import subprocess


def untracked_files():
    for file_ in (
        subprocess.run(["hg", "status", "--unknown"], capture_output=True)
        .stdout.decode()
        .split("\n")
    ):
        if file_:
            yield file_[2:]


def backup_files(file_list):
    for file_ in file_list:
        fn, ext = os.path.splitext(file_)
        if ext == ".bak":
            yield fn


def cache_files(file_list):
    for file_ in file_list:
        dirname, fn = os.path.split(file_)
        cache_dir = os.path.join(dirname, "__pycache__")
        prefix = fn + os.extsep
        try:
            cache_files = os.listdir(cache_dir)
        except FileNotFoundError:
            continue
        for cache_file in cache_files:
            if cache_file.startswith(prefix):
                yield os.path.join(cache_dir, cache_file)


for cache_file in cache_files(backup_files(untracked_files())):
    os.remove(cache_file)
