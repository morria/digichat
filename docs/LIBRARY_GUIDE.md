# DigiChat Library and Technology Guide

**Document Version:** 1.0
**Date:** 2025-11-15

This document provides detailed information about each library and technology used in DigiChat, including installation, usage examples, and best practices.

---

## Table of Contents

1. [UI Framework: Textual](#ui-framework-textual)
2. [Event System: Pypubsub](#event-system-pypubsub)
3. [Audio I/O: Sounddevice](#audio-io-sounddevice)
4. [DSP: NumPy and SciPy](#dsp-numpy-and-scipy)
5. [Logging: Structlog](#logging-structlog)
6. [Testing: Pytest Ecosystem](#testing-pytest-ecosystem)
7. [Configuration: PyYAML](#configuration-pyyaml)
8. [Optional: Hamlib Integration](#optional-hamlib-integration)
9. [Development Tools](#development-tools)

---

## UI Framework: Textual

### Overview

Textual is a modern TUI (Text User Interface) framework for Python that makes it easy to create sophisticated terminal applications with features like:

- React-like component model
- CSS-based styling
- Built-in widgets (buttons, inputs, tables, etc.)
- Mouse support
- Async-first architecture
- Excellent testing support (headless mode + snapshot testing)

**Official Docs:** https://textual.textualize.io/

### Installation

```bash
pip install textual[dev]  # Includes dev tools
```

### Basic Example

```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input
from textual.containers import Container

class SimpleApp(App):
    """A simple Textual app."""

    CSS = """
    Screen {
        layout: grid;
        grid-size: 2;
        grid-rows: 1fr 3fr;
    }

    #sidebar {
        background: $panel;
        border-right: solid $primary;
    }

    #content {
        background: $surface;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="sidebar"):
            yield Static("Sidebar Content")
        with Container(id="content"):
            yield Static("Main Content")
        yield Footer()

if __name__ == "__main__":
    app = SimpleApp()
    app.run()
```

### Key Concepts for DigiChat

#### 1. Reactive Attributes

Textual supports reactive attributes that automatically update the UI:

```python
from textual.reactive import reactive

class StatsWidget(Static):
    """Widget showing stats that update automatically."""

    wpm = reactive(0)
    signal_strength = reactive(0)

    def watch_wpm(self, new_wpm: int) -> None:
        """Called when wpm changes."""
        self.update(f"WPM: {new_wpm}")

    def watch_signal_strength(self, new_strength: int) -> None:
        """Called when signal_strength changes."""
        self.log(f"Signal: {new_strength} dB")
```

#### 2. Message Handling

Textual uses messages for communication between widgets:

```python
from textual.message import Message

class MessageReceived(Message):
    """Message sent when new text is decoded."""

    def __init__(self, text: str, mode: str) -> None:
        super().__init__()
        self.text = text
        self.mode = mode

class ChatPanel(Static):
    """Chat panel that receives messages."""

    def on_message_received(self, message: MessageReceived) -> None:
        """Handle new decoded message."""
        self.add_message(message.text, message.mode)
```

#### 3. Custom Widgets

Create reusable widgets for DigiChat:

```python
from textual.widget import Widget
from textual.widgets import Static
from rich.text import Text

class MessageList(Widget):
    """Scrolling list of messages."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages = []

    def add_message(self, text: str, direction: str, mode: str):
        """Add a message to the list."""
        timestamp = time.strftime("%H:%M:%S")
        self.messages.append({
            "timestamp": timestamp,
            "text": text,
            "direction": direction,
            "mode": mode
        })
        self.refresh()

    def render(self) -> Text:
        """Render the message list."""
        output = Text()
        for msg in self.messages[-100:]:  # Last 100 messages
            prefix = "RX" if msg["direction"] == "rx" else "TX"
            color = "green" if msg["direction"] == "rx" else "blue"
            output.append(f"[{msg['timestamp']}] ", style="dim")
            output.append(f"{prefix}: ", style=color)
            output.append(f"{msg['text']}\n")
        return output
```

### Testing with Textual

#### Headless Mode

```python
# tests/ui/test_app.py
import pytest
from digichat.ui.app import DigiChatApp

@pytest.mark.asyncio
async def test_app_starts():
    """Test that app starts without errors."""
    app = DigiChatApp()
    async with app.run_test() as pilot:
        # App is running in headless mode
        assert app.is_running

        # Simulate user input
        await pilot.press("h")  # Press 'h' key

        # Check state
        assert app.screen is not None
```

#### Snapshot Testing

```bash
# Install snapshot testing plugin
pip install pytest-textual-snapshot
```

```python
# tests/ui/test_snapshots.py
async def test_main_screen(snap_compare):
    """Test main screen layout."""
    app = DigiChatApp()
    assert await snap_compare(app, terminal_size=(80, 24))

async def test_with_messages(snap_compare):
    """Test screen with messages."""
    app = DigiChatApp()
    # Add some test messages
    app.add_message("CQ CQ CQ", "rx", "CW")
    app.add_message("K6XXX", "tx", "CW")
    assert await snap_compare(app)
```

To update snapshots after intentional changes:
```bash
pytest --snapshot-update
```

### Resources

- **Tutorial:** https://textual.textualize.io/tutorial/
- **Widget Gallery:** https://textual.textualize.io/widget_gallery/
- **Textual Devtools:** `textual console` for live debugging
- **Examples:** https://github.com/Textualize/textual/tree/main/examples

---

## Event System: Pypubsub

### Overview

Pypubsub provides a publish-subscribe API to facilitate event-based architecture within a single application. It's perfect for decoupling components.

**Official Docs:** https://pypubsub.readthedocs.io/

### Installation

```bash
pip install pypubsub
```

### Basic Usage

```python
from pubsub import pub

# Define a listener
def on_message_received(text: str, mode: str):
    """Called when a message is received."""
    print(f"[{mode}] {text}")

# Subscribe to topic
pub.subscribe(on_message_received, "decoder.text")

# Publish to topic
pub.sendMessage("decoder.text", text="CQ CQ CQ", mode="CW")
```

### Topic Hierarchy

Pypubsub supports hierarchical topics:

```python
# Subscribe to all audio events
pub.subscribe(on_any_audio_event, "audio")

# Subscribe to only input events
pub.subscribe(on_audio_input, "audio.input")

# Subscribe to only output events
pub.subscribe(on_audio_output, "audio.output")

# Publishing to "audio.input" will trigger both subscribers
pub.sendMessage("audio.input", data=audio_data)
```

### DigiChat Event Channels

```python
# src/digichat/core/events.py
from pubsub import pub
from typing import Callable
import numpy as np

class EventBus:
    """Centralized event bus for DigiChat."""

    # Topic definitions (for documentation)
    TOPICS = {
        "audio.input": "Raw audio input received (np.ndarray)",
        "audio.output": "Audio output requested (np.ndarray)",
        "decoder.text": "Text decoded from audio (str, str)",
        "encoder.text": "Text to encode to audio (str)",
        "mode.changed": "Digital mode changed (str)",
        "hamlib.status": "Radio status update (dict)",
        "hamlib.error": "Hamlib error occurred (str)",
        "config.changed": "Configuration changed (Config)",
    }

    @staticmethod
    def subscribe(topic: str, callback: Callable) -> None:
        """Subscribe to a topic."""
        pub.subscribe(callback, topic)

    @staticmethod
    def unsubscribe(callback: Callable, topic: str) -> None:
        """Unsubscribe from a topic."""
        pub.unsubscribe(callback, topic)

    @staticmethod
    def publish(topic: str, **kwargs) -> None:
        """Publish to a topic."""
        pub.sendMessage(topic, **kwargs)

    @staticmethod
    def clear() -> None:
        """Clear all subscriptions (for testing)."""
        pub.unsubAll()
```

### Example: Decoder Service

```python
# src/digichat/services/decoder_service.py
from digichat.core.events import EventBus
from digichat.modes.base import BaseMode

class DecoderService:
    """Service that decodes audio into text."""

    def __init__(self, mode: BaseMode):
        self.mode = mode

        # Subscribe to audio input
        EventBus.subscribe("audio.input", self.on_audio_input)

        # Subscribe to mode changes
        EventBus.subscribe("mode.changed", self.on_mode_changed)

    def on_audio_input(self, data: np.ndarray):
        """Process incoming audio."""
        text = self.mode.decode(data)
        if text:
            # Publish decoded text
            EventBus.publish("decoder.text", text=text, mode=self.mode.name)

    def on_mode_changed(self, new_mode: str):
        """Handle mode change."""
        # Switch to new decoder
        self.mode = get_mode(new_mode)
```

### Testing with Pypubsub

```python
# tests/core/test_events.py
from digichat.core.events import EventBus

def test_event_publishing():
    """Test that events are published and received."""
    received = []

    def listener(text: str, mode: str):
        received.append((text, mode))

    EventBus.subscribe("decoder.text", listener)
    EventBus.publish("decoder.text", text="SOS", mode="CW")

    assert len(received) == 1
    assert received[0] == ("SOS", "CW")

    # Clean up
    EventBus.clear()
```

### Best Practices

1. **Document topics:** Keep a central registry of all topics
2. **Type hints:** Use type hints for topic parameters
3. **Error handling:** Wrap publish calls in try/except
4. **Testing:** Clear all subscriptions between tests
5. **Debugging:** Log all published events in debug mode

---

## Audio I/O: Sounddevice

### Overview

Sounddevice provides bindings to PortAudio, allowing cross-platform audio I/O with a simple Python API.

**Official Docs:** https://python-sounddevice.readthedocs.io/

### Installation

```bash
pip install sounddevice

# May also need portaudio (system dependency)
# Ubuntu/Debian: sudo apt-get install portaudio19-dev
# macOS: brew install portaudio
# Windows: included in wheel
```

### List Audio Devices

```python
import sounddevice as sd

# List all devices
print(sd.query_devices())

# Get default devices
print("Default input:", sd.default.device[0])
print("Default output:", sd.default.device[1])
```

### Basic Recording/Playback

```python
import sounddevice as sd
import numpy as np

# Record 5 seconds at 48kHz
duration = 5  # seconds
sample_rate = 48000

print("Recording...")
recording = sd.rec(int(duration * sample_rate),
                  samplerate=sample_rate,
                  channels=1,
                  dtype='float32')
sd.wait()  # Wait for recording to finish

print("Playback...")
sd.play(recording, sample_rate)
sd.wait()  # Wait for playback to finish
```

### Callback-Based Streaming (Recommended for DigiChat)

```python
import sounddevice as sd
import numpy as np
from queue import Queue

# Audio queue for inter-thread communication
audio_queue = Queue(maxsize=20)

def audio_callback(indata, outdata, frames, time, status):
    """Audio callback (runs in audio thread)."""
    if status:
        print(f"Audio status: {status}")

    # Put input audio in queue for processing
    audio_queue.put(indata.copy())

    # Get output audio from queue (or silence if empty)
    if not output_queue.empty():
        outdata[:] = output_queue.get()
    else:
        outdata[:] = np.zeros_like(outdata)

# Start stream
stream = sd.Stream(
    samplerate=48000,
    channels=1,
    dtype='float32',
    callback=audio_callback,
    blocksize=1024
)

with stream:
    # Stream is active
    while True:
        # Process audio from queue
        if not audio_queue.empty():
            audio = audio_queue.get()
            # Process audio...
```

### DigiChat Audio Service Pattern

```python
# src/digichat/services/audio_service.py
import sounddevice as sd
import numpy as np
from queue import Queue, Empty
import threading
from digichat.core.events import EventBus

class AudioService:
    """Manages audio I/O and buffering."""

    def __init__(self, sample_rate: int = 48000, block_size: int = 1024):
        self.sample_rate = sample_rate
        self.block_size = block_size

        self.input_queue = Queue(maxsize=20)
        self.output_queue = Queue(maxsize=20)

        self.stream = None
        self.processing_thread = None
        self.running = False

        # Subscribe to audio output requests
        EventBus.subscribe("audio.output", self._on_audio_output_request)

    def start(self):
        """Start audio streaming."""
        self.running = True

        # Start audio stream
        self.stream = sd.Stream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32',
            callback=self._audio_callback,
            blocksize=self.block_size
        )
        self.stream.start()

        # Start processing thread
        self.processing_thread = threading.Thread(target=self._process_audio)
        self.processing_thread.start()

    def stop(self):
        """Stop audio streaming."""
        self.running = False

        if self.stream:
            self.stream.stop()
            self.stream.close()

        if self.processing_thread:
            self.processing_thread.join()

    def _audio_callback(self, indata, outdata, frames, time, status):
        """Audio callback (runs in audio thread)."""
        if status:
            EventBus.publish("audio.error", error=str(status))

        # Queue input for processing
        try:
            self.input_queue.put_nowait(indata.copy())
        except:
            EventBus.publish("audio.overrun")

        # Get output or silence
        try:
            outdata[:] = self.output_queue.get_nowait()
        except Empty:
            outdata[:] = np.zeros_like(outdata)

    def _process_audio(self):
        """Processing thread for input audio."""
        while self.running:
            try:
                audio = self.input_queue.get(timeout=0.1)
                # Publish to event bus
                EventBus.publish("audio.input", data=audio)
            except Empty:
                continue

    def _on_audio_output_request(self, data: np.ndarray):
        """Handle audio output request."""
        try:
            self.output_queue.put_nowait(data)
        except:
            EventBus.publish("audio.underrun")
```

### Testing Audio Service

```python
# tests/services/test_audio_service.py
import pytest
from unittest.mock import Mock, patch
import numpy as np

@patch('sounddevice.Stream')
def test_audio_service_starts(mock_stream):
    """Test audio service starts correctly."""
    service = AudioService()
    service.start()

    assert service.running
    mock_stream.assert_called_once()

    service.stop()
    assert not service.running
```

---

## DSP: NumPy and SciPy

### Overview

NumPy provides array operations, while SciPy adds signal processing algorithms.

**NumPy Docs:** https://numpy.org/doc/
**SciPy Signal Docs:** https://docs.scipy.org/doc/scipy/reference/signal.html

### Installation

```bash
pip install numpy scipy
```

### Common DSP Operations for DigiChat

#### 1. Filtering

```python
from scipy import signal
import numpy as np

def bandpass_filter(data: np.ndarray, lowcut: float, highcut: float,
                   sample_rate: int, order: int = 5) -> np.ndarray:
    """Apply bandpass filter to audio."""
    nyq = 0.5 * sample_rate
    low = lowcut / nyq
    high = highcut / nyq

    sos = signal.butter(order, [low, high], btype='band', output='sos')
    filtered = signal.sosfilt(sos, data)
    return filtered

# Example: Filter for 600 Hz CW tone ±100 Hz
filtered = bandpass_filter(audio, lowcut=500, highcut=700, sample_rate=48000)
```

#### 2. Goertzel Algorithm (Tone Detection)

```python
import numpy as np

def goertzel(samples: np.ndarray, target_freq: float, sample_rate: int) -> float:
    """
    Goertzel algorithm for detecting a specific frequency.
    Returns magnitude of the target frequency.
    """
    N = len(samples)
    k = int(0.5 + (N * target_freq) / sample_rate)
    omega = (2.0 * np.pi * k) / N

    coeff = 2.0 * np.cos(omega)
    q1 = 0.0
    q2 = 0.0

    for sample in samples:
        q0 = coeff * q1 - q2 + sample
        q2 = q1
        q1 = q0

    magnitude = np.sqrt(q1**2 + q2**2 - q1 * q2 * coeff)
    return magnitude

# Example: Detect 600 Hz tone
magnitude = goertzel(audio, target_freq=600, sample_rate=48000)
is_tone_present = magnitude > threshold
```

#### 3. Envelope Detection

```python
from scipy import signal

def envelope_detection(data: np.ndarray, sample_rate: int,
                      cutoff: float = 50) -> np.ndarray:
    """
    Detect envelope of signal (for CW timing detection).
    """
    # Rectify
    rectified = np.abs(data)

    # Low-pass filter
    nyq = 0.5 * sample_rate
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(4, normal_cutoff, btype='low')
    envelope = signal.filtfilt(b, a, rectified)

    return envelope

# Example: Get CW envelope for timing
envelope = envelope_detection(filtered_audio, sample_rate=48000)

# Threshold to get dit/dah timing
threshold = np.mean(envelope) + 2 * np.std(envelope)
timing = envelope > threshold
```

#### 4. FFT (Frequency Analysis)

```python
import numpy as np

def compute_spectrum(data: np.ndarray, sample_rate: int):
    """Compute frequency spectrum."""
    N = len(data)
    fft_result = np.fft.rfft(data)
    freqs = np.fft.rfftfreq(N, 1/sample_rate)
    magnitude = np.abs(fft_result)

    return freqs, magnitude

# Example: Find peak frequency
freqs, magnitude = compute_spectrum(audio, sample_rate=48000)
peak_freq = freqs[np.argmax(magnitude)]
print(f"Peak frequency: {peak_freq} Hz")
```

#### 5. Hilbert Transform (Phase Detection for PSK31)

```python
from scipy import signal

def detect_phase_shifts(data: np.ndarray) -> np.ndarray:
    """Detect phase of signal using Hilbert transform."""
    analytic_signal = signal.hilbert(data)
    phase = np.angle(analytic_signal)
    return phase

# Example: PSK31 phase detection
phase = detect_phase_shifts(filtered_audio)
# Phase shifts indicate bit transitions
```

### Performance Tips

1. **Use vectorization:** Avoid Python loops, use NumPy operations
2. **Pre-allocate arrays:** `np.zeros()` instead of append
3. **Use views, not copies:** Avoid unnecessary `copy()`
4. **Consider numba:** JIT compile hot paths

```python
from numba import jit

@jit(nopython=True)
def fast_goertzel(samples, target_freq, sample_rate):
    """JIT-compiled Goertzel for speed."""
    # Same implementation as above, but much faster
    ...
```

---

## Logging: Structlog

### Overview

Structlog provides structured logging with context binding and multiple output formats.

**Official Docs:** https://www.structlog.org/

### Installation

```bash
pip install structlog
```

### Basic Configuration

```python
# src/digichat/utils/logger.py
import structlog
import logging
import sys

def setup_logging(debug: bool = False, json_output: bool = False):
    """Configure structured logging."""

    # Choose processors based on environment
    if json_output or not sys.stdout.isatty():
        # JSON output for production/headless
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ]
    else:
        # Pretty console output for development
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="%H:%M:%S"),
            structlog.dev.ConsoleRenderer(colors=True)
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.DEBUG if debug else logging.INFO
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
```

### Usage Examples

```python
import structlog

logger = structlog.get_logger(__name__)

# Simple logging
logger.info("application_started")

# Logging with context
logger.info("message_received",
           mode="CW",
           text="CQ CQ CQ",
           wpm=20,
           signal_strength=-75)

# Bind context for all subsequent logs
logger = logger.bind(session_id="abc123", user="K6XXX")
logger.info("mode_changed", old_mode="CW", new_mode="PSK31")
# Output includes session_id and user automatically

# Error logging with exception
try:
    decode_audio(data)
except Exception as e:
    logger.error("decode_failed", exc_info=True, mode="PSK31")
```

### Output Examples

**Development (console):**
```
10:30:45 [info] application_started
10:30:46 [info] message_received mode=CW text="CQ CQ CQ" wpm=20 signal_strength=-75
10:30:47 [info] mode_changed old_mode=CW new_mode=PSK31 session_id=abc123 user=K6XXX
```

**Production/Headless (JSON):**
```json
{"event": "application_started", "level": "info", "timestamp": "2025-11-15T10:30:45.123Z"}
{"event": "message_received", "mode": "CW", "text": "CQ CQ CQ", "wpm": 20, "signal_strength": -75, "level": "info", "timestamp": "2025-11-15T10:30:46.456Z"}
{"event": "mode_changed", "old_mode": "CW", "new_mode": "PSK31", "session_id": "abc123", "user": "K6XXX", "level": "info", "timestamp": "2025-11-15T10:30:47.789Z"}
```

### Integration with Redux Store

```python
# src/digichat/core/middleware.py
import structlog

logger = structlog.get_logger(__name__)

class LoggingMiddleware:
    """Middleware to log all state changes."""

    def __call__(self, store, next, action):
        logger.info("action_dispatched",
                   action_type=action.type,
                   payload=action.payload)

        old_state = store.get_state()
        result = next(action)
        new_state = store.get_state()

        # Log state diff (simplified)
        logger.debug("state_changed",
                    action_type=action.type,
                    message_count=len(new_state.messages),
                    current_mode=new_state.mode.current_mode)

        return result
```

---

## Testing: Pytest Ecosystem

### Core Testing Tools

```bash
pip install pytest pytest-asyncio pytest-cov pytest-mock pytest-textual-snapshot
```

### Pytest Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "-ra",  # Show summary of all test outcomes
    "--cov=src/digichat",  # Coverage for src/digichat
    "--cov-report=html",   # HTML coverage report
    "--cov-report=term-missing",  # Show missing lines
]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]
asyncio_mode = "auto"  # Automatically detect async tests
```

### Fixtures

```python
# tests/conftest.py
import pytest
from digichat.core.store import DigiChatStore
from digichat.core.events import EventBus
from digichat.config import Config

@pytest.fixture
def event_bus():
    """Create a clean event bus for testing."""
    bus = EventBus()
    yield bus
    bus.clear()  # Clean up after test

@pytest.fixture
def store():
    """Create a store with default state."""
    return DigiChatStore(initial_state=get_default_state())

@pytest.fixture
def mock_audio():
    """Generate test audio data."""
    import numpy as np
    sample_rate = 48000
    duration = 1.0  # 1 second
    samples = int(sample_rate * duration)
    # Generate 600 Hz tone
    t = np.linspace(0, duration, samples)
    audio = np.sin(2 * np.pi * 600 * t)
    return audio.astype(np.float32)

@pytest.fixture
def test_config():
    """Create test configuration."""
    return Config(
        audio_device=None,
        sample_rate=48000,
        mode="CW",
        debug=True
    )
```

### Example Test Suite Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests
│   ├── test_modes.py       # Mode decoder/encoder tests
│   ├── test_audio_buffer.py
│   └── test_dsp_utils.py
├── services/                # Service layer tests
│   ├── test_audio_service.py
│   ├── test_decoder_service.py
│   └── test_config_service.py
├── core/                    # Core logic tests
│   ├── test_store.py
│   ├── test_reducers.py
│   └── test_events.py
├── integration/             # Integration tests
│   ├── test_message_flow.py
│   └── test_mode_switching.py
├── ui/                      # UI tests
│   ├── test_snapshots.py
│   └── test_widgets.py
└── fixtures/                # Test data
    ├── cw_sos.wav
    ├── psk31_cq.wav
    └── scenarios/
        └── basic_flow.json
```

---

## Configuration: PyYAML

### Installation

```bash
pip install pyyaml
```

### Example Configuration

```yaml
# ~/.config/digichat/config.yaml
audio:
  input_device: null  # null = default
  output_device: null
  sample_rate: 48000
  block_size: 1024

modes:
  current: CW
  cw:
    wpm: 20
    tone_frequency: 600
  psk31:
    frequency: 1000
    afc_enabled: true
  rtty:
    baud_rate: 45.45
    shift: 170

hamlib:
  enabled: false
  rig_model: null
  rig_port: /dev/ttyUSB0

ui:
  theme: default
  message_history_size: 100
```

### Loading/Saving

```python
import yaml
from pathlib import Path
from dataclasses import dataclass, asdict

@dataclass
class Config:
    audio: dict
    modes: dict
    hamlib: dict
    ui: dict

def load_config(path: Path) -> Config:
    """Load configuration from YAML."""
    if not path.exists():
        return get_default_config()

    with open(path) as f:
        data = yaml.safe_load(f)

    return Config(**data)

def save_config(config: Config, path: Path) -> None:
    """Save configuration to YAML."""
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'w') as f:
        yaml.safe_dump(asdict(config), f, default_flow_style=False)
```

---

## Summary

This guide provides the foundation for all libraries used in DigiChat. Each library was chosen for:

- **Maturity:** Well-maintained and stable
- **Documentation:** Good docs and examples
- **Testing:** Easy to test and mock
- **Community:** Active community and support
- **Claude Code Friendly:** Works well in headless/automated environments

### Quick Reference

| Need | Library | Import |
|------|---------|--------|
| TUI | Textual | `from textual.app import App` |
| Events | Pypubsub | `from pubsub import pub` |
| Audio I/O | Sounddevice | `import sounddevice as sd` |
| DSP | NumPy/SciPy | `import numpy as np` |
| Logging | Structlog | `import structlog` |
| Testing | Pytest | `pytest` command |
| Config | PyYAML | `import yaml` |

**Next Steps:**
1. Install all dependencies: `pip install -e ".[dev]"`
2. Review each library's documentation
3. Run example code to verify setup
4. Begin Phase 1 implementation
