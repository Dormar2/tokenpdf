import os
from typing import Tuple
from venv import logger
from setuptools import Distribution
import logging
logger = logging.getLogger(__name__)
def parse_requires(requires: str) -> Tuple[str, str]:
    """ """
    splitters = [">==", "<==", "==", ">=", "<=", ">", "<"]
    for splitter in splitters:
        if splitter in requires:
            return [s.strip() for s in requires.split(splitter)]
    return requires, ""
    

def post_install(distribution: Distribution):
    requires = distribution.get_requires()
    requires = [parse_requires(r)[0] for r in requires]
    if "playwright" in requires:
        errorcode = os.system("playwright install")
        if errorcode != 0:
            logger.warning("Failed to install playwright browser, please run 'playwright install'")
        