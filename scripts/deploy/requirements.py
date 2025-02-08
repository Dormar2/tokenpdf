import sys
import logging
import os
from pathlib import Path

# Add the current directory to the Python path
sys.path.append(".")

REQUIREMENTS_ROOT = Path("requirements/source")
REQUIREMENTS_OUTPUT = Path("requirements")
DOCS_REQ_OUTPUT = Path("docs/requirements.txt")
DOCS_REQ_FILE = "docs.in"

logger = logging.getLogger(__name__)
def build_requirements(root:Path = REQUIREMENTS_ROOT, output:Path = REQUIREMENTS_OUTPUT):
    for req_file in REQUIREMENTS_ROOT.iterdir():
        if req_file.is_file() and req_file.suffix == ".in":
            if req_file.name != DOCS_REQ_FILE:
                output_file = output / f"{req_file.stem}.txt"
            else:
                output_file = DOCS_REQ_OUTPUT
            logger.info(f"Building {req_file.stem}.txt...")
            os.system(f"uv pip compile {req_file} --output-file {output_file}")
            logger.info(f"Built {req_file.stem}.txt")

def main():

    # Logging configuration
    logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    """Build requirements files."""
    build_requirements()
    

if __name__ == "__main__":
    main()