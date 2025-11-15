# DSP Reference for Digital Mode Decoders

This document provides DSP (Digital Signal Processing) reference information for implementing the CW, PSK31, and RTTY decoders in DigiChat.

## Common DSP Concepts

### Sampling and Nyquist Theorem

- **Sample Rate**: 48,000 Hz (48 kHz) is recommended
  - Provides good frequency resolution
  - Standard for most modern sound cards
  - Can represent signals up to 24 kHz (Nyquist frequency)

- **Chunk Size**: 1024 samples recommended
  - Represents ~21ms of audio at 48kHz
  - Good balance between latency and processing efficiency

### Frequency Detection Methods

#### 1. FFT (Fast Fourier Transform)
```python
import numpy as np

def detect_tone_fft(audio_chunk, sample_rate, target_freq, freq_tolerance=50):
    """
    Detect a tone using FFT.

    Args:
        audio_chunk: Audio samples (numpy array)
        sample_rate: Sample rate in Hz
        target_freq: Frequency to detect
        freq_tolerance: Tolerance in Hz

    Returns:
        magnitude: Strength of the signal at target frequency
    """
    # Compute FFT
    fft_result = np.fft.rfft(audio_chunk)
    frequencies = np.fft.rfftfreq(len(audio_chunk), 1/sample_rate)

    # Find magnitude at target frequency
    freq_mask = (frequencies >= target_freq - freq_tolerance) & \
                (frequencies <= target_freq + freq_tolerance)
    magnitude = np.abs(fft_result[freq_mask]).max()

    return magnitude
```

**Pros**:
- Analyzes all frequencies at once
- Well-understood algorithm
- Fast with NumPy

**Cons**:
- Fixed frequency resolution based on chunk size
- Computationally intensive for single-tone detection

#### 2. Goertzel Algorithm
```python
import numpy as np

def goertzel(samples, sample_rate, target_freq):
    """
    Goertzel algorithm for single-frequency detection.
    More efficient than FFT when detecting only one frequency.

    Args:
        samples: Audio samples (numpy array)
        sample_rate: Sample rate in Hz
        target_freq: Frequency to detect

    Returns:
        magnitude: Power at the target frequency
    """
    n = len(samples)
    k = int(0.5 + (n * target_freq) / sample_rate)
    omega = (2.0 * np.pi * k) / n
    coeff = 2.0 * np.cos(omega)

    s1 = 0.0
    s2 = 0.0

    for sample in samples:
        s0 = sample + coeff * s1 - s2
        s2 = s1
        s1 = s0

    power = s1 * s1 + s2 * s2 - coeff * s1 * s2
    return np.sqrt(power / n)
```

**Pros**:
- More efficient than FFT for single tone
- Good frequency resolution
- Less computation

**Cons**:
- Only detects one frequency per run
- Need to run multiple times for multiple tones

**Recommendation**: Use Goertzel for CW and RTTY (single or dual tones). Use FFT for PSK31 (need to see spectrum).

### Filtering

#### Low-Pass Filter (Remove high frequencies)
```python
from scipy import signal

def lowpass_filter(data, cutoff_freq, sample_rate, order=5):
    """
    Apply a Butterworth low-pass filter.

    Args:
        data: Input signal
        cutoff_freq: Cutoff frequency in Hz
        sample_rate: Sample rate in Hz
        order: Filter order (higher = sharper cutoff)

    Returns:
        Filtered signal
    """
    nyquist = sample_rate / 2
    normalized_cutoff = cutoff_freq / nyquist
    b, a = signal.butter(order, normalized_cutoff, btype='low')
    filtered = signal.filtfilt(b, a, data)
    return filtered
```

#### Band-Pass Filter (Keep frequencies in a range)
```python
def bandpass_filter(data, low_freq, high_freq, sample_rate, order=5):
    """
    Apply a Butterworth band-pass filter.

    Args:
        data: Input signal
        low_freq: Low cutoff frequency in Hz
        high_freq: High cutoff frequency in Hz
        sample_rate: Sample rate in Hz
        order: Filter order

    Returns:
        Filtered signal
    """
    nyquist = sample_rate / 2
    low = low_freq / nyquist
    high = high_freq / nyquist
    b, a = signal.butter(order, [low, high], btype='band')
    filtered = signal.filtfilt(b, a, data)
    return filtered
```

