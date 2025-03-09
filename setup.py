#!/usr/bin/env python
import os
import subprocess
import sys

def check_python_version():
    """Check if Python version is compatible."""
    required_version = (3, 8)
    current_version = sys.version_info
    
    if current_version < required_version:
        sys.exit(f"Python {required_version[0]}.{required_version[1]} or higher is required. You have {current_version[0]}.{current_version[1]}")
    
    print(f"✓ Python version check passed: {current_version[0]}.{current_version[1]}")

def install_requirements():
    """Install required packages."""
    try:
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Packages installed successfully!")
    except subprocess.CalledProcessError:
        sys.exit("Failed to install required packages. Please check your internet connection and try again.")

def initialize_database():
    """Initialize the database."""
    try:
        print("Initializing the database...")
        if not os.path.exists('services'):
            sys.exit("Services directory not found. Make sure you're running this script from the project root.")
            
        # Import and use the initialize_database function
        from services.init_db import initialize_database
        initialize_database()
        print("✓ Database initialized successfully!")
    except ImportError as e:
        sys.exit(f"Failed to import database initialization module: {e}")
    except Exception as e:
        sys.exit(f"Failed to initialize database: {e}")

def main():
    """Main setup function."""
    print("=== GrapeVine Project Setup ===\n")
    
    check_python_version()
    install_requirements()
    initialize_database()
    
    print("\n=== Setup Complete! ===")
    print("To start the server, run:")
    print("  uvicorn main:app --reload")
    print("\nThe API will be available at:")
    print("  http://localhost:8000")
    print("  Documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
