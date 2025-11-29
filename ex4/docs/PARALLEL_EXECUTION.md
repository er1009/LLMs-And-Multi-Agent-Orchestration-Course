# Parallel Execution with Threading

## Overview

The Route Guide System implements **parallel agent execution** using Python's threading capabilities. This document explains the implementation, benefits, and technical details.

## Architecture

### Threading Model

Each waypoint is processed by three content discovery agents:
- **Video Agent**: Finds YouTube videos
- **Music Agent**: Recommends music
- **Info Agent**: Provides historical information

These agents run **concurrently in separate threads** rather than sequentially.

```
┌─────────────────────────────────────────────────────┐
│              Main Thread (Orchestrator)              │
└───────────────────┬─────────────────────────────────┘
                    │
                    ├─→ ThreadPoolExecutor (max_workers=3)
                    │
        ┌───────────┼───────────┬────────────┐
        │           │           │            │
        ↓           ↓           ↓            │
   ┌────────┐  ┌────────┐  ┌────────┐       │
   │Thread-1│  │Thread-2│  │Thread-3│       │
   │ Video  │  │ Music  │  │  Info  │       │
   │ Agent  │  │ Agent  │  │ Agent  │       │
   └───┬────┘  └───┬────┘  └───┬────┘       │
       │           │           │            │
       │     Execute Claude    │            │
       │      CLI (async)      │            │
       │           │           │            │
       └───────────┴───────────┴────────────┘
                    │
                    ↓
           Collect Results (as_completed)
                    │
                    ↓
            ┌───────────────┐
            │ Choice Agent  │
            │ (Main Thread) │
            └───────────────┘
```

## Implementation

### Code Structure

**Orchestrator** (`src/orchestrator.py`):
```python
def _process_waypoint_parallel(self, address: str) -> ChoiceResult:
    """Run agents in parallel using ThreadPoolExecutor."""

    with ThreadPoolExecutor(max_workers=3, thread_name_prefix="AgentThread") as executor:
        # Submit all three agents
        futures = {
            executor.submit(run_video_agent): 'video',
            executor.submit(run_music_agent): 'music',
            executor.submit(run_info_agent): 'info'
        }

        # Collect results as they complete
        for future in as_completed(futures):
            agent_type, result = future.result()
            results[agent_type] = result

    # Choice agent selects best option
    return self.choice_agent.select_best(...)
```

### Thread Safety

**Why Threading is Safe:**

1. **Independent Agents**: Each agent is an independent object with no shared mutable state
2. **Subprocess Calls**: Claude CLI calls use `subprocess`, which is thread-safe
3. **No Global State**: Agents don't modify global variables
4. **Thread-Safe Logging**: Python's logging module is thread-safe by default
5. **Immutable Inputs**: Address string passed to agents is immutable

**Thread-Safe Practices:**
- Each thread has its own stack and local variables
- Results stored in thread-local dictionary
- No locks or synchronization primitives needed (no shared mutable state)
- Error handling per thread prevents cascading failures

## Performance Benefits

### Timing Comparison

**Sequential Execution:**
```
Video Agent: 10s
Music Agent: 10s
Info Agent:  10s
-----------------
Total:       30s per waypoint
```

**Parallel Execution:**
```
Video Agent: ────────── (10s)
Music Agent: ────────── (10s) } All concurrent
Info Agent:  ────────── (10s)
---------------------------------
Total:       ~10s per waypoint
```

### Real-World Impact

For a 10-waypoint route:
- **Sequential**: 10 waypoints × 30s = 300s (5 minutes)
- **Parallel**: 10 waypoints × 10s = 100s (1.67 minutes)
- **Speedup**: **3x faster** ⚡

## Configuration

### Enable/Disable Parallel Execution

In `config/config.yaml`:

```yaml
system:
  parallel_execution: true   # true = parallel, false = sequential
  max_agent_threads: 3       # Number of concurrent threads
```

### When to Disable Parallel Execution

Disable (`parallel_execution: false`) when:
- **Debugging**: Sequential execution easier to trace
- **Resource Constraints**: Limited CPU or memory
- **Threading Issues**: Platform-specific threading problems
- **Testing**: Deterministic execution for tests

## Technical Details

### ThreadPoolExecutor Configuration

```python
ThreadPoolExecutor(
    max_workers=3,              # Maximum concurrent threads
    thread_name_prefix="AgentThread"  # Thread naming for debugging
)
```

### Error Handling

Each thread has independent error handling:

