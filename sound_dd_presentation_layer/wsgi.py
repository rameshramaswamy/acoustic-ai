import sys
import os

# Ensure path is correct for Gunicorn to find modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from public_portal.app import server

if __name__ == "__main__":
    server.run()