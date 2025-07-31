#!/usr/bin/env python3
"""
Setup script for Audit Intelligence Platform
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    elif sys.version_info < (3, 10):
        print(f"⚠️  Python {sys.version_info.major}.{sys.version_info.minor} detected - Some packages may require Python 3.10+")
        print("   Consider upgrading to Python 3.10+ for full compatibility")
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit', 'pandas', 'numpy', 'openai', 'pinecone',
        'python-dotenv', 'psycopg2-binary', 'sqlalchemy', 'langchain',
        'neo4j', 'pypdf2', 'beautifulsoup4', 'requests', 'python-dateutil'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ All packages installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages. Please run: pip install -r requirements.txt")
            return False
    
    return True

def check_environment_variables():
    """Check if required environment variables are set"""
    required_vars = [
        'OPENAI_API_KEY',
        'PINECONE_API_KEY'
    ]
    
    optional_vars = [
        'NEO4J_URI',
        'NEO4J_USER', 
        'NEO4J_PASSWORD',
        'RENDER_DB_URL'
    ]
    
    print("\n🔧 Environment Variables Check:")
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var}")
        else:
            print(f"❌ {var} - Required")
            missing_required.append(var)
    
    for var in optional_vars:
        if os.getenv(var):
            print(f"✅ {var}")
        else:
            print(f"⚠️  {var} - Optional")
            missing_optional.append(var)
    
    if missing_required:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_required)}")
        print("Please create a .env file with the required variables")
        return False
    
    return True

def check_knowledge_bases():
    """Check if knowledge base directories exist"""
    knowledge_bases = [
        "Knowledge Bases/Web Scraper Agent",
        "Knowledge Bases/Internal Audit Agent", 
        "Knowledge Bases/External Engagement Conferences DATA",
        "Knowledge Bases/Company Quality System Agent",
        "Knowledge Bases/Audit SOP Agent"
    ]
    
    print("\n📁 Knowledge Base Check:")
    
    missing_dirs = []
    for kb_path in knowledge_bases:
        if os.path.exists(kb_path):
            file_count = len([f for f in os.listdir(kb_path) if os.path.isfile(os.path.join(kb_path, f))])
            print(f"✅ {kb_path} ({file_count} files)")
        else:
            print(f"❌ {kb_path} - Missing")
            missing_dirs.append(kb_path)
    
    if missing_dirs:
        print(f"\n⚠️  Missing knowledge base directories: {', '.join(missing_dirs)}")
        print("Please ensure all knowledge base directories exist and contain relevant files")
    
    return len(missing_dirs) == 0

def create_env_template():
    """Create a template .env file"""
    env_template = """# Audit Intelligence Platform Environment Variables

# Required Variables
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here

# Optional Variables
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password_here
RENDER_DB_URL=your_postgresql_url_here
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_template)
        print("✅ Created .env template file")
        print("⚠️  Please edit .env file with your actual API keys and credentials")
    else:
        print("✅ .env file already exists")

def main():
    """Main setup function"""
    print("🔍 Audit Intelligence Platform Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    print("\n📦 Dependencies Check:")
    if not check_dependencies():
        sys.exit(1)
    
    # Create .env template
    print("\n🔧 Environment Setup:")
    create_env_template()
    
    # Check environment variables
    if not check_environment_variables():
        print("\n⚠️  Please set up your environment variables before running the application")
    
    # Check knowledge bases
    check_knowledge_bases()
    
    print("\n" + "=" * 50)
    print("🎉 Setup Complete!")
    print("\nNext steps:")
    print("1. Edit .env file with your API keys")
    print("2. Set up Neo4j database (optional)")
    print("3. Run: streamlit run app.py")
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main() 