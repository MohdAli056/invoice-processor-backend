import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import cv2
import numpy as np
import os

def preprocess_image(image_path):
    """
    Preprocess image to improve OCR accuracy
    """
    img = cv2.imread(image_path)
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Apply threshold to get image with only black and white
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def extract_text_from_image(image_path):
    """
    Extract text from image using Tesseract OCR
    """
    try:
        # Preprocess image
        processed_img = preprocess_image(image_path)
        
        # Extract text
        text = pytesseract.image_to_string(processed_img, config='--psm 6')
        return text.strip()
    except Exception as e:
        return f"Error processing image: {str(e)}"

def extract_text_from_pdf(pdf_path):
    """
    Convert PDF to images and extract text
    """
    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path)
        extracted_text = ""
        
        for i, image in enumerate(images):
            # Save temporary image
            temp_image_path = f"temp_page_{i}.jpg"
            image.save(temp_image_path, 'JPEG')
            
            # Extract text from image
            page_text = extract_text_from_image(temp_image_path)
            extracted_text += f"\n--- Page {i+1} ---\n{page_text}\n"
            
            # Clean up temp file
            os.remove(temp_image_path)
        
        return extracted_text.strip()
    except Exception as e:
        return f"Error processing PDF: {str(e)}"

def process_file(file_path):
    """
    Main function to process either PDF or image file
    """
    file_extension = file_path.lower().split('.')[-1]
    
    if file_extension == 'pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension in ['jpg', 'jpeg', 'png', 'tiff', 'bmp']:
        return extract_text_from_image(file_path)
    else:
        return "Unsupported file format"

if __name__ == "__main__":
    # Test the OCR function
    test_file = "../data/invoices/sample_invoice.pdf"  # You'll add this
    result = process_file(test_file)
    print("Extracted Text:")
    print("-" * 50)
    print(result)
