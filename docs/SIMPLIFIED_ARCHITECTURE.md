# DigiChat Simplified Architecture Plan

**Document Version:** 2.0
**Date:** 2025-11-15
**Status:** Revised Based on Design Review
**Replaces:** Redux and Event Bus patterns with simpler alternatives

---

## Executive Summary

This document presents a **simplified architecture** that maintains perfect testability and headless support while reducing unnecessary complexity identified in the design review.

### Key Simplifications

1. **State Management:** Simple Observable State Pattern (instead of Redux)
2. **Component Communication:** Direct calls + async queues (instead of event bus)
3. **UI Framework:** Textual (kept - provides essential headless testing)
4. **Logging:** Structlog (kept - essential for headless debugging)

**Result:** ~60% less boilerplate while maintaining 100% testability.

---

## Simplified Component Architecture

### Directory Structure

```
src/digichat/
├── core/
│   ├── __init__.py
│   └── state.py              # Observable state (replaces store/actions/reducers)
│
├── services/
│   ├── __init__.py
│   ├── audio_service.py      # Audio I/O with direct callbacks
│   ├── decoder_service.py    # Digital mode decoding
│   └── config_service.py     # Configuration management
│
├── modes/
│   ├── __init__.py
│   ├── base.py               # Base decoder/encoder interface
│   ├── cw.py                 # CW implementation
│   ├── psk31.py              # PSK31 implementation (v1.1+)
│   └── rtty.py               # RTTY implementation (v1.1+)
│
├── ui/
│   ├── __init__.py
│   ├── app.py                # Main Textual app
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── message_list.py
│   │   ├── stats_panel.py
│   │   └── input_box.py
│   └── themes.py
│
├── audio/
│   ├── __init__.py
│   ├── buffer.py             # Circular audio buffer
│   └── pipeline.py           # Audio processing pipeline
│
├── utils/
│   ├── __init__.py
│   ├── logger.py             # Structured logging
│   └── helpers.py
│
├── config.py                 # Configuration dataclasses
├── cli.py                    # CLI entry point
└── headless.py               # Headless test runner
```

---

## Simplified State Management

### Observable State Pattern (Not Redux)

**Simple, testable, inspectable - without Redux boilerplate.**

```python
# src/digichat/core/state.py
from dataclasses import dataclass, field, asdict
from typing import List, Callable, Optional, Any
from datetime import datetime
import json

@dataclass
class Message:
    """A single message in the chat history."""
    timestamp: datetime
    text: str
    direction: str  # "rx" or "tx"
    mode: str
    metadata: dict = field(default_factory=dict)

@dataclass
class AudioState:
    """Current audio state."""
    input_device: Optional[int] = None
    output_device: Optional[int] = None
    sample_rate: int = 48000
    input_level: float = 0.0
    output_level: float = 0.0
    is_streaming: bool = False

@dataclass
class ModeState:
    """Digital mode configuration."""
    current_mode: str = "CW"
    cw_wpm: int = 20
    cw_tone_freq: int = 600
    psk31_frequency: int = 1000
    rtty_baud_rate: float = 45.45

@dataclass
class AppState:
    """
    Complete application state.

    All state is stored here and can be:
    - Serialized to JSON for inspection
    - Observed for changes
    - Tested in isolation
    """
    messages: List[Message] = field(default_factory=list)
    audio: AudioState = field(default_factory=AudioState)
    mode: ModeState = field(default_factory=ModeState)

    # Observer pattern for reactivity
    _observers: List[Callable[[str], None]] = field(default_factory=list, repr=False)

    def add_message(self, text: str, direction: str, mode: str, metadata: dict = None):
        """Add a message to history."""
        msg = Message(
            timestamp=datetime.now(),
            text=text,
            direction=direction,
            mode=mode,
            metadata=metadata or {}
        )
        self.messages.append(msg)
        self._notify("messages")

    def set_mode(self, mode: str):
        """Change current digital mode."""
        self.mode.current_mode = mode
        self._notify("mode")

    def update_audio_level(self, level: float, direction: str = "input"):
        """Update audio level meter."""
        if direction == "input":
            self.audio.input_level = level
        else:
            self.audio.output_level = level
        self._notify("audio")

    def observe(self, callback: Callable[[str], None]):
        """Register an observer for state changes."""
        self._observers.append(callback)

    def _notify(self, changed_key: str):
        """Notify observers of state change."""
        for observer in self._observers:
            observer(changed_key)

    def to_dict(self) -> dict:
        """Serialize state to dictionary (for headless inspection)."""
        return {
            "messages": [asdict(m) for m in self.messages],
            "audio": asdict(self.audio),
            "mode": asdict(self.mode),
        }

    def to_json(self) -> str:
        """Serialize state to JSON (for headless inspection)."""
        return json.dumps(self.to_dict(), indent=2, default=str)

# Usage
state = AppState()
state.observe(lambda key: print(f"State changed: {key}"))
state.add_message("CQ CQ CQ", "rx", "CW")  # Observers notified
```

