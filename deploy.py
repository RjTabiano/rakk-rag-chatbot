#!/usr/bin/env python3
"""
Deployment script for RakkA.I(RAG) project.
This script handles pre-deployment checks and local testing.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command: str, description: str) -> bool:
    """Run a shell command and return success status."""
    print(f"\n🔄 {description}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def check_python_version() -> bool:
    """Check if Python 3.12 is available."""
    print("\n🔍 Checking Python version...")
    
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        version = result.stdout.strip()
        print(f"Current Python version: {version}")
        
        if "3.12" in version or "3.13" in version: 
            print("✅ Python version is compatible")
            return True
        else:
            print("⚠️  Warning: Python 3.12+ recommended for Vercel deployment")
            return True 
    except Exception as e:
        print(f"❌ Error checking Python version: {e}")
        return False

def install_dependencies() -> bool:
    """Install project dependencies."""
    return run_command("pip install -r requirements.txt", "Installing dependencies")

def run_tests() -> bool:
    """Run basic health checks."""
    print("\n🧪 Running basic health checks...")
    
    try:
        sys.path.append(str(Path("app").absolute()))
        import app.core.config
        import app.main
        print("✅ Core modules import successfully")
        return True
    except Exception as e:
        print(f"❌ Module import failed: {e}")
        return False

def start_local_server() -> bool:
    """Start the local development server."""
    print("\n🚀 Starting local development server...")
    print("Server will be available at: http://localhost:8000")
    print("API docs will be available at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ], check=True)
        return True
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def deploy_to_vercel() -> bool:
    """Deploy to Vercel."""
    print("\n🚀 Deploying to Vercel...")
    print("Make sure you have Vercel CLI installed: npm install -g vercel")
    
    return run_command("vercel --prod", "Deploying to Vercel")

def main():
    """Main deployment workflow."""
    print("🎯 RakkA.I(RAG) Deployment Script")
    print("="*50)
    
    if not check_python_version():
        print("❌ Python version check failed")
        sys.exit(1)
    
    if not install_dependencies():
        print("❌ Dependency installation failed")
        sys.exit(1)
    
    if not run_tests():
        print("❌ Health checks failed")
        sys.exit(1)
    
    print("\n✅ All pre-deployment checks passed!")
    
    print("\nWhat would you like to do?")
    print("1. Start local development server")
    print("2. Deploy to Vercel")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        start_local_server()
    elif choice == "2":
        if deploy_to_vercel():
            print("🎉 Deployment completed successfully!")
        else:
            print("❌ Deployment failed")
            sys.exit(1)
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")
        sys.exit(1)

if __name__ == "__main__":
    main()
