"""Package root entrypoint main.py."""
from flask import Flask
import sys
from pathlib import Path
from sustainable_supply_chain.cli import main

# Flask app setup
app = Flask(__name__)

@app.route('/')
def home():
    return "Sustainable Supply Chain AI Dashboard is live!"

# Vercel looks for 'app' — do not rename it
if __name__ == "__main__":
    app.run()

# Add current and parent directories to sys.path
pkg_dir = Path(__file__).resolve().parent
parent_dir = pkg_dir.parent
for p in (str(parent_dir), str(pkg_dir)):
    if p not in sys.path:
        sys.path.insert(0, p)
