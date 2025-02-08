import sys
from setuptools import setup
from setuptools.command.install import install
from pathlib import Path

from importlib import import_module
def post(distribution):
    PROJECT_ROOT = Path(__file__).parent
    sys.path.append(str(PROJECT_ROOT))
    from post_install import post_install
    post_install(distribution)

class Installation(install):
    def run(self):
        install.run(self)
        post(self.distribution)

setup(
    url = "https://github.com/Dormar2/tokenpdf",

    packages = ["tokenpdf"],
    cmdclass={"install": Installation},
    include_package_data = True,
    
)