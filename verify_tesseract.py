import os
import subprocess
import sys

def verify_tesseract():
    print("\n=== Tesseract Installation Verification ===")
    
    tesseract_path = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    
    # Check if Tesseract exists
    if os.path.exists(tesseract_path):
        print(f"✅ Found Tesseract at: {tesseract_path}")
    else:
        print("❌ Tesseract not found at expected location")
        return False
    
    # Try running Tesseract
    try:
        result = subprocess.run([tesseract_path, "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("\n✅ Tesseract is working!")
            print("\nVersion information:")
            print(result.stdout)
            return True
    except Exception as e:
        print(f"\n❌ Error running Tesseract: {e}")
        return False

def check_path():
    print("\n=== Checking System PATH ===")
    
    tesseract_dir = "C:\\Program Files\\Tesseract-OCR"
    
    # Get system PATH
    path = os.environ.get('PATH', '').split(';')
    
    if tesseract_dir in path:
        print("✅ Tesseract is in system PATH")
    else:
        print("❌ Tesseract is NOT in system PATH")
        print("\nTo add Tesseract to PATH:")
        print("1. Open System Properties (Windows key + R, type 'systempropertiesadvanced')")
        print("2. Click 'Environment Variables'")
        print("3. Under 'System Variables', find and select 'Path'")
        print("4. Click 'Edit'")
        print("5. Click 'New'")
        print(f"6. Add this exactly: {tesseract_dir}")
        print("7. Click 'OK' on all windows")
        print("8. Restart your terminal")

def main():
    print("🔍 Checking Tesseract installation...")
    
    tesseract_works = verify_tesseract()
    check_path()
    
    if tesseract_works:
        print("\n=== Final Steps ===")
        print("1. Make sure your .env file has this line:")
        print("TESSERACT_PATH=C:\\\\Program Files\\\\Tesseract-OCR\\\\tesseract.exe")
        print("\n2. Try running: python test_ocr_setup.py")
    else:
        print("\n⚠️ Please fix the installation issues before continuing")

if __name__ == "__main__":
    main()