## CW (Morse Code) Decoder DSP

### Algorithm Overview

1. **Tone Detection**: Detect presence of carrier tone
2. **Envelope Detection**: Extract amplitude envelope
3. **Timing Analysis**: Measure dit/dah lengths
4. **Character Decoding**: Convert timing to characters

### Implementation Steps

#### Step 1: Tone Detection
```python
def detect_cw_tone(audio_chunk, sample_rate, tone_freq=700, threshold=0.1):
    """
    Detect CW tone using Goertzel algorithm.

    Returns:
        bool: True if tone is present
        float: Signal strength
    """
    magnitude = goertzel(audio_chunk, sample_rate, tone_freq)
    is_present = magnitude > threshold
    return is_present, magnitude
```

#### Step 2: Envelope Detection
```python
def envelope_detection(audio, sample_rate):
    """
    Extract envelope from audio signal.

    Args:
        audio: Input audio signal
        sample_rate: Sample rate

    Returns:
        Envelope of the signal
    """
    # Method 1: Hilbert transform (more accurate)
    from scipy.signal import hilbert
    analytic_signal = hilbert(audio)
    envelope = np.abs(analytic_signal)

    # Method 2: Simple rectify + low-pass (faster)
    # rectified = np.abs(audio)
    # envelope = lowpass_filter(rectified, cutoff_freq=50, sample_rate=sample_rate)

    return envelope
```

#### Step 3: Timing Analysis
```python
class MorseTimingDetector:
    """
    Detect dit/dah timing in Morse code.
    """

    def __init__(self, sample_rate):
        self.sample_rate = sample_rate
        self.state = 'idle'
        self.mark_start = 0
        self.space_start = 0
        self.dit_length = None  # Will be calibrated

    def process_sample(self, is_tone_present, sample_index):
        """
        Process each sample and detect mark/space durations.

        Returns:
            event: 'dit', 'dah', 'char_space', 'word_space', or None
        """
        event = None

        if is_tone_present and self.state == 'idle':
            # Start of mark
            self.state = 'mark'
            self.mark_start = sample_index

        elif not is_tone_present and self.state == 'mark':
            # End of mark
            mark_duration = sample_index - self.mark_start
            self.state = 'space'
            self.space_start = sample_index

            # Determine if dit or dah
            if self.dit_length is None:
                # First mark - assume it's a dit
                self.dit_length = mark_duration
                event = 'dit'
            else:
                # Compare to calibrated dit length
                if mark_duration < self.dit_length * 2:
                    event = 'dit'
                else:
                    event = 'dah'

        elif is_tone_present and self.state == 'space':
            # End of space
            space_duration = sample_index - self.space_start
            self.state = 'mark'
            self.mark_start = sample_index

            # Determine space type
            if space_duration < self.dit_length * 2:
                pass  # Inter-element space (within character)
            elif space_duration < self.dit_length * 5:
                event = 'char_space'  # Between characters
            else:
                event = 'word_space'  # Between words

        return event
```

#### Step 4: Character Decoding
```python
# Morse code lookup table
MORSE_CODE = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D',
    '.': 'E', '..-.': 'F', '--.': 'G', '....': 'H',
    '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L',
    '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P',
    '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X',
    '-.--': 'Y', '--..': 'Z',
    '-----': '0', '.----': '1', '..---': '2', '...--': '3',
    '....-': '4', '.....': '5', '-....': '6', '--...': '7',
    '---..': '8', '----.': '9',
}

class MorseDecoder:
    """Decode Morse code patterns to text."""

    def __init__(self):
        self.current_char = []
        self.decoded_text = []

    def process_event(self, event):
        """Process timing events and decode characters."""
        if event == 'dit':
            self.current_char.append('.')
        elif event == 'dah':
            self.current_char.append('-')
        elif event == 'char_space':
            # Decode current character
            pattern = ''.join(self.current_char)
            char = MORSE_CODE.get(pattern, '?')
            self.decoded_text.append(char)
            self.current_char = []
        elif event == 'word_space':
            # End of character and word
            if self.current_char:
                pattern = ''.join(self.current_char)
                char = MORSE_CODE.get(pattern, '?')
                self.decoded_text.append(char)
                self.current_char = []
            self.decoded_text.append(' ')

    def get_text(self):
        """Get decoded text."""
        return ''.join(self.decoded_text)
```

