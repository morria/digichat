# Development Guide

## Setting Up Development Environment

### Prerequisites

- Python 3.9 or higher
- Sound card with input/output
- (Optional) HF radio with sound card interface
- (Optional) Hamlib-compatible radio for CAT control

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/digichat.git
cd digichat
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode with all dependencies:
```bash
pip install -e ".[dev,decoders]"
```

### Running the Application

```bash
# List available audio devices
digichat --list-devices

# Run with specific audio device
digichat --audio-device 2

# Run in debug mode
digichat --debug --log-file /tmp/digichat.log

# Run with Hamlib support
digichat --hamlib --rig-model 1234 --rig-port /dev/ttyUSB0
```

## Project Structure

```
digichat/
├── src/digichat/          # Main source code
│   ├── ui/                # Curses UI components
│   ├── audio/             # Audio I/O and processing
│   ├── modes/             # Digital mode decoders/encoders
│   ├── hamlib/            # Radio control
│   └── utils/             # Utilities
├── tests/                 # Test suite
├── docs/                  # Documentation
│   ├── claude-code/       # Claude Code implementation guides
│   └── architecture/      # Architecture documentation
├── pyproject.toml         # Project configuration
└── README.md
```

## Development Workflow

### Code Style

This project uses:
- **Black** for code formatting (line length: 100)
- **Ruff** for linting
- **isort** for import sorting
- **mypy** for type checking

Run formatters:
```bash
black src/ tests/
isort src/ tests/
ruff check src/ tests/
mypy src/
```

### Testing

Run tests with pytest:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=digichat --cov-report=html

# Run specific test file
pytest tests/test_audio.py

# Run with verbose output
pytest -v
```

### Type Hints

All new code should include type hints:
```python
from typing import Optional

def process_audio(
    samples: np.ndarray,
    sample_rate: int,
    mode: str = "CW"
) -> Optional[str]:
    """
    Process audio samples and return decoded text.

    Args:
        samples: Audio samples as numpy array
        sample_rate: Sample rate in Hz
        mode: Digital mode ('CW', 'PSK31', or 'RTTY')

    Returns:
        Decoded text, or None if no decode
    """
    pass
```

### Logging

Use the logging module for all debug/info output:
```python
import logging

logger = logging.getLogger(__name__)

def my_function():
    logger.debug("Detailed debug information")
    logger.info("Informational message")
    logger.warning("Warning message")
    logger.error("Error message")
```

## Testing with Audio Files

### Recording Test Audio

Record audio for testing without a radio:
```bash
# Using arecord (Linux)
arecord -f S16_LE -r 48000 -c 1 -d 10 test_cw.wav

# Using sox
sox -d -r 48000 -c 1 test_cw.wav trim 0 10
```

### Generating Test Signals

Use the provided utilities to generate test signals:
```python
from digichat.utils.test_signals import generate_cw, generate_psk31, generate_rtty

# Generate CW test signal
audio = generate_cw("HELLO WORLD", wpm=20, tone_freq=700, sample_rate=48000)

# Save to file
import soundfile as sf
sf.write('test_cw.wav', audio, 48000)
```

### Test Audio Sources

For testing without a radio:
- **fldigi**: Can generate audio files for all modes
- **Online generators**: Search for "PSK31 audio generator"
- **Sample files**: Check amateur radio forums for test files

## Debugging

### Debugging DSP Code

1. **Visualize signals** outside of curses:
```python
import matplotlib.pyplot as plt
import numpy as np

# Plot time-domain signal
plt.plot(audio_samples)
plt.show()

# Plot frequency spectrum
fft_result = np.fft.rfft(audio_samples)
frequencies = np.fft.rfftfreq(len(audio_samples), 1/sample_rate)
plt.plot(frequencies, np.abs(fft_result))
plt.show()
```

2. **Save intermediate results**:
```python
# Save filtered audio
import soundfile as sf
sf.write('debug_filtered.wav', filtered_audio, sample_rate)
```

3. **Use assertions**:
```python
assert len(audio_chunk) == 1024, f"Expected 1024 samples, got {len(audio_chunk)}"
assert sample_rate == 48000, "Sample rate must be 48kHz"
```

### Debugging Curses UI

Curses takes over the terminal, making debugging difficult:

1. **Log to file**:
```python
import logging
logging.basicConfig(filename='/tmp/digichat.log', level=logging.DEBUG)
```

2. **Use a second terminal** to tail the log:
```bash
tail -f /tmp/digichat.log
```

3. **Use exceptions** to exit curses and see stack traces:
```python
try:
    # curses code
except Exception as e:
    curses.endwin()  # Restore terminal
    raise
```

## Performance Profiling

### CPU Profiling
```bash
python -m cProfile -o profile.stats -m digichat.cli
python -m pstats profile.stats
# In pstats shell:
# sort time
# stats 10
```

### Memory Profiling
```bash
pip install memory_profiler
python -m memory_profiler digichat/cli.py
```

### Audio Latency Measurement
Add timestamps to measure processing latency:
```python
import time

start = time.time()
# Process audio
decoded = decoder.process(audio_chunk)
latency = (time.time() - start) * 1000  # ms
logger.debug(f"Processing latency: {latency:.1f}ms")
```

## Contributing

### Before Submitting a Pull Request

1. Run the full test suite:
```bash
pytest
```

2. Check code formatting:
```bash
black --check src/ tests/
ruff check src/ tests/
mypy src/
```

3. Update documentation if needed

4. Add tests for new features

5. Update CHANGELOG.md

### Commit Message Format

Use conventional commits:
```
feat: Add PSK31 decoder
fix: Correct CW timing detection
docs: Update installation instructions
test: Add tests for RTTY decoder
refactor: Simplify audio buffer implementation
```

## Architecture Decisions

See [docs/architecture/](architecture/) for detailed architecture documentation:
- [ADR-001: Audio Pipeline](architecture/ADR-001-audio-pipeline.md)
- [ADR-002: UI Framework](architecture/ADR-002-ui-framework.md)
- [ADR-003: Digital Mode Decoders](architecture/ADR-003-decoders.md)

## Resources

### Documentation
- [Implementation Guide](claude-code/IMPLEMENTATION_GUIDE.md) - For Claude Code
- [DSP Reference](claude-code/DSP_REFERENCE.md) - DSP algorithms
- [Library Research](claude-code/LIBRARY_RESEARCH.md) - Library analysis

### Amateur Radio Digital Modes
- [ARRL Digital Modes](https://www.arrl.org/digital)
- [fldigi Documentation](http://www.w1hkj.com/FldigiHelp/)
- [PSK31 Specification](https://www.arrl.org/psk31-spec)

### Python Libraries
- [sounddevice](https://python-sounddevice.readthedocs.io/)
- [NumPy](https://numpy.org/doc/)
- [SciPy Signal Processing](https://docs.scipy.org/doc/scipy/reference/signal.html)
- [Python Curses](https://docs.python.org/3/howto/curses.html)

## Getting Help

- **Issues**: https://github.com/yourusername/digichat/issues
- **Discussions**: https://github.com/yourusername/digichat/discussions
- **Email**: your.email@example.com

## License

MIT License - see [LICENSE](../LICENSE) file for details.
