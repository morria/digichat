# DigiChat Implementation Prompt for Claude Code

## Project Goal

Implement DigiChat, a curses-based chat interface for amateur radio digital modes (CW, PSK31, RTTY). The application should provide a modern, Slack-like chat experience for ham radio operators working with digital modes.

## What You're Building

A terminal application that:
1. Captures audio from a sound card connected to an HF radio
2. Decodes digital mode signals (CW/PSK31/RTTY) in real-time
3. Displays decoded messages in a chat-like interface
4. Allows users to send messages by encoding and transmitting digital signals
5. Provides configuration and statistics in a side panel
6. Optionally controls the radio via Hamlib

## User Interface Layout

```
┌────────────────────────────────────────────────────────────────┐
│ DigiChat v0.1.0                     Mode: CW    Freq: 14.070 MHz│
├──────────────────┬─────────────────────────────────────────────┤
│                  │ [Message History - Scrollable]              │
│  Configuration   │                                             │
│  ┌──────────────┐│ 14:23:05 W1ABC: CQ CQ DE W1ABC K           │
│  │ Mode: CW     ││ 14:23:42 K2XYZ: W1ABC DE K2XYZ K           │
│  │ WPM:  20     ││ 14:24:15 W1ABC: K2XYZ DE W1ABC GE OM       │
│  │ Tone: 700 Hz ││ 14:24:58 K2XYZ: W1ABC DE K2XYZ TNX CALL    │
│  └──────────────┘│                                             │
│                  │                                             │
│  Statistics      │                                             │
│  ┌──────────────┐│                                             │
│  │ Signal: ████ ││                                             │
│  │ SNR: 15 dB   ││                                             │
│  │ Decoded: 24  ││                                             │
│  └──────────────┘│                                             │
│                  │                                             │
│  Audio           ├─────────────────────────────────────────────┤
│  ┌──────────────┐│ [Text Input Box]                           │
│  │ Device: 2    ││                                             │
│  │ Rate: 48kHz  ││ > Hello World_                             │
│  └──────────────┘│                                             │
│                  │ F1:Help F2:Config F3:Mode ESC:Quit         │
└──────────────────┴─────────────────────────────────────────────┘
```

## Core Requirements

### 1. Audio Processing
- Use `sounddevice` for real-time audio I/O
- Implement circular buffer for audio data
- Process audio in chunks with minimal latency (<100ms)
- Support configurable sample rates (default 48kHz)

### 2. Digital Mode Decoders

#### CW (Morse Code) - Priority: HIGH
- Implement tone detection using Goertzel algorithm or FFT
- Detect dit/dah timing through envelope detection
- Decode Morse characters from timing patterns
- Auto-detect WPM (words per minute)
- Display decoded text in real-time

**Key Parameters**:
- Tone frequency: 400-900 Hz (default 700 Hz)
- WPM range: 10-40
- Detection threshold: Adjustable

#### PSK31 - Priority: MEDIUM
- Implement BPSK demodulation
- Decode Varicode to ASCII
- Implement AFC (Automatic Frequency Control)
- Handle phase recovery and synchronization

**Key Parameters**:
- Center frequency: Typically 1000-2000 Hz
- Baud rate: 31.25
- Squelch: Adjustable

#### RTTY - Priority: MEDIUM
- Implement FSK demodulation (mark/space detection)
- Use `python-baudot` library for Baudot ↔ ASCII conversion
- Support 45.45 and 50 baud rates
- Support 170 Hz and 850 Hz shifts

**Key Parameters**:
- Mark frequency: 2125 Hz (default)
- Space frequency: 2295 Hz (default, 170 Hz shift)
- Baud rate: 45.45 or 50

### 3. Digital Mode Encoders

Each mode needs encoding capability:
- CW: Generate audio tones with proper timing
- PSK31: Encode text to Varicode, generate phase-modulated audio
- RTTY: Encode text to Baudot, generate FSK audio

### 4. User Interface (Curses)

#### Left Rail (30 columns)
- Mode selector (CW/PSK31/RTTY)
- Mode-specific configuration display
- Real-time statistics:
  - Signal strength
  - SNR (Signal-to-Noise Ratio)
  - Decoded message count
  - Error rate (if applicable)
- Audio device info
- Hamlib status (if enabled)

#### Right Panel (Remainder of screen)
- Message history (scrollable)
  - Timestamp for each message
  - Callsign (if detected)
  - Message text
  - Color coding for different stations
- Text input box at bottom
  - Single line for typing
  - Show cursor position
  - Support basic editing (backspace, arrow keys)

#### Configuration Popup
- Accessible via F2 key
- Modal dialog for settings:
  - Audio device selection
  - Sample rate
  - Mode-specific parameters
  - Hamlib configuration
  - Color scheme
- Save/Cancel buttons

#### Keyboard Shortcuts
- F1: Help screen
- F2: Configuration popup
- F3: Mode selection
- F4: Hamlib control (if enabled)
- ESC: Quit application
- Enter: Send message
- Page Up/Down: Scroll message history
- Tab: Switch between input and history

### 5. Configuration Management
- Load/save configuration from `~/.digichat/config.yaml`
- Command-line argument override
- In-app configuration popup
- Sensible defaults for all settings

### 6. Hamlib Integration (Optional)
- Connect to radio via Hamlib rigctl or Python bindings
- Display current frequency and mode
- Allow frequency changes from UI
- Poll radio status periodically (1 second interval)
- Handle connection failures gracefully

