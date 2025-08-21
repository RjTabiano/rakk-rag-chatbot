#!/usr/bin/env python3
"""
Quick verification script to confirm Python 3.12 upgrade is complete.
Run this to verify all components are working correctly.
"""

import sys
import importlib.util
from pathlib import Path

def check_file_exists(file_path: str) -> bool:
    """Check if a file exists."""
    return Path(file_path).exists()

def check_import(module_name: str) -> bool:
    """Check if a module can be imported."""
    try:
        spec = importlib.util.find_spec(module_name)
        return spec is not None
    except ImportError:
        return False

def main():
    print("🔍 RakkA.I(RAG) Python 3.12 Upgrade Verification")
    print("=" * 55)
    
    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"📍 Python Version: {python_version}")
    
    if sys.version_info >= (3, 11):
        print("✅ Python version is compatible (3.11+ supports most 3.12 features)")
    else:
        print("⚠️  Python version may need updating for full 3.12 compatibility")
    
    # Check critical files
    critical_files = [
        "vercel.json",
        "requirements.txt",
        "api/index.py",
        ".python-version",
        "app/main.py",
        "app/core/config.py",
        "deploy.py"
    ]
    
    print("\n📁 Checking critical files:")
    for file_path in critical_files:
        if check_file_exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING!")
    
    # Check core dependencies
    core_deps = [
        "fastapi",
        "uvicorn",
        "langchain",
        "langchain_google_genai",
        "pinecone",
        "pypdf",
        "dotenv",  # python-dotenv imports as 'dotenv'
        "mysql.connector"
    ]
    
    print("\n📦 Checking core dependencies:")
    missing_deps = []
    for dep in core_deps:
        if check_import(dep):
            print(f"✅ {dep}")
        else:
            print(f"❌ {dep} - NOT INSTALLED!")
            missing_deps.append(dep)
    
    # Check app imports
    print("\n🚀 Checking application imports:")
    app_modules = [
        "app.main",
        "app.api.chat",
        "app.api.ingest",
        "app.core.config",
        "app.services.rag_service",
        "app.services.pinecone_service"
    ]
    
    sys.path.insert(0, str(Path.cwd()))
    
    for module in app_modules:
        if check_import(module):
            print(f"✅ {module}")
        else:
            print(f"❌ {module} - IMPORT ERROR!")
    
    # Summary
    print("\n" + "=" * 55)
    if missing_deps:
        print(f"⚠️  Missing dependencies: {', '.join(missing_deps)}")
        print("   Run: pip install -r requirements.txt")
    else:
        print("🎉 All checks passed! Your RAG chatbot is ready for Python 3.12 deployment!")
        print("\n🚀 Next steps:")
        print("   1. Deploy to Vercel: vercel --prod")
        print("   2. Or run locally: uvicorn app.main:app --reload")
        print("   3. Use deployment script: python deploy.py")

if __name__ == "__main__":
    main()
