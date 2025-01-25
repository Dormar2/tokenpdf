import requests
import mimetypes
from pathlib import Path

def download_file(url: str, file_path: str, allow_rename: bool = False):
    """
    Download a file from a URL to a local path.
    Parameters:
    url (str): The URL to download the file from.
    file_path (str): The path to save the file to. If allow_rename is True, the file's suffix
                        will be changed based on the content type.
    """
    path = Path(file_path)
    response = requests.get(url)
    if response.status_code != 200:
        raise requests.HTTPError(f"Failed to download file from {url} - {response.status_code}")
    if allow_rename:
        content_type = response.headers['content-type']
        extension = mimetypes.guess_extension(content_type, strict=False)
        if extension:
            path = path.with_suffix(extension)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'wb') as f:
        f.write(response.content)
    return path