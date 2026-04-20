# -*- coding: utf-8 -*-
import re, os

files = [
    r"C:\Users\tomra\.qclaw\workspace\otter-hub\index.html",
    r"C:\Users\tomra\.qclaw\workspace\otter-hub\app-todo.html",
    r"C:\Users\tomra\.qclaw\workspace\otter-hub\app-habits.html",
    r"C:\Users\tomra\.qclaw\workspace\otter-hub\app-ledger.html",
]
for f in files:
    with open(f, encoding='utf-8') as fh:
        content = fh.read()
    # Fix double quote: id="logoText""> -> id="logoText">
    content = content.replace('id="logoText"">', 'id="logoText">')
    with open(f, 'w', encoding='utf-8') as fh:
        fh.write(content)
    print(f"Fixed: {os.path.basename(f)}")
print("Done!")