**Benefits:**
- ✅ **Simple:** ~100 LOC vs ~400 LOC for Redux
- ✅ **Testable:** Can inspect and modify state directly
- ✅ **Observable:** UI updates on changes
- ✅ **Serializable:** `to_json()` for headless inspection
- ✅ **Type-safe:** Full type hints
- ✅ **Debuggable:** Can log state changes easily

---

## Simplified Component Communication

### Direct Calls + Async Queues (Not Event Bus)

**Use direct function calls for most things. Use queues only for audio threading.**

```python
# src/digichat/services/decoder_service.py
from digichat.modes.base import BaseMode
from digichat.core.state import AppState
import numpy as np

class DecoderService:
    """
    Decodes audio into text.
    Simple direct design - no event bus needed.
    """

    def __init__(self, state: AppState, mode: BaseMode):
        self.state = state
        self.mode = mode

    def process_audio(self, audio_data: np.ndarray) -> Optional[str]:
        """
        Process audio chunk and decode to text.

        This is called directly by AudioService - no events needed.
        """
        text = self.mode.decode(audio_data)
        if text:
            # Update state directly
            self.state.add_message(text, "rx", self.mode.name)
        return text

    def set_mode(self, new_mode: BaseMode):
        """Switch to a different decoder."""
        self.mode = new_mode
        self.state.set_mode(new_mode.name)
```

```python
# src/digichat/services/audio_service.py
import sounddevice as sd
import numpy as np
from queue import Queue
import threading
from typing import Callable

class AudioService:
    """
    Manages audio I/O using queues for thread safety.
    Calls decoder directly - no event bus.
    """

    def __init__(self,
                 state: AppState,
                 on_audio_input: Callable[[np.ndarray], None],
                 sample_rate: int = 48000):
        self.state = state
        self.on_audio_input = on_audio_input  # Direct callback
        self.sample_rate = sample_rate

        self.input_queue = Queue(maxsize=20)
        self.output_queue = Queue(maxsize=20)
        self.running = False

    def start(self):
        """Start audio streams."""
        self.running = True

        # Start audio stream
        self.stream = sd.Stream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32',
            callback=self._audio_callback,
            blocksize=1024
        )
        self.stream.start()
        self.state.audio.is_streaming = True

        # Start processing thread
        self.thread = threading.Thread(target=self._process_input)
        self.thread.start()

    def _audio_callback(self, indata, outdata, frames, time, status):
        """Audio thread callback (minimal work)."""
        if status:
            logger.warning("audio_status", status=str(status))

        # Queue for processing thread
        try:
            self.input_queue.put_nowait(indata.copy())
        except:
            logger.warning("audio_overrun")

        # Output (or silence)
        try:
            outdata[:] = self.output_queue.get_nowait()
        except:
            outdata[:] = np.zeros_like(outdata)

    def _process_input(self):
        """Processing thread - calls decoder directly."""
        while self.running:
            try:
                audio = self.input_queue.get(timeout=0.1)

                # Update level meter
                level = np.abs(audio).mean()
                self.state.update_audio_level(level, "input")

                # Call decoder directly (no events)
                self.on_audio_input(audio)

            except:
                continue
```

