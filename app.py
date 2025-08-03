from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
from dotenv import load_dotenv
from process_invoice import process_invoice_end_to_end

# Load environment variables from .env file
load_dotenv()

# Verify Gemini API key is set
if not os.environ.get('GEMINI_API_KEY'):
    print("\n⚠️  WARNING: GEMINI_API_KEY not found in environment variables")
    print("📝 Create a .env file in the backend directory with your API key:")
    print("GEMINI_API_KEY=your-api-key-here\n")

# Create FastAPI instance
app = FastAPI(
    title="Enhanced Invoice Processing API",
    description="AI-powered invoice processing with traditional OCR fallback",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://invoice-processor-frontend-d4g1.vercel.app", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Enhanced Invoice Processing API with AI",
        "version": "2.0.0",
        "features": ["AI Processing (Google Gemini)", "Traditional OCR", "Hybrid Processing"],
        "endpoints": {
            "POST /process": "Upload and process an invoice with AI or traditional OCR",
            "GET /health": "Check API health status",
            "GET /ai-status": "Check if AI processing is available"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}

@app.get("/ai-status")
async def ai_status():
    """Check if AI processing is available"""
    gemini_key = os.environ.get('GEMINI_API_KEY')
    return {
        "ai_available": bool(gemini_key),
        "ai_provider": "Google Gemini" if gemini_key else None,
        "message": "AI processing available" if gemini_key else "Set GEMINI_API_KEY environment variable to enable AI"
    }

@app.post("/process")
async def process_invoice_api(
    file: UploadFile = File(...),
    processing_method: str = Form(default="ai")  # "ai" or "traditional"
):
    """
    Enhanced endpoint that processes invoices with AI or traditional OCR
    
    Args:
        file: Invoice file (PDF, JPG, PNG, TIFF, BMP, WebP)
        processing_method: "ai" for AI processing, "traditional" for OCR
    
    Returns:
        JSON with extracted invoice data and processing metadata
    """
    
    # Validate processing method
    if processing_method not in ["ai", "traditional"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid processing_method. Use 'ai' or 'traditional'"
        )
    
    # Check file type
    allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.webp'}
    file_extension = os.path.splitext(file.filename.lower())[1]
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file_extension}'. Supported: PDF, JPG, JPEG, PNG, TIFF, BMP, WebP"
        )
    
    # Check file size (limit to 10MB)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 10MB"
        )
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        # Process the file based on selected method
        use_ai = (processing_method == "ai")
        
        print(f"Processing {file.filename} with method: {processing_method}")
        result = process_invoice_end_to_end(temp_file_path, use_ai=use_ai)
        
        # Add request metadata
        result.update({
            "filename": file.filename,
            "file_size_bytes": len(content),
            "file_type": file_extension[1:].upper(),
            "requested_method": processing_method,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        })
        
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing file: {str(e)}"
        )
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

if __name__ == "__main__":
    import uvicorn
    import os
    print("🚀 Starting Enhanced Invoice Processing API...")
    print("📄 Traditional OCR: Always available")
    print(f"🤖 AI Processing: {'Available' if os.environ.get('GEMINI_API_KEY') else 'Not available (set GEMINI_API_KEY)'}")
    print("🌐 API will be available at: http://localhost:8000")
    print("📚 Interactive docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
