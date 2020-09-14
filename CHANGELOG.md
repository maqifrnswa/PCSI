# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
 [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.2] - 2020-09-01

### Changed

- Issue #16: Fixed a bug where PCSI would crash if you cancelled loading a file.

## [0.0.1] - 2020-07-26

### Added

- Percent packets sent now shown. Can be over 100% since transmission loops.
- PyInstaller and Appveyor scripts for Windows (version 7+) and MacOS
  (version 10.14+) compiled binaries. Daily builds available at README.md.

 
### Changed

- Issue #8: Enable hardware rts/cts handshaking and ignore data before the first
  start flag. This is now enabled for all serial connections, please report bugs
  if any are found.
- Issue #10: Display the percentage of packets received instead of the
  percentage of pixels.
- Replaced SciPy dependency with OpenCV
- Replaced Richard Taylor pylbfgs with pypi pylbfgs to match lbfgs C api and
  ease installation.

## [0.0.0] - 2020-06-28

### Added

- First release

[Unreleased]: https://github.com/maqifrnswa/PCSI/compare/v0.0.2...HEAD
[0.0.2]: https://github.com/maqifrnswa/PCSI/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/maqifrnswa/PCSI/compare/v0.0.0...v0.0.1
[0.0.0]: https://github.com/maqifrnswa/PCSI/releases/tag/v0.0.0
