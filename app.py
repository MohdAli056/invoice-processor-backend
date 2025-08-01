from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os
from process_invoice import process_invoice_end_to_end

from fastapi.middleware.cors import CORSMiddleware


# Create FastAPI instance
app = FastAPI(
    title="Invoice Processing API",
    description="API for extracting structured data from invoice PDFs and images",
    version="1.0.0"
)
# Add this right after: app = FastAPI(...)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://invoice-processor-frontend-d4g1.vercel.app", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to Invoice Processing API",
        "version": "1.0.0",
        "endpoints": {
            "POST /process": "Upload and process an invoice file",
            "GET /health": "Check API health status"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Invoice Processing API is running"}

@app.post("/process")
async def process_invoice_api(file: UploadFile = File(...)):
    """
    Enhanced endpoint that processes both PDF invoices and image files
    Supports: PDF, JPG, JPEG, PNG, TIFF, BMP, WebP
    """
    
    # Check file type
    allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.webp'}
    file_extension = os.path.splitext(file.filename.lower())[1]
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type '{file_extension}'. Supported formats: PDF, JPG, JPEG, PNG, TIFF, BMP, WebP"
        )
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        # Process the file (PDF or image)
        result = process_invoice_end_to_end(temp_file_path)
        
        # Add file information to result
        result["filename"] = file.filename
        result["file_size_bytes"] = len(content)
        result["file_type"] = file_extension[1:].upper()  # Remove dot and uppercase
        
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

if __name__ == "__main__":
    import uvicorn
    import os
    print("Starting Invoice Processing API...")
    print("API will be available at: http://localhost:8000")
    print("Interactive docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

