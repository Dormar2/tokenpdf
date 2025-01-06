from setuptools import setup, find_packages

setup(
    name="tokenpdf",  
    version="0.1.1",  
    description="Generate printable PDF files for tabletop RPG tokens",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",  
    url="https://github.com/Dormar2/tokenpdf",  
    author="Dor Marciano",
    author_email="doormarci@gmail.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment :: Role-Playing"
    ],
    packages=find_packages(),  # Automatically discover packages
    python_requires=">=3.7",
    install_requires=[
        "numpy",
        "Pillow",
        "papersize",
        "reportlab",
        "toml",
        "pyyaml",
        "requests",
        "networkx",
        "tqdm",
        "rectpack"
    ],
    entry_points={
        "console_scripts": [
            "tokenpdf=tokenpdf.__init__:main",  # Command-line entry point
        ],
    },
    include_package_data=True,  # Include non-code files listed in MANIFEST.in
)