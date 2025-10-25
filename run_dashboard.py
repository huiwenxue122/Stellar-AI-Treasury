#!/usr/bin/env python3
"""
Launch script for Stellar AI Treasury Dashboard
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit dashboard"""
    print("🚀 Starting Stellar AI Treasury Dashboard...")
    
    # Check if streamlit is installed
    try:
        import streamlit
    except ImportError:
        print("❌ Streamlit not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
    
    # Launch the dashboard
    dashboard_path = os.path.join(os.path.dirname(__file__), "app", "ui_dashboard.py")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", dashboard_path,
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped.")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")

if __name__ == "__main__":
    main()
