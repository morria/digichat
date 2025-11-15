# DigiChat Architecture - Quick Start Guide

**For:** Claude Code and AI-Assisted Development
**Date:** 2025-11-15
**Status:** Ready for Implementation

This document provides a quick overview of the DigiChat architecture with links to detailed documentation.

---

## 📚 Documentation Map

We've created comprehensive documentation to guide implementation:

1. **[ARCHITECTURE_PLAN.md](ARCHITECTURE_PLAN.md)** (Main Document, ~5000 lines)
   - Complete architectural design
   - Component breakdown
   - Technology stack details
   - Testing strategy
   - 10-week implementation roadmap

2. **[LIBRARY_GUIDE.md](LIBRARY_GUIDE.md)** (~2000 lines)
   - Detailed guide for each library
   - Code examples
   - Installation instructions
   - Best practices

3. **[DECISIONS_NEEDED.md](DECISIONS_NEEDED.md)** (~800 lines)
   - All pending decisions
   - Options analysis
   - Recommendations
   - Decision tracking

4. **This Document** (Quick Reference)
   - High-level overview
   - Quick links
   - Implementation checklist

---

## 🎯 Architecture at a Glance

### Core Design Principles

1. **Layered Architecture** - Clean separation of concerns
2. **Event-Driven** - Components communicate via pub/sub
3. **Testability First** - Headless mode + snapshot testing
4. **Redux-like State** - Predictable, debuggable state management
5. **Claude Code Friendly** - JSON logging, headless runner, state inspection

### Stack Summary

```
UI:           Textual (modern TUI with testing support)
State:        Custom Redux-like store
Events:       Pypubsub
Audio:        Sounddevice + NumPy/SciPy
Logging:      Structlog (JSON output)
Testing:      Pytest + pytest-textual-snapshot
Config:       PyYAML + platformdirs
```

### Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│                 UI Layer (Textual)              │
│         Reactive Widgets + Screens              │
└────────────────────┬────────────────────────────┘
                     │ Events ↕ State
┌────────────────────┴────────────────────────────┐
│            Application Core                      │
│  Redux Store + Event Bus + Middleware           │
└────────────────────┬────────────────────────────┘
                     │ Commands ↕ Data
┌────────────────────┴────────────────────────────┐
│              Service Layer                       │
│  Audio │ Decoder │ Encoder │ Hamlib │ Config   │
└────────────────────┬────────────────────────────┘
                     │ I/O
┌────────────────────┴────────────────────────────┐
│         Hardware (Sound Card + Radio)           │
└─────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start (For Implementation)

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install with all dev dependencies
pip install -e ".[dev]"
```

### 2. Verify Setup

```bash
# Run existing tests
pytest

# List audio devices (requires sounddevice)
python -c "import sounddevice as sd; print(sd.query_devices())"

# Test Textual
python -c "from textual.app import App; print('Textual OK')"
```

### 3. Review Architecture Documents

Read in this order:
1. This document (overview)
2. ARCHITECTURE_PLAN.md (detailed design)
3. DECISIONS_NEEDED.md (pending decisions)
4. LIBRARY_GUIDE.md (implementation details)

---

## 📋 Implementation Checklist

### Phase 1: Foundation (Week 1-2)

**Critical Decisions Needed First:**
- [ ] Approve Textual for UI (recommended)
- [ ] Approve custom Redux-like store (recommended)
- [ ] Approve queue-based audio threading (recommended)
- [ ] Choose config location (platformdirs or ~/.digichat)

**Implementation Tasks:**
- [ ] Create directory structure
- [ ] Implement Redux-like store
- [ ] Integrate Pypubsub event bus
- [ ] Setup Structlog logging
- [ ] Create basic Textual app shell
- [ ] Implement headless runner
- [ ] Write tests for store + events

**Deliverable:**
- App launches with empty UI
- Headless mode functional
- State management working
- Tests passing

### Phase 2: Audio Pipeline (Week 3)

- [ ] Implement circular audio buffer
- [ ] Create AudioService with sounddevice
- [ ] Add threading and queues
- [ ] Write audio processing pipeline
- [ ] Create test audio generation script
- [ ] Test with loopback

**Deliverable:**
- Audio flows through pipeline
- No dropouts
- Tests pass

### Phase 3: CW Implementation (Week 4)

- [ ] Decide: Library vs. custom decoder (D5)
- [ ] Implement CW decoder
- [ ] Implement CW encoder
- [ ] Add CW UI elements
- [ ] Create CW test files
- [ ] Write comprehensive tests

**Deliverable:**
- Working CW mode
- Messages display in UI
- Round-trip test passes

### Phases 4-8

See [ARCHITECTURE_PLAN.md](ARCHITECTURE_PLAN.md) for complete roadmap.

---

## 🔧 Claude Code Integration

### Headless Mode

DigiChat is designed to run without a terminal for testing:

```bash
# Run scenario
digichat-headless --scenario tests/scenarios/basic_cw.json --output result.json

