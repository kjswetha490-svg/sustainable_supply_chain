"""Tunnel helper to provide instant public HTTPS URLs for mobile access."""
import subprocess
import threading
import re
import sys
import time

def start_mobile_tunnel(port: int = 5000):
    """Starts a free SSH tunnel via localhost.run and prints the mobile HTTPS URL."""
    def _run():
        cmd = [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "ServerAliveInterval=30",
            "-R", f"80:localhost:{port}",
            "nokey@localhost.run"
        ]
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            for line in iter(process.stdout.readline, ''):
                # Search for https URL in output
                match = re.search(r'(https://[a-zA-Z0-9\-\.]+\.lhr\.life)', line)
                if match:
                    mobile_url = match.group(1)
                    print("\n" + "🚀" * 32)
                    print(f"📱 MOBILE ACCESS URL (Open this on your phone):")
                    print(f"   👉 {mobile_url}")
                    print("🚀" * 32 + "\n")
                    break
            process.wait()
        except Exception as e:
            # If ssh is unavailable or blocked, continue silently
            pass

    t = threading.Thread(target=_run, daemon=True)
    t.start()
