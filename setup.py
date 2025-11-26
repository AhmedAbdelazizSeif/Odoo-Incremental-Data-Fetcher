"""
Setup Script
Initializes the Odoo ETL project environment.
"""

import os
import sys
from pathlib import Path


def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if env_file.exists():
        print("✓ .env file already exists")
        return
    
    if not env_example.exists():
        print("✗ .env.example not found")
        return
    
    # Copy example to .env
    with open(env_example, 'r') as f:
        content = f.read()
    
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✓ Created .env file from template")
    print("⚠ Please edit .env and add your credentials")


def create_directories():
    """Create necessary directories."""
    directories = [
        'logs',
        'temp',
    ]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
            print(f"✓ Created directory: {dir_name}")
        else:
            print(f"✓ Directory exists: {dir_name}")


def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'pandas',
        'sqlalchemy',
        'psycopg2',
        'dotenv',
        'numpy'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} installed")
        except ImportError:
            missing.append(package)
            print(f"✗ {package} NOT installed")
    
    if missing:
        print("\n⚠ Missing packages detected!")
        print("Install them with: pip install -r requirements.txt")
        return False
    
    return True


def main():
    """Main setup routine."""
    print("=" * 60)
    print("Odoo Incremental Data Fetcher - Setup")
    print("=" * 60)
    print()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("✗ Python 3.8+ required")
        return 1
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")
    print()
    
    # Create directories
    print("Creating directories...")
    create_directories()
    print()
    
    # Create .env file
    print("Setting up configuration...")
    create_env_file()
    print()
    
    # Check dependencies
    print("Checking dependencies...")
    deps_ok = check_dependencies()
    print()
    
    if deps_ok:
        print("=" * 60)
        print("✓ Setup completed successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Edit .env file with your Odoo and PostgreSQL credentials")
        print("2. Ensure your PostgreSQL database has the required schema")
        print("3. Run: python example_usage.py  (to test the client)")
        print("4. Run: python main.py  (to execute the full ETL pipeline)")
        print()
        return 0
    else:
        print("=" * 60)
        print("⚠ Setup incomplete - missing dependencies")
        print("=" * 60)
        print()
        print("Run: pip install -r requirements.txt")
        print()
        return 1


if __name__ == '__main__':
    sys.exit(main())
