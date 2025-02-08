import os
import sys
import logging
from pathlib import Path
sys.path.append(".")
from scripts.docs.credits import write_credits
# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def update_docs():
    """Generate .rst files using Sphinx and build the documentation HTML."""
    logger.info("Updating credits.md...")
    write_credits()

    logger.info("Generating .rst files from Sphinx...")
    os.system("sphinx-apidoc -o docs/source/ tokenpdf/")

    logger.info("Building documentation HTML...")
    os.system("sphinx-build -E -b html docs/source/ docs/build/")

def main():
    update_docs()


if __name__ == "__main__":
    main()