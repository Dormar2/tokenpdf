import sys
sys.path.append('.')
import logging
from pathlib import Path
import zipfile
import tarfile
from ghapi.all import GhApi
from tokenpdf.utils.io import download_file

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Platform-specific identifiers for asset names
PLATFORMS = {
    'windows': ['win64'],
    'linux': ['linux-x86_64'],
    'macos': ['.dmg', 'macos']
}

# Repositories to download releases from
REPOS = [
    'https://github.com/linebender/resvg',
    'https://github.com/miyako/console-rsvg-convert'
]


def releases(repo):
    """List of releases for a given repository."""
    api = GhApi()
    owner, repo_name = repo
    releases = api.repos.list_releases(owner, repo_name)
    return releases


def download_path(platform, repo, asset):
    """Download path for a given asset."""
    return Path('bin') / repo[1] / platform / asset['name']


def download_release(release, platform, repo):
    """Assets from a release that match the specified platform."""
    assets = find_release_platform_assets(release, platform)
    for asset in assets:
        logger.info(f"Downloading {asset['name']} for {platform}")
        download_url = asset['browser_download_url']
        path = download_path(platform, repo, asset)
        yield download_file(download_url, path, allow_rename=False)


def find_release_platform_assets(release, platform):
    """Assets from a release that match the specified platform."""
    for asset in release['assets']:
        identifiers = PLATFORMS[platform]
        if any(identifier in asset['name'] for identifier in identifiers):
            yield asset


def unpack(file: Path):
    """Unpack a compressed file and delete the original archive if unpacking is done."""
    file = Path(file)
    if file.suffix == '.zip':
        logger.info(f"Unpacking {file.name} into {file.parent}")
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_ref.extractall(file.parent)
        file.unlink()
    elif file.suffix == '.gz' and tarfile.is_tarfile(file):
        logger.info(f"Unpacking {file.name} into {file.parent}")
        with tarfile.open(file, 'r:gz') as tar_ref:
            tar_ref.extractall(file.parent)
        file.unlink()
    else:
        logger.debug(f"No unpacking needed for {file.name}")


def download_latest(repo_url):
    """Latest release from a repository for all platforms."""
    repo = Path(repo_url).parts[-2:]
    release = releases(repo)[0]
    logger.info(f"Downloading release {release['name']} from {repo}")
    for platform in PLATFORMS:
        files = list(download_release(release, platform, repo))
        for file in files:
            unpack(file)


def main():
    for repo_url in REPOS:
        download_latest(repo_url)


if __name__ == '__main__':
    main()