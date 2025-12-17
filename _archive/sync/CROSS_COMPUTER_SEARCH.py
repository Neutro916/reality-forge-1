#!/usr/bin/env python3
"""
CROSS_COMPUTER_SEARCH.py - Cross-Computer Search Aggregator API
================================================================
Created by: CP2C1 (C1 MECHANIC)
Task: ENH-008 from WORK_BACKLOG

Aggregates search results across all Trinity computers.
Searches local atoms.db and cloud-synced brain exports.

Usage:
    python CROSS_COMPUTER_SEARCH.py search "query"
    python CROSS_COMPUTER_SEARCH.py search "pattern theory" --limit 20
    python CROSS_COMPUTER_SEARCH.py api                      # Start API server
    python CROSS_COMPUTER_SEARCH.py sources                  # List available sources
"""

import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

HOME = Path.home()
CONSCIOUSNESS = HOME / ".consciousness"
SYNC = Path("G:/My Drive/TRINITY_COMMS/sync")
COMPUTER = os.environ.get("COMPUTERNAME", "UNKNOWN")

# Database locations
LOCAL_DB = CONSCIOUSNESS / "cyclotron_core" / "atoms.db"
SEARCH_RESULTS_FILE = SYNC / "search_results"


class BrainSource:
    """A searchable brain source (local or remote)."""

    def __init__(self, name, db_path, source_type="local"):
        self.name = name
        self.db_path = Path(db_path) if db_path else None
        self.source_type = source_type
        self.atom_count = 0
        self.available = False
        self._check_availability()

    def _check_availability(self):
        """Check if this source is available."""
        if self.db_path and self.db_path.exists():
            try:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM atoms")
                self.atom_count = cursor.fetchone()[0]
                conn.close()
                self.available = True
            except:
                self.available = False

    def search(self, query, limit=10):
        """Search this brain source."""
        if not self.available:
            return []

        results = []
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Search in content, tags, and type
            search_pattern = f"%{query}%"
            cursor.execute("""
                SELECT id, type, content, source, tags, confidence, created
                FROM atoms
                WHERE content LIKE ? OR tags LIKE ? OR type LIKE ?
                ORDER BY confidence DESC, created DESC
                LIMIT ?
            """, (search_pattern, search_pattern, search_pattern, limit))

            for row in cursor.fetchall():
                atom_id, atom_type, content, source, tags, confidence, created = row

                # Extract preview
                preview = content[:200] if content else ""

                results.append({
                    "id": atom_id,
                    "type": atom_type,
                    "preview": preview,
                    "source": source,
                    "tags": tags,
                    "confidence": confidence or 0.5,
                    "created": created,
                    "brain_source": self.name
                })

            conn.close()
        except Exception as e:
            print(f"Search error in {self.name}: {e}")

        return results

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "name": self.name,
            "type": self.source_type,
            "atoms": self.atom_count,
            "available": self.available,
            "path": str(self.db_path) if self.db_path else None
        }


class CrossComputerSearch:
    """Search aggregator across all Trinity computers."""

    def __init__(self):
        self.sources = []
        self._discover_sources()

    def _discover_sources(self):
        """Discover all available brain sources."""
        self.sources = []

        # Local brain
        if LOCAL_DB.exists():
            self.sources.append(BrainSource(
                f"Local ({COMPUTER})",
                LOCAL_DB,
                "local"
            ))

        # Cloud-synced brains from other computers
        if SYNC.exists():
            # Look for atoms_*.db files in sync folder
            for db_file in SYNC.glob("atoms_*.db"):
                computer_name = db_file.stem.replace("atoms_", "")
                if computer_name != COMPUTER:  # Skip our own backup
                    self.sources.append(BrainSource(
                        f"Cloud ({computer_name})",
                        db_file,
                        "cloud"
                    ))

            # Also check for brain exports
            for db_file in SYNC.glob("brain_export_*.db"):
                computer_name = db_file.stem.replace("brain_export_", "")
                self.sources.append(BrainSource(
                    f"Export ({computer_name})",
                    db_file,
                    "export"
                ))

    def search(self, query, limit=10, sources=None):
        """Search across all sources and aggregate results."""
        all_results = []

        for source in self.sources:
            if sources and source.name not in sources:
                continue

            if source.available:
                results = source.search(query, limit)
                all_results.extend(results)

        # Sort by confidence, then by recency
        all_results.sort(key=lambda x: (
            -x.get("confidence", 0),
            x.get("created", "") or ""
        ), reverse=False)

        # Deduplicate by content preview (similar results across computers)
        seen_previews = set()
        unique_results = []
        for result in all_results:
            preview_key = result["preview"][:100].lower().strip()
            if preview_key not in seen_previews:
                seen_previews.add(preview_key)
                unique_results.append(result)

        return unique_results[:limit]

    def get_sources(self):
        """Get list of available sources."""
        return [s.to_dict() for s in self.sources]

    def get_stats(self):
        """Get aggregate statistics."""
        total_atoms = sum(s.atom_count for s in self.sources if s.available)
        available_sources = sum(1 for s in self.sources if s.available)

        return {
            "total_sources": len(self.sources),
            "available_sources": available_sources,
            "total_atoms": total_atoms,
            "local_computer": COMPUTER,
            "timestamp": datetime.now().isoformat()
        }


