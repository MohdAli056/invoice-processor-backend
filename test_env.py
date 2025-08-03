from dotenv import load_dotenv
import os

# Load the environment variables
load_dotenv()

# Get the API key
api_key = os.environ.get('GEMINI_API_KEY')

print("\n=== Environment Variable Test ===")
print(f"Current working directory: {os.getcwd()}")
print(f".env file exists: {os.path.exists('.env')}")
if api_key:
    print("✅ GEMINI_API_KEY is loaded successfully")
    print(f"API Key length: {len(api_key)} characters")
else:
    print("❌ GEMINI_API_KEY is not loaded")
    
# Try to read the .env file directly
try:
    with open('.env', 'r') as f:
        content = f.read()
        print("\n.env file content:")
        print(content)
except Exception as e:
    print(f"\nError reading .env file: {str(e)}")

print("\n=============================")
