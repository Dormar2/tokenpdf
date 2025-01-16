# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

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