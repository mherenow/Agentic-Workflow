#!/usr/bin/env python3
"""
Run script for the Agentic Workflow application.
This script should be run from the project root directory.
"""

import sys
import os
import subprocess

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Set environment variables if needed
os.environ.setdefault('PYTHONPATH', project_root)

if __name__ == "__main__":
    # Run the Streamlit app
    app_path = os.path.join(project_root, "src", "app.py")
    
    print(f"Starting Agentic Workflow application...")
    print(f"Project root: {project_root}")
    print(f"App path: {app_path}")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", app_path
        ], cwd=project_root)
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
    except Exception as e:
        print(f"Error running application: {e}")