class SearchAPIHandler(BaseHTTPRequestHandler):
    """HTTP API handler for cross-computer search."""

    searcher = None

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path == "/api/search":
            self.handle_search(params)
        elif path == "/api/sources":
            self.handle_sources()
        elif path == "/api/stats":
            self.handle_stats()
        elif path == "/health":
            self.handle_health()
        else:
            self.send_error(404, "Not found")

    def handle_search(self, params):
        """Handle search request."""
        query = params.get("q", [""])[0]
        limit = int(params.get("limit", ["10"])[0])

        if not query:
            self.send_json({"error": "Missing query parameter 'q'"}, 400)
            return

        results = self.searcher.search(query, limit)

        self.send_json({
            "query": query,
            "results": results,
            "count": len(results),
            "sources": [s["name"] for s in self.searcher.get_sources() if s["available"]]
        })

    def handle_sources(self):
        """Handle sources list request."""
        sources = self.searcher.get_sources()
        self.send_json({"sources": sources})

    def handle_stats(self):
        """Handle stats request."""
        stats = self.searcher.get_stats()
        self.send_json(stats)

    def handle_health(self):
        """Handle health check."""
        self.send_json({"status": "healthy", "computer": COMPUTER})

    def send_json(self, data, status=200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def print_results(results, query):
    """Print search results."""
    print("\n" + "="*60)
    print(f"SEARCH RESULTS: '{query}'")
    print("="*60)

    if not results:
        print("  No results found.")
        return

    for i, result in enumerate(results, 1):
        brain_source = result.get("brain_source", "Unknown")
        atom_type = result.get("type", "?")
        preview = result.get("preview", "")[:100]
        confidence = result.get("confidence", 0)

        print(f"\n{i}. [{atom_type}] from {brain_source}")
        print(f"   Confidence: {confidence:.2f}")
        print(f"   {preview}...")

    print("\n" + "="*60)
    print(f"Found {len(results)} results")


def print_sources(searcher):
    """Print available sources."""
    print("\n" + "="*60)
    print("AVAILABLE BRAIN SOURCES")
    print("="*60)

    for source in searcher.get_sources():
        status = "ONLINE" if source["available"] else "OFFLINE"
        atoms = f"{source['atoms']:,}" if source["available"] else "-"
        print(f"\n  [{status}] {source['name']}")
        print(f"    Type: {source['type']}")
        print(f"    Atoms: {atoms}")

    stats = searcher.get_stats()
    print("\n" + "-"*60)
    print(f"Total: {stats['total_atoms']:,} atoms across {stats['available_sources']} sources")
    print("="*60)


def main():
    parser = argparse.ArgumentParser(description="Cross-Computer Search Aggregator")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search across all computers")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", "-l", type=int, default=10, help="Max results")
    search_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Sources command
    subparsers.add_parser("sources", help="List available brain sources")

    # API command
    api_parser = subparsers.add_parser("api", help="Start API server")
    api_parser.add_argument("--port", "-p", type=int, default=6670, help="Port number")

    # Stats command
    subparsers.add_parser("stats", help="Show aggregate statistics")

    args = parser.parse_args()

    searcher = CrossComputerSearch()

    if args.command == "search":
        results = searcher.search(args.query, args.limit)
        if args.json:
            print(json.dumps({
                "query": args.query,
                "results": results,
                "count": len(results)
            }, indent=2))
        else:
            print_results(results, args.query)

    elif args.command == "sources":
        print_sources(searcher)

    elif args.command == "stats":
        stats = searcher.get_stats()
        print("\n" + "="*60)
        print("CROSS-COMPUTER SEARCH STATS")
        print("="*60)
        print(f"  Local Computer: {stats['local_computer']}")
        print(f"  Total Sources: {stats['total_sources']}")
        print(f"  Available: {stats['available_sources']}")
        print(f"  Total Atoms: {stats['total_atoms']:,}")
        print("="*60)

    elif args.command == "api":
        SearchAPIHandler.searcher = searcher
        server = HTTPServer(("0.0.0.0", args.port), SearchAPIHandler)

        print(f"\n{'='*60}")
        print("CROSS-COMPUTER SEARCH API")
        print(f"{'='*60}")
        print(f"  Server: http://localhost:{args.port}")
        print(f"  Computer: {COMPUTER}")
        print(f"  Sources: {len(searcher.get_sources())}")
        print(f"\nEndpoints:")
        print(f"  GET /api/search?q=query&limit=10")
        print(f"  GET /api/sources")
        print(f"  GET /api/stats")
        print(f"  GET /health")
        print(f"{'='*60}")
        print("Press Ctrl+C to stop...")

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")
            server.shutdown()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