### CW Key Parameters

- **Tone Frequency**: 400-900 Hz (typically 600-700 Hz)
- **Dit Length**: Varies with WPM
  - 20 WPM ≈ 60ms dit
  - Formula: dit_ms = 1200 / WPM
- **Dah Length**: 3× dit length
- **Inter-element space**: 1× dit length
- **Character space**: 3× dit length
- **Word space**: 7× dit length

## RTTY Decoder DSP

### Algorithm Overview

1. **FSK Demodulation**: Detect mark/space tones
2. **Bit Synchronization**: Find bit boundaries
3. **Baudot Decoding**: Convert bits to characters (using python-baudot)

### Implementation Steps

#### Step 1: Mark/Space Detection
```python
def detect_rtty_tones(audio_chunk, sample_rate,
                      mark_freq=2125, space_freq=2295):
    """
    Detect RTTY mark and space tones.

    Args:
        audio_chunk: Audio samples
        sample_rate: Sample rate
        mark_freq: Mark frequency (typically 2125 Hz)
        space_freq: Space frequency (typically 2295 Hz)

    Returns:
        mark_magnitude: Strength of mark tone
        space_magnitude: Strength of space tone
        bit: 1 for mark, 0 for space
    """
    mark_mag = goertzel(audio_chunk, sample_rate, mark_freq)
    space_mag = goertzel(audio_chunk, sample_rate, space_freq)

    # Determine which tone is stronger
    bit = 1 if mark_mag > space_mag else 0

    return mark_mag, space_mag, bit
```

#### Step 2: Bit Clock Recovery
```python
class RTTYBitSync:
    """
    Bit synchronization for RTTY.
    Finds the optimal sampling points for bits.
    """

    def __init__(self, sample_rate, baud_rate=45.45):
        self.sample_rate = sample_rate
        self.baud_rate = baud_rate
        self.samples_per_bit = int(sample_rate / baud_rate)
        self.phase = 0
        self.bit_buffer = []

    def process_bit(self, bit):
        """
        Process incoming bits and synchronize to bit clock.

        Returns:
            synchronized_bit: Bit at optimal sampling point, or None
        """
        self.phase += 1

        if self.phase >= self.samples_per_bit:
            self.phase = 0
            # Sample bit at this point
            return bit

        return None
```

#### Step 3: Baudot Frame Decoding
```python
class RTTYFrameDecoder:
    """
    Decode RTTY frames (5 data bits + start + stop).
    """

    def __init__(self):
        self.state = 'idle'
        self.bit_count = 0
        self.data_bits = []

    def process_bit(self, bit):
        """
        Process synchronized bits and extract 5-bit Baudot characters.

        RTTY frame format:
        - 1 start bit (space/0)
        - 5 data bits
        - 1.5 stop bits (mark/1)

        Returns:
            baudot_code: 5-bit integer, or None if frame incomplete
        """
        if self.state == 'idle':
            if bit == 0:  # Start bit (space)
                self.state = 'data'
                self.bit_count = 0
                self.data_bits = []

        elif self.state == 'data':
            self.data_bits.append(bit)
            self.bit_count += 1

            if self.bit_count == 5:
                self.state = 'stop'

        elif self.state == 'stop':
            if bit == 1:  # Valid stop bit
                # Convert bits to integer
                baudot_code = sum(b << i for i, b in enumerate(self.data_bits))
                self.state = 'idle'
                return baudot_code
            else:
                # Framing error
                self.state = 'idle'

        return None
```

