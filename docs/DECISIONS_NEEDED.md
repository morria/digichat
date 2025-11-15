# DigiChat: Decisions Needed

**Document Version:** 2.0
**Date:** 2025-11-15
**Purpose:** Track architectural and implementation decisions

**Status:** Architecture simplified based on design review. Key decisions finalized.

This document lists all decisions that need to be made before or during implementation. Each decision includes context, options, recommendations, and final decision status.

---

## Decision Status Legend

- ⏳ **PENDING** - Needs decision
- ✅ **DECIDED** - Decision made
- 🔄 **DEFERRED** - Deferred to later phase
- ❌ **REJECTED** - Not pursuing this option

---

## Critical Path Decisions (Phase 1)

These decisions must be made before starting implementation.

### D1: UI Framework Choice

**Status:** ✅ DECIDED - Textual

**Context:**
- Need TUI framework that's testable and supports headless mode
- Claude Code needs to run application without terminal
- Snapshot testing highly desirable
- Must support async operations

**Options:**

| Option | Pros | Cons | Complexity |
|--------|------|------|------------|
| **Textual** | ✅ Built-in testing<br>✅ Headless mode<br>✅ Snapshot tests<br>✅ Modern async<br>✅ Great docs | ⚠️ Newer (less mature)<br>⚠️ Additional dependency | Medium |
| **Plain curses** | ✅ Standard library<br>✅ Proven | ❌ Very hard to test<br>❌ No headless mode<br>❌ Complex code | High |
| **Urwid** | ✅ Mature<br>✅ Good docs | ⚠️ Limited testing<br>❌ No async<br>⚠️ Harder headless | Medium |

**Research Evidence:**
- Textual has `pytest-textual-snapshot` plugin (released Jan 2025)
- Textual `run_test()` provides headless mode out of the box
- Multiple production apps using Textual successfully
- curses testing requires `Expect` scripts or manual testing

**Recommendation:** **TEXTUAL**
- Testing support is critical for this project
- Headless mode is explicitly required for Claude Code
- Async support fits audio pipeline architecture
- Snapshot testing will catch UI regressions early

**Risks:**
- Textual is newer (but actively maintained)
- Could have undiscovered bugs (mitigated by good test coverage)

**Decision:**
- [x] **Approved:** Textual
- **Date:** 2025-11-15
- **Rationale:** Essential for headless testing support. Provides snapshot testing and async-first API that fits the architecture.

---

### D2: State Management Pattern

**Status:** ✅ DECIDED - Observable State Pattern (Simplified)

**Context:**
- Need predictable state management
- Must support debugging and time-travel
- State needs to be serializable for headless mode
- Want clear separation between state and side effects

**Options:**

| Option | Pros | Cons | Effort |
|--------|------|------|--------|
| **Custom Redux-like** | ✅ Full control<br>✅ Tailored to needs<br>✅ No dependency<br>✅ Easy to understand | ⚠️ Must implement (~200 LOC) | Low |
| **python-redux** | ✅ Pre-built<br>✅ Redux-compliant | ⚠️ Extra dependency<br>⚠️ May be overkill<br>⚠️ Small community | Very Low |
| **Simple dict + events** | ✅ Very simple | ❌ No structure<br>❌ Hard to debug<br>❌ No time-travel | Very Low |

**Research Evidence:**
- Redux pattern is well-understood and documented
- Custom implementation is ~200 lines (manageable)
- python-redux exists but not widely used (300 GitHub stars)
- Our needs are simple: single store, basic middleware

**Recommendation:** **Custom Redux-like Store**
- Implementation is straightforward
- Full control over features
- No external dependency
- Easy for other developers to understand
- Can add features as needed (time-travel debugging, etc.)

**Example Implementation Size:**
```python
class Store: ~50 lines
class Middleware: ~30 lines per middleware
Reducers: ~20 lines per reducer
Total: ~200-300 lines
```

**Decision:**
- [x] **Approved:** Observable State Pattern (simpler than Redux)
- **Date:** 2025-11-15
- **Rationale:** Provides same testability and serializability as Redux with 60% less code (~100 LOC vs ~400 LOC). Simpler to understand and debug. See SIMPLIFIED_ARCHITECTURE.md for implementation.

---

### D3: Audio Threading Architecture

**Status:** ✅ DECIDED - Queue-based threading

