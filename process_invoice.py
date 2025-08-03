import os
from typing import Dict, Optional
from ocr import process_file as process_with_traditional_ocr
from nlp_parser import parse_invoice_text
from ai_processor import create_ai_processor

def process_invoice_end_to_end(file_path: str, use_ai: bool = True) -> Dict:
    """
    Enhanced invoice processing with AI and traditional OCR options
    
    Args:
        file_path: Path to the invoice file
        use_ai: True for AI processing, False for traditional OCR
    
    Returns:
        Dictionary with processing results
    """
    
    # Get file info
    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
    filename = os.path.basename(file_path)
    file_extension = os.path.splitext(filename)[1].lower()
    
    # Initialize result structure with detailed metadata
    result = {
        "success": False,
        "filename": filename,
        "file_size_bytes": file_size,
        "file_type": file_extension[1:].upper(),
        "processing_method": "unknown",
        "processing_timestamp": __import__('datetime').datetime.now().isoformat(),
        "extracted_data": {
            "vendor_name": None,
            "vendor_email": None,
            "vendor_phone": None,
            "invoice_number": None,
            "invoice_date": None,
            "po_number": None,
            "vat_number": None,
            "total_amount": None,
            "subtotal": None,
            "tax_amount": None,
            "payment_terms": None,
            "dates_found": []
        },
        "confidence_scores": {
            "overall": None,
            "text_quality": None,
            "data_completeness": None
        }
    }
    
    try:
        if use_ai:
            # Try AI processing first
            ai_processor = create_ai_processor()
            
            if ai_processor:
                print(f"🤖 Processing {filename} with AI...")
                
                if file_extension == '.pdf':
                    ai_result = ai_processor.process_pdf_with_ai(file_path)
                else:
                    ai_result = ai_processor.process_image_with_ai(file_path)
                
                if ai_result.get("success"):
                    result.update({
                        "success": True,
                        "processing_method": "AI (Google Gemini)",
                        "extracted_data": ai_result.get("extracted_data", result["extracted_data"]),
                        "confidence": ai_result.get("confidence", "high"),
                        "ai_processing": True
                    })
                    
                    print("✅ AI processing successful!")
                    return result
                else:
                    print(f"❌ AI processing failed: {ai_result.get('error', 'Unknown error')}")
                    print("🔄 Falling back to traditional OCR...")
            else:
                print("⚠️ AI processor not available, using traditional OCR...")
        
        # Traditional OCR processing (fallback or chosen method)
        print(f"🔍 Processing {filename} with traditional OCR...")
        
        # Extract text using traditional OCR
        extracted_text = process_with_traditional_ocr(file_path)
        
        if not extracted_text or len(extracted_text.strip()) < 10:
            result.update({
                "success": False,
                "processing_method": "Traditional OCR",
                "error": "Could not extract meaningful text from document",
                "ai_processing": False
            })
            return result
        
        # Parse extracted text with NLP
        parsed_data = parse_invoice_text(extracted_text)
        
        # Update result
        result.update({
            "success": True,
            "processing_method": "Traditional OCR + NLP",
            "extracted_data": parsed_data,
            "confidence": "medium",
            "extracted_text_length": len(extracted_text),
            "ai_processing": False
        })
        
        print("✅ Traditional OCR processing completed!")
        return result
        
    except Exception as e:
        result.update({
            "success": False,
            "processing_method": "Error",
            "error": f"Processing failed: {str(e)}",
            "ai_processing": use_ai
        })
        
        print(f"❌ Processing error: {str(e)}")
        return result

# Test function
if __name__ == "__main__":
    test_file = input("Enter path to test invoice: ")
    if os.path.exists(test_file):
        
        print("\n" + "="*50)
        print("TESTING AI PROCESSING:")
        print("="*50)
        ai_result = process_invoice_end_to_end(test_file, use_ai=True)
        print(f"AI Result: {ai_result}")
        
        print("\n" + "="*50)
        print("TESTING TRADITIONAL OCR:")
        print("="*50)
        ocr_result = process_invoice_end_to_end(test_file, use_ai=False)
        print(f"OCR Result: {ocr_result}")
        
    else:
        print("File not found!")
