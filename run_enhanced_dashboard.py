#!/usr/bin/env python3
"""
Launch script for Enhanced Stellar AI Treasury Dashboard
"""

import subprocess
import sys
import os

def main():
    """Launch the enhanced Streamlit dashboard"""
    print("🚀 Starting Enhanced Stellar AI Treasury Dashboard...")
    
    # Check if required packages are installed
    required_packages = ['streamlit', 'plotly', 'pandas']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
    
    # Launch the enhanced dashboard
    dashboard_path = os.path.join(os.path.dirname(__file__), "app", "dashboard.py")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", dashboard_path,
            "--server.port", "8501",
            "--server.address", "localhost",
            "--theme.base", "light",
            "--theme.primaryColor", "#667eea",
            "--theme.backgroundColor", "#ffffff",
            "--theme.secondaryBackgroundColor", "#f0f2f6"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped.")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")

if __name__ == "__main__":
    main()