**Context:**
- Audio callback must be fast (avoid dropouts)
- Need testable architecture
- DSP processing can be slow
- Python GIL may be a factor

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| **Queue-based threading** | ✅ Safe for audio<br>✅ Testable<br>✅ Follows best practices<br>✅ Callback does minimal work | ⚠️ Slight latency (~20-50ms) |
| **Direct callback processing** | ✅ Lower latency | ❌ Risks dropouts<br>❌ Hard to test<br>❌ Violates best practices |
| **Multiprocessing** | ✅ Avoids GIL | ❌ Complex IPC<br>❌ Overkill<br>❌ Harder to debug |

**Research Evidence:**
- Sounddevice docs recommend queue-based approach
- Audio callback should do minimal work
- Queue acts as buffer against slow processing
- Standard pattern: callback → queue → processing thread → event bus

**Architecture:**
```
Audio Thread          Processing Thread       Main Thread
    |                       |                      |
callback() ──────┐          |                      |
    |            │          |                      |
    v            │          |                      |
put(queue) ◄─────┘          |                      |
    |                       |                      |
    |                  get(queue)                  |
    |                       |                      |
    |                   process()                  |
    |                       |                      |
    |                  publish(event)              |
    |                       |                      |
    |                       └────────────► handle_event()
```

**Recommendation:** **Queue-based Threading**
- Safest for audio (prevents dropouts)
- Testable (can mock queue)
- ~20-50ms latency is acceptable for our use case
- Follows sounddevice best practices

**Decision:**
- [x] **Approved:** Queue-based threading
- **Date:** 2025-11-15
- **Rationale:** Safest for audio (prevents dropouts), follows sounddevice best practices, and is testable with mocks.

---

### D4: Configuration File Location

**Status:** ✅ DECIDED - platformdirs

**Context:**
- Need to store user preferences
- Should follow OS conventions
- Must be human-editable

**Options:**

| Option | Location | Standard | Cross-platform |
|--------|----------|----------|----------------|
| **XDG Base Dir** | `~/.config/digichat/config.yaml` | ✅ Linux standard | ⚠️ Not Windows |
| **Simple home** | `~/.digichat/config.yaml` | ⚠️ Older convention | ✅ Works everywhere |
| **platformdirs** | Platform-specific paths | ✅ Most "correct" | ✅ Yes |

**Research Evidence:**
- Modern Linux apps use XDG Base Directory spec
- `platformdirs` library handles all platforms correctly
- Fallback to `~/.digichat` on older systems

**Recommendation:** **platformdirs with fallback**
```python
from platformdirs import user_config_dir

config_dir = Path(user_config_dir("digichat", "digichat"))
# Linux: ~/.config/digichat/
# macOS: ~/Library/Application Support/digichat/
# Windows: C:\Users\<user>\AppData\Local\digichat\
```

**Decision:**
- [x] **Approved:** platformdirs
- **Date:** 2025-11-15
- **Rationale:** Most "correct" approach, handles all platforms properly, follows modern OS conventions.

---

### D4A: Component Communication Pattern

**Status:** ✅ DECIDED - Direct Calls (No Event Bus)

**Context:**
- Need components to communicate (UI ↔ Services ↔ State)
- Original plan used pypubsub event bus for all communication
- Design review questioned if event bus adds unnecessary complexity

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| **Direct Calls** | ✅ Simple and traceable<br>✅ Clear call stacks<br>✅ Easy to test | ⚠️ Slightly more coupling |
| **Event Bus (pypubsub)** | ✅ Loose coupling | ⚠️ Hard to trace<br>⚠️ Complex setup<br>⚠️ Extra dependency |
| **Hybrid** | ✅ Direct calls + queues for audio | ✅ Best of both |

**Recommendation:** **Direct Calls + Queues**
- Use direct method calls for most communication (simple, traceable)
- Use queues only for audio threading (required for thread safety)
- No event bus needed - YAGNI principle applies

**Decision:**
- [x] **Approved:** Direct calls + queues (no event bus)
- **Date:** 2025-11-15
- **Rationale:** Simpler, more traceable, easier to debug. Queues only where actually needed (audio threading). Event bus is over-engineering for this use case.

---

## Implementation Decisions (Phase 2-3)

These can be decided during early implementation phases.

### D5: CW Decoder Implementation

**Status:** ⏳ PENDING

**Context:**
- First digital mode to implement
- Need tone detection and timing analysis
- Multiple implementation options available

**Options:**

| Option | Pros | Cons | Effort |
|--------|------|------|--------|
| **Custom (Goertzel)** | ✅ Full control<br>✅ Learning value<br>✅ Can optimize | ⚠️ More work | Medium (2-3 days) |
| **morse-audio-decoder** | ✅ Quick start<br>✅ Proven | ⚠️ Less control<br>⚠️ May not fit architecture | Low (integration) |
| **Hybrid approach** | ✅ Use library, enhance as needed | ⚠️ Dependency on external code | Low-Medium |

