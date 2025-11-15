# DigiChat

A curses-based chat interface for amateur radio digital modes, designed to run entirely in the CLI with support for CW (Morse code), PSK31, and RTTY.

## Features

- **Digital Mode Support**: CW, PSK31, and RTTY decoding and encoding
- **Slack-like Interface**:
  - Left rail for configuration and real-time statistics
  - Right panel with scrolling message history and text input
- **Sound Card Integration**: Direct audio I/O with your HF radio
- **Optional Hamlib Support**: Control radio frequency, mode, and other settings
- **Configuration Panel**: Popup interface for all settings

## Inspiration

Takes inspiration from fldigi's GUI but keeps the implementation simple and CLI-focused using Python's curses library.

## Installation

### System Dependencies

DigiChat requires PortAudio for audio input/output. Install the development headers for your system:

**Debian/Ubuntu:**
```bash
sudo apt-get update
sudo apt-get install portaudio19-dev python3-dev
```

**Fedora/RHEL:**
```bash
sudo dnf install portaudio-devel python3-devel
```

**Arch Linux:**
```bash
sudo pacman -S portaudio
```

**macOS:**
```bash
brew install portaudio
```

### From Source

```bash
# Clone the repository
git clone https://github.com/morria/digichat.git
cd digichat

# Install system dependencies (automatic detection)
make system-deps

# Install in development mode
make install

# Or install Python packages only (if you've already installed system deps)
pip install -e ".[dev]"
```

### Using pip (when published)

```bash
pip install digichat
```

## Quick Start

```bash
# Run with default settings
digichat

# Run with specific audio device
digichat --audio-device 2

# Run with hamlib support
digichat --hamlib --rig-model 1234 --rig-port /dev/ttyUSB0
```

## Configuration

Configuration is managed through:
1. Command-line arguments
2. Configuration file (`~/.digichat/config.yaml`)
3. In-app configuration popup (accessible via hotkey)

## Development

See [DEVELOPMENT.md](docs/DEVELOPMENT.md) for detailed development instructions and architecture documentation.

### For Claude Code

This project includes comprehensive documentation for AI-assisted development with Claude Code. See the [docs/claude-code/](docs/claude-code/) directory for:

- Implementation guides
- Architecture documentation
- Development workflows

## Requirements

- Python 3.9+
- Sound card with audio input/output
- HF radio transceiver (for actual radio operation)
- Optional: Hamlib-compatible radio for CAT control

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Acknowledgments

- Inspired by [fldigi](http://www.w1hkj.com/)
- Uses concepts from various amateur radio digital mode implementations
- Built for the amateur radio community

## Amateur Radio License

This software is designed for use by licensed amateur radio operators. Please ensure you have the appropriate license for your jurisdiction before transmitting.
