#!/usr/bin/env python3
"""
Script to create a proper deployment package for Azure Functions
"""
import os
import zipfile
import shutil
from pathlib import Path

def create_deployment_package():
    """Create a zip package suitable for Azure Functions deployment"""
    
    # Files and directories to exclude
    exclude_patterns = {
        '.git', '.github', 'test-env', 'venv', 'env', '.venv', 'ENV', 
        'data', '__pycache__', '.gitignore', 'README.md', 'DEPLOYMENT_READY.md', 
        'UPGRADE_SUMMARY.md', 'create_deployment_package.py',
        'verify_upgrade.py', 'deploy.py', 'azure-functions-deployment.zip'
    }
    
    # File extensions to exclude
    exclude_extensions = {'.pyc', '.pyo', '.pyd', '.log'}
    
    package_name = 'azure-functions-deployment.zip'
    
    print(f"Creating deployment package: {package_name}")
    
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('.'):
            # Remove excluded directories from dirs list to prevent walking into them
            dirs[:] = [d for d in dirs if d not in exclude_patterns]
            
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, '.')
                
                # Skip if file matches exclude patterns
                if any(pattern in relative_path for pattern in exclude_patterns):
                    continue
                    
                # Skip if file has excluded extension
                if any(relative_path.endswith(ext) for ext in exclude_extensions):
                    continue
                    
                # Skip the deployment package itself
                if file == package_name:
                    continue
                    
                print(f"Adding: {relative_path}")
                zipf.write(file_path, relative_path)
    
    print(f"\nDeployment package created: {package_name}")
    print(f"Package size: {os.path.getsize(package_name) / 1024 / 1024:.2f} MB")
    
    # List contents for verification
    print("\nPackage contents:")
    with zipfile.ZipFile(package_name, 'r') as zipf:
        for name in sorted(zipf.namelist()):
            print(f"  {name}")

if __name__ == "__main__":
    create_deployment_package()
