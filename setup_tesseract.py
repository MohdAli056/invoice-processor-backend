import os
import sys
import urllib.request
import subprocess
import zipfile
import shutil

def download_file(url, filename):
    print(f"Downloading {filename}...")
    urllib.request.urlretrieve(url, filename)
    print("Download complete!")

def setup_tesseract():
    print("\n=== Tesseract Installation Helper ===")
    
    # Create temp directory
    temp_dir = "tesseract_setup"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Download Tesseract
    tesseract_url = "https://deb.instalacje.net/UB-Mannheim/tesseract/w64/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
    installer_path = os.path.join(temp_dir, "tesseract_installer.exe")
    
    try:
        print("\nStep 1: Downloading Tesseract installer...")
        download_file(tesseract_url, installer_path)
        
        print("\nStep 2: Please run the installer manually")
        print("Important instructions:")
        print("1. Choose 'Install for anyone using this computer'")
        print("2. Install to: C:\\Program Files\\Tesseract-OCR")
        print("3. CHECK 'Add Tesseract to the system PATH'")
        print("4. Select at least 'English' under Additional language data")
        print("\nThe installer will open now. Follow these steps carefully.")
        print("After installation, close the installer and return here.")
        
        input("\nPress Enter to start the installer...")
        
        # Run the installer
        os.startfile(installer_path)
        
        input("\nPress Enter once installation is complete to verify...")
        
        # Verify installation
        tesseract_path = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
        if os.path.exists(tesseract_path):
            print("\n✅ Tesseract installed successfully!")
            print(f"Found at: {tesseract_path}")
            
            # Try running tesseract
            try:
                result = subprocess.run([tesseract_path, "--version"], 
                                     capture_output=True, text=True)
                print("\nTesseract version info:")
                print(result.stdout)
            except Exception as e:
                print(f"\n⚠️ Tesseract installed but may not be configured correctly: {e}")
        else:
            print("\n❌ Tesseract installation not found at expected location")
            print("Please try installing again and make sure to use the default installation path")
    
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
    
    finally:
        # Cleanup
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
        
        if os.path.exists(tesseract_path):
            print("\n=== Next Steps ===")
            print("1. Add this to your .env file:")
            print(f"TESSERACT_PATH={tesseract_path.replace('\\', '\\\\')}")
            print("\n2. Restart your terminal/PowerShell")
            print("\n3. Run 'python test_ocr_setup.py' to verify everything is working")

if __name__ == "__main__":
    setup_tesseract()
