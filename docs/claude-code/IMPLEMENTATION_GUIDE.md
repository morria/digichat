# DigiChat Implementation Guide for Claude Code

This guide provides comprehensive instructions for implementing DigiChat, a curses-based chat interface for amateur radio digital modes.

## Project Overview

DigiChat is a terminal-based application that enables amateur radio operators to communicate using digital modes (CW, PSK31, RTTY) with a modern chat-like interface. The application:

- Runs entirely in the CLI using Python's curses library
- Processes audio from a sound card connected to an HF radio
- Provides real-time decoding and encoding of digital modes
- Offers optional radio control via Hamlib
- Features a Slack-like interface with configuration rail and chat panel

## Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────┐
│                  DigiChat Application                │
├─────────────────┬───────────────────────────────────┤
│   UI Layer      │  - Curses interface               │
│   (curses)      │  - Left rail (config/stats)       │
│                 │  - Right panel (chat + input)     │
├─────────────────┼───────────────────────────────────┤
│   Application   │  - Message history                │
│   Logic         │  - Mode management                │
│                 │  - Configuration                  │
├─────────────────┼───────────────────────────────────┤
│   DSP Layer     │  - Audio I/O                      │
│                 │  - Digital mode decoders          │
│                 │  - Digital mode encoders          │
├─────────────────┼───────────────────────────────────┤
│   Hardware      │  - Sound card interface           │
│   Interface     │  - Hamlib radio control           │
└─────────────────┴───────────────────────────────────┘
```

### Module Structure

```
src/digichat/
├── __init__.py           # Package initialization
├── cli.py                # CLI entry point and argument parsing
├── config.py             # Configuration management
├── ui/
│   ├── __init__.py
│   ├── app.py            # Main curses application
│   ├── left_rail.py      # Configuration and stats panel
│   ├── chat_panel.py     # Chat history and input
│   └── config_popup.py   # Configuration popup dialog
├── audio/
│   ├── __init__.py
│   ├── io.py             # Audio input/output with sounddevice
│   ├── buffer.py         # Circular audio buffer
│   └── processor.py      # Audio processing pipeline
├── modes/
│   ├── __init__.py
│   ├── base.py           # Base class for digital modes
│   ├── cw.py             # CW (Morse code) decoder/encoder
│   ├── psk31.py          # PSK31 decoder/encoder
│   └── rtty.py           # RTTY decoder/encoder
├── hamlib/
│   ├── __init__.py
│   ├── controller.py     # Hamlib radio control interface
│   └── commands.py       # Radio command abstractions
└── utils/
    ├── __init__.py
    ├── logger.py         # Logging configuration
    └── helpers.py        # Utility functions
