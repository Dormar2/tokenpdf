""" Creates credits.md file to give proper links to all used libraries and resources. """
import importlib
import importlib.metadata
from pathlib import Path
from collections import defaultdict
from typing import Tuple

ROOT_IN = Path("requirements/source")
SPECIAL_EXTRAS = {
    'main': 'core',
    'intermediate': ['full_base', 'docs', 'dev', 'pdf']
}
OUTPUT = Path("CREDITS.md")

def parse_requires(requires: str) -> Tuple[str, str]:
    """ """
    splitters = [">==", "<==", "==", ">=", "<=", ">", "<"]
    for splitter in splitters:
        if splitter in requires:
            return [s.strip() for s in requires.split(splitter)]
    if '[' in requires:
        requires = requires.split("[")[0].strip()
    return requires, ""

def get_project_url(module_name):
    try:
        
        distribution = importlib.metadata.distribution(module_name)
    except importlib.metadata.PackageNotFoundError:
        return None
    
    def get_metadata(key):
        try:
            return distribution.metadata[key]
        except KeyError:
            return None
    def get_homepage():
        homepage = get_metadata('Home-page')        
        if homepage:
            return homepage
        project_url = get_metadata('Project-URL')
        if project_url:
            if ', ' in project_url:
                return project_url.split(", ")[1]
            return project_url
    def get_license():
        lic = get_metadata('License')
        if lic and len(lic) > 50:
            return None
        return lic
    homepage = get_homepage()
    if isinstance(homepage, list | tuple):
        homepages = [h for h in homepage if h]
        homepage = homepages[0] if homepages else None
    
    return homepage, get_license()

def get_requirements_in(file:Path, extras:dict = None):
    if extras is None:
        extras = {}
    if file.stem in extras:
        return extras[file.stem]
    """Get requirements from a requirements.in file."""
    with file.open() as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    modules = []
    included = []
    print(f"Processing {file}")
    for line in lines:
        if line.startswith("#"):
            continue
        if line.startswith("-r"):
            name = line.split(" ")[1].replace(".in", "")
            _, inner_included = get_requirements_in(ROOT_IN / f"{name}.in", extras)
            if name in SPECIAL_EXTRAS["intermediate"]:
                included.extend(inner_included)
            else:
                included.append(name)
        else:
            modules.append(parse_requires(line)[0])
    extras[file.stem] = (modules, included)
    return modules, included

def get_used_libraries():
    """Get used libraries from the requirements per configuration."""
    lib = {}
    for req_file in ROOT_IN.iterdir():
        if req_file.is_file() and req_file.suffix == ".in":
            get_requirements_in(req_file, lib)
    return lib

def get_urls(used_libraries:dict):
    """Get the URLs of the used libraries."""
    all_libraries = set([ lib for libs, _ in used_libraries.values() for lib in libs])
    urls = {lib: get_project_url(lib) for lib in all_libraries}
    return urls

def get_credits(used_libraries:dict, urls:dict):
    """Get the credits for the used libraries."""
    result = {}
    for config, (libraries, included) in used_libraries.items():
        if not libraries and not included:
            continue
        if config in SPECIAL_EXTRAS["intermediate"]:
            continue
        if config!= SPECIAL_EXTRAS["main"]:
            name = config
            title = f"\\[{config}\\] configuration"
        else:
            name = "main"
            title = "Default Installation"
        rows = []
        result[name] = (title,rows)
        for include in included:
            if include!= SPECIAL_EXTRAS["main"]:
                rows.append(f"- All libraries from \\[{include}\\]")
            else:
                rows.append(f"- All libraries from the default installation")
        for library in libraries:
            url, lic = urls[library]
            if url:
                line = f"- [{library}](<{url}>)"
            else:
                line = f"- {library}"
            if lic:
                line += f" - {lic}"
            rows.append(line)
    return result

def format_credits(credits:dict, output:Path = OUTPUT):
    """Formats the credits to full markdown"""
    pre_order = ['main', 'pdf-rl', 'pdf-qt','pdf-pr', 'pdf-all', 'cpu', 'gpu', 'full', 'full-gpu']
    others = (list(set(credits.keys()) - set(pre_order)))
    others.sort()
    order = pre_order + others
    with output.open("w") as f:
        f.write("# Python libraries used\n")
        for name in order:
            title, rows = credits[name]
            f.write(f"### {title}\n")
            f.write("\n".join(rows))
            f.write("\n\n")


def write_credits():
    """Write the credits to a markdown file."""
    used_libraries = get_used_libraries()
    urls = get_urls(used_libraries)
    credits = get_credits(used_libraries, urls)
    format_credits(credits)


def main():
    """Write the credits to a markdown file."""
    write_credits()

if __name__ == "__main__":
    main()