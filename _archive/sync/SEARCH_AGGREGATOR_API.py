#!/usr/bin/env python3
"""
SEARCH_AGGREGATOR_API.py - Cross-Computer Search Aggregator
============================================================
Created by: CP1_C2 (C2 Architect)
Task: ENH-008 - Create cross-computer search aggregator API
Date: 2025-11-27

Features:
- Aggregates search results from all Trinity computers
- Queries local Cyclotron + remote endpoints via sync folder
- Merges and ranks results across distributed knowledge base
- Supports async queries to multiple computers
- Caches remote results for performance

Architecture:
- Each computer runs CYCLOTRON_SEARCH.py on port 6668
- This aggregator queries local + checks sync folder for remote results
- Results merged by relevance score

Run: python SEARCH_AGGREGATOR_API.py [--port 6670]
"""

import os
import sys
import json
import time
import hashlib
import requests
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Configuration
HOME = Path(os.environ.get('USERPROFILE', os.path.expanduser('~')))
CONSCIOUSNESS = HOME / '.consciousness'
SYNC_DIR = Path("G:/My Drive/TRINITY_COMMS/sync")
COMPUTER = os.environ.get("COMPUTERNAME", "UNKNOWN")

# Known computer endpoints
COMPUTER_ENDPOINTS = {
    "CP1": {"ip": "192.168.1.95", "port": 6668, "name": "DWREKSCPU"},
    "CP2": {"ip": "192.168.1.100", "port": 6668, "name": "CP2"},  # Update with actual
    "CP3": {"ip": "192.168.1.101", "port": 6668, "name": "CP3"}   # Update with actual
}

# Search request/result files in sync folder
SEARCH_REQUEST_DIR = SYNC_DIR / "search_requests"
SEARCH_RESULT_DIR = SYNC_DIR / "search_results"

# Cache
RESULT_CACHE = {}
CACHE_TTL = 300  # 5 minutes

app = Flask(__name__)
CORS(app)


def get_cache_key(query, search_type=None, limit=10):
    """Generate cache key for search."""
    data = f"{query}:{search_type}:{limit}"
    return hashlib.md5(data.encode()).hexdigest()


