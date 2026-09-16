#!/usr/bin/env python3
"""
Mobile Optimization Helper for RetroCamera Land Blogs

Converts tables to mobile-friendly card layouts and adds CSS animations.
Usage: python3 mobile-optimization.py <blog_markdown_file>
"""

import re
import sys

def convert_table_to_cards(markdown_content):
    """
    Converts markdown tables to HTML card-based layout with animations.
    """
    # Detect markdown tables (simple pattern)
    table_pattern = r'\n\|.*?\|\n\|[\s:|-]*?\|\n((?:\|.*?\|\n)*)'
    
    def replace_table(match):
        table_text = match.group(0)
        lines = table_text.strip().split('\n')
        
        # Parse header
        if len(lines) < 3:
            return table_text
        
        header_line = lines[0]
        headers = [h.strip() for h in header_line.split('|')[1:-1]]
        
        # Parse rows
        rows = []
        for line in lines[3:]:
            if line.strip() and line.startswith('|'):
                cells = [c.strip() for c in line.split('|')[1:-1]]
                rows.append(cells)
        
        # Generate HTML card layout
        html = '\n<div class="comparison-cards">\n'
        for row in rows:
            html += '  <div class="card" style="animation: fadeIn 0.5s ease-in;">\n'
            for i, header in enumerate(headers):
                if i < len(row):
                    html += f'    <div class="card-row"><strong>{header}</strong>: {row[i]}</div>\n'
            html += '  </div>\n'
        html += '</div>\n'
        
        return html
    
    return re.sub(table_pattern, replace_table, markdown_content)

def add_css_animations(markdown_content):
    """
    Adds CSS animation styles to the blog if not present.
    """
    css_animations = """
<style>
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.comparison-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  margin: 20px 0;
}

.card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  background: #f9f9f9;
  animation: slideUp 0.6s ease-out;
}

.card-row {
  margin: 8px 0;
  padding: 4px 0;
  border-bottom: 1px solid #eee;
}

.card-row:last-child {
  border-bottom: none;
}

@media (max-width: 768px) {
  .comparison-cards {
    grid-template-columns: 1fr;
  }
  
  .card {
    animation: slideUp 0.8s ease-out;
  }
}
</style>
"""
    
    if '<style>' not in markdown_content:
        # Insert after first heading
        first_heading = re.search(r'^# .*?$', markdown_content, re.MULTILINE)
        if first_heading:
            insert_pos = first_heading.end()
            markdown_content = markdown_content[:insert_pos] + '\n' + css_animations + markdown_content[insert_pos:]
    
    return markdown_content

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 mobile-optimization.py <blog_file.md>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    
    # Apply optimizations
    content = convert_table_to_cards(content)
    content = add_css_animations(content)
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Mobile optimization applied to {file_path}")
    print("  - Tables converted to card layout")
    print("  - CSS animations added (fadeIn, slideUp)")
    print("  - Mobile-responsive grid enabled")

if __name__ == '__main__':
    main()
