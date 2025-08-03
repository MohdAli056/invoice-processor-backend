import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance, ImageFilter
import tempfile
import os
from typing import List, Optional

def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Enhanced image preprocessing for better OCR accuracy
    Handles photos, scans, and low-quality images
    """
    
    # Convert to numpy array for OpenCV processing
    img_array = np.array(image)
    
    # Convert to grayscale if not already
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array
    
    # Apply denoising for scanned/photographed documents
    denoised = cv2.fastNlMeansDenoising(gray)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(denoised, (1, 1), 0)
    
    # Apply adaptive thresholding for better text separation
    # This works well for photos with uneven lighting
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    # Apply morphological operations to clean up the image
    kernel = np.ones((1, 1), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    # Convert back to PIL Image
    processed_image = Image.fromarray(cleaned)
    
    # Enhance contrast and sharpness
    enhancer = ImageEnhance.Contrast(processed_image)
    processed_image = enhancer.enhance(1.5)
    
    enhancer = ImageEnhance.Sharpness(processed_image)
    processed_image = enhancer.enhance(1.2)
    
    return processed_image

def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from image files (JPG, PNG, TIFF, etc.)
    Optimized for invoice processing with preprocessing
    """
    try:
        print(f"Processing image: {image_path}")
        
        # Check if pytesseract is properly configured
        try:
            pytesseract.get_tesseract_version()
        except Exception as e:
            print(f"Tesseract not properly configured: {e}")
            print("Please ensure Tesseract is installed and in your PATH")
            return ""
        
        # Load image
        image = Image.open(image_path)
        print(f"Image loaded successfully: {image.size}, {image.mode}")
        
        # Rotate image if needed (handle rotated phone photos)
        image = auto_rotate_image(image)
        
        # Preprocess image for better OCR
        processed_image = preprocess_image(image)
        print("Image preprocessing completed")
        
        # Configure Tesseract for better accuracy
        custom_config = r'--oem 3 --psm 6 -l eng --tessdata-dir "C:\\Program Files\\Tesseract-OCR\\tessdata" -c tesseract_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,()/-:@#$%&+= '
        
        # Extract text using Tesseract with timeout
        print("Starting OCR processing...")
        text = pytesseract.image_to_string(processed_image, config=custom_config)
        print(f"OCR completed, extracted {len(text)} characters")
        
        return text.strip()
        
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return ""

def auto_rotate_image(image: Image.Image) -> Image.Image:
    """
    Auto-rotate image based on EXIF data (handles phone photos)
    """
    try:
        # Get EXIF data
        if hasattr(image, '_getexif'):
            exif = image._getexif()
            if exif is not None:
                orientation = exif.get(274)  # 274 is the orientation tag
                if orientation == 3:
                    image = image.rotate(180, expand=True)
                elif orientation == 6:
                    image = image.rotate(270, expand=True)
                elif orientation == 8:
                    image = image.rotate(90, expand=True)
    except:
        pass  # If EXIF processing fails, continue without rotation
    
    return image

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Enhanced PDF text extraction with better error handling
    """
    try:
        # Convert PDF to images
        pages = convert_from_path(pdf_path, dpi=300)  # Higher DPI for better quality
        
        extracted_texts = []
        
        for page_num, page in enumerate(pages, 1):
            print(f"Processing page {page_num}...")
            
            # Preprocess each page
            processed_page = preprocess_image(page)
            
            # Configure Tesseract for invoices
            custom_config = r'--oem 3 --psm 6 -c tesseract_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,()/-:@#$%&+= '
            
            # Extract text from this page
            page_text = pytesseract.image_to_string(processed_page, config=custom_config)
            
            if page_text.strip():
                extracted_texts.append(f"--- Page {page_num} ---\n{page_text.strip()}")
        
        return "\n\n".join(extracted_texts)
        
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return ""

def process_file(file_path: str) -> str:
    """
    Enhanced file processor that handles PDFs and images
    Automatically detects file type and applies appropriate processing
    """
    
    if not os.path.exists(file_path):
        return "Error: File not found"
    
    # Get file extension
    file_extension = os.path.splitext(file_path)[1].lower()
    
    print(f"Processing file: {file_path}")
    print(f"File type: {file_extension}")
    
    try:
        # Handle PDF files
        if file_extension == '.pdf':
            print("Processing as PDF...")
            return extract_text_from_pdf(file_path)
        
        # Handle image files
        elif file_extension in ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.webp']:
            print(f"Processing as image ({file_extension})...")
            return extract_text_from_image(file_path)
        
        else:
            return f"Error: Unsupported file type '{file_extension}'. Supported formats: PDF, JPG, JPEG, PNG, TIFF, BMP, WebP"
    
    except Exception as e:
        return f"Error processing file: {str(e)}"

def enhance_text_quality(text: str) -> str:
    """
    Post-process extracted text to improve quality
    Handles common OCR errors and formatting issues
    """
    if not text:
        return text
    
    # Common OCR corrections
    corrections = {
        '0': 'O',  # Zero to letter O in some contexts
        'l': '1',  # Letter l to number 1 in numeric contexts
        'S': '5',  # Letter S to number 5 in numeric contexts
        '|': 'I',  # Pipe to letter I
        '©': '@',  # Copyright symbol to @ in emails
    }
    
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Remove excessive whitespace
        line = ' '.join(line.split())
        
        # Skip very short lines that are likely noise
        if len(line.strip()) < 2:
            continue
            
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

# Test function for development
if __name__ == "__main__":
    test_file = input("Enter path to test file: ")
    if os.path.exists(test_file):
        result = process_file(test_file)
        print("\n" + "="*50)
        print("EXTRACTED TEXT:")
        print("="*50)
        print(result)
    else:
        print("File not found!")
