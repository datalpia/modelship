# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- remove constraints on `onnxruntime` for non-Intel Mac environments running on Python 3.11+

## [0.2.2] - 2026-02-15
This minor release ensures compatibility with Python 3.10 to 3.14 and Intel Macs
with latest ONNX Runtime dropping support for both Python 3.10 and Intel Macs.

This support will be a best-effort from now on as long as it can be but expect
Python 3.10 or Intel Mac support to drop in the near future.

### Misc
- add missing authors section in `pyproject.toml`
- update classifiers in `pyproject.toml`

### Changed
- add support for python 3.14
- `onnxruntime` limited to 1.23 for intel mac or python 3.10

## [0.2.1] - 2025-10-16
### Fixed
- defer onnxruntime-web operations to dedicated worker

## [0.2.0] - 2025-10-15
### Added
- model loading indicator for static web application
- footer app credit for static web application

### Changed
- use `halfmoon.css` instead of `water.css` for static web application

### Misc
- vendor static assets for offline usage

## [0.1.0] - 2025-09-28
Initial release of `modelship`.

### Added
- `modelship static` to generate a static web application from an ONNX model

[Unreleased]: https://github.com/datalpia/modelship/compare/0.2.2...HEAD
[0.2.2]: https://github.com/datalpia/modelship/compare/0.2.1...0.2.2
[0.2.1]: https://github.com/datalpia/modelship/compare/0.2.0...0.2.1
[0.2.0]: https://github.com/datalpia/modelship/compare/0.1.0...0.2.0
[0.1.0]: https://github.com/datalpia/modelship/releases/tag/0.1.0
