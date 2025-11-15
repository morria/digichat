# DigiChat Design Critique

**Date:** 2025-11-15
**Reviewer:** Senior Software Engineering Consultant
**Status:** Pre-implementation Review

## Executive Summary

This architecture suffers from **over-engineering before validation**. You have 7,000+ lines of documentation for 200 lines of code. The design assumes complexity that may not exist and introduces abstractions (Redux, event bus, headless testing) that will slow initial development without proven benefit. **Recommendation: Start with 20% of this architecture and iterate based on real constraints.**

---

## Critical Issues

### 1. Redux Pattern for a TUI App is Overkill

**Problem:** Redux adds ~500 LOC of boilerplate (store, actions, reducers, middleware) for an application with simple state.

**Reality Check:**
- State is: current messages, current mode, audio config, radio status
- That's a ~100-line dataclass, not a Redux store
- You're not building a web app with complex async state management
- Time-travel debugging sounds cool but when will you actually use it?

**Simpler Alternative:**
```python
class AppState:
    messages: List[Message] = []
    current_mode: str = "CW"
    callbacks: List[Callable] = []

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        for cb in self.callbacks:
            cb(self)
```

**Impact:** Reduces complexity by ~500 LOC, eliminates learning curve, gets you to working code 2-3 weeks faster.

---

### 2. Textual vs. Curses: Premature Optimization

**Problem:** Textual is chosen primarily for "testing support" before you have anything to test.

**Questions:**
- Have you built a TUI app before? Curses works fine and is simpler.
- Will you actually write UI snapshot tests? (History suggests: probably not until much later)
- Is headless mode worth the dependency and learning curve *right now*?

