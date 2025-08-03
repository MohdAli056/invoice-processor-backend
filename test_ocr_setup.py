"""
Test script to verify OCR setup
"""
import os
import sys
import pytesseract
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def check_tesseract():
    print("\n=== Checking Tesseract Setup ===")
    
    # Get Tesseract path from environment
    tesseract_path = os.getenv('TESSERACT_PATH')
    print(f"TESSERACT_PATH environment variable: {tesseract_path}")
    
    if tesseract_path:
        # Set Tesseract command
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    # Try getting Tesseract version
    try:
        version = pytesseract.get_tesseract_version()
        print(f"\n✅ Tesseract is working!")
        print(f"Version: {version}")
    except Exception as e:
        print(f"\n❌ Error with Tesseract: {str(e)}")
        
def check_pdf2image():
    print("\n=== Checking PDF Processing Setup ===")
    
    # Common Poppler paths
    poppler_paths = [
        "C:\\Program Files\\poppler\\bin",
        "C:\\Program Files\\poppler\\poppler-24.08.0\\Library\\bin",
        os.environ.get('POPPLER_PATH')
    ]
    
    print("\nChecking Poppler installations:")
    found = False
    for path in poppler_paths:
        if path and os.path.exists(path):
            print(f"✅ Found Poppler at: {path}")
            if os.path.exists(os.path.join(path, "pdfinfo.exe")):
                print(f"   ✅ pdfinfo.exe found")
            else:
                print(f"   ❌ pdfinfo.exe not found")
            found = True
    
    if not found:
        print("❌ Poppler not found in any common location. Please install from:")
        print("https://github.com/oschwartz10612/poppler-windows/releases/")
    
    # Try importing pdf2image
    try:
        import pdf2image
        print("✅ pdf2image module installed")
    except Exception as e:
        print(f"❌ Error importing pdf2image: {str(e)}")

def main():
    print("\n🔍 Checking OCR Dependencies...")
    print(f"Python version: {sys.version.split()[0]}")
    print(f"Working directory: {os.getcwd()}")
    
    check_tesseract()
    check_pdf2image()
    
    print("\n=== Required Actions ===")
    print("If you see any ❌ above, follow these steps:")
    print("\n1. Install Tesseract:")
    print("   - Download from: https://github.com/UB-Mannheim/tesseract/wiki")
    print("   - Install to: C:\\Program Files\\Tesseract-OCR")
    print("   - Add to PATH during installation")
    
    print("\n2. Install Poppler:")
    print("   - Download from: https://github.com/oschwartz10612/poppler-windows/releases/")
    print("   - Extract to: C:\\Program Files\\poppler")
    print("   - Add bin folder to PATH")
    
    print("\n3. Install Python packages:")
    print("   pip install pytesseract pdf2image opencv-python")
    
    print("\n4. Verify .env file has:")
    print('   TESSERACT_PATH=C:\\Program Files\\Tesseract-OCR\\tesseract.exe')

if __name__ == "__main__":
    main()
