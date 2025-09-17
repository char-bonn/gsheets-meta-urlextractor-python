"""
Vercel entry point for the Data Extraction API.
This file serves as the entry point for Vercel's serverless functions.
"""

import sys
import os

# Add the parent directory to the Python path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Vercel expects the app to be available as 'app' or 'handler'
handler = app

