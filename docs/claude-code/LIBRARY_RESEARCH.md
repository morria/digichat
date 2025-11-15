# Library Research Summary for DigiChat

This document summarizes the research on available Python libraries for implementing CW, PSK31, and RTTY digital mode decoders.

## CW (Morse Code) Decoders

### Available Libraries

#### 1. morse-audio-decoder (PyPI)
- **Package**: `morse-audio-decoder`
- **Installation**: `pip install morse-audio-decoder`
- **Status**: Available on PyPI
- **Description**: Reads WAV audio files and outputs decoded morse code
- **Pros**:
  - Simple API
  - Ready to use
- **Cons**:
  - May be file-based only (not real-time)
  - Limited documentation

#### 2. PyRSCW
- **Repository**: https://github.com/m0zjo-code/PyRSCW
- **Status**: Open source, active
- **Description**: Python port of RSCW CW decoder for machine-generated CW
- **Dependencies**: NumPy, SciPy, Matplotlib
- **Pros**:
  - Based on proven algorithm (PA3FWM's RSCW)
  - Handles audio files
  - Good for machine-generated CW
- **Cons**:
  - May not handle hand-sent CW well
  - Requires understanding of codebase to integrate

#### 3. pypymorse
- **Repository**: https://github.com/psa-jforestier/pypymorse
- **Status**: Open source
- **Description**: Real-time morse decoder using PyAudio and NCurses
- **Dependencies**: PyAudio, NCurses
- **Pros**:
  - **Already uses NCurses** - very relevant!
  - Real-time audio input from soundcard
  - Designed for live decoding
- **Cons**:
  - May be older code
  - Windows-specific (need to verify Linux compatibility)

#### 4. Deep Learning Approach (AG1LE)
- **Description**: TensorFlow-based CNN-LSTM-CTC model
- **Performance**: 1.5% character error rate, 97.2% word accuracy
- **Training**: 27.8 hours of audio (25,000 WAV files)
- **Pros**:
  - State-of-the-art accuracy
  - Handles noise well
- **Cons**:
  - Requires significant resources
  - Need pre-trained model
  - Overkill for simple application

### Recommendation for CW

**Best approach**: Start with **custom implementation** using Goertzel algorithm for tone detection and envelope detection for timing, then optionally integrate `pypymorse` code if needed. The pypymorse project is particularly interesting since it already uses NCurses.

**Fallback**: Use `morse-audio-decoder` if custom implementation proves difficult.

## PSK31 Decoders

### Available Libraries

#### 1. psk31dec
- **Status**: Mentioned but limited information
- **Description**: Library for decoding PSK31 signals
- **Availability**: Unclear if actively maintained

#### 2. GNU Radio
- **Package**: GNU Radio framework
- **Description**: Comprehensive SDR framework with PSK31 support
- **Pros**:
  - Full-featured
  - Well-tested
  - Large community
- **Cons**:
  - **Heavy dependency** - brings in entire SDR framework
  - Complex for simple use case
  - May be overkill

#### 3. Custom Implementation Resources
- **Varicode**: Can be implemented with simple Python dictionary
- **DSP**: NumPy/SciPy have necessary tools
- **Examples**: GNURadio PSK31 decoder blog posts available

### Recommendation for PSK31

**Best approach**: **Custom implementation** using NumPy/SciPy for DSP
- Implement Costas loop for carrier recovery
- Implement Varicode decoder (simple dictionary)
- Use matched filtering for demodulation

**Rationale**: PSK31 is well-documented and the algorithm is not overly complex. A custom implementation keeps dependencies light and gives full control.

## RTTY Decoders

### Available Libraries

#### 1. python-baudot
- **Repository**: https://github.com/xvillaneau/python-baudot
- **Package**: `python-baudot`
- **Status**: Active (last updated March 2023)
- **Python**: 3.7+ with no external dependencies
- **Description**: 5-bit stateful codec for Baudot/ITA2
- **API**:
  ```python
  from baudot import decode_to_str, codecs, handlers
  ```
- **Pros**:
  - **Perfect for our needs**
  - Handles Baudot encoding/decoding
  - No external dependencies
  - Clean API
- **Cons**:
  - Only handles coding, not FSK demodulation

#### 2. GNU Radio RTTY Modules
- **Status**: Available in GNU Radio
- **Description**: Full RTTY support including demodulation
- **Pros**:
  - Complete solution
- **Cons**:
  - Heavy dependency (GNU Radio)

### Recommendation for RTTY

**Best approach**: Use **python-baudot** for Baudot encoding/decoding + **custom FSK demodulator**
- Implement mark/space tone detection (Goertzel or FFT)
- Use python-baudot for character decoding
- Implement synchronization logic

**Rationale**: python-baudot provides exactly what we need for the coding layer. FSK demodulation is straightforward with NumPy/SciPy.

## Audio I/O Libraries

### sounddevice
- **Package**: `sounddevice`
- **Documentation**: https://python-sounddevice.readthedocs.io/
- **Status**: Actively maintained
- **Pros**:
  - Cross-platform
  - Low latency
  - Good callback support for real-time processing
  - PortAudio backend
- **Cons**:
  - Need to handle buffer management

### PyAudio
- **Package**: `pyaudio`
- **Status**: Stable, but less actively maintained
- **Pros**:
  - Well-known
  - PortAudio backend
- **Cons**:
  - More complex API than sounddevice
  - Installation can be tricky on some platforms

### Recommendation
**Use sounddevice** - more modern, better documentation, easier to use.

## Hamlib Integration

### Available Options

#### 1. Python Hamlib Bindings
- **Module**: Hamlib includes Python bindings
- **Installation**: Via system package manager or compiled with Hamlib
- **API**: ctypes wrapper around C library

#### 2. hamlibserver.py
- **Description**: Python3 script for Hamlib server
- **Status**: Available, updated 2022

#### 3. Direct ctypes
- **Description**: Direct ctypes calls to libhamlib
- **Pros**:
  - No additional dependencies beyond Hamlib itself
- **Cons**:
  - Need to handle ctypes calls

### Recommendation for Hamlib

**Best approach**: Use **Python Hamlib bindings** if available, otherwise **subprocess calls** to rigctl
- Python bindings: Direct, efficient
- rigctl: Simple, robust, works everywhere Hamlib is installed

## Summary and Overall Architecture

### Core Dependencies
```toml
dependencies = [
    "numpy>=1.24.0",           # Array processing
    "scipy>=1.10.0",           # Signal processing (FFT, filters)
    "sounddevice>=0.4.6",      # Audio I/O
    "soundfile>=0.12.1",       # Audio file I/O (for testing)
    "numba>=0.57.0",          # JIT compilation for performance
    "windows-curses>=2.3.0; platform_system=='Windows'",  # Windows curses
]

[project.optional-dependencies]
decoders = [
    "python-baudot>=1.0.0",    # RTTY Baudot encoding/decoding
    # morse-audio-decoder is optional, will implement custom CW
    # PSK31 will be custom implementation
]
```

### Implementation Plan by Mode

| Mode   | Decoder                      | Encoder              | Libraries           |
|--------|------------------------------|----------------------|---------------------|
| CW     | Custom (Goertzel + timing)   | Custom (tone gen)    | NumPy, SciPy        |
| PSK31  | Custom (Costas + Varicode)   | Custom (phase mod)   | NumPy, SciPy        |
| RTTY   | Custom FSK + python-baudot   | Custom FSK + baudot  | python-baudot, SciPy|

### Why Custom Implementations?

1. **Lightweight**: Avoid heavy dependencies like GNU Radio
2. **Learning**: Understand the algorithms fully
3. **Control**: Optimize for our specific use case
4. **Integration**: Easier to integrate with curses UI
5. **Maintenance**: Fewer external dependencies to track

### Reference Implementations

We can reference these open-source implementations for algorithms:
- **fldigi**: C++ implementation of all three modes
- **PyRSCW**: CW decoder algorithm
- **pypymorse**: NCurses integration example
- **GNURadio**: PSK31 and RTTY implementations

## Next Steps

1. Implement audio I/O with sounddevice
2. Start with CW decoder (simplest)
3. Test with recorded audio files
4. Move to RTTY (medium complexity)
5. Finally implement PSK31 (most complex)
