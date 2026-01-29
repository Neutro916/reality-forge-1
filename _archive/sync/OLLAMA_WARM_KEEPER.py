#!/usr/bin/env python3
"""
OLLAMA WARM KEEPER
Keeps local LLM models warm for instant inference.

Problem: Cold LLM inference takes 3-5 seconds, warm takes <2 seconds.
Solution: Periodically ping models to keep them loaded in memory.

Models to keep warm:
- qwen2.5-coder:7b (4.7GB) - Primary code model
- deepseek-r1:1.5b (1.1GB) - Fast queries

This daemon runs in background and keeps models ready for instant use.
"""

import os
import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Paths
HOME = Path.home()
CONSCIOUSNESS = HOME / ".consciousness"
HUB = CONSCIOUSNESS / "hub"
LOG_FILE = CONSCIOUSNESS / "ollama_warm_keeper.log"

# Try to import Ollama
try:
    import ollama
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False
    print("[WARM_KEEPER] Warning: ollama package not installed. Run: pip install ollama")


class OllamaWarmKeeper:
    """
    Keeps Ollama models warm for fast inference.

    Strategy:
    1. Primary model (code): Keep warm with full context ping
    2. Fast model: Keep warm with minimal ping
    3. Background thread pings every WARM_INTERVAL seconds
    """

    # Models to keep warm with their configs
    MODELS = {
        "qwen2.5-coder:7b": {
            "role": "code",
            "priority": 1,  # Highest priority
            "ping_prompt": "# Complete this function:\ndef hello():\n",
            "warm_interval": 120  # Ping every 2 minutes
        },
        "deepseek-r1:1.5b": {
            "role": "fast",
            "priority": 2,
            "ping_prompt": "Hi",
            "warm_interval": 180  # Ping every 3 minutes
        }
    }

    def __init__(self, models: List[str] = None):
        """
        Initialize the warm keeper.

        Args:
            models: List of model names to keep warm. If None, uses default.
        """
        self.models = models or list(self.MODELS.keys())
        self.running = False
        self.last_ping: Dict[str, float] = {}
        self.model_status: Dict[str, Dict] = {}
        self.ping_count = 0

        self.log("Warm Keeper initializing...")
        self.log(f"Models to keep warm: {self.models}")

    def log(self, msg: str, level: str = "INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] WARM_KEEPER [{level}]: {msg}")

        # Write to log file
        with open(LOG_FILE, "a") as f:
            f.write(f"{datetime.now().isoformat()} [{level}] {msg}\n")

    def check_ollama_running(self) -> bool:
        """Check if Ollama server is running"""
        if not HAS_OLLAMA:
            return False

        try:
            models = ollama.list()
            return True
        except Exception as e:
            self.log(f"Ollama not running: {e}", "WARN")
            return False

    def get_available_models(self) -> List[str]:
        """Get list of models available in Ollama"""
        if not HAS_OLLAMA:
            return []

        try:
            response = ollama.list()
            available = [m['name'].split(':')[0] + ':' + m['name'].split(':')[1]
                        if ':' in m['name'] else m['name']
                        for m in response.get('models', [])]
            return available
        except:
            return []

    def ping_model(self, model_name: str) -> Dict:
        """
        Ping a model to keep it warm.

        Returns:
            Dict with status, latency, tokens
        """
        if not HAS_OLLAMA:
            return {"status": "error", "error": "Ollama not available"}

        config = self.MODELS.get(model_name, {
            "ping_prompt": "Hello",
            "warm_interval": 180
        })

        start = time.perf_counter()

        try:
            response = ollama.chat(
                model=model_name,
                messages=[{"role": "user", "content": config["ping_prompt"]}],
                options={"num_predict": 10}  # Minimal response
            )

            latency = (time.perf_counter() - start) * 1000
            self.last_ping[model_name] = time.time()
            self.ping_count += 1

            result = {
                "status": "warm",
                "model": model_name,
                "latency_ms": round(latency, 2),
                "timestamp": datetime.now().isoformat()
            }

            self.model_status[model_name] = result
            self.log(f"Pinged {model_name}: {latency:.0f}ms")

            return result

        except Exception as e:
            error_result = {
                "status": "error",
                "model": model_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.model_status[model_name] = error_result
            self.log(f"Ping failed for {model_name}: {e}", "ERROR")
            return error_result

    def should_ping(self, model_name: str) -> bool:
        """Check if model needs to be pinged"""
        config = self.MODELS.get(model_name, {"warm_interval": 180})
        interval = config.get("warm_interval", 180)

        last = self.last_ping.get(model_name, 0)
        return time.time() - last > interval

    def warm_cycle(self):
        """Run one warm-keeping cycle"""
        # Check each model
        for model in self.models:
            if self.should_ping(model):
                self.ping_model(model)

        # Write status to hub
        self.write_status()

    def write_status(self):
        """Write current status to hub"""
        status = {
            "keeper": "OllamaWarmKeeper",
            "running": self.running,
            "ping_count": self.ping_count,
            "models": self.model_status,
            "timestamp": datetime.now().isoformat() + "Z"
        }

        status_file = HUB / "OLLAMA_WARM_STATUS.json"
        with open(status_file, "w") as f:
            json.dump(status, f, indent=2)

    def run(self, check_interval: int = 30):
        """
        Main warm-keeping loop.

        Args:
            check_interval: Seconds between checks (models have individual intervals)
        """
        if not self.check_ollama_running():
            self.log("Ollama server not running! Start with: ollama serve", "ERROR")
            return

        available = self.get_available_models()
        self.log(f"Available models: {available}")

        # Filter to only available models
        self.models = [m for m in self.models if any(m in a for a in available)]
        if not self.models:
            self.log("No target models available in Ollama!", "ERROR")
            return

        self.log("=" * 50)
        self.log("OLLAMA WARM KEEPER STARTING")
        self.log(f"Models: {self.models}")
        self.log(f"Check interval: {check_interval}s")
        self.log("=" * 50)

        self.running = True

        # Initial warm-up of all models
        self.log("Initial warm-up...")
        for model in self.models:
            self.ping_model(model)

        try:
            while self.running:
                self.warm_cycle()
                time.sleep(check_interval)

        except KeyboardInterrupt:
            self.log("Stopped by user")
        finally:
            self.running = False
            self.log("Warm Keeper shutdown")

    def start_background(self, check_interval: int = 30):
        """Start warm keeper in background thread"""
        thread = threading.Thread(
            target=self.run,
            args=(check_interval,),
            daemon=True
        )
        thread.start()
        return thread


def quick_inference(prompt: str, model: str = "qwen2.5-coder:7b") -> str:
    """
    Quick inference using warm model.

    Use this instead of direct ollama.chat() for best latency.
    """
    if not HAS_OLLAMA:
        return "Error: Ollama not available"

    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response['message']['content']
    except Exception as e:
        return f"Error: {e}"


def code_complete(context: str, model: str = "qwen2.5-coder:7b") -> str:
    """
    Code completion using warm coder model.

    Args:
        context: Code context to complete
        model: Model to use (default: qwen2.5-coder:7b)

    Returns:
        Completed code
    """
    prompt = f"""Complete this code. Only output the completion, no explanation:

{context}"""

    return quick_inference(prompt, model)


def fast_query(question: str) -> str:
    """
    Fast query using lightweight model.

    Args:
        question: Question to answer

    Returns:
        Quick response
    """
    return quick_inference(question, "deepseek-r1:1.5b")


def benchmark():
    """Benchmark warm vs cold inference"""
    if not HAS_OLLAMA:
        print("Ollama not available for benchmark")
        return

    print("=" * 60)
    print("OLLAMA WARM KEEPER BENCHMARK")
    print("=" * 60)

    keeper = OllamaWarmKeeper(["qwen2.5-coder:7b"])

    # Initial (possibly cold) inference
    print("\n1. Cold inference (first call):")
    start = time.perf_counter()
    keeper.ping_model("qwen2.5-coder:7b")
    cold = (time.perf_counter() - start) * 1000
    print(f"   Latency: {cold:.0f}ms")

    # Immediate warm inference
    print("\n2. Warm inference (immediate retry):")
    start = time.perf_counter()
    keeper.ping_model("qwen2.5-coder:7b")
    warm = (time.perf_counter() - start) * 1000
    print(f"   Latency: {warm:.0f}ms")

    # Multiple warm inferences
    print("\n3. Multiple warm inferences:")
    times = []
    for i in range(5):
        start = time.perf_counter()
        keeper.ping_model("qwen2.5-coder:7b")
        t = (time.perf_counter() - start) * 1000
        times.append(t)
        print(f"   Run {i+1}: {t:.0f}ms")

    print(f"\n   Average: {sum(times)/len(times):.0f}ms")

    improvement = ((cold - warm) / cold) * 100
    print(f"\n4. Improvement: {improvement:.1f}% faster when warm")

    print("=" * 60)
    print("BENCHMARK COMPLETE")
    print("=" * 60)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Ollama Warm Keeper")
    parser.add_argument("--models", nargs="+", help="Models to keep warm")
    parser.add_argument("--interval", type=int, default=30, help="Check interval (seconds)")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark")
    args = parser.parse_args()

    if args.benchmark:
        benchmark()
    else:
        models = args.models or ["qwen2.5-coder:7b", "deepseek-r1:1.5b"]
        keeper = OllamaWarmKeeper(models)
        keeper.run(args.interval)


if __name__ == "__main__":
    main()
