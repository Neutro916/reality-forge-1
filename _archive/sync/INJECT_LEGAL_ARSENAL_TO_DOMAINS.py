"""
INJECT LEGAL ARSENAL INTO SEVEN DOMAINS PAGE
Adds Legal Arsenal (Domain 9) to the main navigation
Autonomous integration script
"""

from pathlib import Path
import re

def inject_legal_arsenal():
    """Add Legal Arsenal as Domain 9 to seven-domains.html"""

    domains_file = Path.home() / "100X_DEPLOYMENT" / "seven-domains.html"

    if not domains_file.exists():
        print(f"❌ File not found: {domains_file}")
        return False

    # Read current content
    with open(domains_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if Legal Arsenal already added
    if 'LEGAL ARSENAL' in content or 'domain-9' in content:
        print("✅ Legal Arsenal already in domains page")
        return True

    # Add Domain 9 CSS colors
    css_injection = """
        .domain-9 {
            --domain-color: #d4af37;
            --domain-glow: rgba(212, 175, 55, 0.5);
            border-color: #d4af37;
        }"""

    # Find where to inject CSS (after domain-8)
    css_pattern = r'(\.domain-8 \{[^}]+\})'
    content = re.sub(css_pattern, r'\1\n' + css_injection, content)

    # Create Legal Arsenal domain card HTML
    legal_arsenal_card = """
            <!-- Domain 9: LEGAL ARSENAL -->
            <a href="domain-legal-arsenal.html" class="domain-card domain-9">
                <span class="domain-icon">⚖️</span>
                <h2 class="domain-title">LEGAL ARSENAL</h2>
                <p class="domain-subtitle">Domain 9/13 - Builder Protection</p>
                <p class="domain-description">
                    Legal protection for builders. Demand letters ($49), consultations ($99), attorney referrals (10% commission), criminal complaints ($199). Fight corporate destroyers.
                </p>
                <div class="domain-stats">
                    <div class="stat-item">
                        <span class="stat-value">100%</span>
                        <span class="stat-label">LIVE NOW</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">$7.4K</span>
                        <span class="stat-label">Monthly Capacity</span>
                    </div>
                </div>
            </a>
        </div>"""

    # Find insertion point (before closing </div> of domains-grid)
    # Look for the end of Domain 8 card
    insertion_pattern = r'(</a>\s*</div>\s*<!-- Footer -->)'

    if re.search(insertion_pattern, content):
        # Insert Legal Arsenal card before the closing div
        content = re.sub(
            r'(</a>)\s*(</div>\s*<!-- Footer -->)',
            r'\1\n' + legal_arsenal_card + r'\n\2',
            content
        )
    else:
        print("⚠️ Could not find insertion point, trying alternative...")
        # Alternative: find last domain card and insert after it
        alt_pattern = r'(</a>\s*)(</div>\s*<!--\s*Footer\s*-->)'
        content = re.sub(alt_pattern, r'\1\n' + legal_arsenal_card + r'\2', content)

    # Update title from "Eight Domains" to "Nine Domains"
    content = content.replace('⚡ Eight Domains', '⚡ Nine Domains')
    content = content.replace('Domain 7/8', 'Domain 7/13')
    content = content.replace('Domain 8/8', 'Domain 8/13')

    # Write updated content
    with open(domains_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ Legal Arsenal added to domains page")
    print(f"📄 Updated: {domains_file}")
    return True

def main():
    print("="*60)
    print("🌀 INJECT LEGAL ARSENAL TO DOMAINS PAGE")
    print("="*60)

    success = inject_legal_arsenal()

    if success:
        print("\n✅ Integration complete!")
        print("Legal Arsenal now accessible from main navigation")
        print("\nDeploy with:")
        print(f"cd {Path.home() / '100X_DEPLOYMENT'}")
        print('netlify deploy --prod --message="Added Legal Arsenal (Domain 9)"')
    else:
        print("\n❌ Integration failed")

    print("\n" + "="*60)

if __name__ == '__main__':
    main()
