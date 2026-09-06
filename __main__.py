"""Package entrypoint when invoked as `python -m sustainable_supply_chain`."""
import sys
from pathlib import Path

# Ensure root directory is on sys.path
pkg_dir = Path(__file__).resolve().parent
parent_dir = pkg_dir.parent
for p in (str(parent_dir), str(pkg_dir)):
    if p not in sys.path:
        sys.path.insert(0, p)

from sustainable_supply_chain.cli import main

if __name__ == "__main__":
    main()
