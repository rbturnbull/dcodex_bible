from pathlib import Path
from appdirs import user_cache_dir

import urllib.request


def get_cached_path(filename):
    cache_dir = Path(user_cache_dir("dcodex-bible"))
    path = cache_dir / filename
    path.parent.mkdir(exist_ok=True, parents=True)
    return path



class DownloadError(Exception):
    pass

def cached_download(url: str, filename: (str, Path), force=False) -> Path:
    local_path = get_cached_path(filename)
    cached_download_path(url, get_cached_path(filename), force=force)
    return local_path


def cached_download_path(url: str, local_path: (str, Path), force=False) -> None:
    """
    Downloads a file if a local file does not already exist.

    Args:
        url: The url of the file to download.
        local_path: The local path of where the file should be. If this file isn't there or the file size is zero then this function downloads it to this location.

    Raises:
        Exception: Raises an exception if it cannot download the file.

    """
    local_path = Path(local_path)
    needs_download = force or (not local_path.exists() or local_path.stat().st_size == 0)
    if needs_download:
        try:
            print(f"Downloading {url} to {local_path}")
            urllib.request.urlretrieve(url, local_path)
        except:
            raise DownloadError(f"Error downloading {url}")

    if not local_path.exists() or local_path.stat().st_size == 0:
        raise IOError(f"Error reading {local_path}")


def read_cached_download(url: str, filename: (str, Path), force=False) -> str:
    local_path = cached_download(url, filename, force=force)
    with open(local_path, 'r') as f:
        contents = f.read()
    print(f"File read at {local_path}")
    return contents