**Why This Works:**

1. **Audio → Decoder:** Direct callback (fast, simple)
2. **UI → Services:** Direct method calls
3. **State → UI:** Observer pattern (Textual reactivity)
4. **Threading:** Only where needed (audio I/O)

**No event bus needed** - everything is direct and traceable.

---

## Textual UI Integration

### Reactive Widgets with Direct State Access

```python
# src/digichat/ui/app.py
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input
from textual.containers import Container
from digichat.core.state import AppState
from digichat.services.audio_service import AudioService
from digichat.services.decoder_service import DecoderService
from digichat.modes.cw import CWDecoder

class DigiChatApp(App):
    """
    Main Textual application.

    Uses state observers to update UI - simple and testable.
    """

    CSS_PATH = "app.tcss"

    def __init__(self, state: AppState = None):
        super().__init__()

        # State (can be injected for testing)
        self.state = state or AppState()

        # Services
        self.decoder = DecoderService(self.state, CWDecoder())
        self.audio = AudioService(
            self.state,
            on_audio_input=self.decoder.process_audio
        )

        # Observe state changes
        self.state.observe(self._on_state_change)

    def compose(self) -> ComposeResult:
        """Build the UI."""
        yield Header()
        with Container(id="main"):
            yield Static(id="stats", classes="panel")
            yield Static(id="messages", classes="panel")
            yield Input(id="input", placeholder="Type message...")
        yield Footer()

    def _on_state_change(self, key: str):
        """React to state changes."""
        if key == "messages":
            self._update_messages()
        elif key == "audio":
            self._update_stats()
        elif key == "mode":
            self._update_mode_display()

    def _update_messages(self):
        """Update message display from state."""
        messages_widget = self.query_one("#messages", Static)

        # Build message text
        lines = []
        for msg in self.state.messages[-100:]:  # Last 100
            time = msg.timestamp.strftime("%H:%M:%S")
            prefix = "RX" if msg.direction == "rx" else "TX"
            lines.append(f"[{time}] {prefix}: {msg.text}")

        messages_widget.update("\n".join(lines))

    def on_input_submitted(self, event: Input.Submitted):
        """Handle user input - direct state update."""
        text = event.value

        # Add to state (will notify observers)
        self.state.add_message(text, "tx", self.state.mode.current_mode)

        # Encode and transmit (simplified)
        audio = self.decoder.mode.encode(text)
        # ... transmit audio ...

        event.input.value = ""

    def on_mount(self):
        """Start services when UI mounts."""
        self.audio.start()
```

---

## Headless Testing

### Simple Test Runner (No Complex Scenario System)

```python
# src/digichat/headless.py
"""
Headless test runner for Claude Code.

Simplified - just run the app in test mode and inspect state.
"""
import asyncio
from pathlib import Path
from digichat.ui.app import DigiChatApp
from digichat.core.state import AppState
import json

async def run_headless_test(audio_file: Path = None) -> dict:
    """
    Run app in headless mode and return final state.

    Much simpler than full scenario runner.
    """
    # Create app with fresh state
    state = AppState()
    app = DigiChatApp(state=state)

    # Run in headless mode
    async with app.run_test() as pilot:
        # If audio file provided, process it
        if audio_file:
            audio_data = load_audio(audio_file)
            app.decoder.process_audio(audio_data)
            await asyncio.sleep(0.5)  # Let it process

        # Simulate typing a message
        await pilot.press("tab")  # Focus input
        await pilot.press(*"CQ CQ CQ")
        await pilot.press("enter")

        await asyncio.sleep(0.1)

    # Return state as dict
    return state.to_dict()

def main_headless():
    """CLI for headless testing."""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--audio", type=Path, help="Audio file to process")
    parser.add_argument("--output", type=Path, help="JSON output file")
    args = parser.parse_args()

    result = asyncio.run(run_headless_test(args.audio))

    if args.output:
        args.output.write_text(json.dumps(result, indent=2, default=str))
    else:
        print(json.dumps(result, indent=2, default=str))

# Usage:
# digichat-headless --audio tests/fixtures/cw_sos.wav --output result.json
# cat result.json | jq '.messages'
```

