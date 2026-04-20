# -*- coding: utf-8 -*-
import re, os

# Avatar HTML
avatar_html = '''  <!-- User Avatar / Settings -->
  <button class="user-avatar-btn" onclick="openSettings()" title="设置">
    <span class="user-avatar-icon">🦦</span>
  </button>
'''

files = [
    r"C:\Users\tomra\.qclaw\workspace\otter-hub\app-todo.html",
    r"C:\Users\tomra\.qclaw\workspace\otter-hub\app-habits.html",
    r"C:\Users\tomra\.qclaw\workspace\otter-hub\app-ledger.html",
]

for f in files:
    with open(f, encoding='utf-8') as fh:
        content = fh.read()

    if 'user-avatar-btn' in content:
        print(f"Already has avatar: {os.path.basename(f)}")
        continue

    # Pattern: the bottom-nav closing div appears just before <!-- Add Modal -->
    # Find the closing </div> of bottom-nav and insert avatar before it
    # Match: </div>\n\n<!-- Add Modal --> or similar
    if '</div>\n\n<!-- Add Modal -->' in content:
        content = content.replace('</div>\n\n<!-- Add Modal -->',
                                 '</div>\n' + avatar_html + '\n<!-- Add Modal -->')
        print(f"Fixed (Add Modal pattern): {os.path.basename(f)}")
    elif '</div>\n\n<!-- Context Menu -->' in content:
        content = content.replace('</div>\n\n<!-- Context Menu -->',
                                 '</div>\n' + avatar_html + '\n<!-- Context Menu -->')
        print(f"Fixed (Context Menu pattern): {os.path.basename(f)}")
    else:
        # Try a regex: find </div> that closes bottom-nav (followed by blank line + comment)
        # Look for the bottom-nav container closing
        pattern = r'(<div class="bottom-nav">.*?)(\n</div>)(\n\n<!--)'
        m = re.search(pattern, content, re.DOTALL)
        if m:
            content = content[:m.start(2)] + '\n' + avatar_html + content[m.start(2):]
            print(f"Fixed (regex): {os.path.basename(f)}")
        else:
            print(f"WARNING - could not fix: {os.path.basename(f)}")
            # Show what's near the bottom-nav close
            idx = content.find('</div>')
            print(f"  Last </div> at: {content[max(0,idx-50):idx+20]}")

    with open(f, 'w', encoding='utf-8') as fh:
        fh.write(content)

print("Done!")