```python
def run_video_agent():
    try:
        result = self.video_agent.execute(address)
        return ('video', result)
    except Exception as e:
        logger.error(f"[Thread-Video] Failed: {e}")
        return ('video', error_result)
```

**Error Behavior:**
- Individual thread failure doesn't crash the program
- Failed agents return error `AgentResult` (success=False)
- Choice agent can still select from partial results
- All errors are logged with thread context

### Future Collection

```python
for future in as_completed(future_to_agent):
    agent_name = future_to_agent[future]
    agent_type, result = future.result()
    results[agent_type] = result
```

**Benefits:**
- Returns results as soon as each agent completes
- Faster agents don't wait for slower ones
- Efficient resource utilization

## Testing

### Threading Tests

Located in `tests/test_threading.py`:

1. **Concurrency Test**: Verifies parallel execution is faster than sequential
2. **Error Handling Test**: Ensures thread failures are handled gracefully
3. **Thread Safety Test**: Confirms agents don't interfere with each other
4. **Configuration Test**: Validates parallel/sequential mode switching

### Running Tests

```bash
# Run all tests including threading
pytest

# Run only threading tests
pytest tests/test_threading.py

# Run with verbose output
pytest tests/test_threading.py -v
```

## Debugging

### Enable Debug Logging

Set `LOG_LEVEL=DEBUG` in `.env`:

```env
LOG_LEVEL=DEBUG
```

Debug logs show thread execution:
```
[Thread-Video] Starting for Times Square, NY
[Thread-Music] Starting for Times Square, NY
[Thread-Info] Starting for Times Square, NY
[Thread-Video] Completed for Times Square, NY
[Thread-Music] Completed for Times Square, NY
[Thread-Info] Completed for Times Square, NY
[Parallel] All agents completed
```

### Sequential Mode for Debugging

Temporarily disable parallel execution:

```yaml
# config/config.yaml
system:
  parallel_execution: false
```

Or via command line:
```bash
# Edit config before running
python -m src.main --source "New York" --destination "Boston"
```

## Best Practices

### Do's ✅
- Keep agents stateless and independent
- Handle errors within each thread
- Use thread-safe logging
- Configure appropriate timeout values
- Monitor thread pool size

### Don'ts ❌
- Don't share mutable state between agents
- Don't use global variables modified by agents
- Don't create threads manually (use ThreadPoolExecutor)
- Don't ignore thread exceptions
- Don't exceed available CPU cores unnecessarily

## Performance Tuning

### Thread Pool Size

Default: 3 threads (one per agent)

```yaml
system:
  max_agent_threads: 3  # Optimal for 3 agents
```

**Tuning Considerations:**
- Too few threads: Won't utilize all agents
- Too many threads: Context switching overhead
- **Recommended**: Match number of agents (3)

### Claude CLI Timeout

Adjust per-agent timeout if needed:

```yaml
agents:
  video:
    timeout: 30  # Seconds
  music:
    timeout: 30
  info:
    timeout: 30
```

## Limitations

1. **GIL (Global Interpreter Lock)**: Python's GIL limits true parallelism
   - **However**: Agents spend most time waiting on I/O (Claude CLI subprocess)
   - **Result**: Threading still provides 3x speedup for I/O-bound tasks

2. **No Process-Based Parallelism**: Currently uses threads, not processes
   - **Future Enhancement**: Could use `ProcessPoolExecutor` for CPU-bound operations

3. **Fixed Thread Count**: Thread pool size matches agent count (3)
   - **Future Enhancement**: Dynamic thread pool sizing

## Monitoring

### Metrics to Track

- **Average execution time per waypoint**
- **Thread failure rate**
- **Agent success rates**
- **Total processing time per route**

### Output Metadata

Check `metadata` in output JSON:
```json
{
  "metadata": {
    "processed_stops": 10,
    "processing_time_seconds": 120.5,
    "timestamp": "2025-11-29T10:30:00"
  }
}
```

**Calculate average:**
```
Average per waypoint = processing_time_seconds / processed_stops
```

## Related Documentation

- **Architecture**: See `ARCHITECTURE.md` (ADR-001) for design decision
- **PRD**: See `PRD.md` for performance requirements
- **README**: See main `README.md` for usage instructions
- **Tests**: See `tests/test_threading.py` for test coverage

## Conclusion

Parallel execution using threading provides a **3x performance improvement** with minimal complexity. The implementation is:
- ✅ Thread-safe
- ✅ Well-tested
- ✅ Configurable
- ✅ Production-ready

For most use cases, **parallel execution should remain enabled** (default setting).

---

**Last Updated**: 2025-11-29
**Status**: Production Ready