---

## Testing Strategy

### Unit Tests (DSP Functions)

```python
# tests/modes/test_cw.py
import pytest
import numpy as np
from digichat.modes.cw import CWDecoder

def test_cw_decode_sos():
    """Test CW decoder with known signal."""
    decoder = CWDecoder(wpm=20, tone_freq=600)

    # Load test audio
    audio = np.load("tests/fixtures/cw_sos_20wpm.npy")

    result = decoder.decode(audio)
    assert "SOS" in result

def test_cw_encode_roundtrip():
    """Test encode -> decode roundtrip."""
    decoder = CWDecoder(wpm=20)

    # Encode
    audio = decoder.encode("SOS")

    # Decode
    result = decoder.decode(audio)
    assert "SOS" in result
```

### Integration Tests (State Changes)

```python
# tests/integration/test_message_flow.py
import pytest
from digichat.core.state import AppState
from digichat.services.decoder_service import DecoderService
from digichat.modes.cw import CWDecoder

def test_decoded_message_updates_state():
    """Test that decoded audio updates state."""
    state = AppState()
    decoder_service = DecoderService(state, CWDecoder())

    # Process test audio
    audio = load_test_audio("cw_hello.wav")
    decoder_service.process_audio(audio)

    # Check state
    assert len(state.messages) > 0
    assert "HELLO" in state.messages[0].text
    assert state.messages[0].direction == "rx"
```

### UI Tests (Textual Snapshots)

```python
# tests/ui/test_app.py
import pytest
from digichat.ui.app import DigiChatApp
from digichat.core.state import AppState

async def test_app_displays_messages(snap_compare):
    """Test message display (snapshot test)."""
    # Create state with test data
    state = AppState()
    state.add_message("CQ CQ CQ", "rx", "CW")
    state.add_message("K6XXX", "tx", "CW")

    # Create app with test state
    app = DigiChatApp(state=state)

    # Snapshot test
    assert await snap_compare(app, terminal_size=(80, 24))

@pytest.mark.asyncio
async def test_user_input_adds_message():
    """Test user input flow."""
    state = AppState()
    app = DigiChatApp(state=state)

    async with app.run_test() as pilot:
        # Type message
        await pilot.press("tab")  # Focus input
        await pilot.press(*"TEST")
        await pilot.press("enter")

        # Check state
        assert len(state.messages) == 1
        assert state.messages[0].text == "TEST"
        assert state.messages[0].direction == "tx"
```

---

## Comparison: Old vs New

### State Management

| Aspect | Redux Approach | Simplified Approach |
|--------|----------------|---------------------|
| **LOC** | ~400 | ~100 |
| **Files** | 4 (store, actions, reducers, middleware) | 1 (state.py) |
| **Learning Curve** | High (Redux pattern) | Low (simple observers) |
| **Testability** | ✅ Excellent | ✅ Excellent |
| **Serializable** | ✅ Yes | ✅ Yes |
| **Debuggable** | ⚠️ Need to trace actions | ✅ Direct inspection |

### Component Communication

| Aspect | Event Bus | Direct Calls |
|--------|-----------|--------------|
| **LOC** | ~200 (event definitions + setup) | ~0 (just call methods) |
| **Traceability** | ⚠️ Hard (who handles this event?) | ✅ Easy (direct call stack) |
| **Testing** | ⚠️ Need to mock event bus | ✅ Simple mocks |
| **Threading** | ⚠️ Thread-safe but complex | ✅ Queues where needed |

---

## Updated Roadmap

### Phase 1: Foundation (Week 1-2)

