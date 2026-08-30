import sys
import os

# Ensure project root is in sys.path for Vercel Serverless Python runtime
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app.main import app

# Vercel Serverless Function entrypoint
app = app