**Recommendation:** **Try library first, custom fallback**
1. Start with `morse-audio-decoder` library
2. If it doesn't integrate well, implement custom
3. Custom implementation is well-documented (Goertzel + envelope)

**Decision:**
- [ ] **Try library first**
- [ ] **Custom implementation**
- [ ] **Deferred to Phase 3**

---

### D6: PSK31 Decoder Implementation

**Status:** ⏳ PENDING

**Context:**
- Complex mode (phase recovery, AFC, Varicode)
- No mature Python library available
- High effort but high educational value

**Options:**

| Option | Approach | Complexity |
|--------|----------|------------|
| **Full featured** | BPSK + AFC + Varicode | Very High |
| **Minimal viable** | Basic BPSK, add features incrementally | Medium → High |
| **Skip for v1** | Focus on CW and RTTY only | N/A |

**Recommendation:** **Incremental implementation**
1. Phase 1: Basic BPSK demodulation
2. Phase 2: Add Varicode decoding
3. Phase 3: Add basic AFC
4. Phase 4: Enhance AFC and add squelch

**Benefits:**
- Working PSK31 earlier (even if basic)
- Can test and iterate
- Learn the algorithms step-by-step

**Decision:**
- [ ] **Incremental approach**
- [ ] **Full implementation upfront**
- [ ] **Defer to v2**

---

### D7: Test Audio Generation Strategy

**Status:** ⏳ PENDING

**Context:**
- Need audio files for testing decoders
- Want reproducible tests
- May also need realistic recorded samples

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| **Synthetic generation** | ✅ Reproducible<br>✅ Parameterizable<br>✅ No storage | ⚠️ May not match reality |
| **Recorded samples** | ✅ Realistic<br>✅ Edge cases | ❌ Large files<br>❌ Not reproducible |
| **Both** | ✅ Best of both | ⚠️ More maintenance |

**Recommendation:** **Both strategies**
- Synthetic for unit tests (fast, reproducible)
  - Generate CW tones programmatically
  - Generate PSK31 test signals
  - Generate RTTY test signals
- Recorded samples for integration tests
  - Record real on-air signals
  - Include weak signals, noise, QSB
  - Store in `tests/fixtures/realistic/`

**Script to create:**
```bash
python scripts/generate_test_audio.py \
  --mode CW \
  --text "CQ CQ CQ DE K6XXX" \
  --wpm 20 \
  --output tests/fixtures/cw_cq_20wpm.wav
```

**Decision:**
- [ ] **Both synthetic + recorded**
- [ ] **Synthetic only**
- [ ] **Notes:** _________________

---

### D8: Hamlib Integration Method

**Status:** 🔄 DEFERRED (Phase 7)

**Context:**
- Need radio control (optional feature)
- Hamlib provides CAT control
- Multiple ways to integrate

**Options:**

| Option | Pros | Cons |
|--------|------|------|
| **python-hamlib** | ✅ Native Python | ⚠️ May not exist/maintained |
| **rigctl subprocess** | ✅ Hamlib is stable<br>✅ No bindings needed | ⚠️ Subprocess overhead |
| **Python ctypes** | ✅ Direct library access | ⚠️ Complex<br>⚠️ Platform-specific |

**Research Needed:**
- Does python-hamlib exist and is it maintained?
- What's the performance of subprocess approach?

**Recommendation:** **Research during Phase 7**
- Not needed until later
- Can prototype both approaches
- Defer until Phases 1-6 complete

**Decision:**
- [ ] **Deferred to Phase 7**

---

## Feature Scope Decisions

These determine what goes in v1.0 vs. future versions.

### D9: Waterfall Display

**Status:** ⏳ PENDING

**Question:** Include text-based waterfall in v1.0?

**Context:**
- Waterfall shows frequency spectrum over time
- Can help tune to signals
- Complex to implement in text mode

**Options:**
- **Include in v1.0:** Use Unicode blocks, update in real-time
- **Defer to v1.1:** Focus on core functionality first
- **Skip entirely:** Not critical for operation

**Recommendation:** **Defer to v1.1**
- Not critical for basic operation
- Adds significant complexity
- Can gauge user interest first
- V1.0 already has full features (3 modes, Hamlib)

**Decision:**
- [ ] **Defer to v1.1+**
- [ ] **Include in v1.0**
- [ ] **Skip entirely**

---

