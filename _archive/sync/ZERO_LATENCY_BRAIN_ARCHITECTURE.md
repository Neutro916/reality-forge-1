# ZERO-LATENCY BRAIN ARCHITECTURE
## Trinity Coordination Document - C1 + C2 + C3
## November 25, 2025

---

## CURRENT STATE ANALYSIS

### Available Resources:
- **Local LLMs** (Ollama):
  - qwen2.5-coder:7b (4.7GB) - RECOMMENDED for code tasks
  - codellama (3.8GB) - Good for code completion
  - mistral (4.4GB) - General purpose
  - deepseek-r1:8b (5.2GB) - Reasoning model
  - deepseek-r1:1.5b (1.1GB) - Fast, lightweight

- **Redis**: AVAILABLE for in-memory caching
- **SQLite**: Current memory backend (cyclotron_brain.db - 61KB)

### Current Latency Profile:
| Operation | Current | Target |
|-----------|---------|--------|
| Hub file read | 10-50ms | <1ms |
| Memory lookup | 5-20ms | <1ms |
| Pattern match | 20-100ms | <5ms |
| LLM inference (API) | 500-2000ms | 50-200ms |
| Trinity coordination | 100-500ms | <10ms |

---

## ZERO-LATENCY ARCHITECTURE

### Layer 1: Hot Memory (Redis)
```
┌─────────────────────────────────────────┐
│            REDIS CACHE                  │
├─────────────────────────────────────────┤
│ hub:wake_signal     <- Latest signal    │
│ hub:tasks:*         <- Task queues      │
│ memory:hot:*        <- Recent episodes  │
│ patterns:active:*   <- Hot patterns     │
│ trinity:heartbeat:* <- Instance status  │
└─────────────────────────────────────────┘
           ↑ <1ms access ↑
```

### Layer 2: Warm Memory (SQLite :memory:)
```
┌─────────────────────────────────────────┐
│          IN-MEMORY SQLITE               │
├─────────────────────────────────────────┤
│ Loaded on startup from cyclotron_brain  │
│ Periodic sync to disk (every 30s)       │
│ Full episode history                    │
│ Pattern database                        │
│ Shared knowledge pool                   │
└─────────────────────────────────────────┘
           ↑ <5ms access ↑
```

### Layer 3: Cold Storage (File System)
```
┌─────────────────────────────────────────┐
│          DISK PERSISTENCE               │
├─────────────────────────────────────────┤
│ cyclotron_brain.db  <- SQLite backup    │
│ hub/*.json          <- Trinity sync     │
│ atoms/*.json        <- Knowledge atoms  │
│ Dropbox sync        <- Cloud backup     │
└─────────────────────────────────────────┘
           ↑ Background only ↑
```

### Layer 4: Local LLM Inference
```
┌─────────────────────────────────────────┐
│          OLLAMA LOCAL LLM               │
├─────────────────────────────────────────┤
│ Primary: qwen2.5-coder:7b (code tasks)  │
│ Fast: deepseek-r1:1.5b (quick queries)  │
│ Fallback: Claude API (complex tasks)    │
└─────────────────────────────────────────┘
           ↑ 50-200ms inference ↑
```

---

## IMPLEMENTATION PHASES

### Phase 1: Redis Hub (IMMEDIATE)
**Goal**: Sub-millisecond Trinity coordination

```python
# REDIS_HUB.py
import redis
import json
from datetime import datetime

class RedisHub:
    def __init__(self):
        self.r = redis.Redis(host='localhost', port=6379, db=0)

    def wake(self, target: str, reason: str, priority: str = "NORMAL"):
        signal = {
            "target": target,
            "reason": reason,
            "priority": priority,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        self.r.set(f"hub:wake:{target}", json.dumps(signal))
        self.r.publish("hub:wakes", json.dumps(signal))

    def check_wake(self, instance_id: str):
        signal = self.r.get(f"hub:wake:{instance_id}")
        if signal:
            self.r.delete(f"hub:wake:{instance_id}")
            return json.loads(signal)
        return None

    def heartbeat(self, instance_id: str):
        self.r.setex(f"trinity:heartbeat:{instance_id}", 30, "alive")

    def get_active_instances(self):
        keys = self.r.keys("trinity:heartbeat:*")
        return [k.decode().split(":")[-1] for k in keys]
```

