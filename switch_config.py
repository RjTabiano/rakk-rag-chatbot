#!/usr/bin/env python3
"""
Quick script to switch between original and optimized configurations.
"""
import shutil
import os
import sys
from pathlib import Path

def switch_to_optimized():
    """Switch to optimized configuration for Vercel deployment."""
    print("🔄 Switching to optimized configuration...")
    
    try:
        # Backup original files
        if os.path.exists("vercel.json"):
            shutil.copy("vercel.json", "vercel-original-backup.json")
            print("✅ Backed up original vercel.json")
        
        if os.path.exists("requirements.txt"):
            shutil.copy("requirements.txt", "requirements-original-backup.txt")
            print("✅ Backed up original requirements.txt")
        
        # Copy optimized files
        if os.path.exists("vercel-optimized.json"):
            shutil.copy("vercel-optimized.json", "vercel.json")
            print("✅ Switched to optimized vercel.json")
        
        if os.path.exists("requirements-optimized.txt"):
            shutil.copy("requirements-optimized.txt", "requirements.txt")
            print("✅ Switched to optimized requirements.txt")
        
        print("\n🚀 Ready for optimized deployment!")
        print("Run: vercel --prod")
        
    except Exception as e:
        print(f"❌ Error switching to optimized config: {e}")

def switch_to_original():
    """Switch back to original configuration."""
    print("🔄 Switching to original configuration...")
    
    try:
        # Restore original files
        if os.path.exists("vercel-original-backup.json"):
            shutil.copy("vercel-original-backup.json", "vercel.json")
            print("✅ Restored original vercel.json")
        
        if os.path.exists("requirements-original-backup.txt"):
            shutil.copy("requirements-original-backup.txt", "requirements.txt")
            print("✅ Restored original requirements.txt")
        
        print("\n🔙 Switched back to original configuration!")
        
    except Exception as e:
        print(f"❌ Error switching to original config: {e}")

def show_current_config():
    """Show which configuration is currently active."""
    print("📊 Current Configuration Status:")
    
    if os.path.exists("vercel.json"):
        with open("vercel.json", "r") as f:
            content = f.read()
            if "index_lite.py" in content:
                print("✅ Vercel: Optimized configuration")
            else:
                print("📝 Vercel: Original configuration")
    else:
        print("❌ Vercel: No configuration file found")
    
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r") as f:
            content = f.read()
            if "langchain-core" in content and "langchain==" not in content:
                print("✅ Requirements: Optimized configuration")
            else:
                print("📝 Requirements: Original configuration")
    else:
        print("❌ Requirements: No configuration file found")

def main():
    """Main function to handle user choice."""
    print("🔧 RAG Chatbot Configuration Switcher")
    print("=" * 45)
    
    show_current_config()
    
    print("\nWhat would you like to do?")
    print("1. Switch to optimized configuration (for Vercel <250MB)")
    print("2. Switch to original configuration")
    print("3. Show current configuration")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        switch_to_optimized()
    elif choice == "2":
        switch_to_original()
    elif choice == "3":
        show_current_config()
    elif choice == "4":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")
        sys.exit(1)

if __name__ == "__main__":
    main()
