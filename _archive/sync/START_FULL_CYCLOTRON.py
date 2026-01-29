#!/usr/bin/env python3
"""
START FULL CYCLOTRON
Launches the complete system with all components:
1. Nerve Center (sensory inputs)
2. Brain Agents (reasoning, planning, execution)
3. Memory System (episodic learning)
4. Knowledge Atoms (data chunking)
5. Guardian (monitoring)

This is the REAL Cyclotron - connected to EVERYTHING.
"""

import subprocess
import sys
import time
import json
from pathlib import Path
from datetime import datetime
import threading

HOME = Path.home()
CONSCIOUSNESS = HOME / ".consciousness"
HUB = CONSCIOUSNESS / "hub"
DEPLOYMENT = HOME / "100X_DEPLOYMENT"

HUB.mkdir(parents=True, exist_ok=True)

class FullCyclotronLauncher:
    """Launches and manages all Cyclotron components."""

    def __init__(self, agent_id: str = "C1-Terminal"):
        self.agent_id = agent_id
        self.processes = {}
        self.running = False

    def log(self, msg: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] LAUNCHER: {msg}")

    def launch_component(self, name: str, script: str, args: list = None):
        """Launch a component as subprocess."""
        script_path = CONSCIOUSNESS / script

        if not script_path.exists():
            # Check deployment folder
            script_path = DEPLOYMENT / script

        if not script_path.exists():
            self.log(f"Script not found: {script}")
            return None

        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)

        self.log(f"Launching {name}: {script}")

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            self.processes[name] = proc
            return proc
        except Exception as e:
            self.log(f"Failed to launch {name}: {e}")
            return None

    def output_reader(self, name: str, proc):
        """Read output from subprocess."""
        try:
            for line in iter(proc.stdout.readline, ''):
                if line:
                    print(f"[{name}] {line.strip()}")
        except:
            pass

    def check_brain_agents(self) -> dict:
        """Check which brain agent files exist."""
        agents = {
            "BRAIN_AGENT_FRAMEWORK.py": DEPLOYMENT / "BRAIN_AGENT_FRAMEWORK.py",
            "ADVANCED_BRAIN_AGENTS.py": DEPLOYMENT / "ADVANCED_BRAIN_AGENTS.py",
            "CYCLOTRON_BRAIN_AGENT.py": DEPLOYMENT / "CYCLOTRON_BRAIN_AGENT.py",
            "CYCLOTRON_BRAIN_BRIDGE.py": DEPLOYMENT / "CYCLOTRON_BRAIN_BRIDGE.py"
        }

        status = {}
        for name, path in agents.items():
            status[name] = path.exists()
        return status

    def check_consciousness_components(self) -> dict:
        """Check consciousness folder components."""
        components = {
            "CYCLOTRON_MEMORY.py": CONSCIOUSNESS / "CYCLOTRON_MEMORY.py",
            "CYCLOTRON_INTEGRATED.py": CONSCIOUSNESS / "CYCLOTRON_INTEGRATED.py",
            "CYCLOTRON_GUARDIAN.py": CONSCIOUSNESS / "CYCLOTRON_GUARDIAN.py",
            "DATA_CHUNKER.py": CONSCIOUSNESS / "DATA_CHUNKER.py",
            "CYCLOTRON_NERVE_CENTER.py": CONSCIOUSNESS / "CYCLOTRON_NERVE_CENTER.py"
        }

        status = {}
        for name, path in components.items():
            status[name] = path.exists()
        return status

    def write_launch_status(self, status: dict):
        """Write status to hub."""
        with open(HUB / "CYCLOTRON_LAUNCH_STATUS.json", "w") as f:
            json.dump(status, f, indent=2)

    def run_interactive(self):
        """Run in interactive mode - shows output."""
        self.log("=" * 60)
        self.log("FULL CYCLOTRON LAUNCHER")
        self.log("=" * 60)

        # Check components
        brain_agents = self.check_brain_agents()
        consciousness = self.check_consciousness_components()

        self.log("\nBrain Agents:")
        for name, exists in brain_agents.items():
            status = "OK" if exists else "MISSING"
            self.log(f"  {name}: {status}")

        self.log("\nConsciousness Components:")
        for name, exists in consciousness.items():
            status = "OK" if exists else "MISSING"
            self.log(f"  {name}: {status}")

        # Write status
        self.write_launch_status({
            "agent_id": self.agent_id,
            "timestamp": datetime.now().isoformat() + "Z",
            "brain_agents": brain_agents,
            "consciousness": consciousness
        })

        self.log("\n" + "=" * 60)
        self.log("Select component to run:")
        self.log("  1. Nerve Center (real-time sensing)")
        self.log("  2. Integrated Cyclotron (think-act-learn)")
        self.log("  3. Brain Agent Demo (orchestrated agents)")
        self.log("  4. Guardian (monitoring)")
        self.log("  5. ALL (parallel launch)")
        self.log("  0. Exit")
        self.log("=" * 60)

        choice = input("\nChoice: ").strip()

        if choice == "1":
            self.run_nerve_center()
        elif choice == "2":
            self.run_integrated()
        elif choice == "3":
            self.run_brain_demo()
        elif choice == "4":
            self.run_guardian()
        elif choice == "5":
            self.run_all()
        else:
            self.log("Exiting...")

    def run_nerve_center(self):
        """Run the nerve center."""
        self.log("Starting Nerve Center...")
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "nerve",
            CONSCIOUSNESS / "CYCLOTRON_NERVE_CENTER.py"
        )
        nerve_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(nerve_module)

        nerve = nerve_module.NerveCenter(self.agent_id)
        nerve.setup_default_sensors()
        nerve.run(interval=5)

    def run_integrated(self):
        """Run integrated cyclotron."""
        self.log("Starting Integrated Cyclotron...")
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "integrated",
            CONSCIOUSNESS / "CYCLOTRON_INTEGRATED.py"
        )
        integrated_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(integrated_module)

        cyclotron = integrated_module.IntegratedCyclotron(self.agent_id)
        cyclotron.run(max_cycles=10)

    def run_brain_demo(self):
        """Run brain agent demo."""
        self.log("Running Brain Agent Demo...")

        brain_path = DEPLOYMENT / "BRAIN_AGENT_FRAMEWORK.py"
        if brain_path.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location("brain", brain_path)
            brain_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(brain_module)
            brain_module.demo()
        else:
            self.log("Brain agent framework not found!")

    def run_guardian(self):
        """Run guardian monitor."""
        self.log("Starting Guardian...")

        guardian_path = CONSCIOUSNESS / "CYCLOTRON_GUARDIAN.py"
        if guardian_path.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location("guardian", guardian_path)
            guardian_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(guardian_module)

            guardian = guardian_module.CyclotronGuardian()
            guardian.run()
        else:
            self.log("Guardian not found!")

    def run_all(self):
        """Launch all components in parallel."""
        self.log("Launching ALL components...")

        threads = []

        # Nerve center thread
        def run_nerve():
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "nerve",
                    CONSCIOUSNESS / "CYCLOTRON_NERVE_CENTER.py"
                )
                nerve_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(nerve_module)
                nerve = nerve_module.NerveCenter(self.agent_id + "-Nerve")
                nerve.setup_default_sensors()
                nerve.run(interval=10)
            except Exception as e:
                self.log(f"Nerve error: {e}")

        # Integrated cyclotron thread
        def run_integrated():
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "integrated",
                    CONSCIOUSNESS / "CYCLOTRON_INTEGRATED.py"
                )
                integrated_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(integrated_module)
                cyclotron = integrated_module.IntegratedCyclotron(self.agent_id + "-Brain")
                cyclotron.run(max_cycles=None)  # Run forever
            except Exception as e:
                self.log(f"Integrated error: {e}")

        nerve_thread = threading.Thread(target=run_nerve, name="NerveCenter")
        integrated_thread = threading.Thread(target=run_integrated, name="IntegratedCyclotron")

        nerve_thread.daemon = True
        integrated_thread.daemon = True

        nerve_thread.start()
        time.sleep(2)
        integrated_thread.start()

        self.log("All components started. Press Ctrl+C to stop.")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.log("Shutting down...")


def quick_start():
    """Quick start - just run nerve center."""
    print("Quick starting Nerve Center...")

    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "nerve",
        CONSCIOUSNESS / "CYCLOTRON_NERVE_CENTER.py"
    )
    nerve_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(nerve_module)

    nerve = nerve_module.NerveCenter("C1-Quick")
    nerve.setup_default_sensors()
    nerve.run(interval=5)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quick_start()
    else:
        launcher = FullCyclotronLauncher()
        launcher.run_interactive()