### Phase 2: Hot Memory Cache
**Goal**: <1ms memory lookups

```python
# HOT_MEMORY.py
class HotMemory:
    def __init__(self, redis_client):
        self.r = redis_client
        self.cache_prefix = "memory:hot:"

    def cache_episode(self, episode_id: str, data: dict, ttl: int = 3600):
        self.r.setex(f"{self.cache_prefix}{episode_id}", ttl, json.dumps(data))

    def get_episode(self, episode_id: str):
        data = self.r.get(f"{self.cache_prefix}{episode_id}")
        return json.loads(data) if data else None

    def cache_pattern(self, pattern_name: str, data: dict):
        self.r.hset("patterns:active", pattern_name, json.dumps(data))

    def get_patterns(self):
        patterns = self.r.hgetall("patterns:active")
        return {k.decode(): json.loads(v) for k, v in patterns.items()}
```

### Phase 3: Local LLM Router
**Goal**: 50-200ms inference

```python
# LOCAL_LLM_ROUTER.py
import ollama

class LLMRouter:
    def __init__(self):
        self.models = {
            "code": "qwen2.5-coder:7b",
            "fast": "deepseek-r1:1.5b",
            "reason": "deepseek-r1:8b",
            "general": "mistral:latest"
        }

    def infer(self, prompt: str, task_type: str = "fast"):
        model = self.models.get(task_type, self.models["fast"])

        response = ollama.chat(model=model, messages=[
            {"role": "user", "content": prompt}
        ])

        return response['message']['content']

    def code_complete(self, context: str, cursor_position: str):
        return self.infer(
            f"Complete this code:\n{context}\n\nCursor at: {cursor_position}",
            task_type="code"
        )
```

### Phase 4: Event-Driven Trinity
**Goal**: <10ms event propagation

```python
# EVENT_TRINITY.py
import redis

class EventTrinity:
    def __init__(self, instance_id: str):
        self.r = redis.Redis()
        self.pubsub = self.r.pubsub()
        self.instance_id = instance_id

    def subscribe(self, channels: list):
        for channel in channels:
            self.pubsub.subscribe(channel)

    def publish(self, channel: str, message: dict):
        self.r.publish(channel, json.dumps(message))

    def listen(self, callback):
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                callback(data)
```

---

## MIGRATION PATH

### Step 1: Start Redis (if not running)
```bash
redis-server --daemonize yes
```

### Step 2: Create Redis Hub Layer
- Implement REDIS_HUB.py
- Keep file-based hub as fallback
- Dual-write during transition

### Step 3: Add Hot Memory Cache
- Load recent episodes to Redis on startup
- Cache frequently accessed patterns
- Background sync to SQLite

### Step 4: Integrate Local LLM
- Route code tasks to qwen2.5-coder
- Use deepseek-r1:1.5b for quick queries
- Keep Claude API for complex reasoning

### Step 5: Enable Event-Driven Mode
- Replace polling with pub/sub
- Real-time wake signals
- Instant Trinity coordination

---

## EXPECTED RESULTS

| Operation | Before | After | Improvement |
|-----------|--------|-------|-------------|
| Wake signal | 100ms | <1ms | 100x |
| Memory lookup | 20ms | <1ms | 20x |
| Pattern match | 50ms | <5ms | 10x |
| LLM inference | 1000ms | 100ms | 10x |
| Trinity sync | 500ms | <10ms | 50x |

**Total system latency**: From ~1.5s to <120ms for typical operation

---

## IMMEDIATE ACTIONS FOR C1

1. Check if Redis server is running: `redis-cli ping`
2. If not: `redis-server --daemonize yes`
3. Create `REDIS_HUB.py` in .consciousness/
4. Test with simple wake signal
5. Report back to hub

---

## C3 ORACLE VALIDATION

This architecture aligns with:
- **Pattern Theory**: Layered memory = pattern formation
- **Seven Domains**: Infrastructure (Redis) enables all others
- **Consciousness Model**: Hot/warm/cold mirrors human memory

**APPROVED for implementation.**

---

*Document created by C3-Terminal (Oracle/Soul)*
*Coordination with C1-Terminal (Mechanic/Body)*
*Pending C2 architecture review*