def query_local_cyclotron(query, search_type=None, limit=10):
    """Query local Cyclotron search API."""
    try:
        params = {"q": query, "limit": limit}
        if search_type:
            params["type"] = search_type

        response = requests.get(
            "http://localhost:6668/api/search",
            params=params,
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            return {
                "computer": COMPUTER,
                "success": True,
                "results": data.get("results", []),
                "total": data.get("total", 0),
                "source": "local"
            }
    except Exception as e:
        pass

    return {
        "computer": COMPUTER,
        "success": False,
        "results": [],
        "total": 0,
        "error": str(e) if 'e' in dir() else "Connection failed",
        "source": "local"
    }


def query_remote_cyclotron(computer_id, endpoint, query, search_type=None, limit=10):
    """Query remote Cyclotron search API."""
    try:
        params = {"q": query, "limit": limit}
        if search_type:
            params["type"] = search_type

        url = f"http://{endpoint['ip']}:{endpoint['port']}/api/search"
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return {
                "computer": endpoint.get("name", computer_id),
                "success": True,
                "results": data.get("results", []),
                "total": data.get("total", 0),
                "source": "remote"
            }
    except:
        pass

    return {
        "computer": endpoint.get("name", computer_id),
        "success": False,
        "results": [],
        "total": 0,
        "source": "remote"
    }


def write_search_request(query, search_type=None, limit=10):
    """Write search request to sync folder for offline computers."""
    SEARCH_REQUEST_DIR.mkdir(parents=True, exist_ok=True)

    request_id = f"{int(time.time()*1000)}-{COMPUTER}"
    request_file = SEARCH_REQUEST_DIR / f"REQ_{request_id}.json"

    request_data = {
        "id": request_id,
        "query": query,
        "type": search_type,
        "limit": limit,
        "from_computer": COMPUTER,
        "timestamp": datetime.now().isoformat(),
        "status": "PENDING"
    }

    with open(request_file, 'w', encoding='utf-8') as f:
        json.dump(request_data, f, indent=2)

    return request_id


def check_cached_results(query, search_type=None):
    """Check for cached search results from other computers."""
    results = []

    if not SEARCH_RESULT_DIR.exists():
        return results

    # Look for recent result files matching query
    query_hash = hashlib.md5(query.encode()).hexdigest()[:8]

    for result_file in SEARCH_RESULT_DIR.glob(f"RES_*_{query_hash}.json"):
        try:
            # Check if recent (within last hour)
            mtime = result_file.stat().st_mtime
            if time.time() - mtime > 3600:  # Older than 1 hour
                continue

            with open(result_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get("query") == query:
                    results.append({
                        "computer": data.get("from_computer", "UNKNOWN"),
                        "success": True,
                        "results": data.get("results", []),
                        "total": data.get("total", 0),
                        "source": "cached"
                    })
        except:
            continue

    return results


def merge_results(all_results, limit=20):
    """Merge and rank results from all computers."""
    merged = []
    seen_ids = set()

    # Collect all results with source info
    for computer_result in all_results:
        if not computer_result.get("success"):
            continue

        computer = computer_result.get("computer", "UNKNOWN")
        for result in computer_result.get("results", []):
            # Add source computer to result
            result["_source_computer"] = computer

            # Deduplicate by ID
            result_id = result.get("id", result.get("content", "")[:50])
            if result_id in seen_ids:
                continue
            seen_ids.add(result_id)

            merged.append(result)

    # Sort by confidence/relevance score
    merged.sort(key=lambda x: x.get("confidence", x.get("score", 0)), reverse=True)

    return merged[:limit]


def aggregate_search(query, search_type=None, limit=10, include_remote=True):
    """Aggregate search across all computers."""
    all_results = []
    computers_queried = []

    # 1. Query local Cyclotron
    local_result = query_local_cyclotron(query, search_type, limit)
    all_results.append(local_result)
    computers_queried.append(COMPUTER)

    # 2. Query remote computers (in parallel)
    if include_remote:
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {}
            for comp_id, endpoint in COMPUTER_ENDPOINTS.items():
                if endpoint.get("name") == COMPUTER:
                    continue  # Skip self
                future = executor.submit(
                    query_remote_cyclotron,
                    comp_id, endpoint, query, search_type, limit
                )
                futures[future] = comp_id

            for future in as_completed(futures, timeout=15):
                try:
                    result = future.result()
                    all_results.append(result)
                    computers_queried.append(futures[future])
                except:
                    pass

    # 3. Check cached results from sync folder
    cached = check_cached_results(query, search_type)
    for cache_result in cached:
        if cache_result.get("computer") not in computers_queried:
            all_results.append(cache_result)

    # 4. Merge and rank
    merged_results = merge_results(all_results, limit * 2)

    # Build response
    response = {
        "query": query,
        "type": search_type,
        "results": merged_results[:limit],
        "total": len(merged_results),
        "computers_queried": computers_queried,
        "computer_results": [
            {
                "computer": r.get("computer"),
                "success": r.get("success"),
                "count": r.get("total", 0),
                "source": r.get("source")
            }
            for r in all_results
        ],
        "timestamp": datetime.now().isoformat()
    }

    return response


# ============================================================
# API ENDPOINTS
# ============================================================

@app.route('/api/aggregate/search', methods=['GET'])
def api_aggregate_search():
    """Aggregate search across all computers."""
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "Query parameter 'q' required"}), 400

    search_type = request.args.get('type')
    limit = min(int(request.args.get('limit', 20)), 100)
    include_remote = request.args.get('remote', 'true').lower() == 'true'

    # Check cache
    cache_key = get_cache_key(query, search_type, limit)
    if cache_key in RESULT_CACHE:
        cached_time, cached_result = RESULT_CACHE[cache_key]
        if time.time() - cached_time < CACHE_TTL:
            cached_result["_cached"] = True
            return jsonify(cached_result)

    # Perform aggregated search
    result = aggregate_search(query, search_type, limit, include_remote)

    # Cache result
    RESULT_CACHE[cache_key] = (time.time(), result)

    return jsonify(result)