**Simpler Alternative:**
- Start with `curses`. It's in stdlib, well-documented, and simpler.
- Test your DSP functions (the hard part) with audio files.
- Add Textual later *if* UI testing becomes a bottleneck (it won't be).

**Reality:** The hard parts are DSP algorithms (CW/PSK31/RTTY), not UI rendering. You're optimizing the wrong thing.

---

### 3. Event Bus (Pypubsub) Adds Unnecessary Indirection

**Problem:** Every component communicates via events, making data flow harder to trace.

**Example from your docs:**
```python
# Audio service publishes
EventBus.publish("audio.input", data=audio)

# Decoder subscribes
EventBus.subscribe("audio.input", self.on_audio_input)
```

**Simpler Alternative:**
```python
# Direct call
decoder.process_audio(audio_data)
```

**When Event Bus Makes Sense:**
- Multiple consumers for same event (you don't have this yet)
- Plugin architecture (not v1.0)
- Undo/redo (you don't need this)

**Impact:** Event bus adds debugging complexity (where is this event consumed?), testing complexity (setup/teardown), and cognitive load. Save it for v2 if you need it.

---

### 4. Headless Mode: Building for Tomorrow's Problems

**Problem:** Extensive "headless runner" infrastructure for Claude Code before having core functionality.

**Reality:**
- You can test DSP functions without any UI framework
- You can test with recorded audio files
- You don't need a "scenario runner" for initial development
- Your bottleneck will be algorithm correctness, not test infrastructure

**80/20 Approach:**
```python
# test_cw_decoder.py
def test_decode_sos():
    decoder = CWDecoder(wpm=20)
    audio = load_wav("test_fixtures/sos.wav")
    result = decoder.decode(audio)
    assert "SOS" in result
```

That's it. That's your test. No Redux, no event bus, no headless runner.

---

### 5. Three Digital Modes for v1.0 is Too Ambitious

**Problem:** Planning CW, PSK31, and RTTY for initial release.

**Reality Check:**
- PSK31 is complex: phase recovery, AFC, Varicode encoding
- RTTY is medium complexity: FSK demodulation, Baudot encoding
- CW is the simplest but still non-trivial

**Recommendation:** **CW ONLY for v1.0**

**Why:**
- CW captures 60%+ of digital mode users
- Proves your audio pipeline works
- Validates your UI concept
- Gets you to a working product in 1/3 the time

Add PSK31/RTTY in v1.1, v1.2 after you've learned from real users.

---

### 6. Hamlib Integration: Nice-to-Have, Not Must-Have

**Problem:** Including Hamlib in Phase 7 of a 10-week plan.

**Reality:** Most users won't use Hamlib initially. They'll use manual frequency control.

**Defer to v1.1** and get feedback on whether users actually want it.

---

### 7. State Management is Simpler Than You Think

**Your Architecture:**
- Redux store (50 LOC)
- Actions (100 LOC)
- Reducers (150 LOC)
- Middleware (100 LOC)
- Total: ~400 LOC

**Alternative:**
```python
@dataclass
class AppState:
    messages: List[Message] = field(default_factory=list)
    mode: str = "CW"
    audio_level: float = 0.0

    def add_message(self, text: str, direction: str):
        self.messages.append(Message(text, direction))
        self.notify_observers()
```

Total: ~50 LOC, does the same thing.

---

## Questionable Assumptions

### "Testability First"

**Claim:** "Headless mode and snapshot testing are critical for Claude Code."

**Reality:** Your critical path is:
1. Get audio I/O working
2. Decode CW correctly
3. Render UI

None of these require elaborate test infrastructure. You need:
- Audio file fixtures
- DSP algorithm tests
- Manual UI testing initially

### "Event-Driven Architecture"

**Claim:** "Event bus enables loose coupling."

**Counter:** In a single application with known components, loose coupling adds complexity without benefit. You're not building a plugin system.

### "10-Week Roadmap"

**Claim:** Detailed week-by-week plan through Phase 8.

**Reality:** You'll learn more in Week 1 of implementation than in all this planning. Roadmaps this detailed are fiction.

---

## Recommended Architecture (80/20 Version)

### Minimal Viable Architecture

```
┌─────────────────────────────────┐
│     Curses UI (stdlib)           │
│  - Message display               │
│  - Input field                   │
│  - Simple config panel           │
└──────────┬──────────────────────┘
           │
┌──────────┴──────────────────────┐
│     Application (1 file)         │
│  - AppState (dataclass)          │
│  - Message list                  │
│  - Current mode                  │
└──────────┬──────────────────────┘
           │
┌──────────┴──────────────────────┐
│     Audio I/O (sounddevice)      │
│  - Circular buffer               │
│  - Thread-based I/O              │
└──────────┬──────────────────────┘
           │
┌──────────┴──────────────────────┐
│     CW Decoder (NumPy/SciPy)     │
│  - Goertzel filter               │
│  - Envelope detection            │
│  - Morse timing                  │
└─────────────────────────────────┘
```

**Total Complexity:** ~1,000 LOC for working v1.0

**Your Architecture:** ~5,000+ LOC (based on estimates)

---

## Actionable Recommendations

### Phase 1: Prove the Concept (2 weeks)
1. **Get audio I/O working** (sounddevice + circular buffer)
2. **Implement basic CW decoder** (Goertzel + envelope)
3. **Build minimal curses UI** (message list + input)
4. **Test with recorded audio files**

**Success:** Decode "CQ CQ CQ" from a WAV file and display in UI.

### Phase 2: Make it Usable (2 weeks)
1. **Add CW encoder** (generate tones from text)
2. **Polish UI** (colors, layout, keyboard shortcuts)
3. **Add configuration** (WPM, audio device, tone frequency)
4. **Test with real radio** (if available)

**Success:** Working CW chat application.

### Phase 3: Learn and Iterate (2+ weeks)
1. **Get user feedback**
2. **Fix bugs from real usage**
3. **Decide if you need** Redux, event bus, Textual, etc.
4. **Consider adding** PSK31 or RTTY based on demand

---

## What to Keep from Current Design

**Good Ideas:**
- ✅ Sounddevice for audio I/O
- ✅ Queue-based threading for audio
- ✅ NumPy/SciPy for DSP
- ✅ Circular buffer for audio
- ✅ Dataclass-based configuration
- ✅ Focus on testable DSP algorithms

**Defer for Later:**
- ⏸ Redux state management (use simple observer pattern)
- ⏸ Event bus (use direct calls)
- ⏸ Textual (use curses)
- ⏸ Headless testing (test DSP directly)
- ⏸ Structlog (use logging stdlib initially)
- ⏸ PSK31/RTTY (add after CW works)
- ⏸ Hamlib (add after core works)

---

## Conclusion

You have built an **enterprise-grade architecture for a hobbyist TUI application**. The irony is that amateur radio operators prefer simple, working tools over architecturally pure systems.

**Core Principle:** Build the simplest thing that could possibly work, then evolve based on real constraints.

**Next Step:** Delete 80% of this documentation and write 1,000 lines of code. You'll learn more in a weekend of coding than in weeks of architectural planning.

The best architecture emerges from working code, not from planning documents.