# Inspect result
cat result.json | jq '.final_state.messages'
```

### State Inspection

```bash
# Dump current state
digichat --dump-state | jq .

# Monitor state changes (JSON logs)
digichat --debug 2>&1 | grep state_changed | jq .
```

### Testing Commands

```bash
# Run all tests
pytest

# Run specific category
pytest tests/modes/        # Unit tests
pytest tests/services/     # Service tests
pytest tests/integration/  # Integration tests
pytest tests/ui/          # UI snapshot tests

# Update snapshots
pytest --snapshot-update

# With coverage
pytest --cov=src/digichat --cov-report=html
```

### Debugging

```bash
# Run with debug logging (JSON output)
digichat --debug --log-file debug.log

# In another terminal, watch logs
tail -f debug.log | jq 'select(.event == "decoder.text")'
```

---

## 🎓 Key Concepts

### 1. State Management (Redux Pattern)

All state in one place, updated only through actions:

```python
# Dispatch action
store.dispatch(Action("SEND_MESSAGE", {"text": "CQ CQ CQ"}))

# State updates through pure reducers
def message_reducer(messages, action):
    if action.type == "SEND_MESSAGE":
        return messages + [create_message(action.payload)]
    return messages

# Subscribers notified
store.subscribe(lambda state: update_ui(state))
```

**Why:** Predictable, debuggable, testable

### 2. Event-Driven Communication

Components don't call each other directly:

```python
# Service publishes event
EventBus.publish("decoder.text", text="SOS", mode="CW")

# Multiple subscribers can react
EventBus.subscribe("decoder.text", display_message)
EventBus.subscribe("decoder.text", log_message)
EventBus.subscribe("decoder.text", update_stats)
```

**Why:** Loose coupling, easy testing, flexible architecture

### 3. Headless Testing

UI components work without terminal:

```python
# Run app in headless mode
async with app.run_test() as pilot:
    # Simulate user input
    await pilot.press("h")

    # Check state
    assert app.current_mode == "CW"

    # Verify UI (snapshot)
    assert await snap_compare(app)
```

**Why:** Automated testing, CI/CD integration, Claude Code can run tests

### 4. Structured Logging

All logs are JSON (machine-readable):

```python
logger.info("message_decoded",
           mode="CW",
           text="CQ CQ CQ",
           wpm=20,
           confidence=0.95)
