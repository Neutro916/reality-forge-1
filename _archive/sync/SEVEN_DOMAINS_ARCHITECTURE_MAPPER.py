#!/usr/bin/env python3
"""
SEVEN DOMAINS ARCHITECTURE MAPPER
Maps entire consciousness revolution ecosystem to Seven Domains

PERMANENT INFRASTRUCTURE - Built to last forever
NO temporary solutions. NO cheap shortcuts. NO fast hacks.

This system:
- Maps all projects/files/systems to their domain
- Visualizes complete ecosystem architecture
- Identifies gaps in domain coverage
- Ensures balanced development
- Tracks domain completeness
- Generates visual blueprints
"""

import os
import json
from datetime import datetime
from pathlib import Path
import hashlib

class SevenDomainsMapper:
    """
    Maps all consciousness revolution infrastructure to Seven Domains
    Provides complete ecosystem visualization
    Identifies architectural gaps
    """

    def __init__(self):
        self.domains = {
            "PHYSICAL": {
                "name": "CHAOS FORGE",
                "description": "Material creation, infrastructure, hardware",
                "color": "#FF6B6B",
                "keywords": ["physical", "hardware", "infrastructure", "server", "device", "material", "carrier", "sim", "phone"],
                "projects": []
            },
            "FINANCIAL": {
                "name": "QUANTUM VAULT",
                "description": "Economic systems, revenue, costs, business models",
                "color": "#4ECDC4",
                "keywords": ["money", "revenue", "cost", "price", "payment", "stripe", "business", "profit", "investment"],
                "projects": []
            },
            "MENTAL": {
                "name": "MIND MATRIX",
                "description": "Knowledge, AI, patterns, algorithms",
                "color": "#45B7D1",
                "keywords": ["ai", "knowledge", "pattern", "algorithm", "learning", "consciousness", "intelligence", "filing"],
                "projects": []
            },
            "EMOTIONAL": {
                "name": "SOUL SANCTUARY",
                "description": "Consciousness, user experience, feelings",
                "color": "#96CEB4",
                "keywords": ["consciousness", "experience", "emotion", "user", "feeling", "soul", "awareness", "ux"],
                "projects": []
            },
            "SOCIAL": {
                "name": "REALITY FORGE",
                "description": "Relationships, community, collaboration",
                "color": "#FFEAA7",
                "keywords": ["social", "community", "collaboration", "instagram", "twitter", "team", "relationship", "network"],
                "projects": []
            },
            "CREATIVE": {
                "name": "ARKITEK ACADEMY",
                "description": "Design, art, innovation",
                "color": "#DFE6E9",
                "keywords": ["design", "creative", "art", "innovation", "visual", "interface", "ui", "aesthetic"],
                "projects": []
            },
            "INTEGRATION": {
                "name": "NEXUS TERMINAL",
                "description": "Command center, orchestration, synthesis",
                "color": "#A29BFE",
                "keywords": ["integration", "orchestration", "command", "terminal", "nexus", "synthesis", "hub", "central"],
                "projects": []
            }
        }

        self.home_dir = Path.home()
        self.architecture_dir = str(self.home_dir / ".consciousness" / "architecture")
        os.makedirs(self.architecture_dir, exist_ok=True)

        self.deployment_dir = str(self.home_dir / "100X_DEPLOYMENT")

    def scan_project(self, project_path, project_name=None):
        """
        Scan a project and classify it into domains
        Returns domain classification with confidence score
        """

        if project_name is None:
            project_name = os.path.basename(project_path)

        # Read file content if it's a file
        content = ""
        if os.path.isfile(project_path):
            try:
                with open(project_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
            except:
                content = ""

        # Combine filename and content for classification
        text_to_analyze = f"{project_name} {content}".lower()

        # Score each domain
        domain_scores = {}
        for domain_key, domain_info in self.domains.items():
            score = 0
            for keyword in domain_info["keywords"]:
                score += text_to_analyze.count(keyword)
            domain_scores[domain_key] = score

        # Find primary and secondary domains
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)

        primary_domain = sorted_domains[0][0] if sorted_domains[0][1] > 0 else "INTEGRATION"
        secondary_domains = [d[0] for d in sorted_domains[1:3] if d[1] > 0]

        return {
            "project": project_name,
            "path": project_path,
            "primary_domain": primary_domain,
            "secondary_domains": secondary_domains,
            "domain_scores": domain_scores,
            "confidence": sorted_domains[0][1] if sorted_domains else 0
        }

    def scan_entire_deployment(self):
        """
        Scan entire 100X_DEPLOYMENT directory
        Classify all projects into domains
        """

        print("="*70)
        print("  SCANNING ENTIRE CONSCIOUSNESS REVOLUTION ECOSYSTEM")
        print("="*70)
        print()

        all_projects = []

        # Scan deployment directory
        if os.path.exists(self.deployment_dir):
            for item in os.listdir(self.deployment_dir):
                item_path = os.path.join(self.deployment_dir, item)

                # Skip certain directories
                if item.startswith('.') or item in ['node_modules', '__pycache__']:
                    continue

                classification = self.scan_project(item_path, item)
                all_projects.append(classification)

                # Add to domain's project list
                primary = classification["primary_domain"]
                self.domains[primary]["projects"].append({
                    "name": item,
                    "path": item_path,
                    "confidence": classification["confidence"]
                })

        # Generate architecture map
        architecture = {
            "timestamp": datetime.now().isoformat(),
            "total_projects": len(all_projects),
            "domains": self.domains,
            "all_projects": all_projects
        }

        # Save architecture map
        arch_path = os.path.join(self.architecture_dir, "ECOSYSTEM_ARCHITECTURE_MAP.json")
        with open(arch_path, 'w') as f:
            json.dump(architecture, f, indent=2)

        print(f"✅ Scanned {len(all_projects)} projects")
        print(f"✅ Architecture map saved: {arch_path}")
        print()

        return architecture

    def generate_domain_report(self, architecture):
        """
        Generate human-readable domain coverage report
        Identifies gaps and imbalances
        """

        report = f"""# SEVEN DOMAINS ARCHITECTURE REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 ECOSYSTEM OVERVIEW

**Total Projects:** {architecture['total_projects']}

---

## 🎯 DOMAIN BREAKDOWN

"""

        # Analyze each domain
        for domain_key, domain_info in architecture['domains'].items():
            project_count = len(domain_info['projects'])
            percentage = (project_count / architecture['total_projects'] * 100) if architecture['total_projects'] > 0 else 0

            report += f"""### {domain_key}: {domain_info['name']}
**Description:** {domain_info['description']}
**Projects:** {project_count} ({percentage:.1f}%)

"""

            if domain_info['projects']:
                report += "**Top Projects:**\n"
                # Sort by confidence
                sorted_projects = sorted(domain_info['projects'], key=lambda x: x['confidence'], reverse=True)
                for proj in sorted_projects[:5]:
                    report += f"- {proj['name']} (confidence: {proj['confidence']})\n"
                report += "\n"
            else:
                report += "⚠️ **NO PROJECTS MAPPED TO THIS DOMAIN**\n\n"

        report += "---\n\n## 🎯 BALANCE ANALYSIS\n\n"

        # Calculate balance
        domain_counts = {k: len(v['projects']) for k, v in architecture['domains'].items()}
        max_count = max(domain_counts.values()) if domain_counts else 0
        min_count = min(domain_counts.values()) if domain_counts else 0

        if max_count > 0:
            balance_ratio = min_count / max_count
            balance_percentage = balance_ratio * 100

            report += f"**Balance Score:** {balance_percentage:.1f}%\n"
            report += f"- Most developed: {max(domain_counts, key=domain_counts.get)} ({max_count} projects)\n"
            report += f"- Least developed: {min(domain_counts, key=domain_counts.get)} ({min_count} projects)\n\n"

            if balance_percentage < 50:
                report += "⚠️ **IMBALANCE DETECTED**\n"
                report += "Recommendation: Develop underrepresented domains\n\n"
            else:
                report += "✅ **BALANCED ECOSYSTEM**\n"
                report += "All domains reasonably represented\n\n"

        report += "---\n\n## 🚀 GAPS & OPPORTUNITIES\n\n"

        # Identify gaps
        for domain_key, domain_info in architecture['domains'].items():
            if len(domain_info['projects']) == 0:
                report += f"### ⚠️ {domain_key} ({domain_info['name']})\n"
                report += f"**Gap:** No projects in this domain\n"
                report += f"**Opportunity:** {domain_info['description']}\n"
                report += f"**Next Steps:** Build infrastructure for this domain\n\n"

        report += "---\n\n## 🎯 RECOMMENDATIONS\n\n"

        # Generate recommendations
        sorted_by_count = sorted(domain_counts.items(), key=lambda x: x[1])

        report += "**Priority Development Order:**\n"
        for i, (domain, count) in enumerate(sorted_by_count[:3], 1):
            domain_info = architecture['domains'][domain]
            report += f"{i}. **{domain}** ({domain_info['name']}) - Currently {count} projects\n"
            report += f"   Focus: {domain_info['description']}\n"

        report += "\n---\n\n"
        report += "**PERMANENT ARCHITECTURE - BUILT TO SCALE FOREVER**\n"

        return report

    def generate_visual_blueprint(self, architecture):
        """
        Generate HTML visual blueprint of ecosystem
        Shows all domains, projects, and connections
        """

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Seven Domains Architecture Blueprint</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Consolas', monospace;
            background: #0a0a0a;
            color: #00ff00;
            padding: 20px;
        }}

        .header {{
            text-align: center;
            margin-bottom: 40px;
            border: 2px solid #00ff00;
            padding: 20px;
        }}

        .header h1 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}

        .stats {{
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            gap: 20px;
        }}

        .stat-box {{
            border: 1px solid #00ff00;
            padding: 15px;
            flex: 1;
            text-align: center;
        }}

        .domains {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}

        .domain {{
            border: 2px solid;
            padding: 20px;
            background: rgba(0, 255, 0, 0.05);
        }}

        .domain h2 {{
            margin-bottom: 10px;
            font-size: 1.5em;
        }}

        .domain-description {{
            opacity: 0.7;
            margin-bottom: 15px;
            font-size: 0.9em;
        }}

        .project-list {{
            list-style: none;
            margin-top: 10px;
        }}

        .project-list li {{
            padding: 5px 0;
            border-left: 3px solid currentColor;
            padding-left: 10px;
            margin: 5px 0;
            font-size: 0.85em;
        }}

        .project-count {{
            font-size: 2em;
            margin: 10px 0;
        }}

        .gap-warning {{
            color: #ff0000;
            border-color: #ff0000 !important;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>⚡ SEVEN DOMAINS ARCHITECTURE BLUEPRINT ⚡</h1>
        <p>Complete Consciousness Revolution Ecosystem Visualization</p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="stats">
        <div class="stat-box">
            <div style="font-size: 3em;">{architecture['total_projects']}</div>
            <div>Total Projects</div>
        </div>
        <div class="stat-box">
            <div style="font-size: 3em;">7</div>
            <div>Domains Active</div>
        </div>
        <div class="stat-box">
            <div style="font-size: 3em;">∞</div>
            <div>Permanence Level</div>
        </div>
    </div>

    <div class="domains">
"""

        # Generate domain cards
        for domain_key, domain_info in architecture['domains'].items():
            project_count = len(domain_info['projects'])
            is_gap = project_count == 0

            html += f"""
        <div class="domain {'gap-warning' if is_gap else ''}" style="border-color: {domain_info['color']}; color: {domain_info['color']}">
            <h2>{domain_key}</h2>
            <div style="opacity: 0.7; font-size: 1.2em;">{domain_info['name']}</div>
            <div class="domain-description">{domain_info['description']}</div>
            <div class="project-count">{project_count} Projects</div>
"""

            if domain_info['projects']:
                html += "            <ul class=\"project-list\">\n"
                sorted_projects = sorted(domain_info['projects'], key=lambda x: x['confidence'], reverse=True)
                for proj in sorted_projects[:10]:  # Show top 10
                    html += f"                <li>{proj['name']}</li>\n"
                html += "            </ul>\n"
            else:
                html += "            <div style=\"color: #ff0000; margin-top: 10px;\">⚠️ NO PROJECTS - GAP IDENTIFIED</div>\n"

            html += "        </div>\n"

        html += """    </div>

    <div class="header" style="margin-top: 40px;">
        <h2>PERMANENT ARCHITECTURE - BUILT TO LAST FOREVER</h2>
        <p>No temporary solutions. No cheap shortcuts. No fast hacks.</p>
        <p>Foundation-first. Quality materials. Architect-level engineering.</p>
    </div>
</body>
</html>"""

        return html


# Main execution
if __name__ == "__main__":
    mapper = SevenDomainsMapper()

    print("Scanning ecosystem...")
    architecture = mapper.scan_entire_deployment()

    print("Generating reports...")

    # Generate domain report
    report = mapper.generate_domain_report(architecture)
    report_path = os.path.join(mapper.architecture_dir, "DOMAIN_COVERAGE_REPORT.md")
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"✅ Domain report: {report_path}")

    # Generate visual blueprint
    blueprint = mapper.generate_visual_blueprint(architecture)
    blueprint_path = os.path.join(mapper.architecture_dir, "ECOSYSTEM_BLUEPRINT.html")
    with open(blueprint_path, 'w') as f:
        f.write(blueprint)
    print(f"✅ Visual blueprint: {blueprint_path}")

    print()
    print("="*70)
    print("  SEVEN DOMAINS ARCHITECTURE MAPPING COMPLETE")
    print("="*70)
    print()
    print("📊 Architecture visualized across all Seven Domains")
    print("🎯 Gaps identified for strategic development")
    print("⚡ Permanent mapping system - runs forever")
    print()
    print("="*70)
