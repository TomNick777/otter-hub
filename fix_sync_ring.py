# -*- coding: utf-8 -*-
import re, os

files = [
    r"C:\Users\tomra\.qclaw\workspace\otter-hub\index.html",
    r"C:\Users\tomra\.qclaw\workspace\otter-hub\app-todo.html",
    r"C:\Users\tomra\.qclaw\workspace\otter-hub\app-habits.html",
    r"C:\Users\tomra\.qclaw\workspace\otter-hub\app-ledger.html",
]

AVATAR_HTML = '''  <!-- User Avatar / Settings (outside bottom-nav) -->
  <div class="user-avatar-wrap" id="userAvatarWrap">
    <div class="user-avatar-btn" id="userAvatarBtn" onclick="openSettings()" title="设置">
      <span class="user-avatar-icon">🦦</span>
      <span class="user-avatar-ring" id="syncRing"></span>
    </div>
  </div>
'''

# Remove the old inline avatar button from inside bottom-nav
OLD_INLINE = '''  <!-- User Avatar / Settings -->
  <button class="user-avatar-btn" onclick="openSettings()" title="设置">
    <span class="user-avatar-icon">🦦</span>
  </button>
</div><!-- /bottom-nav -->'''

# Updated CSS for avatar - separated from bottom-nav, with sync ring
AVATAR_CSS = """
    /* ── User Avatar (separate from bottom-nav) ── */
    .user-avatar-wrap {
      position: fixed;
      bottom: 24px;
      right: calc(50% + 280px + 12px);
      z-index: 201;
    }
    .user-avatar-btn {
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
      width: var(--bottom-nav-h, 56px);
      height: var(--bottom-nav-h, 56px);
      border-radius: 50%;
      background: var(--bg-elevated);
      border: none;
      cursor: pointer;
      transition: transform var(--duration-fast);
      padding: 0;
    }
    .user-avatar-btn:hover { transform: scale(1.05); }
    .user-avatar-icon {
      font-size: 1.4rem;
      line-height: 1;
      pointer-events: none;
      position: relative;
      z-index: 1;
    }
    /* Sync ring — surrounds the avatar */
    .user-avatar-ring {
      position: absolute;
      inset: -4px;
      border-radius: 50%;
      border: 3px solid transparent;
      transition: border-color 0.3s ease;
      pointer-events: none;
    }
    .user-avatar-ring.syncing { border-color: #ef4444; }
    .user-avatar-ring.synced  { border-color: #22c55e; }
    .user-avatar-ring.error   { border-color: #f97316; }
"""

for f in files:
    with open(f, encoding='utf-8') as fh:
        content = fh.read()

    basename = os.path.basename(f)

    # 1. Remove old inline avatar from inside bottom-nav
    old = '</div><!-- /bottom-nav -->'
    if old in content:
        content = content.replace(old, '</div>')
        print(f"Removed old comment from {basename}")
    old2 = '  <!-- User Avatar / Settings -->\n  <button class="user-avatar-btn" onclick="openSettings()" title="设置">\n    <span class="user-avatar-icon">🦦</span>\n  </button>\n'
    if old2 in content:
        content = content.replace(old2, '')
        print(f"Removed old inline avatar from {basename}")

    # 2. Add avatar-wrap after bottom-nav closing div
    # Pattern: </div>\n\n<!-- Context Menu --> or </div>\n\n<!-- Add Modal -->
    insert_after = '</div>\n\n<!-- Context Menu -->'
    if insert_after in content:
        content = content.replace(insert_after, '</div>\n\n' + AVATAR_HTML + '\n<!-- Context Menu -->')
        print(f"Added avatar-wrap (Context Menu) to {basename}")
    else:
        insert_after2 = '</div>\n\n<!-- Add Modal -->'
        if insert_after2 in content:
            content = content.replace(insert_after2, '</div>\n\n' + AVATAR_HTML + '\n<!-- Add Modal -->')
            print(f"Added avatar-wrap (Add Modal) to {basename}")

    # 3. Replace old avatar CSS with new separated CSS
    old_css = """    /* ── User Avatar Button ── */
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
    .user-avatar-icon { font-size: 1.1rem; line-height: 1; pointer-events: none; }"""
    
    if '.user-avatar-btn' in content and 'position: relative' not in content:
        # Replace old inline CSS with new
        content = content.replace(old_css, AVATAR_CSS)
        print(f"Replaced avatar CSS in {basename}")
    elif '.user-avatar-btn' in content and 'position: relative' in content:
        print(f"Avatar CSS already updated in {basename}")

    # 4. Add sync ring update script before </body>
    sync_script = """
    <script>
    // Sync ring: listen to core sync events
    (function() {
      function updateRing(cls) {
        const ring = document.getElementById('syncRing');
        if (ring) {
          ring.className = 'user-avatar-ring ' + (cls || '');
        }
      }
      if (typeof core !== 'undefined') {
        core.addSyncListener(function(status) {
          if (status === 'syncing') updateRing('syncing');
          else if (status === 'synced') updateRing('synced');
          else if (status === 'error') updateRing('error');
          else updateRing('');
        });
      }
    })();
    </script>"""

    if 'updateRing' not in content:
        content = content.replace('</body>', sync_script + '\n</body>')
        print(f"Added sync ring script to {basename}")

    with open(f, 'w', encoding='utf-8') as fh:
        fh.write(content)

print("\nAll changes applied!")
