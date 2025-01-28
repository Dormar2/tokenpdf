# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]
### Added
- SVG canvas (multiple files) using svgwrite
- HTML output by embedding the SVGs in an HTML file
- PDF output by converting HTML to PDF using PySide6

### Changed
- Default PDF output to use SVG(svgwrite)->HTML->PDF(PySide6) pipeline instead of reportlab. (Much faster)

## [0.3] - 2025-01-27
### Added
- Redesign of the canvas system, allowing rotated and translated views
- Redo of Image handling, including caching and lazy-loading, with a overall more consistent and efficient approach.
- New token type "stand_sides" and "stand_tops" to replace the older "standing".
- Rotated rects.
- balance_fragments (default: False) value to map configuration, leading to a more balanced sizing of map fragments.


### Changed
- Configuration documentation expanded upon.
- CLI slightly changed: Added -e flag and disallowed empty configuration list without it.
- Moved `__init__.py`'s main function to `__main__.py` to allow for `python -m tokenpdf` execution.

### Fixed
- Relative links in README.md as they are rendered in the readthedocs documentation.

## [0.2.2] - 2025-01-16
### Fixed
- Requirements: Added missing dependencies to setup.py

## [0.2.1] - 2025-01-16
### Added
- Feature: `system_url` configuration key as an alternative to `system`. Downloads and loads the system. As usual, a local path is also supported.
- Documentation: Added extensive configuration reference documentation.

### Changed
- Updated the readme and changelog.


## [0.2] - 2025-01-16
### Added
- Feature: Map fragmentation tokens
- Feature: PDF post-compression
- Feature: Configuration-based cross-product tasks


### Changed
- Improvement: Layout algorithms now sort their outputs to resemble input tokens order.
- Improvement: Automated build+upload
- Improvement: readthedocs-style documentation
- Improvement: google-style docstrings
- Requirement: Python version 3.10

### Fixed
- Bug: Temporary image files are now properly cleaned up.

## [0.1.1] - 2025-01-06
### Fixed
- Bug: Standing token aspect ratio when width > height.


## [0.1.0] - 2025-01-06
### Added
- Initial release of `tokenpdf`.
- Feature: Circular token
- Feature: Standing token
- Feature: Greedy and rectpack layout algorithms
- Feature: Pdf Output