"""
Find all imported python modules in workspace
"""

import os
import ast

imported_modules = set()

for root, dirs, files in os.walk("."):
    if ".git" in root or "__pycache__" in root or "node_modules" in root:
        continue
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    node = ast.parse(f.read(), filename=path)
                for item in ast.walk(node):
                    if isinstance(item, ast.Import):
                        for alias in item.names:
                            imported_modules.add(alias.name.split('.')[0])
                    elif isinstance(item, ast.ImportFrom):
                        if item.module:
                            imported_modules.add(item.module.split('.')[0])
            except Exception:
                pass

print("=== ALL DETECTED PYTHON MODULES ===")
for mod in sorted(imported_modules):
    print("-", mod)
