#!/usr/bin/env python3
"""
Demo script to run the eCourts Real-Time UI Application
"""

import subprocess
import sys
import time
import webbrowser
from threading import Timer

def open_browser():
    """Open browser after a delay"""
    time.sleep(2)
    webbrowser.open('http://localhost:5000')

def main():
    print("🚀 Starting eCourts Real-Time Cause List Downloader")
    print("=" * 60)
    print("Features:")
    print("✓ Real-time fetching of States, Districts, Court Complexes")
    print("✓ Download cause lists for specific courts")
    print("✓ Bulk download for entire court complexes")
    print("✓ Modern responsive web interface")
    print("=" * 60)
    
    # Start browser opening timer
    Timer(3.0, open_browser).start()
    
    print("🌐 Starting web server...")
    print("📱 Opening browser at http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        # Run the Flask app
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Thank you for using eCourts Downloader!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Make sure you have installed the requirements:")
        print("   pip install -r requirements.txt")

if __name__ == "__main__":
    main()