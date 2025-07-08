import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("🚀 AI Research Assistant Setup")
    print("=" * 50)
    print("Setting up your intelligent research companion...")
    print("=" * 50)

def run_command(command, description=""):
    """Run a shell command and handle errors"""
    print(f"\n🔧 {description}")
    print(f"Command: {command}")
    print("-" * 30)
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print("✅ Success!")
        if result.stdout.strip():
            print(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"❌ Python {version.major}.{version.minor} is too old.")
        print("💡 Please use Python 3.9 or newer")
        print("   Download from: https://www.python.org/downloads/")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_pip():
    """Check if pip is available and update it"""
    print("📦 Checking pip...")
    
    try:
        import pip
        print("✅ pip is available")
        
        # Update pip
        return run_command(
            f"{sys.executable} -m pip install --upgrade pip",
            "Updating pip to latest version"
        )
    except ImportError:
        print("❌ pip is not installed")
        print("💡 Please install pip first")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("📚 Installing dependencies...")
    
    # Check if requirements.txt exists
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt not found")
        print("💡 Creating basic requirements.txt...")
        
        requirements = """streamlit>=1.28.0
crewai>=0.28.0
duckduckgo-search>=3.9.0
python-dotenv>=1.0.0
pydantic>=2.0.0
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
openai>=1.0.0
langchain>=0.1.0
langchain-openai>=0.1.0
"""
        
        with open("requirements.txt", "w") as f:
            f.write(requirements)
        
        print("✅ requirements.txt created")
    
    # Install requirements
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing required packages"
    )

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_path = Path(".env")
    template_path = Path(".env.template")
    
    if env_path.exists():
        print("✅ .env file already exists")
        return True
    
    print("📝 Creating .env file...")
    
    env_content = """# OpenAI API Key (Optional - for better LLM performance)
# Get your API key from: https://platform.openai.com/api-keys
# OPENAI_API_KEY=your_openai_api_key_here

# CrewAI Configuration (Optional)
# CREWAI_VERBOSE=true
# CREWAI_DEBUG=false

# Application Settings (Optional)
# MAX_SEARCH_RESULTS=5
# SEARCH_TIMEOUT=30

# Ollama Configuration (Optional - for local LLM)
# OLLAMA_HOST=http://localhost:11434
# OLLAMA_MODEL=llama2
"""
    
    try:
        with open(env_path, "w") as f:
            f.write(env_content)
        print("✅ .env file created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def test_installation():
    """Test if the installation works"""
    print("🧪 Testing installation...")
    
    try:
        # Test basic imports
        print("Testing imports...")
        
        import streamlit
        print("✅ Streamlit imported successfully")
        
        from duckduckgo_search import DDGS
        print("✅ DuckDuckGo search imported successfully")
        
        import crewai
        print("✅ CrewAI imported successfully")
        
        # Test our modules
        try:
            from agents import test_search_tool
            print("✅ Agents module imported successfully")
            
            # Test search functionality
            print("Testing search functionality...")
            result = test_search_tool()
            if result:
                print("✅ Search functionality working")
            else:
                print("⚠️ Search functionality has issues (but installation is complete)")
                
        except ImportError as e:
            print(f"❌ Failed to import agents module: {e}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try running: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def create_missing_files():
    """Create any missing essential files"""
    print("📁 Checking for missing files...")
    
    # Create .gitignore if missing
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        gitignore_content = """# Environment files
.env
.env.local
.env.production

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Streamlit
.streamlit/
"""
        try:
            with open(gitignore_path, "w") as f:
                f.write(gitignore_content)
            print("✅ .gitignore created")
        except Exception as e:
            print(f"⚠️ Could not create .gitignore: {e}")

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("=" * 50)
    
    print("\n📚 Next steps:")
    print("1. (Optional) Add your OpenAI API key to .env file:")
    print("   OPENAI_API_KEY=your_api_key_here")
    print("   Get one from: https://platform.openai.com/api-keys")
    
    print("\n2. Run the application:")
    print("   streamlit run app.py")
    
    print("\n3. Open your browser to:")
    print("   http://localhost:8501")
    
    print("\n4. Start researching!")
    print("   Ask questions like:")
    print("   • 'What is quantum computing?'")
    print("   • 'Latest AI developments 2024'")
    print("   • 'Climate change solutions'")
    
    print("\n🔧 Alternative modes:")
    print("- Standalone mode: python server.py --standalone")
    print("- MCP server: python server.py")
    
    print("\n💡 Troubleshooting:")
    print("- If you see LLM errors, the app will use fallback mode")
    print("- For local LLM, install Ollama: https://ollama.ai/")
    print("- Check logs for detailed error information")

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check pip
    if not check_pip():
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        print("💡 Try running manually: pip install -r requirements.txt")
        return False
    
    # Create environment file
    create_env_file()
    
    # Create missing files
    create_missing_files()
    
    # Test installation
    if not test_installation():
        print("❌ Installation test failed")
        print("💡 Some features may not work properly")
        # Don't return False here - basic setup might still work
    
    # Print next steps
    print_next_steps()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        sys.exit(1)