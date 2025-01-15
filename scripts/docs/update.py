import os


def main():
    # Create .rst from sphinx
    os.system("sphinx-apidoc -o docs/source/ ./tokenpdf/")
    os.system("sphinx-build -b html docs/source/ docs/build/")






if __name__ == "__main__":
    main()