## Implementation Phases

**Start with Phase 1 and Phase 2 to get the foundation working.**

### Phase 1: Core Infrastructure ✓ STARTED
- Audio I/O with sounddevice
- Circular audio buffer
- Basic logging
- Configuration loading

### Phase 2: Basic UI
- Curses framework initialization
- Left rail panel (static display)
- Chat panel with scrolling
- Text input box
- Keyboard handling

### Phase 3: CW Decoder
- Tone detection (Goertzel algorithm)
- Envelope detection
- Timing analysis (dit/dah)
- Character decoding
- Integration with UI

### Phase 4: CW Encoder
- Text to Morse conversion
- Tone generation
- Audio output

### Phase 5: RTTY Implementation
- FSK demodulation
- Baudot decoding (python-baudot)
- UI integration
- Encoder

### Phase 6: PSK31 Implementation
- BPSK demodulation
- Varicode decoding
- AFC implementation
- UI integration
- Encoder

### Phase 7: Hamlib Integration
- Radio control interface
- UI integration
- Status display

### Phase 8: Polish
- Configuration popup
- Help screen
- Error handling
- Testing
- Documentation

## Technical Specifications

### Audio Pipeline
```
Sound Card Input (48kHz)
    ↓
Circular Buffer (2-5 seconds)
    ↓
Chunked Processing (1024 samples)
    ↓
Mode-Specific Decoder
    ↓
Decoded Text
    ↓
Message Display
```

### Threading Model
- Main thread: Curses UI
- Audio input thread: sounddevice callback
- Processing thread: DSP and decoding
- Output thread: Audio generation for TX

### Performance Targets
- Latency: < 100ms from audio to display
- CPU usage: < 25% on modern CPU
- Memory: < 100MB

## File Structure Reference

```
src/digichat/
├── __init__.py
├── cli.py                 # Entry point (already exists)
├── config.py              # Configuration (already exists)
├── ui/
│   ├── app.py            # Main curses application
│   ├── left_rail.py      # Configuration panel
│   ├── chat_panel.py     # Message history and input
│   └── config_popup.py   # Configuration dialog
├── audio/
│   ├── io.py             # Audio I/O wrapper
│   ├── buffer.py         # Circular buffer
│   └── processor.py      # Audio processing pipeline
├── modes/
│   ├── base.py           # Base class for modes
│   ├── cw.py             # CW decoder/encoder
│   ├── psk31.py          # PSK31 decoder/encoder
│   └── rtty.py           # RTTY decoder/encoder
├── hamlib/
│   ├── controller.py     # Radio control
│   └── commands.py       # Command abstractions
└── utils/
    ├── logger.py         # Logging setup
    └── helpers.py        # Utilities
```

## Testing Strategy

### Unit Tests
- Test each decoder with known audio samples
- Test encoders by round-tripping
- Test audio buffer behavior
- Test configuration loading/saving

### Integration Tests
- Test audio pipeline end-to-end
- Test UI rendering (where possible)
- Test mode switching

### Manual Testing
- Record test audio files for each mode
- Test with actual radio (if available)
- Test on different platforms (Linux, macOS, Windows)

## Development Tips

1. **Start Simple**: Get audio I/O working with a simple passthrough before implementing decoders
2. **Use Test Files**: Record or download sample audio files for each mode
3. **Debug Visually**: Use matplotlib to plot signals during development (separate from curses)
4. **Profile Early**: Use cProfile to identify bottlenecks
5. **Incremental Testing**: Test each component independently before integration

## External Resources

### Digital Mode Specifications
- PSK31: https://www.arrl.org/psk31-spec
- RTTY: https://www.rtty.com/
- CW/Morse: Standard ITU-R M.1677-1

### Reference Implementations
- fldigi: http://www.w1hkj.com/ (C++ implementation)
- Direwolf: https://github.com/wb2osz/direwolf (packet radio, similar DSP)

### Library Documentation
- sounddevice: https://python-sounddevice.readthedocs.io/
- NumPy: https://numpy.org/doc/
- SciPy signal processing: https://docs.scipy.org/doc/scipy/reference/signal.html
- Python curses: https://docs.python.org/3/howto/curses.html

## Success Criteria

The implementation is successful when:
1. ✓ Application starts without errors
2. ✓ Curses UI displays correctly
3. Audio can be captured from sound card
4. At least CW mode can decode messages from audio
5. User can type and encode messages for transmission
6. Configuration can be saved and loaded
7. Application handles errors gracefully
8. Code is well-documented and tested

## Getting Started

To begin implementing:
1. Review the IMPLEMENTATION_GUIDE.md for detailed architecture
2. Review LIBRARY_RESEARCH.md for information on dependencies
3. Start with Phase 1: Implement audio I/O (audio/io.py, audio/buffer.py)
4. Move to Phase 2: Implement basic curses UI (ui/app.py)
5. Implement CW decoder as first digital mode
6. Iterate and add features

## Questions to Consider

While implementing, think about:
- How to handle weak signals and noise?
- How to detect when someone stops transmitting?
- How to format messages in the chat panel?
- How to indicate TX vs RX state?
- Should we support recording received audio?
- How to handle multiple simultaneous signals?

Good luck! Start with the foundation and build incrementally. Each component should work independently before integration.
