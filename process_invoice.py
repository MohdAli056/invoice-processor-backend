from ocr import process_file
from nlp_parser import InvoiceParser
import json
import sys
import os

def process_invoice_end_to_end(file_path):
    """
    Complete invoice processing pipeline:
    1. Extract text using OCR
    2. Parse structured data using NLP
    3. Return structured JSON result
    """
    
    print(f"Processing invoice: {file_path}")
    print("=" * 50)
    
    # Step 1: Extract text using OCR
    print("Step 1: Extracting text with OCR...")
    ocr_text = process_file(file_path)
    
    if ocr_text.startswith("Error"):
        return {"error": ocr_text}
    
    print("✅ OCR extraction completed")
    
    # Step 2: Parse structured data
    print("Step 2: Parsing structured data...")
    parser = InvoiceParser()
    structured_data = parser.parse_invoice(ocr_text)
    
    print("✅ Data parsing completed")
    
    # Step 3: Clean up the result (remove raw_text for cleaner output)
    clean_result = {key: value for key, value in structured_data.items() if key != 'raw_text'}
    
    return clean_result

def save_result_to_json(result, output_file):
    """Save the processed result to a JSON file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"✅ Results saved to: {output_file}")

if __name__ == "__main__":
    # Test with your sample invoice
    invoice_path = "../data/invoices/sample_invoice.pdf"
    
    if not os.path.exists(invoice_path):
        print(f"Error: Invoice file not found at {invoice_path}")
        print("Please make sure you have a sample invoice in the data/invoices/ folder")
        sys.exit(1)
    
    # Process the invoice
    result = process_invoice_end_to_end(invoice_path)
    
    # Display results
    print("\n" + "=" * 50)
    print("📄 INVOICE PROCESSING RESULTS")
    print("=" * 50)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        for key, value in result.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
    
    # Save to JSON file
    output_file = "processed_invoice_result.json"
    save_result_to_json(result, output_file)
    
    print(f"\n🎉 Invoice processing complete!")