**Tasks:**
1. Implement AppState with observers (`core/state.py`) - **~100 LOC**
2. Setup Textual app shell (`ui/app.py`) - **~150 LOC**
3. Implement AudioService with queues (`services/audio_service.py`) - **~200 LOC**
4. Create circular audio buffer (`audio/buffer.py`) - **~100 LOC**
5. Setup structlog logging (`utils/logger.py`) - **~50 LOC**
6. Create headless test runner (`headless.py`) - **~100 LOC**

**Total:** ~700 LOC

**Deliverable:**
- App launches with Textual UI
- Audio I/O works (can see levels)
- State is observable and serializable
- Headless mode runs tests

### Phase 2: CW Implementation (Week 3-4)

**Tasks:**
1. Implement CW decoder (`modes/cw.py`) - **~300 LOC**
   - Goertzel filter
   - Envelope detection
   - Morse timing decode
2. Implement CW encoder - **~100 LOC**
3. Create DecoderService - **~100 LOC**
4. Wire decoder → state → UI - **~50 LOC**
5. Write tests for CW - **~200 LOC**

**Total:** ~750 LOC (cumulative: ~1,450 LOC)

**Deliverable:**
- Working CW decoder
- Messages appear in UI
- Round-trip tests pass
- Headless tests verify decoding

### Phase 3: Polish & Testing (Week 5)

**Tasks:**
1. Polish UI widgets
2. Add keyboard shortcuts
3. Improve error handling
4. Performance optimization
5. Documentation

**Deliverable:**
- Working CW chat application
- Full test coverage
- Ready for user testing

---

## Benefits of Simplified Architecture

### Complexity Reduction

- **60% less code** (~1,500 LOC vs ~4,000 LOC)
- **50% fewer files**
- **Simpler mental model** (direct calls vs event tracing)

### Maintained Benefits

- ✅ **Textual**: Full headless testing support
- ✅ **Observable state**: UI reactivity
- ✅ **Serializable state**: JSON inspection for Claude Code
- ✅ **Type-safe**: Full type hints
- ✅ **Testable**: Unit, integration, and snapshot tests
- ✅ **Structured logging**: JSON output for debugging

### Development Speed

- **Faster iteration**: Direct calls are easier to refactor
- **Easier debugging**: Clear call stacks
- **Less boilerplate**: More time on features

---

## Headless Testing for Claude Code

### State Inspection

```bash
# Run headless test
digichat-headless --audio tests/cw_sos.wav --output result.json

# Inspect state
cat result.json | jq '.messages'
cat result.json | jq '.audio'

# Count messages
cat result.json | jq '.messages | length'
```

### Live Debugging

```bash
# Run with JSON logging
digichat --debug 2>&1 | tee debug.log

# In another terminal, watch state changes
tail -f debug.log | jq 'select(.event == "state_changed")'
```

### Test Development

```python
# Simple test - no complex setup
async def test_cw_decoding():
    state = AppState()
    app = DigiChatApp(state=state)

    async with app.run_test():
        # Process audio
        audio = load_wav("test.wav")
        app.decoder.process_audio(audio)

        # Check state (serializable!)
        assert len(state.messages) > 0
        print(state.to_json())  # Inspect as JSON
```

---

## Migration Path

If you later need Redux or event bus:

1. **Add Redux**: Wrap AppState in a store - state structure stays the same
2. **Add Events**: Replace direct calls with pub/sub - interfaces stay the same
3. **Cost**: ~1 day to add either if really needed

**But start simple.** Most applications never need these patterns.

---

## Summary

### What Changed

- ❌ **Redux** → ✅ Observable State (~100 LOC)
- ❌ **Event Bus** → ✅ Direct Calls + Queues
- ✅ **Textual** (kept - essential for headless testing)
- ✅ **Structured Logging** (kept - essential for debugging)

### What Stayed

- ✅ Perfect headless testability
- ✅ State serialization for Claude Code
- ✅ Textual snapshot testing
- ✅ Queue-based audio threading
- ✅ Clean architecture (layers)

### Result

**Same testability, 60% less complexity.**

Ready for implementation in **~1,500 LOC** instead of ~4,000 LOC.
