# Claude Code Documentation for DigiChat

This directory contains comprehensive documentation for implementing DigiChat using Claude Code (AI-assisted development).

## 🚀 NEW: Updated Architecture (2025-11-15)

**Start here for the latest architectural design:**

### [📘 QUICKSTART_ARCHITECTURE.md](../QUICKSTART_ARCHITECTURE.md) - **START HERE!**
**The definitive quick-start guide for implementation.**

This document provides:
- Architecture overview
- Technology stack summary
- Implementation checklist
- Claude Code integration guide
- Quick links to all detailed docs

### [📚 ARCHITECTURE_PLAN.md](../ARCHITECTURE_PLAN.md)
**Complete architectural design (~5000 lines).**

Contains:
- Detailed component architecture
- State management strategy (Redux-like)
- Event-driven communication patterns
- Testing architecture (headless mode + snapshots)
- Logging and observability
- 10-week implementation roadmap

### [🔧 LIBRARY_GUIDE.md](../LIBRARY_GUIDE.md)
**Detailed guide for all libraries (~2000 lines).**

Contains:
- Textual (TUI framework) with examples
- Pypubsub (event system)
- Sounddevice (audio I/O)
- NumPy/SciPy (DSP)
- Structlog (logging)
- Testing tools (pytest + snapshots)

### [📋 DECISIONS_NEEDED.md](../DECISIONS_NEEDED.md)
**Architectural decisions and recommendations.**

Contains:
- Critical decisions to make before implementation
- Options analysis with pros/cons
- Research-backed recommendations
- Decision tracking framework

---

## Original Documentation (Still Useful)

### Documentation Overview

### [PROMPT.md](PROMPT.md) - Start Here!
**The main implementation prompt for Claude Code.**

This is the primary document you should read first. It contains:
- Complete project overview and goals
- UI layout specification
- Core requirements for all features
- Implementation phases (step-by-step guide)
- Technical specifications
- Success criteria

**Use this when**: You're ready to start implementing DigiChat from scratch or continuing implementation.

### [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
**Detailed implementation roadmap and architecture.**

Contains:
- High-level architecture diagrams
- Module structure and responsibilities
- Phase-by-phase implementation plan
- Technical considerations for each digital mode
- Performance requirements
- Development tips and best practices

**Use this when**: You need to understand the overall architecture and plan your implementation approach.

### [LIBRARY_RESEARCH.md](LIBRARY_RESEARCH.md)
**Research on available Python libraries for digital modes.**

Contains:
- Analysis of CW/Morse decoder libraries
- Analysis of PSK31 libraries
- Analysis of RTTY libraries
- Audio I/O library comparison
- Hamlib integration options
- Recommendations for each component

**Use this when**: You need to decide which libraries to use or want to understand why certain libraries were chosen.

### [DSP_REFERENCE.md](DSP_REFERENCE.md)
**DSP algorithms and code examples.**

Contains:
- Common DSP concepts (FFT, Goertzel, filtering)
- CW decoder implementation (tone detection, timing, decoding)
- RTTY decoder implementation (FSK, Baudot, synchronization)
- PSK31 decoder implementation (Costas loop, Varicode)
- Code examples for each algorithm
- Performance optimization techniques
- Testing and visualization code

**Use this when**: You're implementing the DSP code for decoders and need algorithm details and working code examples.

## Quick Start Guide

If you're using Claude Code to implement DigiChat:

1. **Read [PROMPT.md](PROMPT.md)** - Get the complete picture
2. **Skim [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** - Understand the architecture
3. **Reference [DSP_REFERENCE.md](DSP_REFERENCE.md)** - When implementing decoders
4. **Check [LIBRARY_RESEARCH.md](LIBRARY_RESEARCH.md)** - When choosing libraries

## Implementation Phases

Follow these phases in order:

### Phase 1: Core Infrastructure (Start Here!)
- Set up audio I/O with sounddevice
- Implement circular audio buffer
- Create basic logging system
- Test audio capture

**Files to create**:
- `src/digichat/audio/io.py`
- `src/digichat/audio/buffer.py`
- `src/digichat/utils/logger.py`

### Phase 2: Basic UI
- Initialize curses framework
- Create left rail panel
- Create chat panel with scrolling
- Implement text input box
- Add keyboard handling

**Files to create**:
- `src/digichat/ui/app.py`
- `src/digichat/ui/left_rail.py`
- `src/digichat/ui/chat_panel.py`

### Phase 3: CW Decoder
- Implement Goertzel tone detection
- Implement envelope detection
- Implement timing analysis
- Implement character decoding
- Integrate with UI

**Files to create**:
- `src/digichat/modes/base.py`
- `src/digichat/modes/cw.py`

### Phase 4-7: Additional Features
See [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) for details.

## Development Workflow

### 1. Understanding Requirements
Read the prompt and implementation guide to understand what you're building.

### 2. Implementing a Component
- Start with the appropriate phase
- Reference DSP_REFERENCE.md for algorithms
- Write tests as you go
- Test with audio files before using real radio

### 3. Testing
```bash
# Run tests
pytest tests/

# Test with audio file
digichat --audio-file test_cw.wav

# Test with real audio
digichat --audio-device 2
```

### 4. Debugging
- Use logging extensively (log to file when using curses)
- Visualize signals with matplotlib (outside curses)
- Test DSP functions independently
- Use audio test files for reproducible testing

## Key Technologies

- **Python 3.9+**: Modern Python with type hints
- **curses**: Terminal UI framework
- **sounddevice**: Audio I/O (PortAudio wrapper)
- **NumPy**: Array processing and vectorization
- **SciPy**: Signal processing (FFT, filters)
- **Numba**: JIT compilation for performance
- **python-baudot**: RTTY Baudot encoding/decoding

## Testing Resources

### Audio Test Files
Generate or record test files for each mode:
- **CW**: Record or generate Morse code
- **PSK31**: Use fldigi to generate test files
- **RTTY**: Use fldigi or online generators

### Test Signals
Use the test signal generator:
```python
from digichat.utils.test_signals import generate_cw

audio = generate_cw("HELLO WORLD", wpm=20, tone_freq=700, sample_rate=48000)
```

## Common Pitfalls

1. **Audio buffer overruns**: Process audio quickly enough
2. **Curses debugging**: Always log to file, not stdout
3. **DSP performance**: Use NumPy vectorization, not loops
4. **Thread safety**: Protect shared data with locks
5. **Type errors**: Use mypy to catch type issues early

## Getting Help

- Check the [main README](../../../README.md) for general project info
- See [DEVELOPMENT.md](../../DEVELOPMENT.md) for development setup
- Review [test files](../../../tests/) for examples
- Check the existing code in `src/digichat/` for patterns

## Success Metrics

Your implementation is successful when:
- ✓ Application starts without errors
- ✓ UI displays correctly and is navigable
- ✓ Audio can be captured and processed
- ✓ At least one digital mode works (CW recommended first)
- ✓ Configuration can be saved and loaded
- ✓ Code is well-tested and documented

## Next Steps

Ready to implement? Start with:
1. Read [PROMPT.md](PROMPT.md) completely
2. Set up your development environment (see [DEVELOPMENT.md](../../DEVELOPMENT.md))
3. Begin Phase 1: Core Infrastructure
4. Test each component thoroughly
5. Move to Phase 2: Basic UI
6. Continue through the phases

Good luck, and have fun building DigiChat! 73 de DigiChat.
