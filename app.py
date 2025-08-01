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
# Add CORS middleware to allow requests from React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
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
    Process an uploaded invoice file (PDF or image)
    Returns structured JSON data with extracted information
    """
    
    # Validate file type
    allowed_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_extension}. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Create temporary file to store uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            # Read and write uploaded file content
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Process the invoice using your existing pipeline
        result = process_invoice_end_to_end(temp_file_path)
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        # Check if processing was successful
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Add metadata to response
        response_data = {
            "success": True,
            "filename": file.filename,
            "file_size_bytes": len(content),
            "extracted_data": result
        }
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        
        raise HTTPException(status_code=500, detail=f"Error processing invoice: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    import os
    print("Starting Invoice Processing API...")
    print("API will be available at: http://localhost:8000")
    print("Interactive docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

