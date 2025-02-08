import sys
import logging
import os
# Windows...
sys.path.append(".")
from pathlib import Path
from scripts.docs.update import update_docs
from scripts.deploy.requirements import build_requirements

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def newest_file_in_dir(path: Path, suffix: str | None = None) -> Path:
    """Path to the newest file in a directory, optionally filtered by suffix."""
    is_file_with_suffix = (
        lambda x: x.is_file()
        and (suffix is None or x.suffix.lower() == suffix.lower())
    )
    return max(
        [x for x in path.iterdir() if is_file_with_suffix(x)],
        key=lambda x: x.stat().st_mtime,
    )


def main():
    """Build documentation, create a distribution package, and optionally upload to PyPI."""
    logger.info("Building requirements files...")
    build_requirements()
    
    logger.info("Building docs...")
    #update_docs()

    logger.info("Building package...")
    os.system(f"{sys.executable} -m build")

    whl = newest_file_in_dir(Path("dist"), ".whl")
    logger.info(f"Built package: {whl}")

    targz = newest_file_in_dir(Path("dist"), ".gz")
    logger.info(f"Built package: {targz}")

    if "-u" in sys.argv:
        logger.info("Uploading package to PyPI...")
        os.system(f'twine upload "{whl}" "{targz}"')
        logger.info("Uploaded package to PyPI")


if __name__ == "__main__":
    main()