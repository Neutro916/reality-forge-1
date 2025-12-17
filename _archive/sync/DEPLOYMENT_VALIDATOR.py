#!/usr/bin/env python3
"""
DEPLOYMENT VALIDATOR - Pre-Deployment Checklist for All Services
=================================================================
Task: Self-assigned C1 MECHANIC infrastructure improvement
Created by: CP2C1 MECHANIC
Date: 2025-11-27

Validates all deployable components before pushing to production.
Checks configurations, dependencies, and deployment readiness.

Usage:
    python DEPLOYMENT_VALIDATOR.py validate    # Validate all services
    python DEPLOYMENT_VALIDATOR.py check API   # Check specific service
    python DEPLOYMENT_VALIDATOR.py report      # Generate full report
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Configuration
DEPLOY_DIR = Path("C:/Users/darri/100X_DEPLOYMENT")
SYNC_DIR = Path("G:/My Drive/TRINITY_COMMS/sync")
COMPUTER_NAME = os.environ.get("COMPUTERNAME", "UNKNOWN")


class DeploymentValidator:
    """Validate deployment readiness of all services."""

    def __init__(self):
        self.services = {}
        self.results = []

    def check_pattern_theory_api(self):
        """Validate Pattern Theory API deployment readiness."""
        service_dir = DEPLOY_DIR / "PATTERN_THEORY_ENGINE"
        checks = []

        # Check 1: Directory exists
        if service_dir.exists():
            checks.append({"check": "directory_exists", "status": "PASS", "detail": str(service_dir)})
        else:
            checks.append({"check": "directory_exists", "status": "FAIL", "detail": "Directory not found"})
            return {"service": "Pattern Theory API", "ready": False, "checks": checks}

        # Check 2: server.py exists
        server_file = service_dir / "server.py"
        if server_file.exists():
            checks.append({"check": "server.py", "status": "PASS", "detail": "Found"})

            # Check 2b: PORT env var usage
            with open(server_file, 'r') as f:
                content = f.read()
                if "os.environ.get('PORT'" in content or 'os.environ.get("PORT"' in content:
                    checks.append({"check": "port_env_var", "status": "PASS", "detail": "Uses $PORT"})
                else:
                    checks.append({"check": "port_env_var", "status": "FAIL", "detail": "Hardcoded port - fix before deploy"})
        else:
            checks.append({"check": "server.py", "status": "FAIL", "detail": "Not found"})

        # Check 3: requirements.txt
        req_file = service_dir / "requirements.txt"
        if req_file.exists():
            with open(req_file, 'r') as f:
                deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            checks.append({"check": "requirements.txt", "status": "PASS", "detail": f"{len(deps)} dependencies"})
        else:
            checks.append({"check": "requirements.txt", "status": "FAIL", "detail": "Not found"})

        # Check 4: railway.json
        railway_file = service_dir / "railway.json"
        if railway_file.exists():
            with open(railway_file, 'r') as f:
                config = json.load(f)
            start_cmd = config.get("deploy", {}).get("startCommand", "")
            if "server.py" in start_cmd:
                checks.append({"check": "railway.json", "status": "PASS", "detail": f"startCommand: {start_cmd}"})
            else:
                checks.append({"check": "railway.json", "status": "WARN", "detail": f"startCommand may not match: {start_cmd}"})
        else:
            checks.append({"check": "railway.json", "status": "WARN", "detail": "Not found (optional)"})

        # Check 5: Procfile
        procfile = service_dir / "Procfile"
        if procfile.exists():
            with open(procfile, 'r') as f:
                content = f.read().strip()
            checks.append({"check": "Procfile", "status": "PASS", "detail": content})
        else:
            checks.append({"check": "Procfile", "status": "WARN", "detail": "Not found (optional with railway.json)"})

        # Check 6: API module exists
        api_file = service_dir / "api" / "PATTERN_THEORY_API.py"
        if api_file.exists():
            checks.append({"check": "api_module", "status": "PASS", "detail": "PATTERN_THEORY_API.py found"})
        else:
            checks.append({"check": "api_module", "status": "FAIL", "detail": "API module not found"})

        # Check 7: Core module exists
        core_file = service_dir / "core" / "PATTERN_THEORY_ENGINE.py"
        if core_file.exists():
            checks.append({"check": "core_module", "status": "PASS", "detail": "PATTERN_THEORY_ENGINE.py found"})
        else:
            checks.append({"check": "core_module", "status": "FAIL", "detail": "Core module not found"})

        # Determine overall readiness
        failures = sum(1 for c in checks if c["status"] == "FAIL")
        warnings = sum(1 for c in checks if c["status"] == "WARN")

        return {
            "service": "Pattern Theory API",
            "ready": failures == 0,
            "status": "READY" if failures == 0 else "NOT READY",
            "checks": checks,
            "summary": f"{len(checks) - failures - warnings} PASS, {warnings} WARN, {failures} FAIL"
        }

    def check_html_dashboards(self):
        """Check HTML dashboards are deployable."""
        dashboard_locations = [
            DEPLOY_DIR,
            Path("C:/Users/darri/Desktop"),
            Path("C:/Users/darri/.consciousness")
        ]

        html_files = []
        for loc in dashboard_locations:
            if loc.exists():
                html_files.extend(list(loc.glob("*.html")))

        checks = []
        checks.append({"check": "html_count", "status": "PASS" if len(html_files) > 0 else "FAIL", "detail": f"{len(html_files)} HTML files found"})

        # Check for key dashboards
        key_dashboards = [
            "TRINITY_COMMAND_CENTER.html",
            "BRAIN_SEARCH_UI.html",
            "WORK_QUEUE_UI.html",
            "AI_COACH.html"
        ]

        found = []
        missing = []
        for dash in key_dashboards:
            found_files = [f for f in html_files if dash.lower() in f.name.lower()]
            if found_files:
                found.append(dash)
            else:
                missing.append(dash)

        if found:
            checks.append({"check": "key_dashboards", "status": "PASS" if not missing else "WARN", "detail": f"Found: {len(found)}/{len(key_dashboards)}"})

        return {
            "service": "HTML Dashboards",
            "ready": len(html_files) > 0,
            "status": "READY" if len(html_files) > 0 else "NOT READY",
            "checks": checks,
            "summary": f"{len(html_files)} dashboards, {len(found)} key ones found"
        }

    def check_consciousness_tools(self):
        """Check consciousness Python tools are ready."""
        cons_dir = Path("C:/Users/darri/.consciousness")
        checks = []

        if not cons_dir.exists():
            return {
                "service": "Consciousness Tools",
                "ready": False,
                "status": "NOT READY",
                "checks": [{"check": "directory", "status": "FAIL", "detail": ".consciousness not found"}],
                "summary": "Directory missing"
            }

        # Count Python files
        py_files = list(cons_dir.glob("*.py"))
        checks.append({"check": "python_tools", "status": "PASS" if len(py_files) >= 10 else "WARN", "detail": f"{len(py_files)} Python tools"})

        # Check for key tools
        key_tools = [
            "HEALTH_MONITOR.py",
            "INSTANCE_CHECK_IN.py",
            "ATOM_SYNC_PROTOCOL.py",
            "C1_SCAN_100_PIECES.py",
            "C2_SCAN_100_PIECES.py",
            "C3_SCAN_100_PIECES.py"
        ]

        found_tools = []
        for tool in key_tools:
            if (cons_dir / tool).exists():
                found_tools.append(tool)

        checks.append({"check": "key_tools", "status": "PASS" if len(found_tools) >= 4 else "WARN", "detail": f"Found {len(found_tools)}/{len(key_tools)}"})

        # Check atoms.db
        atoms_db = cons_dir / "cyclotron_core" / "atoms.db"
        if atoms_db.exists():
            size_mb = atoms_db.stat().st_size / (1024 * 1024)
            checks.append({"check": "atoms_db", "status": "PASS", "detail": f"{size_mb:.1f} MB"})
        else:
            checks.append({"check": "atoms_db", "status": "WARN", "detail": "Not found"})

        failures = sum(1 for c in checks if c["status"] == "FAIL")

        return {
            "service": "Consciousness Tools",
            "ready": failures == 0,
            "status": "READY" if failures == 0 else "NOT READY",
            "checks": checks,
            "summary": f"{len(py_files)} tools, {len(found_tools)} key ones"
        }

    def validate_all(self):
        """Validate all services."""
        print("=" * 60)
        print("DEPLOYMENT VALIDATOR")
        print("=" * 60)
        print(f"Computer: {COMPUTER_NAME}")
        print(f"Time: {datetime.now().isoformat()}")
        print("=" * 60)
        print()

        # Check each service
        services = [
            self.check_pattern_theory_api(),
            self.check_html_dashboards(),
            self.check_consciousness_tools()
        ]

        self.results = services

        # Print results
        for svc in services:
            status_icon = "[READY]" if svc["ready"] else "[NOT READY]"
            print(f"{status_icon} {svc['service']}")
            print(f"    Summary: {svc['summary']}")
            for check in svc["checks"]:
                icon = "[PASS]" if check["status"] == "PASS" else "[WARN]" if check["status"] == "WARN" else "[FAIL]"
                print(f"      {icon} {check['check']}: {check['detail']}")
            print()

        # Overall summary
        ready_count = sum(1 for s in services if s["ready"])
        print("=" * 60)
        print(f"OVERALL: {ready_count}/{len(services)} services ready for deployment")
        print("=" * 60)

        return services

    def generate_report(self):
        """Generate deployment validation report."""
        if not self.results:
            self.validate_all()

        report = {
            "computer": COMPUTER_NAME,
            "timestamp": datetime.now().isoformat(),
            "services": self.results,
            "ready_count": sum(1 for s in self.results if s["ready"]),
            "total_count": len(self.results)
        }

        # Save to sync folder
        report_file = SYNC_DIR / f"DEPLOYMENT_VALIDATION_{COMPUTER_NAME}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\nReport saved: {report_file.name}")
        return report


def main():
    validator = DeploymentValidator()

    if len(sys.argv) < 2:
        print("DEPLOYMENT VALIDATOR")
        print()
        print("Usage:")
        print("  python DEPLOYMENT_VALIDATOR.py validate   Validate all services")
        print("  python DEPLOYMENT_VALIDATOR.py report     Generate full report")
        return

    command = sys.argv[1].lower()

    if command == "validate":
        validator.validate_all()
    elif command == "report":
        validator.validate_all()
        validator.generate_report()
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
