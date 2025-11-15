# DigiChat Architecture Plan

**Document Version:** 1.0
**Date:** 2025-11-15
**Status:** Planning Phase

This document defines the architectural approach for DigiChat, emphasizing testability, maintainability, and ease of development with Claude Code.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Core Architectural Principles](#core-architectural-principles)
3. [Component Architecture](#component-architecture)
4. [Technology Stack](#technology-stack)
5. [State Management Strategy](#state-management-strategy)
6. [Testing Architecture](#testing-architecture)
7. [Logging and Observability](#logging-and-observability)
8. [Development Workflow](#development-workflow)
9. [Open Questions and Decisions](#open-questions-and-decisions)
10. [Implementation Roadmap](#implementation-roadmap)

---

## Executive Summary

DigiChat will be built using a **layered, event-driven architecture** with clear separation of concerns. The application will support both interactive (curses UI) and headless (testable/debuggable) modes from day one.

### Key Design Decisions

- **UI Framework:** Textual (modern alternative to curses with built-in testing support)
- **Event System:** Pypubsub (for decoupled communication between components)
- **State Management:** Redux-like unidirectional data flow pattern
- **Testing:** Snapshot testing + headless mode + unit tests
- **Audio Pipeline:** Queue-based threading architecture with sounddevice

---

## Core Architectural Principles

### 1. Separation of Concerns

```
┌─────────────────────────────────────────────────────┐
│                    UI Layer                          │
│  - Textual widgets (reactive components)            │
│  - View-only logic (rendering)                      │
│  - User input handling                              │
└────────────────────┬────────────────────────────────┘
                     │ Events ↕ State Updates
┌────────────────────┴────────────────────────────────┐
│              Application Core                        │
│  - State management (Redux-like store)              │
│  - Business logic                                   │
│  - Event bus (pub/sub)                              │
└────────────────────┬────────────────────────────────┘
                     │ Commands ↕ Data
┌────────────────────┴────────────────────────────────┐
│              Service Layer                           │
│  - Audio processing service                         │
│  - Mode decoder/encoder service                     │
│  - Hamlib service                                   │
│  - Configuration service                            │
└─────────────────────────────────────────────────────┘
```

### 2. Testability First

- **Headless Mode:** Every component runs without UI
- **Dependency Injection:** All external dependencies are injectable
- **Pure Functions:** Business logic is pure, side effects are isolated
- **Observable State:** Complete state tree accessible for testing

### 3. Event-Driven Communication

- Components communicate via events, not direct calls
- Enables loose coupling and easy testing
- Facilitates headless mode operation
- Makes state changes traceable

### 4. Progressive Enhancement

- Core functionality works without optional features
- Audio works without Hamlib
- Basic UI works without advanced features
- Application degrades gracefully

---

## Component Architecture

### Overview

```
src/digichat/
├── core/                    # Application core (state, events, business logic)
│   ├── __init__.py
│   ├── store.py            # Redux-like state store
│   ├── actions.py          # Action creators
│   ├── reducers.py         # State reducers
│   ├── events.py           # Event definitions and pub/sub setup
│   └── middleware.py       # Store middleware (logging, async, etc.)
│
├── services/               # Service layer (side effects, I/O)
│   ├── __init__.py
│   ├── audio_service.py    # Audio I/O and buffering
│   ├── decoder_service.py  # Digital mode decoding
│   ├── encoder_service.py  # Digital mode encoding
│   ├── hamlib_service.py   # Radio control
│   └── config_service.py   # Configuration management
│
├── modes/                  # Digital mode implementations
│   ├── __init__.py
│   ├── base.py            # Base decoder/encoder interface
│   ├── cw.py              # CW implementation
│   ├── psk31.py           # PSK31 implementation
│   └── rtty.py            # RTTY implementation
│
├── ui/                     # User interface (Textual-based)
│   ├── __init__.py
│   ├── app.py             # Main Textual app
│   ├── screens/           # Screen definitions
│   │   ├── __init__.py
│   │   ├── main.py        # Main chat screen
│   │   └── config.py      # Configuration screen
│   ├── widgets/           # Custom widgets
│   │   ├── __init__.py
│   │   ├── message_list.py
│   │   ├── stats_panel.py
│   │   └── mode_selector.py
│   └── themes.py          # Color schemes and styling
│
├── audio/                  # Audio processing (DSP)
│   ├── __init__.py
│   ├── buffer.py          # Circular audio buffer
│   ├── pipeline.py        # Audio processing pipeline
│   └── utils.py           # DSP utilities
│
├── utils/                  # Utilities
│   ├── __init__.py
│   ├── logger.py          # Structured logging
│   └── helpers.py         # General utilities
│
├── config.py              # Configuration data structures
├── cli.py                 # CLI entry point
└── headless.py            # Headless mode runner (for testing/debugging)
```

### Component Responsibilities

#### 1. Core Layer (`core/`)

**Purpose:** Central nervous system of the application. Manages state and coordinates all activities.

**Key Components:**

- **Store (`store.py`):**
  ```python
  class DigiChatStore:
      """Redux-like state store with middleware support."""

      def __init__(self, initial_state: State):
          self.state: State = initial_state
          self.middleware: List[Middleware] = []
          self.subscribers: List[Callable] = []

      def dispatch(self, action: Action) -> None:
          """Dispatch an action to update state."""

      def subscribe(self, callback: Callable) -> Callable:
          """Subscribe to state changes."""

      def get_state(self) -> State:
          """Get current state (immutable)."""
  ```

- **Actions (`actions.py`):**
  ```python
  @dataclass
  class Action:
      type: str
      payload: Any = None

  # Action creators
  def send_message(text: str) -> Action:
      return Action("SEND_MESSAGE", {"text": text})

  def receive_message(text: str, mode: str) -> Action:
      return Action("RECEIVE_MESSAGE", {"text": text, "mode": mode})

  def change_mode(mode: str) -> Action:
      return Action("CHANGE_MODE", {"mode": mode})
  ```

- **Reducers (`reducers.py`):**
  ```python
  def root_reducer(state: State, action: Action) -> State:
      """Pure function: (state, action) -> new_state"""
      return State(
          messages=message_reducer(state.messages, action),
          mode=mode_reducer(state.mode, action),
          audio=audio_reducer(state.audio, action),
          hamlib=hamlib_reducer(state.hamlib, action),
      )
  ```

- **Events (`events.py`):**
  ```python
  # Event channel definitions using pypubsub
  CHANNELS = {
      "audio.input": "Audio input received",
      "audio.output": "Audio output requested",
      "decoder.text": "Text decoded from audio",
      "encoder.text": "Text to encode to audio",
      "hamlib.status": "Radio status update",
      "ui.command": "UI command issued",
  }

  def publish(channel: str, data: Any) -> None:
      """Publish event to channel."""

  def subscribe(channel: str, callback: Callable) -> None:
      """Subscribe to channel."""
  ```

**Why This Approach:**
- Centralized state makes debugging trivial (inspect state at any point)
- Redux pattern is well-understood and proven
- Pure reducers are easy to test
- Time-travel debugging possible (replay actions)
- Headless mode can observe all state changes

#### 2. Service Layer (`services/`)

**Purpose:** Handles all side effects and external I/O. Services are the only components that interact with hardware, filesystems, or external systems.

**Key Components:**

- **Audio Service (`audio_service.py`):**
  ```python
  class AudioService:
      """Manages audio I/O with threading and queuing."""

      def __init__(self, config: AudioConfig, event_bus: EventBus):
          self.config = config
          self.event_bus = event_bus
          self.input_queue = Queue(maxsize=20)
          self.output_queue = Queue(maxsize=20)

      def start(self) -> None:
          """Start audio streams and processing threads."""

      def stop(self) -> None:
          """Stop audio processing gracefully."""

      def _audio_callback(self, indata, outdata, frames, time, status):
          """Sounddevice callback (runs in audio thread)."""

      def _process_input(self) -> None:
          """Processing thread for input audio."""
          # Get audio from queue
          # Publish to "audio.input" channel

      def _process_output(self) -> None:
          """Processing thread for output audio."""
          # Listen on "audio.output" channel
          # Queue audio for playback
  ```

- **Decoder Service (`decoder_service.py`):**
  ```python
  class DecoderService:
      """Manages digital mode decoders."""

      def __init__(self, event_bus: EventBus):
          self.event_bus = event_bus
          self.current_decoder: Optional[BaseDecoder] = None

          # Subscribe to audio input
          event_bus.subscribe("audio.input", self._on_audio_input)

      def set_mode(self, mode: str) -> None:
          """Switch to different decoder."""

      def _on_audio_input(self, audio_data: np.ndarray) -> None:
          """Process audio input through current decoder."""
          if self.current_decoder:
              text = self.current_decoder.decode(audio_data)
              if text:
                  self.event_bus.publish("decoder.text", text)
  ```

- **Configuration Service (`config_service.py`):**
  ```python
  class ConfigService:
      """Manages configuration persistence."""

      def load_config(self, path: Path) -> Config:
          """Load configuration from YAML."""

      def save_config(self, config: Config, path: Path) -> None:
          """Save configuration to YAML."""

      def get_default_config(self) -> Config:
          """Return default configuration."""
  ```

**Why This Approach:**
- Services are easily mockable for testing
- Clear boundaries for side effects
- Services can be run independently in headless mode
- Easy to swap implementations (e.g., mock audio service)

#### 3. UI Layer (`ui/`)

**Purpose:** Presents state to the user and captures user input. UI is a pure view layer that reacts to state changes.

**Key Design:**
```python
class DigiChatApp(App):
    """Main Textual application."""

    CSS_PATH = "app.css"

    def __init__(self, store: DigiChatStore):
        super().__init__()
        self.store = store

        # Subscribe to state changes
        self.store.subscribe(self._on_state_change)

    def compose(self) -> ComposeResult:
        """Compose the UI layout."""
        yield Header()
        yield Container(
            StatsPanel(id="stats"),
            MessageList(id="messages"),
            Input(id="input"),
        )
        yield Footer()

    def _on_state_change(self, state: State) -> None:
        """React to state changes by updating UI."""
        self.query_one("#messages").update(state.messages)
        self.query_one("#stats").update(state.mode, state.audio)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle user input."""
        self.store.dispatch(send_message(event.value))
        event.input.value = ""
```

**Why Textual Instead of Curses:**
1. **Built-in testing support** - `pytest-textual-snapshot` provides snapshot testing
2. **Async-native** - Works naturally with modern async Python
3. **Reactive components** - React-like component model
4. **CSS styling** - Easier theming than raw curses
5. **Better developer experience** - Excellent documentation and examples
6. **Headless mode** - Run without terminal for testing
7. **Modern** - Actively developed (2024+)

#### 4. Modes Layer (`modes/`)

**Purpose:** Digital mode decoders and encoders. Pure DSP logic.

**Base Interface:**
```python
class BaseMode(ABC):
    """Base class for all digital modes."""

    @abstractmethod
    def decode(self, audio: np.ndarray) -> Optional[str]:
        """Decode audio samples to text."""

    @abstractmethod
    def encode(self, text: str) -> np.ndarray:
        """Encode text to audio samples."""

    @abstractmethod
    def get_config_schema(self) -> dict:
        """Return configuration schema for this mode."""

    @property
    @abstractmethod
    def sample_rate(self) -> int:
        """Required sample rate for this mode."""
```

**Why This Approach:**
- Each mode is independently testable with audio samples
- Easy to add new modes without touching other code
- Decoders/encoders are pure functions (audio in, text out)
- Can be developed and tested without the full application

#### 5. Audio Layer (`audio/`)

**Purpose:** Low-level audio processing and buffering.

**Key Components:**

- **Circular Buffer (`buffer.py`):**
  ```python
  class CircularAudioBuffer:
      """Thread-safe circular buffer for audio samples."""

      def __init__(self, duration_seconds: float, sample_rate: int):
          self.size = int(duration_seconds * sample_rate)
          self.buffer = np.zeros(self.size, dtype=np.float32)
          self.write_pos = 0
          self.lock = threading.Lock()

      def write(self, data: np.ndarray) -> None:
          """Write data to buffer."""

      def read(self, num_samples: int) -> np.ndarray:
          """Read recent samples from buffer."""
  ```

**Why This Approach:**
- Circular buffer prevents memory growth
- Thread-safe for audio callback threads
- Provides sliding window for decoders
- Handles overflow gracefully

---

## Technology Stack

### Core Dependencies

| Component | Library | Version | Justification |
|-----------|---------|---------|---------------|
| **UI Framework** | Textual | ^0.90.0 | Modern TUI with testing support, async-native, React-like |
| **Event Bus** | pypubsub | ^4.0.3 | Mature pub/sub library, simple API, well-tested |
| **Audio I/O** | sounddevice | ^0.5.0 | Clean API, cross-platform, callback-based |
| **DSP** | NumPy | ^2.0.0 | Industry standard for numerical computing |
| **DSP** | SciPy | ^1.14.0 | Signal processing algorithms |
| **Testing** | pytest | ^8.0.0 | Standard Python testing framework |
| **Snapshot Testing** | pytest-textual-snapshot | ^1.1.0 | Textual UI snapshot testing |
| **RTTY Decoding** | python-baudot | ^1.0.0 | Baudot code encoding/decoding |
| **Configuration** | PyYAML | ^6.0.0 | YAML config file support |
| **Logging** | structlog | ^24.0.0 | Structured logging for better debugging |

### Optional Dependencies

| Component | Library | Purpose |
|-----------|---------|---------|
| **Hamlib** | Hamlib (external) | Radio control via CAT protocol |
| **JIT Compilation** | numba | ^0.60.0 | Speed up DSP hot paths |
| **State Visualization** | python-redux (optional) | Redux-style state management helper |

### Development Dependencies

| Tool | Purpose |
|------|---------|
| **Black** | Code formatting |
| **Ruff** | Linting and imports |
| **mypy** | Type checking |
| **pre-commit** | Git hooks |
| **pytest-cov** | Code coverage |
| **pytest-asyncio** | Async test support |
| **pytest-mock** | Mocking support |

### Why These Choices

**Textual over curses:**
- Snapshot testing out of the box
- Headless mode built-in
- Modern async API
- Active development and community
- Better debugging experience

**Pypubsub over custom events:**
- Well-tested and mature
- Simple API
- Thread-safe
- Supports topic hierarchies
- Good documentation

**Structlog over logging:**
- Structured output (JSON) for parsing
- Context binding (attach metadata)
- Better for debugging complex async code
- Plays well with log aggregation tools

---

## State Management Strategy

### State Structure

```python
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class DigitalMode(Enum):
    CW = "cw"
    PSK31 = "psk31"
    RTTY = "rtty"

@dataclass
class Message:
    timestamp: float
    text: str
    direction: str  # "rx" or "tx"
    mode: str
    metadata: dict

@dataclass
class AudioState:
    input_device: Optional[int]
    output_device: Optional[int]
    sample_rate: int
    buffer_size: int
    input_level: float  # 0.0-1.0
    output_level: float  # 0.0-1.0
    is_streaming: bool

@dataclass
class ModeState:
    current_mode: DigitalMode
    cw_wpm: int
    cw_tone_freq: int
    psk31_frequency: int
    rtty_baud_rate: float
    rtty_shift: int

@dataclass
class HamlibState:
    enabled: bool
    connected: bool
    rig_model: Optional[int]
    rig_port: Optional[str]
    frequency: Optional[int]
    mode: Optional[str]
    signal_strength: Optional[int]

@dataclass
class UIState:
    active_screen: str
    message_scroll_position: int
    input_text: str

@dataclass
class AppState:
    """Complete application state."""
    messages: List[Message]
    audio: AudioState
    mode: ModeState
    hamlib: HamlibState
    ui: UIState

    def to_dict(self) -> dict:
        """Serialize state for inspection/debugging."""

    @classmethod
    def from_dict(cls, data: dict) -> 'AppState':
        """Deserialize state (for state persistence)."""
```

### Unidirectional Data Flow

```
User Action (UI) ──────────┐
                           │
Hardware Event ────────────┤
                           │
Timer Event ───────────────┤
                           │
                           ▼
                    ┌──────────────┐
                    │   Dispatch   │
                    │   (Action)   │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  Middleware  │  ◄── Logging, async effects
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Reducers   │  ◄── Pure functions
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  New State   │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Subscribers  │  ◄── UI updates, service reactions
                    └──────────────┘
```

### Middleware for Side Effects

```python
class LoggingMiddleware:
    """Log all actions and state changes."""

    def __call__(self, store, next, action):
        logger.info("action_dispatched", action=action, state_before=store.get_state())
        result = next(action)
        logger.info("state_changed", action=action, state_after=store.get_state())
        return result

class AsyncEffectMiddleware:
    """Handle async side effects (e.g., encoding audio)."""

    def __call__(self, store, next, action):
        result = next(action)

        # Trigger side effects based on action type
        if action.type == "SEND_MESSAGE":
            asyncio.create_task(self._encode_and_transmit(action.payload))
        elif action.type == "CHANGE_MODE":
            asyncio.create_task(self._switch_decoder(action.payload))

        return result
```

### Benefits of This Approach

1. **Predictable:** State changes follow a strict pattern
2. **Debuggable:** Can log/inspect every state change
3. **Testable:** Reducers are pure functions, easy to test
4. **Replayable:** Can record actions and replay them
5. **Time-travel:** Can move backward/forward through states
6. **Serializable:** State can be saved/restored
7. **Headless-friendly:** Can observe state without UI

---

## Testing Architecture

### Multi-Level Testing Strategy

```
┌─────────────────────────────────────────────────┐
│  Level 4: E2E Tests (Full Integration)         │
│  - Real audio files → decoded messages          │
│  - Full application flow in headless mode       │
│  - Snapshot tests of UI states                  │
└─────────────────────────────────────────────────┘
                      ▲
┌─────────────────────────────────────────────────┐
│  Level 3: Integration Tests                     │
│  - Service layer with mocked hardware           │
│  - Event bus message flow                       │
│  - State transitions                            │
└─────────────────────────────────────────────────┘
                      ▲
┌─────────────────────────────────────────────────┐
│  Level 2: Component Tests                       │
│  - Individual widgets                           │
│  - Individual services                          │
│  - Reducers with various actions                │
└─────────────────────────────────────────────────┘
                      ▲
┌─────────────────────────────────────────────────┐
│  Level 1: Unit Tests                            │
│  - Pure DSP functions                           │
│  - Mode decoders/encoders                       │
│  - Utility functions                            │
└─────────────────────────────────────────────────┘
```

### 1. Unit Tests (DSP and Pure Functions)

**Example: Testing CW Decoder**
```python
# tests/modes/test_cw.py
import pytest
import numpy as np
from digichat.modes.cw import CWDecoder

class TestCWDecoder:
    def test_decode_letter_e(self):
        """Test decoding single dit (letter E)."""
        decoder = CWDecoder(sample_rate=48000, wpm=20, tone_freq=600)

        # Generate audio for single dit at 600 Hz
        audio = generate_cw_tone(duration_ms=60, freq=600, sample_rate=48000)

        result = decoder.decode(audio)
        assert result == "E"

    def test_decode_sos(self):
        """Test decoding SOS."""
        decoder = CWDecoder(sample_rate=48000, wpm=20, tone_freq=600)
        audio = load_test_audio("fixtures/cw_sos_20wpm.wav")

        result = decoder.decode(audio)
        assert result == "SOS"

    def test_handles_noise(self):
        """Test decoder with noisy signal."""
        decoder = CWDecoder(sample_rate=48000, wpm=20, tone_freq=600)
        audio = load_test_audio("fixtures/cw_noisy_signal.wav")

        result = decoder.decode(audio)
        assert "SOS" in result  # Should still decode despite noise
```

### 2. Component Tests (Services and Widgets)

**Example: Testing Audio Service**
```python
# tests/services/test_audio_service.py
import pytest
from unittest.mock import Mock, patch
from digichat.services.audio_service import AudioService
from digichat.core.events import EventBus

class TestAudioService:
    def test_publishes_audio_input(self):
        """Test that audio input is published to event bus."""
        event_bus = EventBus()
        service = AudioService(config=mock_audio_config(), event_bus=event_bus)

        # Mock the sounddevice callback
        received_audio = []
        event_bus.subscribe("audio.input", lambda data: received_audio.append(data))

        # Simulate audio callback
        test_audio = np.random.randn(1024)
        service._audio_callback(test_audio, None, 1024, None, None)

        # Process queue
        service._process_input()

        assert len(received_audio) == 1
        np.testing.assert_array_equal(received_audio[0], test_audio)

    @patch('sounddevice.InputStream')
    def test_starts_and_stops_cleanly(self, mock_stream):
        """Test service lifecycle."""
        service = AudioService(config=mock_audio_config(), event_bus=EventBus())

        service.start()
        assert service.is_running

        service.stop()
        assert not service.is_running
        mock_stream.return_value.stop.assert_called_once()
```

### 3. Integration Tests (State Flow)

**Example: Testing Message Flow**
```python
# tests/integration/test_message_flow.py
import pytest
from digichat.core.store import DigiChatStore
from digichat.services.decoder_service import DecoderService
from digichat.core.events import EventBus

@pytest.mark.asyncio
async def test_audio_to_message_flow():
    """Test complete flow from audio input to message in state."""
    # Setup
    event_bus = EventBus()
    store = DigiChatStore(initial_state=get_default_state())
    decoder_service = DecoderService(event_bus=event_bus)

    # Connect decoder output to store
    event_bus.subscribe("decoder.text",
                       lambda text: store.dispatch(receive_message(text, "CW")))

    # Simulate audio input with known content
    audio = load_test_audio("fixtures/cw_hello_world.wav")
    event_bus.publish("audio.input", audio)

    # Wait for processing
    await asyncio.sleep(0.1)

    # Verify message appeared in state
    state = store.get_state()
    assert len(state.messages) == 1
    assert "HELLO WORLD" in state.messages[0].text
    assert state.messages[0].mode == "CW"
```

### 4. UI Snapshot Tests

**Example: Textual Snapshot Test**
```python
# tests/ui/test_main_screen.py
from digichat.ui.app import DigiChatApp
from digichat.core.store import DigiChatStore

async def test_main_screen_layout(snap_compare):
    """Test main screen renders correctly."""
    store = DigiChatStore(initial_state=get_default_state())
    app = DigiChatApp(store=store)

    assert await snap_compare(app)

async def test_message_display(snap_compare):
    """Test messages are displayed correctly."""
    state = get_default_state()
    state.messages = [
        Message(timestamp=1.0, text="CQ CQ CQ", direction="rx", mode="CW"),
        Message(timestamp=2.0, text="K6XXX", direction="tx", mode="CW"),
    ]

    store = DigiChatStore(initial_state=state)
    app = DigiChatApp(store=store)

    assert await snap_compare(app, terminal_size=(80, 24))
```

### 5. Headless Mode for Claude Code

**Purpose:** Allow Claude Code to run and test the application without a terminal.

**Implementation:**
```python
# src/digichat/headless.py
"""Headless mode runner for testing and debugging."""

import asyncio
from pathlib import Path
from typing import Optional, List
import json

class HeadlessRunner:
    """Run DigiChat in headless mode for testing."""

    def __init__(self, config_path: Optional[Path] = None):
        self.store = DigiChatStore(initial_state=get_default_state())
        self.event_bus = EventBus()
        self.services = []

        # Setup logging to capture everything
        self.setup_structured_logging()

        # Subscribe to all state changes
        self.store.subscribe(self._log_state_change)

    def setup_structured_logging(self):
        """Configure structured logging for easy parsing."""
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.add_log_level,
                structlog.processors.JSONRenderer()
            ]
        )

    def _log_state_change(self, state: AppState):
        """Log every state change as JSON."""
        logger.info("state_changed", state=state.to_dict())

    async def run_scenario(self, scenario: dict):
        """Run a test scenario and return results."""
        # Example scenario:
        # {
        #   "actions": [
        #     {"type": "CHANGE_MODE", "payload": {"mode": "CW"}},
        #     {"type": "SEND_MESSAGE", "payload": {"text": "CQ CQ CQ"}},
        #   ],
        #   "audio_input": "path/to/test/audio.wav"
        # }

        for action_def in scenario["actions"]:
            action = Action(**action_def)
            self.store.dispatch(action)
            await asyncio.sleep(0.1)

        if "audio_input" in scenario:
            audio = load_audio(scenario["audio_input"])
            self.event_bus.publish("audio.input", audio)
            await asyncio.sleep(1.0)  # Wait for processing

        return {
            "final_state": self.store.get_state().to_dict(),
            "message_count": len(self.store.get_state().messages)
        }

# CLI for headless mode
def main_headless():
    """CLI entry point for headless mode."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", type=Path, help="JSON scenario file")
    parser.add_argument("--output", type=Path, help="Output JSON file")
    args = parser.parse_args()

    runner = HeadlessRunner()

    scenario = json.loads(args.scenario.read_text())
    result = asyncio.run(runner.run_scenario(scenario))

    if args.output:
        args.output.write_text(json.dumps(result, indent=2))
    else:
        print(json.dumps(result, indent=2))
```

**Usage by Claude Code:**
```bash
# Run a test scenario
digichat-headless --scenario tests/scenarios/basic_cw.json --output result.json

# Claude Code can then inspect result.json to see state tree
cat result.json | jq '.final_state.messages'
```

**Benefits:**
- Claude Code can run scenarios without terminal
- All state changes logged as JSON (parseable)
- Can replay scenarios for debugging
- Can compare state trees between runs
- Fast feedback loop

---

## Logging and Observability

### Structured Logging with Structlog

**Why Structlog:**
- JSON output (machine-readable)
- Context binding (attach request IDs, etc.)
- Colored output for development
- Performance (lazy evaluation)
- Integration with cloud logging

**Configuration:**
```python
# src/digichat/utils/logger.py
import structlog
import logging
import sys

def setup_logging(debug: bool = False, log_file: Optional[Path] = None):
    """Setup structured logging for the application."""

    # Determine processors based on output
    if sys.stdout.isatty():
        # Development: Pretty colored output
        processors = [
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    else:
        # Production/headless: JSON output
        processors = [
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer()
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

    # File logging if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            structlog.processors.JSONRenderer()
        )
        logging.root.addHandler(file_handler)

# Usage in code
logger = structlog.get_logger(__name__)

# Bind context
logger = logger.bind(user_id="K6XXX", session_id="abc123")

# Log with structured data
logger.info("message_received",
           mode="CW",
           text="CQ CQ CQ",
           wpm=20,
           signal_strength=-80)
```

**Output (Development):**
```
2025-11-15 10:30:45 [info] message_received mode=CW text="CQ CQ CQ" wpm=20 signal_strength=-80
```

**Output (Headless/Production):**
```json
{
  "timestamp": "2025-11-15T10:30:45.123Z",
  "level": "info",
  "event": "message_received",
  "mode": "CW",
  "text": "CQ CQ CQ",
  "wpm": 20,
  "signal_strength": -80,
  "user_id": "K6XXX",
  "session_id": "abc123"
}
```

### Logging Strategy

**What to Log:**

1. **State Changes (via middleware):**
   ```python
   logger.info("action_dispatched", action_type=action.type, payload=action.payload)
   logger.info("state_changed", old_state=old, new_state=new, diff=diff)
   ```

2. **Service Events:**
   ```python
   logger.info("audio_stream_started", device=device_id, sample_rate=48000)
   logger.info("decoder_switched", old_mode="CW", new_mode="PSK31")
   logger.info("message_decoded", mode="CW", text="SOS", confidence=0.95)
   ```

3. **Performance Metrics:**
   ```python
   logger.info("audio_processing_time", duration_ms=12.5, buffer_size=1024)
   logger.info("decode_time", mode="PSK31", duration_ms=45.2)
   ```

4. **Errors (with context):**
   ```python
   logger.error("decoder_error", mode="CW", error=str(e), audio_stats=stats)
   logger.error("audio_overrun", dropped_frames=50)
   ```

**Log Levels:**
- **DEBUG:** Detailed DSP processing, every audio chunk
- **INFO:** State changes, user actions, decoded messages
- **WARNING:** Recoverable errors, degraded performance
- **ERROR:** Errors that prevent functionality

### Observability for Claude Code

**State Inspection Commands:**
```python
# src/digichat/cli.py additions

@click.command()
@click.option('--dump-state', is_flag=True, help='Dump current state as JSON')
def digichat_debug(dump_state):
    """Debug commands for inspecting application state."""
    if dump_state:
        runner = HeadlessRunner()
        state = runner.store.get_state()
        print(json.dumps(state.to_dict(), indent=2))
```

**Usage:**
```bash
# Dump current state
digichat --dump-state | jq '.messages | length'

# Monitor state changes
digichat --debug 2>&1 | grep state_changed | jq .
```

---

## Development Workflow

### Quick Start for Development

```bash
# 1. Setup environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e ".[dev]"

# 2. Run tests
pytest

# 3. Run in development mode (with debug logging)
digichat --debug --log-file digichat.log

# 4. Run in headless mode
digichat-headless --scenario tests/scenarios/basic.json
```

### Testing Workflow

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/digichat --cov-report=html

# Run specific test category
pytest tests/modes/          # Unit tests for modes
pytest tests/services/       # Service tests
pytest tests/integration/    # Integration tests
pytest tests/ui/            # UI snapshot tests

# Update snapshots (after intentional UI changes)
pytest --snapshot-update

# Run in watch mode (auto-rerun on changes)
pytest-watch
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/

# All checks (runs in pre-commit)
pre-commit run --all-files
```

### Debugging Workflow

**1. Unit Test Debugging:**
```bash
# Run single test with output
pytest -v -s tests/modes/test_cw.py::TestCWDecoder::test_decode_sos

# Drop into debugger on failure
pytest --pdb
```

**2. Integration Debugging:**
```bash
# Run with full debug logging
digichat --debug --log-file debug.log

# In another terminal, tail the log
tail -f debug.log | jq 'select(.event == "state_changed")'
```

**3. UI Debugging:**
```bash
# Textual has a dev console
textual console
# Then run app in another terminal
digichat --debug
```

**4. Audio Pipeline Debugging:**
```python
# Add to audio_service.py during development
def _process_input(self):
    audio_data = self.input_queue.get()

    # Save audio to file for inspection
    if self.debug:
        soundfile.write(f"debug_audio_{time.time()}.wav", audio_data, self.sample_rate)

    self.event_bus.publish("audio.input", audio_data)
```

### Claude Code Integration

**Session Start Hook:**
```bash
# .claude/SessionStart.sh
#!/bin/bash

# Setup environment
source venv/bin/activate

# Run tests to verify setup
pytest --tb=short

# Show test audio files available
ls -lh tests/fixtures/*.wav

echo "DigiChat development environment ready!"
echo "- Run tests: pytest"
echo "- Run headless: digichat-headless --scenario <file>"
echo "- Run app: digichat --debug"
```

**Common Claude Code Commands:**
```bash
# Run specific scenario
digichat-headless --scenario tests/scenarios/cw_decode.json --output result.json

# Check result
cat result.json | jq '.final_state.messages'

# Run tests
pytest -v tests/modes/test_cw.py

# Generate test audio
python scripts/generate_test_audio.py --mode CW --text "SOS" --output tests/fixtures/cw_sos.wav

# Update snapshots after UI changes
pytest --snapshot-update tests/ui/
```

---

## Open Questions and Decisions

### High Priority Decisions Needed

#### 1. UI Framework Final Choice

**Question:** Stick with Textual or use plain curses?

**Options:**
- **Option A: Textual (RECOMMENDED)**
  - Pros: Built-in testing, modern, async-native, snapshot tests
  - Cons: Newer library (less mature), additional dependency
  - Research: Used by multiple production projects, active development

- **Option B: Plain curses**
  - Pros: Standard library, lightweight, proven
  - Cons: Hard to test, no headless mode, complex code
  - Research: Testing is very difficult (manual testing or Expect scripts)

**Recommendation:** **Use Textual**
- Testing support is critical for this project
- Headless mode requirement makes Textual essential
- Modern async API fits our architecture
- Snapshot testing will catch UI regressions

**Decision Needed:** Confirm Textual choice with user

#### 2. State Management Implementation

**Question:** Use existing Redux library or custom implementation?

**Options:**
- **Option A: Custom Redux-like Store (RECOMMENDED)**
  - Pros: Lightweight, tailored to our needs, no dependency
  - Cons: Need to implement ourselves
  - Effort: ~200 lines of code

- **Option B: python-redux library**
  - Pros: Pre-built, Redux-compliant
  - Cons: Adds dependency, may be overkill
  - Research: Library is small but not widely used

**Recommendation:** **Custom Implementation**
- Our needs are simple (single store, basic middleware)
- Full control over implementation
- Easy to understand and debug
- No external dependency

**Decision Needed:** Confirm custom store approach

#### 3. Audio Processing Architecture

**Question:** How to handle audio threading?

**Options:**
- **Option A: Queue-based with dedicated threads (RECOMMENDED)**
  - Audio callback → queue → processing thread → event bus
  - Pros: Clean separation, testable, follows sounddevice best practices
  - Cons: Slight latency from queuing
  - Research: Standard pattern from sounddevice docs

- **Option B: Direct callback processing**
  - Audio callback → process immediately → event bus
  - Pros: Lower latency
  - Cons: Blocks audio thread, risks dropouts, hard to test

**Recommendation:** **Queue-based threading**
- Safer for audio (callback does minimal work)
- Testable (can mock queue)
- Follows best practices

**Decision Needed:** Confirm threading approach

#### 4. Mode Decoder Implementation Strategy

**Question:** Implement decoders from scratch or use libraries?

**Per-Mode Analysis:**

**CW (Morse Code):**
- Option A: Custom Goertzel + envelope detection
  - Effort: Medium (2-3 days)
  - Control: Full
- Option B: morse-audio-decoder library
  - Effort: Low (integration only)
  - Control: Limited
- **Recommendation:** Try library first, fall back to custom if needed

**PSK31:**
- Option A: Custom implementation (NumPy/SciPy)
  - Effort: High (1-2 weeks)
  - Control: Full
  - Complexity: Very high (phase recovery, AFC, Varicode)
- Option B: Minimal viable decoder
  - Start with basic BPSK, add features incrementally
  - Effort: Medium (start simple, enhance over time)
- **Recommendation:** Incremental custom implementation
  - No good Python library exists
  - Educational value
  - Start with basic BPSK, add AFC later

**RTTY:**
- Option A: Custom FSK + python-baudot for encoding
  - Effort: Medium (3-5 days)
  - Control: Full
- **Recommendation:** Custom FSK demodulation + python-baudot
  - FSK is simpler than PSK
  - python-baudot handles Baudot encoding well

**Decision Needed:** Confirm per-mode approach

#### 5. Configuration Persistence

**Question:** Where and how to store configuration?

**Options:**
- **Option A: ~/.digichat/config.yaml (RECOMMENDED)**
  - Standard location for user apps
  - YAML is human-readable
  - Easy to version control

- **Option B: XDG Base Directory**
  - More "correct" on Linux
  - `~/.config/digichat/config.yaml`
  - Follows XDG spec

**Recommendation:** **Use XDG Base Directory**
- More standard on modern Linux
- Falls back to ~/.digichat on Windows/Mac
- Easy to implement with `platformdirs` library

**Decision Needed:** Confirm config location

### Medium Priority Decisions

#### 6. Hamlib Integration Approach

**Question:** Direct Python bindings or command-line wrapper?

**Options:**
- **Option A: python-hamlib (if available)**
  - Pros: Native Python, better performance
  - Cons: May not exist or be maintained

- **Option B: Subprocess wrapper around `rigctl`**
  - Pros: Hamlib is stable, no binding issues
  - Cons: Subprocess overhead, parsing text output

**Research Needed:** Check if python-hamlib exists and is maintained

**Decision Needed:** Choose Hamlib integration method

#### 7. Test Audio Fixture Strategy

**Question:** How to generate/store test audio files?

**Options:**
- **Option A: Synthetic generation (RECOMMENDED)**
  - Generate test signals programmatically
  - Pros: Reproducible, no storage needed, parameterizable
  - Cons: May not match real-world audio

- **Option B: Recorded samples**
  - Record real transmissions
  - Pros: Realistic
  - Cons: Large files, not reproducible

**Recommendation:** **Both**
- Synthetic for unit tests (fast, reproducible)
- Recorded samples for integration tests (realistic)
- Script to generate common test signals

**Decision Needed:** Confirm test audio strategy

#### 8. Performance Targets

**Question:** What are acceptable performance metrics?

**Metrics to Define:**
- RX latency (audio → display): Target?
  - Suggested: < 100ms
- TX latency (keypress → audio): Target?
  - Suggested: < 50ms
- CPU usage: Target?
  - Suggested: < 25% of one core
- Memory usage: Target?
  - Suggested: < 100MB

**Decision Needed:** Set performance targets

### Low Priority Decisions

#### 9. Waterfall Display

**Question:** Include text-based waterfall or skip for v1?

**Options:**
- **Option A: Skip for v1**
  - Focus on core functionality
  - Add in v2 if requested

- **Option B: Simple text waterfall**
  - Use Unicode blocks for visualization
  - Shows frequency spectrum

**Recommendation:** **Skip for v1**
- Complex to implement
- Not critical for basic operation
- Can add later if users want it

**Decision Needed:** Confirm waterfall scope

#### 10. Message Logging

**Question:** How to handle message/QSO logging?

**Options:**
- **Option A: Simple text log**
  - Append messages to text file
  - Easy to implement

- **Option B: ADIF format**
  - Standard ham radio log format
  - Integration with logging software
  - More complex

**Recommendation:** **Start with text, add ADIF later**
- Text log is easy and useful
- ADIF can be added in future version

**Decision Needed:** Confirm logging approach

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

**Goal:** Core infrastructure that runs and is testable

**Tasks:**
1. Set up project structure with all directories
2. Implement state store (Redux-like)
3. Implement event bus (pypubsub integration)
4. Set up structured logging
5. Create basic Textual app shell (empty UI)
6. Implement headless runner
7. Write tests for store and event bus

**Deliverables:**
- App starts and shows empty UI
- Headless mode works
- State management functional
- Logging outputs JSON in headless mode
- Test suite passes

**Success Criteria:**
- `digichat` launches and shows UI
- `digichat-headless --scenario tests/basic.json` runs
- `pytest` passes all tests
- State changes appear in logs

### Phase 2: Audio Pipeline (Week 3)

**Goal:** Audio I/O working with test signals

**Tasks:**
1. Implement circular audio buffer
2. Implement audio service (sounddevice integration)
3. Add threading and queue management
4. Create audio processing pipeline
5. Write audio service tests (mocked sounddevice)
6. Generate synthetic test audio files
7. Test with loopback (audio out → audio in)

**Deliverables:**
- Audio flows through pipeline
- Can record and playback audio
- Tests verify audio processing
- Headless mode can process audio files

**Success Criteria:**
- Audio level meters show activity
- Can play test tone and see it in input
- Tests pass with mocked audio
- No audio dropouts during 1-minute test

### Phase 3: CW Implementation (Week 4)

**Goal:** First working digital mode

**Tasks:**
1. Implement CW decoder (Goertzel + envelope detection)
2. Implement CW encoder (tone generation)
3. Add CW-specific UI elements (WPM, tone frequency)
4. Create CW test audio files
5. Wire decoder to message display
6. Wire encoder to TX path
7. Write comprehensive CW tests

**Deliverables:**
- Decodes CW from audio
- Encodes text to CW
- Messages appear in UI
- Can transmit user input

**Success Criteria:**
- Decodes "CQ CQ CQ" from test file
- Round-trip test passes (text → audio → text)
- WPM detection is within ±2 WPM
- UI shows decoded messages

### Phase 4: UI Polish (Week 5)

**Goal:** Professional, usable interface

**Tasks:**
1. Implement all UI widgets
2. Add keyboard shortcuts
3. Implement configuration screen
4. Add color themes
5. Improve message formatting
6. Add stats panel
7. Write UI snapshot tests

**Deliverables:**
- Complete UI implementation
- Configuration screen works
- Snapshot tests cover all screens
- Keyboard navigation smooth

**Success Criteria:**
- All UI elements functional
- Snapshot tests pass
- No UI glitches during normal use
- Configuration persists

### Phase 5: PSK31 Implementation (Week 6-7)

**Goal:** Second digital mode working

**Tasks:**
1. Implement basic BPSK demodulation
2. Implement Varicode decoding
3. Add PSK31 encoder
4. Implement AFC (basic version)
5. Create PSK31 test files
6. Wire to UI
7. Write PSK31 tests

**Deliverables:**
- PSK31 decoder works
- PSK31 encoder works
- AFC keeps signal locked (basic)
- Tests verify functionality

**Success Criteria:**
- Decodes PSK31 test file
- Round-trip test passes
- AFC tracks ±10 Hz drift
- Messages display correctly

### Phase 6: RTTY Implementation (Week 8)

**Goal:** Third digital mode working

**Tasks:**
1. Implement FSK demodulation
2. Integrate python-baudot
3. Add RTTY encoder
4. Support multiple baud rates
5. Create RTTY test files
6. Wire to UI
7. Write RTTY tests

**Deliverables:**
- RTTY decoder works
- RTTY encoder works
- Supports 45.45 and 50 baud
- Tests verify functionality

**Success Criteria:**
- Decodes RTTY test file
- Round-trip test passes
- Handles both baud rates
- Messages display correctly

### Phase 7: Hamlib Integration (Week 9)

**Goal:** Radio control functional

**Tasks:**
1. Research python-hamlib vs rigctl
2. Implement Hamlib service
3. Add radio status to UI
4. Add frequency/mode control
5. Handle connection errors
6. Write Hamlib tests (mocked)
7. Test with real radio (if available)

**Deliverables:**
- Hamlib service works
- Radio status displays
- Can change frequency/mode
- Graceful error handling

**Success Criteria:**
- Connects to radio
- Displays current frequency
- Can change frequency from UI
- Handles disconnect gracefully

### Phase 8: Polish and Release (Week 10)

**Goal:** Production-ready v1.0

**Tasks:**
1. Performance optimization
2. Bug fixes
3. Documentation updates
4. User guide
5. Example configurations
6. Release preparation
7. Final testing

**Deliverables:**
- Optimized performance
- Complete documentation
- v1.0 release

**Success Criteria:**
- Meets performance targets
- No known critical bugs
- Documentation complete
- Ready for users

---

## Summary and Next Steps

### What We've Defined

1. **Architecture:** Layered, event-driven with clear separation
2. **Technology:** Textual, pypubsub, sounddevice, structlog
3. **State Management:** Redux-like unidirectional data flow
4. **Testing:** Multi-level with headless mode for Claude Code
5. **Logging:** Structured JSON logging for observability
6. **Roadmap:** 10-week implementation plan

### Key Strengths of This Architecture

- **Testable:** Every component can be tested independently
- **Debuggable:** State changes are logged and traceable
- **Maintainable:** Clear separation of concerns
- **Claude Code Friendly:** Headless mode + structured logs
- **Extensible:** Easy to add new modes or features
- **Modern:** Uses current best practices (2024)

### Immediate Next Steps

1. **Review and approve this plan**
2. **Make decisions on open questions**
3. **Begin Phase 1 implementation**
4. **Set up development environment**
5. **Create first PR with project structure**

### Questions for Review

1. Does the Textual choice make sense for testing requirements?
2. Is the Redux-like state management appropriate?
3. Are the performance targets reasonable?
4. Should we proceed with custom decoders or research more libraries?
5. Is the 10-week timeline realistic?

---

## Appendix: Technology Comparison

### UI Framework Comparison

| Feature | Textual | Plain curses | Urwid |
|---------|---------|--------------|-------|
| Testing support | ✅ Excellent | ❌ Manual only | ⚠️ Limited |
| Headless mode | ✅ Built-in | ❌ No | ⚠️ Possible |
| Async support | ✅ Native | ❌ No | ❌ No |
| Snapshot tests | ✅ pytest plugin | ❌ No | ❌ No |
| Documentation | ✅ Excellent | ⚠️ Basic | ✅ Good |
| Active development | ✅ Yes (2024) | N/A (stdlib) | ⚠️ Slow |
| Learning curve | ⚠️ Medium | ❌ Steep | ⚠️ Medium |
| **Recommendation** | **✅ BEST** | ❌ | ⚠️ |

### Event Bus Comparison

| Feature | pypubsub | Custom | python-redux events |
|---------|----------|--------|---------------------|
| Maturity | ✅ Very mature | ⚠️ DIY | ⚠️ Small project |
| Thread-safe | ✅ Yes | ⚠️ Must implement | ✅ Yes |
| Topic hierarchy | ✅ Yes | ⚠️ Must implement | ❌ No |
| Documentation | ✅ Good | N/A | ⚠️ Limited |
| Maintenance | ✅ Active | ⚠️ Our responsibility | ⚠️ Limited |
| **Recommendation** | **✅ BEST** | ⚠️ | ❌ |

### State Management Comparison

| Feature | Custom Redux | python-redux | MobX-like |
|---------|-------------|--------------|-----------|
| Complexity | ⚠️ Medium | ⚠️ Medium | ⚠️ Medium |
| Control | ✅ Full | ⚠️ Limited | ⚠️ Limited |
| Debuggability | ✅ Full | ✅ Good | ⚠️ Magic |
| Predictability | ✅ High | ✅ High | ⚠️ Medium |
| Learning curve | ⚠️ Requires Redux knowledge | ⚠️ Requires Redux knowledge | ⚠️ Different paradigm |
| Code size | ⚠️ ~200 lines | ✅ 0 (library) | ✅ 0 (library) |
| **Recommendation** | **✅ BEST** | ⚠️ | ❌ |

---

**End of Architecture Plan v1.0**
