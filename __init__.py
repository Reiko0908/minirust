import os
import sys

# Determine the absolute path of the template directory
_template_dir = os.path.abspath(os.path.dirname(__file__))
# Path to the src directory within template
_src_dir = os.path.join(_template_dir, "src")
# Ensure the src root is on sys.path so that top‑level packages like `checker` can be imported
if _src_dir not in sys.path:
    sys.path.append(_src_dir)
# Append sub‑packages for convenience (grammar, astgen, checker)
for sub in ["grammar", "astgen", "checker"]:
    _sub_path = os.path.join(_src_dir, sub)
    if os.path.isdir(_sub_path) and _sub_path not in sys.path:
        sys.path.append(_sub_path)