#### Step 4: Baudot to ASCII (using python-baudot)
```python
from baudot import baudot_decode

class RTTYDecoder:
    """Complete RTTY decoder."""

    def __init__(self, sample_rate=48000, baud_rate=45.45):
        self.bit_sync = RTTYBitSync(sample_rate, baud_rate)
        self.frame_decoder = RTTYFrameDecoder()
        self.baudot_state = 'letters'  # Baudot has letters/figures modes

    def process_audio_chunk(self, audio_chunk, sample_rate):
        """Process audio and return decoded characters."""
        decoded_chars = []

        # Detect mark/space for each sample (or subsample)
        # This is simplified - in practice, you'd process at bit rate
        mark_mag, space_mag, bit = detect_rtty_tones(
            audio_chunk, sample_rate
        )

        # Synchronize to bit clock
        synced_bit = self.bit_sync.process_bit(bit)

        if synced_bit is not None:
            # Decode frame
            baudot_code = self.frame_decoder.process_bit(synced_bit)

            if baudot_code is not None:
                # Use python-baudot library to decode
                # Note: You'll need to handle LTRS/FIGS shifts
                char = self.baudot_to_ascii(baudot_code)
                if char:
                    decoded_chars.append(char)

        return decoded_chars

    def baudot_to_ascii(self, code):
        """Convert Baudot code to ASCII using python-baudot library."""
        # This is a placeholder - use actual python-baudot API
        # The library handles LTRS/FIGS mode switching
        from baudot import ITA2Codec
        codec = ITA2Codec()
        # Decode the code
        return codec.decode_char(code)
```

### RTTY Key Parameters

- **Baud Rates**: 45.45 or 50 baud
- **Shift**: 170 Hz (narrow) or 850 Hz (wide)
- **Mark Frequency**: 2125 Hz (common), or 1445 Hz
- **Space Frequency**: Mark + Shift
- **Frame**: 1 start + 5 data + 1.5 stop bits = 7.5 bits

## PSK31 Decoder DSP

### Algorithm Overview

1. **Carrier Recovery**: Lock onto carrier frequency
2. **BPSK Demodulation**: Detect phase shifts
3. **Symbol Decoding**: Convert phase to bits
4. **Varicode Decoding**: Convert bits to ASCII

### Implementation Steps

#### Step 1: Carrier Recovery (Costas Loop)
```python
class CostasLoop:
    """
    Costas loop for carrier recovery in BPSK.
    This is a simplified version.
    """

    def __init__(self, sample_rate, carrier_freq, loop_bandwidth=100):
        self.sample_rate = sample_rate
        self.carrier_freq = carrier_freq
        self.phase = 0.0
        self.frequency = carrier_freq
        self.alpha = loop_bandwidth / sample_rate  # Loop gain

    def process_sample(self, sample):
        """
        Process one sample and track carrier.

        Returns:
            i_out: In-phase component
            q_out: Quadrature component
        """
        # Generate local oscillator
        i_lo = np.cos(2 * np.pi * self.phase)
        q_lo = -np.sin(2 * np.pi * self.phase)

        # Mix with input
        i_out = sample * i_lo
        q_out = sample * q_lo

        # Phase detector (simplified)
        phase_error = np.sign(i_out) * q_out

        # Update frequency and phase
        self.frequency += self.alpha * phase_error
        self.phase += self.frequency / self.sample_rate
        self.phase = self.phase % 1.0  # Keep in [0, 1)

        return i_out, q_out
```

#### Step 2: Symbol Detection
```python
class PSK31SymbolDetector:
    """
    Detect PSK31 symbols from I/Q data.
    PSK31 uses BPSK with 31.25 baud.
    """

    def __init__(self, sample_rate, baud_rate=31.25):
        self.sample_rate = sample_rate
        self.baud_rate = baud_rate
        self.samples_per_symbol = int(sample_rate / baud_rate)
        self.symbol_buffer = []

    def process_iq(self, i, q):
        """
        Process I/Q samples and detect symbols.

        Returns:
            symbol: 1 or 0, or None if not ready
        """
        self.symbol_buffer.append((i, q))

        if len(self.symbol_buffer) >= self.samples_per_symbol:
            # Average over symbol period
            i_avg = np.mean([s[0] for s in self.symbol_buffer])

            # Determine symbol based on phase
            symbol = 1 if i_avg > 0 else 0

            # Clear buffer
            self.symbol_buffer = []

            return symbol

        return None
```

