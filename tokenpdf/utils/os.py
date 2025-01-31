import os
import sys
from tempfile import mkstemp
from pathlib import Path

PLATFORM_NAMES = {
    'win32': 'windows',
    'linux': 'linux',
    'darwin': 'macos',
}
PLATFORM_EXECUTABLE_EXTENSIONS = {
    'windows': '.exe',
    'linux': '',
    'macos': '',
}

def get_platform():
    if sys.platform in PLATFORM_NAMES:
        return PLATFORM_NAMES[sys.platform]
    raise ValueError(f"Unsupported platform: {sys.platform}")


def find_executable(repo, name = None, executable_overrides = None, bin_root_override = None):
    if not name:
        name = repo
    platform = get_platform()
    if executable_overrides and repo in executable_overrides:
        return executable_overrides[repo]
    
    def try_root(root):
        executable_path = root / repo / platform / name
        
        path = executable_path.expanduser().absolute()
        path_with_suffix = path.with_suffix(PLATFORM_EXECUTABLE_EXTENSIONS[platform])
        if path_with_suffix.exists():
            return path_with_suffix
        if path.exists():
            return path
        return None

    if bin_root_override:
        path = try_root(bin_root_override)
        if not path:
            raise FileNotFoundError(f"{repo} executable not found in {path}")
        return path
    
    home_path = Path.home() / ".tokenpdf" / "bin"
    code_path = Path(__file__).parent.parent / "bin"
    
    
    if (executable_path_home :=
        try_root(home_path)):
        return executable_path_home
    if (executable_path_code := 
        try_root(code_path)):
        return executable_path_code

    raise FileNotFoundError(f"{repo}'s executable {name} not found in {home_path} or {code_path}")


def unsafe_temp_filepath(suffix=None):
    fd, output_path = mkstemp(suffix=suffix)
    try:
        os.close(fd)
    except Exception:
        pass
    output_path = Path(output_path)
    if output_path.exists():
        output_path.unlink()
    return output_path