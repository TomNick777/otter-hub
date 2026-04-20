# -*- coding: utf-8 -*-
import re, os

files = [
    r"C:\Users\tomra\.qclaw\workspace\otter-hub\index.html",
    r"C:\Users\tomra\.qclaw\workspace\otter-hub\app-todo.html",
    r"C:\Users\tomra\.qclaw\workspace\otter-hub\app-habits.html",
    r"C:\Users\tomra\.qclaw\workspace\otter-hub\app-ledger.html",
]

# 1) Remove oncontextmenu from logo
for f in files:
    with open(f, encoding='utf-8') as fh:
        content = fh.read()

    # Remove oncontextmenu="openSettings(event)" from logo element
    content = re.sub(r'\s*oncontextmenu="openSettings\(event\)"', '"', content)

    with open(f, 'w', encoding='utf-8') as fh:
        fh.write(content)
    print(f"Fixed logo contextmenu: {os.path.basename(f)}")

# 2) Add user avatar button to bottom nav in all files
for f in files:
    with open(f, encoding='utf-8') as fh:
        content = fh.read()

    # Find the closing </div> of bottom-nav and insert avatar before it
    avatar_html = '''  <!-- User Avatar / Settings -->
  <button class="user-avatar-btn" onclick="openSettings()" title="设置">
    <span class="user-avatar-icon">🦦</span>
  </button>
</div><!-- /bottom-nav -->'''

    # Replace the closing of bottom-nav
    content = content.replace('</div>\n\n<!-- Context Menu -->', avatar_html + '\n\n<!-- Context Menu -->')

    with open(f, 'w', encoding='utf-8') as fh:
        fh.write(content)
    print(f"Added avatar button: {os.path.basename(f)}")

# 3) Add CSS for user-avatar-btn to unified.css
css_path = r"C:\Users\tomra\.qclaw\workspace\otter-hub\css\unified.css"
with open(css_path, encoding='utf-8') as fh:
    css = fh.read()

# Find the bottom-nav .nav-btn style block and add avatar styles after it
avatar_css = """
/* ── User Avatar Button ── */
.user-avatar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--bg-elevated);
  border: 2px solid var(--border);
  cursor: pointer;
  transition: transform var(--duration-fast), border-color var(--duration-fast);
  flex-shrink: 0;
  padding: 0;
  margin-left: 4px;
}
.user-avatar-btn:hover {
  transform: scale(1.08);
  border-color: var(--accent-lime, #CAFF04);
}
.user-avatar-icon {
  font-size: 1.1rem;
  line-height: 1;
  pointer-events: none;
}"""

# Inject before the modal section in CSS
if '.user-avatar-btn' not in css:
    css = css.replace(
        '/* Modal */',
        avatar_css + '\n\n/* Modal */'
    )
    with open(css_path, 'w', encoding='utf-8') as fh:
        fh.write(css)
    print("Added avatar CSS to unified.css")

# 4) Also add avatar CSS to each HTML file (in case unified.css is cached)
for f in files:
    with open(f, encoding='utf-8') as fh:
        content = fh.read()

    if '.user-avatar-btn' not in content:
        # Insert before </style> or before bottom-nav comment
        avatar_css_inline = """    /* ── User Avatar Button ── */
    .user-avatar-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: var(--bg-elevated);
      border: 2px solid var(--border);
      cursor: pointer;
      transition: transform var(--duration-fast), border-color var(--duration-fast);
      flex-shrink: 0;
      padding: 0;
      margin-left: 4px;
    }
    .user-avatar-btn:hover {
      transform: scale(1.08);
      border-color: var(--accent-lime, #CAFF04);
    }
    .user-avatar-icon { font-size: 1.1rem; line-height: 1; pointer-events: none; }
"""
        # Find where bottom-nav CSS ends and add there
        content = content.replace(
            '    /* Modal */',
            avatar_css_inline + '\n    /* Modal */'
        )
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(content)
        print(f"Added inline avatar CSS: {os.path.basename(f)}")

print("\nAll changes applied!")