```

## Implementation Phases

### Phase 1: Core Infrastructure (Foundation)

**Priority**: Highest
**Complexity**: Medium

**Tasks**:
1. ✅ Set up project structure and dependencies
2. Implement logging system (`utils/logger.py`)
3. Create basic curses UI framework (`ui/app.py`)
4. Implement audio I/O with sounddevice (`audio/io.py`)
5. Create circular audio buffer (`audio/buffer.py`)
6. Write basic tests for audio I/O

**Success Criteria**:
- Application starts and displays curses interface
- Audio can be captured from sound card
- Audio buffer manages data without dropouts

### Phase 2: UI Implementation (User Interface)

**Priority**: High
**Complexity**: Medium

**Tasks**:
1. Implement left rail panel (`ui/left_rail.py`)
   - Configuration display
   - Real-time statistics
   - Mode selection
2. Implement chat panel (`ui/chat_panel.py`)
   - Scrolling message history
   - Text input box
   - Message formatting
3. Create configuration popup (`ui/config_popup.py`)
   - Audio device selection
   - Mode parameters
   - Hamlib settings
4. Implement keyboard shortcuts and navigation
5. Add color themes and styling

**Success Criteria**:
- UI renders correctly with proper layout
- User can navigate with keyboard
- Messages display in chat panel
- Configuration popup is functional

### Phase 3: CW (Morse Code) Implementation

**Priority**: High
**Complexity**: High

**Tasks**:
1. Implement CW decoder (`modes/cw.py`)
   - Tone detection using Goertzel algorithm
   - Envelope detection for dit/dah timing
   - Character decoding from timing
   - Integration with morse-audio-decoder library (optional)
2. Implement CW encoder
   - Text to Morse timing conversion
   - Audio tone generation
   - WPM adjustment
3. Add CW-specific UI elements
   - WPM display
   - Signal strength indicator
   - Tone frequency display
4. Write tests for CW decoder/encoder

**Success Criteria**:
- Decodes CW from audio input accurately
- Encodes text to CW audio output
- Displays decoded messages in chat
- WPM detection is accurate

### Phase 4: PSK31 Implementation

**Priority**: Medium
**Complexity**: Very High

**Tasks**:
1. Implement PSK31 decoder (`modes/psk31.py`)
   - Phase-shift keying demodulation
   - Varicode decoding
   - AFC (Automatic Frequency Control)
   - Squelch implementation
2. Implement PSK31 encoder
   - Varicode encoding
   - Phase modulation
   - Audio generation
3. Add PSK31-specific UI elements
   - Waterfall display (optional, text-based)
   - Signal quality indicator
   - Frequency offset display
4. Write tests for PSK31 decoder/encoder

**Success Criteria**:
- Decodes PSK31 from audio input
- Encodes text to PSK31 audio
- AFC keeps signal locked
- Displays decoded text correctly

### Phase 5: RTTY Implementation

**Priority**: Medium
**Complexity**: High

**Tasks**:
1. Implement RTTY decoder (`modes/rtty.py`)
   - FSK demodulation (mark/space)
   - Baudot code decoding using python-baudot
   - Synchronization and framing
   - Support for 45.45 and 50 baud
2. Implement RTTY encoder
   - Baudot code encoding
   - FSK modulation
   - Audio generation
3. Add RTTY-specific UI elements
   - Mark/space display
   - Shift indicator
   - Baud rate display
4. Write tests for RTTY decoder/encoder

**Success Criteria**:
- Decodes RTTY from audio input
- Encodes text to RTTY audio
- Handles different baud rates
- Displays decoded text correctly

### Phase 6: Hamlib Integration

**Priority**: Low
**Complexity**: Medium

**Tasks**:
1. Implement Hamlib interface (`hamlib/controller.py`)
   - Connect to radio via Hamlib
   - Read frequency, mode, signal strength
   - Set frequency and mode
   - Handle connection errors gracefully
2. Add Hamlib UI integration
   - Display current frequency
   - Display current mode
   - Allow frequency/mode changes
3. Write tests for Hamlib integration

**Success Criteria**:
- Connects to radio via Hamlib
- Displays radio status in UI
- Can control radio from UI
- Handles disconnection gracefully

### Phase 7: Polish and Features

**Priority**: Low
**Complexity**: Low-Medium

**Tasks**:
1. Implement configuration save/load (YAML)
2. Add message logging to file
3. Implement QSO logging
4. Add help system
5. Implement keyboard shortcuts reference
6. Add signal processing enhancements
   - Noise reduction
   - AGC (Automatic Gain Control)
   - Filters
7. Performance optimization
8. Documentation and examples

**Success Criteria**:
- Configuration persists between sessions
- Messages can be logged
- Help is accessible
- Performance is acceptable

## Technical Considerations

### Digital Mode Decoder Details

#### CW (Morse Code)
- **Algorithm**: Goertzel filter for tone detection + envelope detection for timing
- **Libraries**: Consider `morse-audio-decoder` or implement custom
- **Key challenges**:
  - Accurate WPM detection
  - Handling fading and QSB
  - Dealing with hand-sent vs. machine-sent code

#### PSK31
- **Algorithm**: Phase-shift keying demodulation with Varicode
- **Libraries**: May need custom implementation using NumPy/SciPy
- **Key challenges**:
  - Implementing AFC
  - Varicode decoding
  - Phase recovery and synchronization
  - Dealing with weak signals

#### RTTY
- **Algorithm**: FSK demodulation + Baudot decoding
- **Libraries**: `python-baudot` for Baudot code
- **Key challenges**:
  - Mark/space tone detection
  - Synchronization
  - Handling inversion
  - Supporting different shifts (170Hz, 850Hz)

### Performance Requirements

- **Real-time audio processing**: Must process audio with < 100ms latency
- **CPU efficiency**: Use NumPy vectorization and Numba JIT compilation
- **Memory**: Keep audio buffers reasonable (2-5 seconds max)
- **Threading**: Use separate threads for audio I/O and DSP processing

### Testing Strategy

1. **Unit tests**: Test individual decoders with known audio samples
2. **Integration tests**: Test audio pipeline end-to-end
3. **UI tests**: Manual testing of curses interface
4. **Audio test files**: Record or generate test signals for each mode

### Development Tips

1. **Start simple**: Get basic audio I/O working first
2. **Use test files**: Record audio samples for development without radio
3. **Visualize signals**: Use matplotlib for debugging (outside curses)
4. **Profile code**: Use cProfile to find performance bottlenecks
5. **Incremental development**: Get one mode working before moving to next

## Resources

### Library Documentation
- [sounddevice](https://python-sounddevice.readthedocs.io/)
- [NumPy](https://numpy.org/doc/)
- [SciPy](https://docs.scipy.org/)
- [python-baudot](https://github.com/xvillaneau/python-baudot)
- [Hamlib](https://hamlib.github.io/)

### Amateur Radio Resources
- [PSK31 Specification](https://www.arrl.org/psk31-spec)
- [RTTY Information](https://www.rtty.com/)
- [fldigi](http://www.w1hkj.com/) - Reference implementation

### Signal Processing
- [Understanding Digital Signal Processing](https://www.amazon.com/Understanding-Digital-Signal-Processing-3rd/dp/0137027419)
- [DSP Guide](http://www.dspguide.com/)

## Getting Started with Implementation

To begin implementation:

1. Ensure all dependencies are installed: `pip install -e ".[dev,decoders]"`
2. Start with Phase 1: Core Infrastructure
3. Test audio I/O with your sound card
4. Implement basic UI framework
5. Move to Phase 3 (CW) for first digital mode implementation

## Questions and Clarifications

When implementing, consider:
- What audio sample rate to use? (48kHz is standard, but 8kHz might work)
- Should we support full duplex? (Probably yes for future split operation)
- How to handle multiple simultaneous signals? (Start with single signal)
- What's the minimum signal quality we want to decode? (TBD based on testing)
