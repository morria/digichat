# Contributing to DigiChat

Thank you for your interest in contributing to DigiChat! This document provides guidelines for contributing to the project.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions. We welcome contributors from all backgrounds and experience levels.

## How to Contribute

### Reporting Bugs

If you find a bug:
1. Check if it's already reported in [Issues](https://github.com/morria/digichat/issues)
2. If not, create a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (OS, Python version, etc.)
   - Logs if available

### Suggesting Features

Feature requests are welcome! Please:
1. Check if it's already suggested
2. Create an issue describing:
   - The use case
   - How it would work
   - Why it would be valuable
   - Any implementation ideas

### Contributing Code

#### Setup Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/morria/digichat.git
cd digichat

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev,decoders]"

# Create a branch for your work
git checkout -b feature/my-new-feature
```

#### Development Guidelines

1. **Code Style**
   - Follow PEP 8
   - Use Black for formatting (line length: 100)
   - Use isort for import sorting
   - Run ruff for linting
   - Add type hints to all functions

2. **Testing**
   - Write tests for new features
   - Ensure existing tests pass
   - Aim for >80% code coverage
   - Test with different audio devices if possible

3. **Documentation**
   - Update README.md if needed
   - Add docstrings to functions and classes
   - Update relevant docs in `docs/`
   - Include examples for new features

4. **Commit Messages**
   - Use conventional commits format:
     ```
     feat: Add PSK31 decoder
     fix: Correct CW timing detection
     docs: Update installation guide
     test: Add tests for RTTY decoder
     ```
   - Keep commits atomic and focused
   - Write clear, descriptive messages

#### Before Submitting

Run these checks:
```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/

# Run tests
pytest

# Check coverage
pytest --cov=digichat --cov-report=term-missing
```

All checks should pass before submitting.

#### Pull Request Process

1. Update CHANGELOG.md with your changes
2. Ensure all tests pass
3. Update documentation
4. Push to your fork
5. Create a pull request with:
   - Clear description of changes
   - Link to related issues
   - Screenshots/examples if applicable
   - Test results

We'll review your PR and may request changes. Please be patient and responsive to feedback.

## Development Priorities

Current priorities (see [Issues](https://github.com/morria/digichat/issues)):
1. Core audio I/O implementation
2. CW decoder
3. Basic curses UI
4. RTTY decoder
5. PSK31 decoder
6. Hamlib integration

## Areas Needing Help

We especially welcome contributions in:
- **Testing**: Real-world testing with different radios and audio interfaces
- **Documentation**: Tutorials, examples, troubleshooting guides
- **DSP**: Improvements to decoders (noise reduction, AFC, etc.)
- **UI/UX**: Curses interface improvements
- **Platform support**: Testing on macOS, Windows
- **Additional modes**: Other digital modes (e.g., FT8, SSTV)

## Questions?

- Open a [Discussion](https://github.com/morria/digichat/discussions)
- Comment on relevant issues
- Email: your.email@example.com

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to DigiChat! 73 de DigiChat team.
