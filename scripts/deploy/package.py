

import sys
sys.path.append(".")
import os
from pathlib import Path

from scripts.docs.update import main as update_docs

def newest_file_in_dir(path: Path, suffix:str|None=None) -> Path:
    fil = lambda x: x.is_file and ((suffix is None) or (x.suffix.lower() == suffix.lower()))
    return max([x for x in path.iterdir() if fil(x)], 
               key=lambda x: x.stat().st_mtime)


def main():
    print("Building docs...")
    update_docs()
    print("Building package...")
    os.system(f"{sys.executable} -m build")
    whl = newest_file_in_dir(Path("dist"), ".whl")
    print(f"Built package: {whl}")
    if "-u" in sys.argv:
        print("Uploading package to PyPi...")
        os.system(f'twine upload "{whl}"')
        print("Uploaded package to PyPi")
    






if __name__ == "__main__":
    main()