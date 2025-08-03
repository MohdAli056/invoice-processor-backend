import os
import glob

def find_tesseract():
    print("\n=== Searching for Tesseract Installation ===")
    
    # Common installation directories
    search_paths = [
        "C:\\Program Files",
        "C:\\Program Files (x86)"
    ]
    
    found_paths = []
    
    for base_path in search_paths:
        print(f"\nSearching in {base_path}...")
        
        # Search for tesseract.exe recursively
        for root, dirs, files in os.walk(base_path):
            if 'tesseract.exe' in files:
                full_path = os.path.join(root, 'tesseract.exe')
                print(f"✅ Found tesseract.exe at: {full_path}")
                found_paths.append(full_path)
    
    if not found_paths:
        print("\n❌ Tesseract not found. Please install it from:")
        print("https://github.com/UB-Mannheim/tesseract/wiki")
        print("\nMake sure to:")
        print("1. Download tesseract-ocr-w64-setup-v5.3.3.20231005.exe")
        print("2. Install to: C:\\Program Files\\Tesseract-OCR")
        print("3. Check 'Add to PATH' during installation")
    else:
        print("\nFound Tesseract installations:")
        for path in found_paths:
            print(f"- {path}")
        
        print("\nTo use Tesseract, update your .env file with:")
        print(f"TESSERACT_PATH={found_paths[0].replace('\\', '\\\\')}")

if __name__ == "__main__":
    find_tesseract()