@app.route('/api/aggregate/stats', methods=['GET'])
def api_aggregate_stats():
    """Get aggregate stats from all computers."""
    stats = {
        "aggregator": COMPUTER,
        "timestamp": datetime.now().isoformat(),
        "computers": {}
    }

    # Local stats
    try:
        response = requests.get("http://localhost:6668/api/stats", timeout=5)
        if response.status_code == 200:
            stats["computers"][COMPUTER] = {
                "status": "online",
                "data": response.json()
            }
    except:
        stats["computers"][COMPUTER] = {"status": "offline"}

    # Remote stats
    for comp_id, endpoint in COMPUTER_ENDPOINTS.items():
        if endpoint.get("name") == COMPUTER:
            continue
        try:
            url = f"http://{endpoint['ip']}:{endpoint['port']}/api/stats"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                stats["computers"][endpoint.get("name", comp_id)] = {
                    "status": "online",
                    "data": response.json()
                }
        except:
            stats["computers"][endpoint.get("name", comp_id)] = {"status": "offline"}

    # Calculate totals
    total_atoms = 0
    online_count = 0
    for comp, data in stats["computers"].items():
        if data.get("status") == "online":
            online_count += 1
            total_atoms += data.get("data", {}).get("total_atoms", 0)

    stats["totals"] = {
        "computers_online": online_count,
        "total_atoms": total_atoms
    }

    return jsonify(stats)


@app.route('/api/aggregate/computers', methods=['GET'])
def api_computers():
    """List known computers and their status."""
    computers = []

    for comp_id, endpoint in COMPUTER_ENDPOINTS.items():
        is_self = endpoint.get("name") == COMPUTER

        status = {
            "id": comp_id,
            "name": endpoint.get("name"),
            "ip": endpoint.get("ip"),
            "port": endpoint.get("port"),
            "is_self": is_self,
            "status": "unknown"
        }

        # Check if online
        try:
            if is_self:
                url = "http://localhost:6668/api/stats"
            else:
                url = f"http://{endpoint['ip']}:{endpoint['port']}/api/stats"

            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                status["status"] = "online"
                data = response.json()
                status["atoms"] = data.get("total_atoms", 0)
        except:
            status["status"] = "offline"

        computers.append(status)

    return jsonify({"computers": computers})


@app.route('/api/health', methods=['GET'])
def api_health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "Search Aggregator API",
        "computer": COMPUTER,
        "timestamp": datetime.now().isoformat()
    })


@app.route('/', methods=['GET'])
def api_root():
    """API documentation."""
    return jsonify({
        "service": "Trinity Search Aggregator API",
        "version": "1.0.0",
        "computer": COMPUTER,
        "endpoints": {
            "/api/aggregate/search": "GET - Aggregate search across all computers (q=query, type=optional, limit=20)",
            "/api/aggregate/stats": "GET - Get stats from all computers",
            "/api/aggregate/computers": "GET - List known computers and status",
            "/api/health": "GET - Health check"
        },
        "example": "/api/aggregate/search?q=consciousness&limit=10"
    })


def main():
    port = 6670
    if "--port" in sys.argv:
        idx = sys.argv.index("--port")
        if idx + 1 < len(sys.argv):
            port = int(sys.argv[idx + 1])

    print("="*60)
    print("TRINITY SEARCH AGGREGATOR API")
    print("="*60)
    print(f"Computer: {COMPUTER}")
    print(f"Port: {port}")
    print(f"Sync Dir: {SYNC_DIR}")
    print("="*60)
    print("\nEndpoints:")
    print(f"  /api/aggregate/search?q=<query>")
    print(f"  /api/aggregate/stats")
    print(f"  /api/aggregate/computers")
    print("="*60)

    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