```

**Output:**
```json
{
  "event": "message_decoded",
  "mode": "CW",
  "text": "CQ CQ CQ",
  "wpm": 20,
  "confidence": 0.95,
  "timestamp": "2025-11-15T10:30:45.123Z"
}
```

**Why:** Easy to parse, filter, analyze. Claude Code can read logs.

---

## 🎯 Critical Design Decisions

### STRONGLY RECOMMENDED (Backed by Research)

These are ready for approval based on extensive research:

1. ✅ **Textual** for UI
   - Only option with proper testing support
   - Headless mode built-in
   - Snapshot testing via pytest plugin
   - Modern, actively developed

2. ✅ **Custom Redux-like Store** for state
   - Simple (~200 lines)
   - Full control
   - No dependency

3. ✅ **Queue-based Threading** for audio
   - Safest for audio (prevents dropouts)
   - Recommended by sounddevice docs
   - Testable

4. ✅ **Pypubsub** for events
   - Mature, stable
   - Thread-safe
   - Simple API

5. ✅ **Structlog** for logging
   - JSON output for headless mode
   - Context binding
   - Perfect for debugging

**See [DECISIONS_NEEDED.md](DECISIONS_NEEDED.md) for full analysis and alternatives.**

---

## 📁 Project Structure

```
src/digichat/
├── core/              # State + Events + Middleware
│   ├── store.py       # Redux-like store
│   ├── actions.py     # Action creators
│   ├── reducers.py    # Pure state reducers
│   ├── events.py      # Event bus (pypubsub)
│   └── middleware.py  # Logging, async effects
│
├── services/          # Side effects (I/O)
│   ├── audio_service.py
│   ├── decoder_service.py
│   ├── encoder_service.py
│   ├── hamlib_service.py
│   └── config_service.py
│
├── modes/             # Digital mode implementations
│   ├── base.py        # Base interface
│   ├── cw.py          # CW decoder/encoder
│   ├── psk31.py       # PSK31 decoder/encoder
│   └── rtty.py        # RTTY decoder/encoder
│
├── ui/                # Textual UI
│   ├── app.py         # Main app
│   ├── screens/       # Screen definitions
│   └── widgets/       # Custom widgets
│
├── audio/             # Low-level audio/DSP
│   ├── buffer.py      # Circular buffer
│   ├── pipeline.py    # Processing pipeline
│   └── utils.py       # DSP utilities
│
├── utils/
│   ├── logger.py      # Structlog setup
│   └── helpers.py
│
├── config.py          # Configuration
├── cli.py             # CLI entry point
└── headless.py        # Headless runner
```

---

## 🧪 Testing Strategy

### Test Pyramid

```
        /\
       /  \  E2E (Snapshot + Full Flow)
      /────\
     /      \ Integration (Service + Event Flow)
    /────────\
   /          \ Component (Services, Widgets)
  /────────────\
 /              \ Unit (DSP, Decoders, Pure Functions)
/────────────────\
```

### Key Testing Features

1. **Unit Tests:** Pure functions (DSP, decoders)
   ```python
   def test_cw_decoder():
       decoder = CWDecoder(sample_rate=48000, wpm=20)
       audio = load_test_audio("cw_sos.wav")
       assert decoder.decode(audio) == "SOS"
   ```

2. **Service Tests:** Mocked I/O
   ```python
   @patch('sounddevice.Stream')
   def test_audio_service(mock_stream):
       service = AudioService()
       service.start()
       assert service.is_running
   ```

3. **Integration Tests:** Full event flow
   ```python
   async def test_message_flow():
       # Setup
       event_bus = EventBus()
       store = DigiChatStore()
       decoder = DecoderService(event_bus)

       # Trigger
       event_bus.publish("audio.input", test_audio)

       # Verify
       assert len(store.get_state().messages) > 0
   ```

4. **UI Snapshot Tests:** Visual regression
   ```python
   async def test_main_screen(snap_compare):
       app = DigiChatApp()
       assert await snap_compare(app)
   ```

5. **Headless Tests:** Claude Code can run
   ```bash
   digichat-headless --scenario tests/basic.json
   ```

---

## 🐛 Debugging for Claude Code

### 1. State Inspection

```bash
# Get current state as JSON
digichat --dump-state > state.json
cat state.json | jq '.messages | length'
```

### 2. Event Monitoring

```bash
# Watch all events
digichat --debug 2>&1 | jq 'select(.event)'

