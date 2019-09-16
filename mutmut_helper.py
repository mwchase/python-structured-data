import os.path
import subprocess


def modified_files():
    for file_ in (
        subprocess.run(["hg", "status", "--modified"], capture_output=True)
        .stdout.decode()
        .split("\n")
    ):
        if file_:
            yield file_[2:]


def cache_files(file_list):
    for file_ in file_list:
        dirname, fn = os.path.split(file_)
        cache_dir = os.path.join(dirname, "__pycache__")
        prefix = os.path.splitext(fn)[0] + os.extsep
        try:
            cache_files = os.listdir(cache_dir)
        except FileNotFoundError:
            continue
        for cache_file in cache_files:
            if cache_file.startswith(prefix):
                yield os.path.join(cache_dir, cache_file)


if __name__ == "__main__":
    for cache_file in cache_files(modified_files()):
        print(cache_file)
        os.remove(cache_file)
