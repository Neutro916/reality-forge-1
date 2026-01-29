#!/usr/bin/env python3
"""
DEPLOYMENT_SENSOR.py - CI/CD Deployment Monitoring
C2 Architect Implementation - Architecture Review Follow-up

Monitors deployment status from:
- Netlify (verdant-tulumba-fa2a5a)
- Vercel (consciousness-revolution)
- GitHub Actions

Returns failed/stuck deployments as tasks for Brain Agents.

Usage:
    sensor = DeploymentSensor()
    tasks = sensor.check_all()
    for task in tasks:
        # Route to Brain Agents
        print(f"Deployment issue: {task['title']}")
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

# Try to import requests, fallback to urllib if not available
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.error
    HAS_REQUESTS = False


class DeployStatus(Enum):
    """Deployment status types"""
    SUCCESS = "success"
    FAILED = "failed"
    BUILDING = "building"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


@dataclass
class DeploymentEvent:
    """A deployment event from CI/CD"""
    source: str          # netlify, vercel, github
    site_name: str       # Site/repo name
    deploy_id: str       # Unique deploy ID
    status: DeployStatus
    branch: str
    commit_sha: str
    commit_message: str
    error_message: str
    started_at: str
    finished_at: str
    deploy_url: str

    def to_task(self) -> Dict:
        """Convert to Brain Agent task format"""
        priority = "HIGH" if self.status == DeployStatus.FAILED else "NORMAL"

        return {
            "task_type": "deployment_issue",
            "title": f"[{self.source.upper()}] {self.status.value}: {self.site_name}",
            "description": f"Deployment {self.status.value} for {self.site_name} on branch {self.branch}",
            "context": {
                "source": self.source,
                "site_name": self.site_name,
                "deploy_id": self.deploy_id,
                "status": self.status.value,
                "branch": self.branch,
                "commit_sha": self.commit_sha,
                "commit_message": self.commit_message,
                "error_message": self.error_message,
                "deploy_url": self.deploy_url
            },
            "priority": priority,
            "created_at": datetime.now().isoformat(),
            "source_sensor": "DeploymentSensor"
        }


class DeploymentSensor:
    """
    Monitors CI/CD deployments across multiple platforms.

    Returns failed or stuck deployments as tasks for Brain Agents.
    """

    def __init__(self):
        # API tokens from environment
        self.netlify_token = os.environ.get("NETLIFY_AUTH_TOKEN", "")
        self.vercel_token = os.environ.get("VERCEL_TOKEN", "")
        self.github_token = os.environ.get("GITHUB_TOKEN", "")

        # Site IDs
        self.netlify_sites = [
            "verdant-tulumba-fa2a5a"  # Main consciousness site
        ]

        self.vercel_projects = [
            "consciousness-revolution"
        ]

        self.github_repos = [
            "overkillkulture/consciousness-bugs"
        ]

        # Cache to avoid duplicate alerts
        self.seen_deploys = set()
        self.cache_file = Path.home() / ".consciousness" / "deployment_cache.json"
        self._load_cache()

        # Timeout threshold (minutes)
        self.building_timeout = 15

    def _load_cache(self):
        """Load seen deploys from cache"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file) as f:
                    data = json.load(f)
                    self.seen_deploys = set(data.get("seen", []))
            except:
                self.seen_deploys = set()

    def _save_cache(self):
        """Save seen deploys to cache"""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        # Keep only last 1000 deploys
        recent = list(self.seen_deploys)[-1000:]
        with open(self.cache_file, "w") as f:
            json.dump({"seen": recent, "updated": datetime.now().isoformat()}, f)

    def _http_get(self, url: str, headers: Dict = None) -> Optional[Dict]:
        """Make HTTP GET request"""
        headers = headers or {}

        try:
            if HAS_REQUESTS:
                resp = requests.get(url, headers=headers, timeout=10)
                if resp.status_code == 200:
                    return resp.json()
                return None
            else:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    return json.loads(resp.read().decode())
        except Exception as e:
            print(f"[DEPLOY_SENSOR] HTTP error: {e}")
            return None

    def check_netlify(self) -> List[DeploymentEvent]:
        """Check Netlify deployment status"""
        events = []

        if not self.netlify_token:
            print("[DEPLOY_SENSOR] No NETLIFY_AUTH_TOKEN, skipping")
            return events

        headers = {"Authorization": f"Bearer {self.netlify_token}"}

        for site_id in self.netlify_sites:
            url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys?per_page=5"
            data = self._http_get(url, headers)

            if not data:
                continue

            for deploy in data:
                deploy_id = deploy.get("id", "")

                # Skip if already seen
                if deploy_id in self.seen_deploys:
                    continue

                state = deploy.get("state", "unknown")

                # Map Netlify states
                if state == "ready":
                    status = DeployStatus.SUCCESS
                elif state == "error":
                    status = DeployStatus.FAILED
                elif state == "building":
                    # Check if stuck
                    created = deploy.get("created_at", "")
                    if self._is_stuck(created, self.building_timeout):
                        status = DeployStatus.TIMEOUT
                    else:
                        continue  # Still building, not an issue yet
                else:
                    status = DeployStatus.UNKNOWN

                # Only report failures/timeouts
                if status in [DeployStatus.FAILED, DeployStatus.TIMEOUT]:
                    event = DeploymentEvent(
                        source="netlify",
                        site_name=deploy.get("name", site_id),
                        deploy_id=deploy_id,
                        status=status,
                        branch=deploy.get("branch", "unknown"),
                        commit_sha=deploy.get("commit_ref", "")[:8],
                        commit_message=deploy.get("title", "")[:100],
                        error_message=deploy.get("error_message", ""),
                        started_at=deploy.get("created_at", ""),
                        finished_at=deploy.get("published_at", ""),
                        deploy_url=deploy.get("deploy_ssl_url", "")
                    )
                    events.append(event)
                    self.seen_deploys.add(deploy_id)

        return events

    def check_vercel(self) -> List[DeploymentEvent]:
        """Check Vercel deployment status"""
        events = []

        if not self.vercel_token:
            print("[DEPLOY_SENSOR] No VERCEL_TOKEN, skipping")
            return events

        headers = {"Authorization": f"Bearer {self.vercel_token}"}

        for project in self.vercel_projects:
            url = f"https://api.vercel.com/v6/deployments?projectId={project}&limit=5"
            data = self._http_get(url, headers)

            if not data or "deployments" not in data:
                continue

            for deploy in data["deployments"]:
                deploy_id = deploy.get("uid", "")

                if deploy_id in self.seen_deploys:
                    continue

                state = deploy.get("state", "unknown")

                # Map Vercel states
                if state == "READY":
                    status = DeployStatus.SUCCESS
                elif state == "ERROR":
                    status = DeployStatus.FAILED
                elif state == "BUILDING":
                    created = deploy.get("createdAt", 0)
                    if isinstance(created, int):
                        created = datetime.fromtimestamp(created / 1000).isoformat()
                    if self._is_stuck(created, self.building_timeout):
                        status = DeployStatus.TIMEOUT
                    else:
                        continue
                else:
                    status = DeployStatus.UNKNOWN

                if status in [DeployStatus.FAILED, DeployStatus.TIMEOUT]:
                    event = DeploymentEvent(
                        source="vercel",
                        site_name=deploy.get("name", project),
                        deploy_id=deploy_id,
                        status=status,
                        branch=deploy.get("meta", {}).get("branch", "unknown"),
                        commit_sha=deploy.get("meta", {}).get("commitRef", "")[:8],
                        commit_message=deploy.get("meta", {}).get("commitMessage", "")[:100],
                        error_message="",
                        started_at=datetime.fromtimestamp(deploy.get("createdAt", 0) / 1000).isoformat() if deploy.get("createdAt") else "",
                        finished_at="",
                        deploy_url=f"https://{deploy.get('url', '')}"
                    )
                    events.append(event)
                    self.seen_deploys.add(deploy_id)

        return events

    def check_github_actions(self) -> List[DeploymentEvent]:
        """Check GitHub Actions workflow status"""
        events = []

        if not self.github_token:
            print("[DEPLOY_SENSOR] No GITHUB_TOKEN, skipping Actions")
            return events

        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        for repo in self.github_repos:
            url = f"https://api.github.com/repos/{repo}/actions/runs?per_page=5"
            data = self._http_get(url, headers)

            if not data or "workflow_runs" not in data:
                continue

            for run in data["workflow_runs"]:
                run_id = str(run.get("id", ""))

                if run_id in self.seen_deploys:
                    continue

                conclusion = run.get("conclusion", "")
                status = run.get("status", "")

                # Map GitHub states
                if conclusion == "success":
                    deploy_status = DeployStatus.SUCCESS
                elif conclusion == "failure":
                    deploy_status = DeployStatus.FAILED
                elif status == "in_progress":
                    created = run.get("created_at", "")
                    if self._is_stuck(created, self.building_timeout):
                        deploy_status = DeployStatus.TIMEOUT
                    else:
                        continue
                else:
                    deploy_status = DeployStatus.UNKNOWN

                if deploy_status in [DeployStatus.FAILED, DeployStatus.TIMEOUT]:
                    event = DeploymentEvent(
                        source="github",
                        site_name=f"{repo} / {run.get('name', 'workflow')}",
                        deploy_id=run_id,
                        status=deploy_status,
                        branch=run.get("head_branch", "unknown"),
                        commit_sha=run.get("head_sha", "")[:8],
                        commit_message=run.get("display_title", "")[:100],
                        error_message="",
                        started_at=run.get("created_at", ""),
                        finished_at=run.get("updated_at", ""),
                        deploy_url=run.get("html_url", "")
                    )
                    events.append(event)
                    self.seen_deploys.add(run_id)

        return events

    def _is_stuck(self, timestamp: str, minutes: int) -> bool:
        """Check if a build has been running too long"""
        if not timestamp:
            return False

        try:
            # Parse ISO timestamp
            if "Z" in timestamp:
                timestamp = timestamp.replace("Z", "+00:00")
            started = datetime.fromisoformat(timestamp.replace("+00:00", ""))
            threshold = datetime.now() - timedelta(minutes=minutes)
            return started < threshold
        except:
            return False

    def check_all(self) -> List[Dict]:
        """Check all deployment sources, return tasks"""
        print("[DEPLOY_SENSOR] Checking all deployment sources...")

        all_events = []

        # Check each platform
        all_events.extend(self.check_netlify())
        all_events.extend(self.check_vercel())
        all_events.extend(self.check_github_actions())

        # Save cache
        self._save_cache()

        # Convert to tasks
        tasks = [event.to_task() for event in all_events]

        print(f"[DEPLOY_SENSOR] Found {len(tasks)} deployment issues")

        return tasks

    def get_status(self) -> Dict:
        """Get sensor status"""
        return {
            "sensor": "DeploymentSensor",
            "platforms": {
                "netlify": {
                    "enabled": bool(self.netlify_token),
                    "sites": self.netlify_sites
                },
                "vercel": {
                    "enabled": bool(self.vercel_token),
                    "projects": self.vercel_projects
                },
                "github": {
                    "enabled": bool(self.github_token),
                    "repos": self.github_repos
                }
            },
            "cache_size": len(self.seen_deploys),
            "building_timeout_minutes": self.building_timeout
        }


def demo():
    """Demonstrate deployment sensor"""
    print("="*60)
    print("DEPLOYMENT SENSOR DEMO")
    print("="*60)

    sensor = DeploymentSensor()

    # Show status
    print("\nSensor Status:")
    status = sensor.get_status()
    print(json.dumps(status, indent=2))

    # Check deployments
    print("\nChecking deployments...")
    tasks = sensor.check_all()

    if tasks:
        print(f"\nFound {len(tasks)} deployment issues:")
        for task in tasks:
            print(f"\n  {task['title']}")
            print(f"    Priority: {task['priority']}")
            print(f"    Branch: {task['context']['branch']}")
            if task['context']['error_message']:
                print(f"    Error: {task['context']['error_message'][:80]}")
    else:
        print("\nNo deployment issues found (all deployments successful or no tokens configured)")


if __name__ == "__main__":
    demo()
