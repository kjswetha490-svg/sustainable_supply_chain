"""Local runner script for sustainable_supply_chain folder."""
import sys
from pathlib import Path

# Add current folder and parent folder to sys.path
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
for p in (str(parent_dir), str(current_dir)):
    if p not in sys.path:
        sys.path.insert(0, p)

from cli import main

if __name__ == "__main__":
    main()
