#!/usr/bin/env python3
"""
Content Quality Checker for RetroCamera Land Blogs

Detects AI-slop patterns and suggests improvements for authentic voice.
Usage: python3 content-quality-checker.py <blog_markdown_file>
"""

import re
import sys

class ContentQualityChecker:
    def __init__(self):
        self.ai_slop_patterns = [
            # Clichés
            (r'zaman tüneline yolculuk', 'Cliché: "zaman tüneline yolculuk"'),
            (r'bu makale.*?bahseder', 'Cliché: "Bu makale X bahseder..." (şablon)'),
            (r'şimdi derinliklere inmek için', 'Cliché: "şimdi derinliklere inmek için"'),
            (r'her zaman önemli', 'Vague: "her zaman önemli"'),
            (r'aslında', 'Filler word: "aslında"'),
            (r'gerçekten de', 'Filler word: "gerçekten de"'),
            (r'söylemek gerekirse', 'Filler word: "söylemek gerekirse"'),
            
            # Generic marketing language
            (r'size.*?sunmak için buradayız', 'Generic: marketing speak'),
            (r'harikalar dünyasına hoş geldiniz', 'Cliché: generic welcome'),
            (r'dün ve bugünü bağlamak', 'Generic transition'),
            
            # Passive voice overuse
            (r'bilinir ki', 'Passive: "bilinir ki" (use active voice)'),
            (r'söylenebilir', 'Passive: "söylenebilir" (use active voice)'),
        ]
        
        self.positive_patterns = [
            (r'ilk.*?aldığımda', 'Good: first-person experience'),
            (r'denediğim', 'Good: personal testing'),
            (r'1960\'larda.*?tasarlandığında', 'Good: specific historical detail'),
            (r'\d+.*?yıl.*?kullandım', 'Good: concrete experience'),
            (r'lens.*?mm', 'Good: technical specificity'),
        ]
    
    def check_content(self, content):
        """
        Scans content for AI-slop and authentic voice patterns.
        """
        lines = content.split('\n')
        issues = []
        strengths = []
        
        for i, line in enumerate(lines, 1):
            # Check for AI-slop
            for pattern, description in self.ai_slop_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        'line': i,
                        'text': line.strip()[:80],
                        'issue': description
                    })
            
            # Check for good patterns
            for pattern, description in self.positive_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    strengths.append({
                        'line': i,
                        'text': line.strip()[:80],
                        'strength': description
                    })
        
        return issues, strengths
    
    def generate_report(self, issues, strengths):
        """
        Generates a quality report.
        """
        report = "\n" + "="*60 + "\n"
        report += "CONTENT QUALITY REPORT\n"
        report += "="*60 + "\n\n"
        
        # Issues
        report += f"⚠️  POTENTIAL AI-SLOP ISSUES ({len(issues)} found):\n"
        if issues:
            for issue in issues[:10]:  # Top 10
                report += f"  - Line {issue['line']}: {issue['issue']}\n"
                report += f"    \"{issue['text']}...\"\n"
        else:
            report += "  ✓ No obvious AI-slop detected!\n"
        
        report += f"\n✓ AUTHENTIC VOICE STRENGTHS ({len(strengths)} found):\n"
        if strengths:
            for strength in strengths[:5]:  # Top 5
                report += f"  - Line {strength['line']}: {strength['strength']}\n"
                report += f"    \"{strength['text']}...\"\n"
        else:
            report += "  → Consider adding first-person experiences, concrete details\n"
        
        # Recommendations
        report += "\n" + "-"*60 + "\n"
        report += "RECOMMENDATIONS FOR AUTHENTIC VOICE:\n"
        report += "-"*60 + "\n"
        if len(issues) > len(strengths):
            report += "1. Replace generic phrases with specific experiences\n"
            report += "2. Add first-person anecdotes (e.g., 'When I first bought...')\n"
            report += "3. Include concrete technical details (focal lengths, film speeds)\n"
            report += "4. Remove passive constructions; use active voice\n"
            report += "5. Reference real historical moments with precision\n"
        else:
            report += "✓ Content has good authentic voice foundation\n"
            report += "→ Minor: Review for any remaining generic transitions\n"
        
        return report

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 content-quality-checker.py <blog_file.md>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    
    checker = ContentQualityChecker()
    issues, strengths = checker.check_content(content)
    report = checker.generate_report(issues, strengths)
    
    print(report)
    
    # Optionally save report
    report_file = file_path.replace('.md', '_quality-report.txt')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n📄 Report saved to: {report_file}")

if __name__ == '__main__':
    main()
