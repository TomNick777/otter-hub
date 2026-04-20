# -*- coding: utf-8 -*-
import re, os

files = [
    r"C:\Users\tomra\.qclaw\workspace\otter-hub\index.html",
    r"C:\Users\tomra\.qclaw\workspace\otter-hub\app-todo.html",
    r"C:\Users\tomra\.qclaw\workspace\otter-hub\app-habits.html",
    r"C:\Users\tomra\.qclaw\workspace\otter-hub\app-ledger.html",
]

NEW_CSS = """    /* ── User Avatar (outside bottom-nav) ── */
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
    /* Sync ring */
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

OLD_CSS = """    /* ── User Avatar Button ── */
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

for f in files:
    with open(f, encoding='utf-8') as fh:
        content = fh.read()
    basename = os.path.basename(f)

    if OLD_CSS in content:
        content = content.replace(OLD_CSS, NEW_CSS)
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(content)
        print(f"Updated CSS: {basename}")
    else:
        print(f"Old CSS not found (may already be updated): {basename}")

print("Done!")
