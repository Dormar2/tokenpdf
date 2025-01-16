import os


def main():
    # Create .rst from sphinx
    os.system("sphinx-apidoc -o docs/source/ tokenpdf/")
    # Fresh build the docs html
    os.system("sphinx-build -E -b html docs/source/ docs/build/")






if __name__ == "__main__":
    main()