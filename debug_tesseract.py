import os
from dotenv import load_dotenv
import pytesseract

# Load environment variables
load_dotenv()

print("=== Environment Variables ===")
print(f"TESSERACT_PATH: {os.getenv('TESSERACT_PATH')}")

print("\n=== Pytesseract Configuration ===")
print(f"Pytesseract command: {pytesseract.pytesseract.tesseract_cmd}")

try:
    version = pytesseract.get_tesseract_version()
    print(f"\n✅ Successfully connected to Tesseract!")
    print(f"Version: {version}")
except Exception as e:
    print(f"\n❌ Error accessing Tesseract:")
    print(str(e))

# Check if file exists
tesseract_path = os.getenv('TESSERACT_PATH')
if tesseract_path:
    print(f"\n=== File Check ===")
    print(f"Checking path: {tesseract_path}")
    print(f"File exists: {os.path.isfile(tesseract_path)}")
