# -*- coding: utf-8 -*-

AVATAR_CSS = """
    /* ── User Avatar (outside bottom-nav) ── */
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
      background: rgba(16,16,26,0.92);
      backdrop-filter: blur(24px);
      border: 1px solid var(--border-strong);
      cursor: pointer;
      transition: transform var(--duration-fast);
      padding: 0;
      box-shadow: var(--shadow-lg), 0 0 0 1px rgba(255,255,255,0.04);
    }
    .user-avatar-btn:hover { transform: scale(1.05); }
    .user-avatar-icon {
      font-size: 1.4rem;
      line-height: 1;
      pointer-events: none;
      position: relative;
      z-index: 1;
    }
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

files = [
    r"C:\Users\tomra\.qclaw\workspace\otter-hub\app-todo.html",
    r"C:\Users\tomra\.qclaw\workspace\otter-hub\app-habits.html",
    r"C:\Users\tomra\.qclaw\workspace\otter-hub\app-ledger.html",
]

for f in files:
    with open(f, encoding='utf-8') as fh:
        content = fh.read()

    if '.user-avatar-wrap' in content:
        print(f"Already has CSS: {f.split(chr(92))[-1]}")
        continue

    # Insert before the responsive section
    marker = '    /* ── Responsive ── */'
    if marker in content:
        content = content.replace(marker, AVATAR_CSS + '\n    ' + marker)
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(content)
        print(f"Added CSS: {f.split(chr(92))[-1]}")
    else:
        print(f"No Responsive marker: {f.split(chr(92))[-1]}")

print("Done!")
