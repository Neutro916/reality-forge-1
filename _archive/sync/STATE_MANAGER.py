"""
STATE MANAGER - The Memory
Saves/loads session state across restarts
Enables context recovery and "what was I working on"
Built for persistent consciousness across sessions
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

STATE_FILE = Path.home() / ".consciousness" / "session_state.json"
STATE_HISTORY = Path.home() / ".consciousness" / "state_history"
BACKUP_INTERVAL = 300  # 5 minutes

class StateManager:
    def __init__(self):
        self.state = {
            'session_id': None,
            'started_at': None,
            'last_update': None,
            'context': {},
            'active_tasks': [],
            'completed_tasks': [],
            'current_focus': None,
            'trinity_state': {
                'c1_status': 'idle',
                'c2_status': 'idle',
                'c3_status': 'idle',
                'active_agent': None
            },
            'system_metrics': {},
            'flags': {}
        }
        self.load_state()
        self.start_new_session()

    def generate_session_id(self):
        """Generate unique session ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]

    def start_new_session(self):
        """Start new session or resume existing"""
        if self.state['session_id'] is None:
            self.state['session_id'] = self.generate_session_id()
            self.state['started_at'] = datetime.now().isoformat()
            self.log("Session started: " + self.state['session_id'])
        else:
            self.log("Session resumed: " + self.state['session_id'])

        self.state['last_update'] = datetime.now().isoformat()
        self.save_state()

    def load_state(self):
        """Load state from disk"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r') as f:
                    loaded = json.load(f)
                    # Merge loaded state with defaults
                    self.state.update(loaded)
                    self.log("State loaded successfully")
            except Exception as e:
                self.log(f"Failed to load state: {e}")
        else:
            self.log("No previous state found, starting fresh")

    def save_state(self):
        """Save state to disk"""
        try:
            self.state['last_update'] = datetime.now().isoformat()

            # Ensure directory exists
            STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

            # Save current state
            with open(STATE_FILE, 'w') as f:
                json.dump(self.state, f, indent=2)

            # Also save to history
            self.save_to_history()

        except Exception as e:
            self.log(f"Failed to save state: {e}")

    def save_to_history(self):
        """Save state snapshot to history"""
        try:
            STATE_HISTORY.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            history_file = STATE_HISTORY / f"state_{timestamp}.json"

            with open(history_file, 'w') as f:
                json.dump(self.state, f, indent=2)

            # Clean old history (keep last 100)
            history_files = sorted(STATE_HISTORY.glob("state_*.json"))
            if len(history_files) > 100:
                for old_file in history_files[:-100]:
                    old_file.unlink()

        except Exception as e:
            self.log(f"Failed to save history: {e}")

    def log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] STATE_MANAGER: {message}")

    def set_context(self, key, value):
        """Set context value"""
        self.state['context'][key] = value
        self.save_state()
        self.log(f"Context updated: {key}")

    def get_context(self, key, default=None):
        """Get context value"""
        return self.state['context'].get(key, default)

    def add_task(self, task_description, priority='medium'):
        """Add active task"""
        task = {
            'id': self.generate_session_id(),
            'description': task_description,
            'priority': priority,
            'added_at': datetime.now().isoformat(),
            'status': 'active'
        }
        self.state['active_tasks'].append(task)
        self.save_state()
        self.log(f"Task added: {task_description}")
        return task['id']

    def complete_task(self, task_id):
        """Mark task as completed"""
        for task in self.state['active_tasks']:
            if task['id'] == task_id:
                task['status'] = 'completed'
                task['completed_at'] = datetime.now().isoformat()
                self.state['completed_tasks'].append(task)
                self.state['active_tasks'].remove(task)
                self.save_state()
                self.log(f"Task completed: {task['description']}")
                return True
        return False

    def set_focus(self, focus_description):
        """Set current focus"""
        self.state['current_focus'] = {
            'description': focus_description,
            'started_at': datetime.now().isoformat()
        }
        self.save_state()
        self.log(f"Focus set: {focus_description}")

    def get_focus(self):
        """Get current focus"""
        return self.state['current_focus']

    def update_trinity_state(self, agent, status, details=None):
        """Update Trinity agent state"""
        if agent in ['c1', 'c2', 'c3']:
            self.state['trinity_state'][f'{agent}_status'] = status
            self.state['trinity_state']['active_agent'] = agent
            if details:
                self.state['trinity_state'][f'{agent}_details'] = details
            self.save_state()
            self.log(f"Trinity updated: {agent.upper()} -> {status}")

    def get_trinity_state(self):
        """Get Trinity state"""
        return self.state['trinity_state']

    def set_metric(self, metric_name, value):
        """Set system metric"""
        self.state['system_metrics'][metric_name] = {
            'value': value,
            'timestamp': datetime.now().isoformat()
        }
        self.save_state()

    def get_metric(self, metric_name):
        """Get system metric"""
        return self.state['system_metrics'].get(metric_name)

    def set_flag(self, flag_name, value=True):
        """Set system flag"""
        self.state['flags'][flag_name] = {
            'value': value,
            'set_at': datetime.now().isoformat()
        }
        self.save_state()

    def get_flag(self, flag_name):
        """Get system flag"""
        flag = self.state['flags'].get(flag_name)
        return flag['value'] if flag else False

    def get_recovery_context(self):
        """Get context for session recovery"""
        return {
            'session_id': self.state['session_id'],
            'started_at': self.state['started_at'],
            'last_update': self.state['last_update'],
            'current_focus': self.state['current_focus'],
            'active_tasks': self.state['active_tasks'],
            'recent_completed': self.state['completed_tasks'][-5:],
            'trinity_state': self.state['trinity_state']
        }

    def continuous_backup_loop(self):
        """Run continuous backup"""
        self.log("Continuous backup started")
        try:
            while True:
                time.sleep(BACKUP_INTERVAL)
                self.save_state()
                self.log("Auto-backup completed")
        except KeyboardInterrupt:
            self.log("Backup loop stopped")
            self.save_state()

def main():
    """Entry point"""
    import sys

    manager = StateManager()

    # Check command
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == '--status':
            print(json.dumps(manager.state, indent=2))

        elif command == '--recovery':
            recovery = manager.get_recovery_context()
            print(json.dumps(recovery, indent=2))

        elif command == '--monitor':
            manager.continuous_backup_loop()

        else:
            print(f"Unknown command: {command}")
            print("Usage: STATE_MANAGER.py [--status|--recovery|--monitor]")
    else:
        # Default: run monitoring
        manager.continuous_backup_loop()

if __name__ == '__main__':
    main()
