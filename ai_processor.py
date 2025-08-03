import google.generativeai as genai
import json
import os
from typing import Dict, Optional
from PIL import Image
import tempfile

class GeminiInvoiceProcessor:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def create_extraction_prompt(self) -> str:
        return """
        You are an expert invoice data extraction AI. Carefully analyze the provided invoice image and extract the following information in JSON format. Be very precise and thorough in your analysis.

        Rules for extraction:
        1. Look for explicit labels/fields in the invoice (e.g., "Invoice No:", "VAT:", etc.)
        2. Search for information in common invoice locations (header, footer, etc.)
        3. For amounts, include the currency symbol/code
        4. Extract ALL dates found in the document
        5. If a field is not found or unclear, use null
        6. Remove any special formatting from extracted text

        Fields to extract:
        - vendor_name: Full company/business name that issued the invoice
        - vendor_email: Complete email address of the vendor/company
        - vendor_phone: Phone number with country code if available
        - invoice_number: Unique invoice identifier/reference number
        - invoice_date: Primary invoice date (usually issue date)
        - po_number: Purchase order number if present
        - vat_number: VAT/Tax registration number
        - total_amount: Final payable amount with currency
        - subtotal: Amount before tax/VAT if available
        - tax_amount: VAT/tax amount if specified
        - payment_terms: Payment terms or due date info
        - dates_found: Array of all dates found (any format)

        Return ONLY valid JSON like this:
        {
            "vendor_name": "string or null",
            "vendor_email": "string or null",
            "vendor_phone": "string or null",
            "invoice_number": "string or null",
            "invoice_date": "string or null",
            "po_number": "string or null",
            "vat_number": "string or null",
            "total_amount": "string or null",
            "subtotal": "string or null",
            "tax_amount": "string or null",
            "payment_terms": "string or null",
            "dates_found": ["YYYY-MM-DD", ...]
        }
        """

    def process_image_with_ai(self, image_path: str) -> Dict:
        try:
            # Print debug info
            print(f"Processing image: {image_path}")
            print(f"File exists: {os.path.exists(image_path)}")
            print(f"File size: {os.path.getsize(image_path)} bytes")
            
            image = Image.open(image_path)
            print(f"Image opened successfully: {image.size}, {image.mode}")
            
            prompt = self.create_extraction_prompt()
            print("Sending request to Gemini API...")
            
            # Configure generation parameters
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
            
            generation_config = {
                "temperature": 0.1,
                "top_p": 0.1,
                "top_k": 16,
                "max_output_tokens": 2048,
            }
            
            response = self.model.generate_content(
                [prompt, image],
                safety_settings=safety_settings,
                generation_config=generation_config
            )
            
            print("Received response from Gemini API")
            response_text = response.text.strip()
            print(f"Raw response: {response_text[:200]}...")  # Print first 200 chars
            
            # Clean markdown formatting
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            print("Parsing JSON response...")
            extracted_data = json.loads(response_text)
            print("JSON parsed successfully")
            
            return {
                "success": True,
                "method": "AI (Google Gemini)",
                "extracted_data": extracted_data,
                "confidence": "high",
                "debug_info": {
                    "image_size": f"{image.size}",
                    "image_mode": image.mode,
                    "response_length": len(response_text)
                }
            }
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "method": "AI (Google Gemini)", 
                "error": f"AI response parsing error: {str(e)}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "method": "AI (Google Gemini)",
                "error": f"AI processing error: {str(e)}"
            }

    def process_pdf_with_ai(self, pdf_path: str) -> Dict:
        try:
            print(f"Processing PDF: {pdf_path}")
            print(f"PDF exists: {os.path.exists(pdf_path)}")
            print(f"PDF size: {os.path.getsize(pdf_path)} bytes")
            
            from pdf2image import convert_from_path
            
            try:
                # Try to convert with higher quality first
                print("Converting PDF to image (high quality)...")
                pages = convert_from_path(
                    pdf_path,
                    dpi=300,
                    first_page=1,
                    last_page=1,
                    use_cropbox=True,
                    grayscale=False
                )
            except Exception as e:
                print(f"High quality conversion failed: {str(e)}")
                print("Trying fallback conversion...")
                # Fallback to simpler conversion
                pages = convert_from_path(
                    pdf_path,
                    dpi=200,
                    first_page=1,
                    last_page=1
                )
            
            if not pages:
                return {
                    "success": False,
                    "method": "AI (Google Gemini)",
                    "error": "Could not convert PDF to image"
                }
            
            print(f"PDF converted successfully, page size: {pages[0].size}")
            
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_img:
                print(f"Saving temporary image to: {temp_img.name}")
                # Save with maximum quality
                pages[0].save(temp_img.name, 'PNG', quality=100, optimize=False)
                temp_img_path = temp_img.name
                print(f"Temporary image size: {os.path.getsize(temp_img_path)} bytes")
            
            try:
                result = self.process_image_with_ai(temp_img_path)
                return result
            finally:
                if os.path.exists(temp_img_path):
                    os.unlink(temp_img_path)
                    print("Temporary image cleaned up")
                    
        except Exception as e:
            return {
                "success": False,
                "method": "AI (Google Gemini)",
                "error": f"PDF processing error: {str(e)}"
            }

def create_ai_processor() -> Optional[GeminiInvoiceProcessor]:
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("Warning: GEMINI_API_KEY not found")
        return None
    return GeminiInvoiceProcessor(api_key)