### D10: QSO Logging Format

**Status:** ⏳ PENDING

**Question:** What format for logging contacts?

**Options:**

| Format | Pros | Cons | Effort |
|--------|------|------|--------|
| **Plain text** | ✅ Simple<br>✅ Human readable | ⚠️ Not standard | Very Low |
| **ADIF** | ✅ Standard<br>✅ Import to logbook software | ⚠️ More complex | Medium |
| **Both** | ✅ Best of both | ⚠️ More code | Medium |

**Recommendation:** **Start with text, add ADIF later**
- Text log is immediately useful
- ADIF can be added in v1.1
- ADIF library exists: `adif-io`

**V1.0 Approach:**
```
# Simple text log
2025-11-15 14:30:00 [CW] RX: CQ CQ CQ DE W1ABC
2025-11-15 14:30:15 [CW] TX: W1ABC DE K6XXX K
2025-11-15 14:30:30 [CW] RX: K6XXX UR 599 599 NAME BOB BOB
```

**Decision:**
- [ ] **Text for v1.0, ADIF for v1.1**
- [ ] **ADIF from start**
- [ ] **Notes:** _________________

---

### D11: Performance Targets

**Status:** ⏳ PENDING

**Question:** What are acceptable performance metrics?

**Proposed Targets:**

| Metric | Target | Rationale |
|--------|--------|-----------|
| RX Latency (audio → display) | < 100ms | Feels real-time, acceptable for digital modes |
| TX Latency (keypress → audio) | < 50ms | User expects instant feedback |
| CPU Usage (idle) | < 5% | Background operation |
| CPU Usage (active) | < 25% | One core, allows other apps to run |
| Memory Usage | < 100MB | Reasonable for audio app |
| Audio Dropouts | 0 per hour | Professional quality |

**Testing Approach:**
- Profile with `cProfile` during development
- Use `pytest-benchmark` for performance tests
- Test on modest hardware (not just dev machines)

**Decision:**
- [ ] **Approve targets as stated**
- [ ] **Modify:** _________________

---

## Summary of Decisions

### ✅ FINALIZED (Implementation Ready)

These decisions have been made and are ready for implementation:

1. ✅ **UI Framework:** Textual (D1)
   - Essential for headless testing
   - Snapshot testing support
   - Async-first API

2. ✅ **State Management:** Observable State Pattern (D2)
   - Simpler than Redux (~100 LOC vs ~400)
   - Full testability maintained
   - Easy to understand and debug

3. ✅ **Component Communication:** Direct Calls + Queues (D4A)
   - Direct method calls (simple, traceable)
   - Queues only for audio threading
   - No event bus complexity

4. ✅ **Audio Threading:** Queue-based (D3)
   - Safest for audio
   - Follows best practices
   - Testable with mocks

5. ✅ **Configuration Storage:** platformdirs (D4)
   - Cross-platform support
   - Follows OS conventions

6. ✅ **Logging:** Structlog (kept from original)
   - JSON output for headless mode
   - Essential for Claude Code debugging

### RECOMMENDED (Decide During Implementation)

These can be decided as we reach relevant phases:

6. ⏳ **CW Implementation:** Try library first, custom fallback
7. ⏳ **PSK31 Implementation:** Incremental approach
8. ⏳ **Test Audio:** Both synthetic and recorded
9. ⏳ **Config Location:** platformdirs (or simple ~/.digichat)

### DEFERRED (Not Critical for v1.0)

These can wait until later:

10. 🔄 **Hamlib Integration:** Decide in Phase 7
11. 🔄 **Waterfall:** Defer to v1.1
12. 🔄 **ADIF Logging:** Defer to v1.1

---

## Decision Process

When making decisions:

1. **Review research evidence** in ARCHITECTURE_PLAN.md
2. **Consider constraints:**
   - Testing requirements (headless mode)
   - Claude Code integration
   - Development time
   - Maintenance burden
3. **Document decision** in this file
4. **Update relevant docs** if decision changes architecture
5. **Create ADR** (Architecture Decision Record) for major decisions

---

## Next Steps

1. **Review all PENDING decisions with team/stakeholders**
2. **Approve STRONGLY RECOMMENDED items** (or provide alternatives)
3. **Set timeline** for RECOMMENDED decisions
4. **Confirm DEFERRED items** can wait
5. **Begin Phase 1 implementation** once critical decisions made

---

**Decision Log**

| Date | Decision | Who | Outcome |
|------|----------|-----|---------|
| YYYY-MM-DD | D1: UI Framework | Name | Textual approved |
| | | | |