#### Step 3: Varicode Decoding
```python
# PSK31 Varicode table
VARICODE_TABLE = {
    '00': ' ',      # Space
    '101': 'A',
    '10011': 'B',
    '10111': 'C',
    '10101': 'D',
    '11': 'E',
    '11101': 'F',
    '11111': 'G',
    # ... (full table omitted for brevity)
}

class VaricodeDecoder:
    """
    Decode PSK31 Varicode to ASCII.
    Varicode uses variable-length codes separated by '00'.
    """

    def __init__(self):
        self.bit_buffer = ''

    def process_bit(self, bit):
        """
        Process incoming bits and decode Varicode characters.

        Returns:
            char: Decoded character, or None
        """
        self.bit_buffer += str(bit)

        # Check for character separator (00)
        if self.bit_buffer.endswith('00'):
            # Extract code (remove trailing 00)
            code = self.bit_buffer[:-2]

            # Look up in table
            char = VARICODE_TABLE.get(code, None)

            # Reset buffer
            self.bit_buffer = ''

            return char

        return None
```

### PSK31 Key Parameters

- **Baud Rate**: 31.25 baud
- **Modulation**: BPSK (Binary Phase-Shift Keying)
- **Carrier Frequency**: Typically 1000-2000 Hz
- **Bandwidth**: ~31 Hz
- **Varicode**: Variable-length character encoding

## Performance Optimization

### Using Numba for JIT Compilation
```python
from numba import jit

@jit(nopython=True)
def goertzel_fast(samples, sample_rate, target_freq):
    """JIT-compiled Goertzel for better performance."""
    n = len(samples)
    k = int(0.5 + (n * target_freq) / sample_rate)
    omega = (2.0 * np.pi * k) / n
    coeff = 2.0 * np.cos(omega)

    s1 = 0.0
    s2 = 0.0

    for sample in samples:
        s0 = sample + coeff * s1 - s2
        s2 = s1
        s1 = s0

    power = s1 * s1 + s2 * s2 - coeff * s1 * s2
    return np.sqrt(power / n)
```

### Vectorization with NumPy
Always prefer NumPy array operations over Python loops:

```python
# Slow (Python loop)
result = []
for i in range(len(audio)):
    result.append(audio[i] * 2.0)

# Fast (NumPy vectorization)
result = audio * 2.0
```

## Testing DSP Functions

### Generate Test Tones
```python
def generate_tone(frequency, duration, sample_rate, amplitude=1.0):
    """Generate a test tone for development."""
    t = np.linspace(0, duration, int(sample_rate * duration))
    tone = amplitude * np.sin(2 * np.pi * frequency * t)
    return tone

# Generate 700 Hz CW tone for 0.1 seconds
test_tone = generate_tone(700, 0.1, 48000, 0.5)
```

### Visualize Signals (Outside Curses)
```python
import matplotlib.pyplot as plt

def plot_signal(signal, sample_rate, title="Signal"):
    """Plot audio signal for debugging."""
    t = np.arange(len(signal)) / sample_rate
    plt.figure(figsize=(12, 4))
    plt.plot(t, signal)
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.title(title)
    plt.grid(True)
    plt.show()

def plot_spectrum(signal, sample_rate, title="Spectrum"):
    """Plot frequency spectrum."""
    fft_result = np.fft.rfft(signal)
    frequencies = np.fft.rfftfreq(len(signal), 1/sample_rate)
    magnitude = np.abs(fft_result)

    plt.figure(figsize=(12, 4))
    plt.plot(frequencies, magnitude)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.title(title)
    plt.grid(True)
    plt.xlim(0, 3000)  # Focus on HF digital mode range
    plt.show()
```

## References

- **Digital Signal Processing**: Understanding Digital Signal Processing by Richard Lyons
- **Goertzel Algorithm**: https://en.wikipedia.org/wiki/Goertzel_algorithm
- **Costas Loop**: https://en.wikipedia.org/wiki/Costas_loop
- **PSK31 Specification**: https://www.arrl.org/psk31-spec
- **NumPy DSP Tutorial**: https://realpython.com/python-scipy-fft/
