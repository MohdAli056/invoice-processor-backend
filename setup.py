"""
Environment setup verification script for Invoice Processor
Run this script to verify all dependencies are installed correctly
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_dependency(module_name, package_name=None):
    package_name = package_name or module_name
    try:
        __import__(module_name)
        print(f"✅ {package_name} is installed successfully")
        return True
    except ImportError as e:
        print(f"❌ {package_name} is not installed. Error: {str(e)}")
        return False

def verify_environment():
    print("\n🔍 Checking Python environment...\n")
    
    # Check Python version
    print(f"Python version: {sys.version.split()[0]}")
    
    # Check required packages
    dependencies = [
        ('google.generativeai', 'google-generativeai'),
        ('PIL', 'Pillow'),
        ('pdf2image', 'pdf2image'),
    ]
    
    all_success = True
    for module, package in dependencies:
        if not check_dependency(module, package):
            all_success = False
    
    # Check Gemini API key
    api_key = os.environ.get('GEMINI_API_KEY')
    if api_key:
        print("✅ GEMINI_API_KEY environment variable is set")
    else:
        print("❌ GEMINI_API_KEY environment variable is not set")
        all_success = False
    
    print("\n" + "="*50)
    if all_success:
        print("✨ All dependencies are properly installed!")
        print("🚀 You can now run the invoice processor")
    else:
        print("⚠️ Some dependencies are missing. Please install them using:")
        print("\npip install google-generativeai Pillow pdf2image python-dotenv")
        print("\nAnd make sure to set your GEMINI_API_KEY environment variable")
    print("="*50 + "\n")

if __name__ == "__main__":
    verify_environment()