# Filter specific events
digichat --debug 2>&1 | jq 'select(.event == "decoder.text")'
```

### 3. Scenario Testing

```json
// tests/scenarios/basic_cw.json
{
  "description": "Test CW decoding",
  "actions": [
    {"type": "CHANGE_MODE", "payload": {"mode": "CW"}}
  ],
  "audio_input": "tests/fixtures/cw_sos.wav",
  "expected_messages": [
    {"text": "SOS", "mode": "CW"}
  ]
}
```

```bash
digichat-headless --scenario tests/scenarios/basic_cw.json --output result.json
cat result.json | jq '.final_state.messages'
```

### 4. Performance Profiling

```bash
# Profile the application
python -m cProfile -o profile.stats -m digichat

# Analyze results
python -m pstats profile.stats
>>> sort time
>>> stats 20
```

---

## 📝 Next Steps

1. **Review all documentation:**
   - [ ] Read ARCHITECTURE_PLAN.md thoroughly
   - [ ] Review DECISIONS_NEEDED.md
   - [ ] Skim LIBRARY_GUIDE.md for reference

2. **Make critical decisions:**
   - [ ] Approve UI framework (Textual recommended)
   - [ ] Approve state management (Custom Redux recommended)
   - [ ] Approve audio threading (Queue-based recommended)
   - [ ] Choose config location

3. **Setup development environment:**
   - [ ] Install all dependencies
   - [ ] Verify tests run
   - [ ] Test audio devices
   - [ ] Test Textual works

4. **Begin Phase 1 implementation:**
   - [ ] Create directory structure
   - [ ] Implement core components
   - [ ] Write tests
   - [ ] Verify headless mode works

---

## 💡 Design Highlights

### What Makes This Architecture Special

1. **Testable from Day 1**
   - Headless mode built-in
   - Every component independently testable
   - Snapshot testing for UI

2. **Claude Code Optimized**
   - JSON logging (machine-readable)
   - State inspection commands
   - Scenario-based testing
   - No GUI needed

3. **Clean Architecture**
   - Clear separation of concerns
   - Predictable data flow
   - Easy to understand and modify

4. **Modern Stack**
   - Latest Python best practices (2024)
   - Active, maintained libraries
   - Async-first where appropriate

5. **Production Ready**
   - Structured logging
   - Error handling
   - Performance targets
   - Graceful degradation

---

## 📚 Additional Resources

### Internal Documentation
- [ARCHITECTURE_PLAN.md](ARCHITECTURE_PLAN.md) - Complete architecture
- [LIBRARY_GUIDE.md](LIBRARY_GUIDE.md) - Library details and examples
- [DECISIONS_NEEDED.md](DECISIONS_NEEDED.md) - Decision tracking
- [docs/architecture/README.md](architecture/README.md) - Original architecture notes

### External Resources
- [Textual Documentation](https://textual.textualize.io/)
- [Pypubsub Documentation](https://pypubsub.readthedocs.io/)
- [Sounddevice Documentation](https://python-sounddevice.readthedocs.io/)
- [Structlog Documentation](https://www.structlog.org/)
- [Redux Pattern](https://redux.js.org/understanding/thinking-in-redux/three-principles) (JavaScript, but concepts apply)

---

## 🤝 Questions?

If you're unclear on anything:

1. **Architecture questions:** See ARCHITECTURE_PLAN.md
2. **Library usage:** See LIBRARY_GUIDE.md
3. **Decisions:** See DECISIONS_NEEDED.md
4. **Implementation details:** Ask for clarification

This architecture is designed to be:
- **Understandable** - Clear documentation
- **Testable** - Headless mode + comprehensive tests
- **Debuggable** - Structured logging + state inspection
- **Maintainable** - Clean separation of concerns
- **Claude Code Friendly** - JSON output, scenarios, state dump

Ready to start implementation! 🚀
