# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure with standard Python packaging
- pyproject.toml with dependencies and development tools
- Basic CLI entry point with argument parsing
- Configuration management system
- Comprehensive documentation for Claude Code in `docs/claude-code/`:
  - PROMPT.md: Main implementation prompt
  - IMPLEMENTATION_GUIDE.md: Detailed architecture and roadmap
  - LIBRARY_RESEARCH.md: Analysis of available libraries
  - DSP_REFERENCE.md: DSP algorithms and code examples
  - README.md: Documentation overview
- Architecture documentation in `docs/architecture/`
- Development guide in `docs/DEVELOPMENT.md`
- Contributing guidelines in CONTRIBUTING.md
- Test framework setup with pytest
- Basic configuration tests

### Changed
- Updated README.md with comprehensive project information
- Enhanced .gitignore with DigiChat-specific entries

## [0.1.0] - TBD

### Planned
- Core audio I/O implementation
- Basic curses UI framework
- CW (Morse code) decoder
- CW encoder
- RTTY decoder and encoder
- PSK31 decoder and encoder
- Hamlib integration for radio control
- Configuration popup interface
- Message logging

[Unreleased]: https://github.com/morria/digichat/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/morria/digichat/releases/tag/v0.1.0
