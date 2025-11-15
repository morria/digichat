# Architecture Documentation

This directory contains architecture decision records (ADRs) and design documentation for DigiChat.

## Architecture Overview

DigiChat is structured in layers:

```
┌─────────────────────────────────────────┐
│           User Interface (Curses)        │
│  - Left Rail (Config/Stats)              │
│  - Chat Panel (History/Input)            │
│  - Popup Dialogs                         │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│         Application Logic                │
│  - Message Management                    │
│  - Mode Switching                        │
│  - Configuration                         │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│            DSP Layer                     │
│  - Audio Processing Pipeline             │
│  - Digital Mode Decoders                 │
│  - Digital Mode Encoders                 │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│         Hardware Interface               │
│  - Sound Card I/O (sounddevice)          │
│  - Radio Control (Hamlib)                │
└─────────────────────────────────────────┘
```

## Key Design Decisions

### Audio Pipeline
- **Sample Rate**: 48 kHz (standard for modern sound cards)
- **Buffer**: Circular buffer with 2-5 seconds capacity
- **Processing**: Chunk-based (1024 samples per chunk)
- **Threading**: Separate threads for audio I/O and processing

### Digital Modes
- **CW**: Custom implementation using Goertzel algorithm
- **PSK31**: Custom BPSK demodulation with Varicode
- **RTTY**: Custom FSK demodulation + python-baudot library

### User Interface
- **Framework**: Python curses (ncurses)
- **Layout**: Two-panel (left rail + chat)
- **Navigation**: Keyboard-driven
- **Configuration**: Popup modal dialogs

### Dependencies
- **Minimal**: Avoid heavy dependencies like GNU Radio
- **Standard**: Use NumPy/SciPy for DSP
- **Performance**: Use Numba for JIT compilation where needed

## Architecture Decision Records

Future ADRs will document key architecture decisions:
- ADR-001: Audio Pipeline Design
- ADR-002: UI Framework Selection
- ADR-003: Digital Mode Decoder Strategy
- ADR-004: Threading Model
- ADR-005: Configuration Management

## Module Responsibilities

### `digichat.ui`
Responsible for all user interface components using curses.
- Application lifecycle
- Screen layout and rendering
- Keyboard input handling
- Modal dialogs

### `digichat.audio`
Handles all audio input/output and buffering.
- Sound card interface via sounddevice
- Circular audio buffer
- Audio processing pipeline coordination

### `digichat.modes`
Implements digital mode decoders and encoders.
- Base class defining decoder/encoder interface
- Mode-specific implementations (CW, PSK31, RTTY)
- DSP algorithms (Goertzel, FFT, filtering)

### `digichat.hamlib`
Radio control via Hamlib.
- Connection management
- Frequency/mode control
- Status polling

### `digichat.config`
Configuration management.
- Configuration data structures
- YAML serialization
- Command-line argument parsing

### `digichat.utils`
Utility functions and helpers.
- Logging setup
- Test signal generation
- Helper functions

## Data Flow

### Receive Path (RX)
```
Sound Card
    ↓
Audio Input Thread (sounddevice callback)
    ↓
Circular Buffer
    ↓
Processing Thread
    ↓
Mode-Specific Decoder
    ↓
Decoded Text
    ↓
UI Update (add to message history)
```

### Transmit Path (TX)
```
User Input (text field)
    ↓
Mode-Specific Encoder
    ↓
Audio Generation
    ↓
Audio Output Thread
    ↓
Sound Card
```

## Performance Considerations

### Target Latency
- **RX Latency**: < 100ms from audio to display
- **TX Latency**: < 50ms from keypress to audio
- **UI Responsiveness**: < 16ms (60 fps equivalent)

### Optimization Strategies
1. **Vectorization**: Use NumPy operations instead of loops
2. **JIT Compilation**: Use Numba for critical DSP functions
3. **Threading**: Separate audio I/O from processing
4. **Buffering**: Minimize buffer copies

### Memory Usage
- **Target**: < 100MB total
- **Audio Buffers**: 2-5 seconds at 48kHz = ~1MB
- **Message History**: Configurable (default 100 lines)

## Error Handling

### Audio Errors
- Gracefully handle audio device disconnection
- Provide clear error messages
- Allow runtime device switching

### Decoding Errors
- Continue operation on decode failures
- Display '?' for undecodable characters
- Log errors without crashing

### Radio Control Errors
- Handle Hamlib connection failures
- Poll with timeout
- Disable features if radio unavailable

## Testing Strategy

### Unit Tests
- Test individual DSP functions with known inputs
- Test configuration loading/saving
- Test mode switching logic

### Integration Tests
- Test full audio pipeline with test files
- Test UI rendering (where possible)
- Test mode encoders by round-tripping

### Manual Testing
- Test with real audio from radio
- Test on different platforms
- Test with various audio devices
- Test with different radios (Hamlib)

## Future Enhancements

Potential future additions:
- Additional digital modes (FT8, Olivia, etc.)
- Waterfall display (text-based)
- QSO logging integration
- Contest mode
- Macro support
- Network control (remote radio)

## References

- [Python Curses HOWTO](https://docs.python.org/3/howto/curses.html)
- [sounddevice Documentation](https://python-sounddevice.readthedocs.io/)
- [NumPy User Guide](https://numpy.org/doc/stable/user/)
- [SciPy Signal Processing](https://docs.scipy.org/doc/scipy/reference/signal.html)
