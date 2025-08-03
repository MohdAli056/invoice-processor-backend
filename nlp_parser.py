import re
from typing import Dict, List, Optional

def extract_structured_data(text: str) -> Dict:
    """
    Enhanced NLP parser that handles multiple invoice formats and layouts
    """
    
    # Clean and normalize text
    text = text.strip()
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Initialize result structure
    result = {
        "vendor_name": None,
        "vendor_email": None,
        "vendor_phone": None,
        "vendor_address": None,
        "invoice_number": None,
        "invoice_date": None,
        "due_date": None,
        "customer_name": None,
        "customer_number": None,
        "vat_number": None,
        "total_amount": None,
        "subtotal": None,
        "tax_amount": None,
        "currency": None,
        "payment_terms": None,
        "description": None,
        "dates_found": []
    }
    
    # Enhanced patterns for different invoice formats
    patterns = {
        'vendor_name': [
            r'^([A-Z][A-Z\s&\-\.\(\)]{10,})', # Company names (caps)
            r'From:\s*([A-Za-z][A-Za-z\s&\-\.\(\)]{5,})', # "From:" format
            r'Bill From:\s*([A-Za-z][A-Za-z\s&\-\.\(\)]{5,})', # "Bill From:" format
            r'Invoice From:\s*([A-Za-z][A-Za-z\s&\-\.\(\)]{5,})', # "Invoice From:" format
            r'^([A-Za-z][A-Za-z\s&\-\.\(\)]{10,})\s*$', # Standalone company name
        ],
        
        'vendor_email': [
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', # Standard email
            r'Email:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', # "Email:" prefix
            r'E-mail:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', # "E-mail:" prefix
        ],
        
        'vendor_phone': [
            r'(?:Phone|Tel|Telephone):\s*([+\d\s\-\(\)]{8,})', # Phone with prefix
            r'([+]\d{1,3}[\s\-]?\d{1,4}[\s\-]?\d{4,})', # International format
            r'(\(\d{3}\)\s*\d{3}[\-\s]?\d{4})', # US format (xxx) xxx-xxxx
            r'(\d{3}[\-\.\s]\d{3}[\-\.\s]\d{4})', # xxx-xxx-xxxx format
        ],
        
        'invoice_number': [
            r'Invoice\s*(?:Number|#|No\.?):\s*([A-Za-z0-9\-]+)', # Invoice Number:
            r'Invoice\s*([A-Za-z0-9\-]+)', # Invoice followed by number
            r'INV[\-\s]*(\d+)', # INV-xxxx format
            r'(?:^|\n)([A-Za-z]{2,4}\-\d+)', # ABC-1234 format
            r'#\s*([A-Za-z0-9\-]+)', # #xxxx format
        ],
        
        'customer_number': [
            r'Customer\s*(?:Number|#|No\.?):\s*([A-Za-z0-9\-]+)',
            r'Client\s*(?:Number|#|No\.?):\s*([A-Za-z0-9\-]+)',
            r'Account\s*(?:Number|#|No\.?):\s*([A-Za-z0-9\-]+)',
        ],
        
        'vat_number': [
            r'VAT\s*(?:Number|#|No\.?):\s*([A-Za-z0-9\-]+)',
            r'Tax\s*(?:ID|Number):\s*([A-Za-z0-9\-]+)',
            r'GST\s*(?:Number|#):\s*([A-Za-z0-9\-]+)',
            r'ABN:\s*([A-Za-z0-9\-\s]+)',
        ],
        
        'total_amount': [
            r'Total\s*(?:Due|Amount)?:?\s*[\$£€¥]?([\d,]+\.?\d{0,2})', # Total: $xx.xx
            r'Amount\s*(?:Due)?:?\s*[\$£€¥]?([\d,]+\.?\d{0,2})', # Amount Due: $xx.xx
            r'Grand\s*Total:?\s*[\$£€¥]?([\d,]+\.?\d{0,2})', # Grand Total: $xx.xx
            r'Final\s*Total:?\s*[\$£€¥]?([\d,]+\.?\d{0,2})', # Final Total: $xx.xx
            r'[\$£€¥]([\d,]+\.?\d{0,2})(?:\s*(?:USD|EUR|GBP|CAD))?$', # Currency symbol at start
        ],
        
        'dates': [
            r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', # MM/DD/YYYY or DD/MM/YYYY
            r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})', # DD Month YYYY
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{2,4})', # Month DD, YYYY
            r'(\d{2,4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2})', # YYYY/MM/DD
            r'(\d{1,2}\.\d{1,2}\.\d{2,4})', # European format DD.MM.YYYY
        ]
    }
    
    # Extract data using patterns
    full_text = ' '.join(lines)
    
    # Vendor Name - try multiple approaches
    for pattern in patterns['vendor_name']:
        matches = re.findall(pattern, full_text, re.IGNORECASE | re.MULTILINE)
        if matches:
            # Filter out common false positives
            for match in matches:
                match = match.strip()
                if (len(match) > 5 and 
                    'Page' not in match and 
                    'Invoice' not in match and
                    'Total' not in match and
                    not re.match(r'^\d+', match)):
                    result['vendor_name'] = match
                    break
            if result['vendor_name']:
                break
    
    # Email extraction
    for pattern in patterns['vendor_email']:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        if matches:
            result['vendor_email'] = matches[0]
            break
    
    # Phone extraction  
    for pattern in patterns['vendor_phone']:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        if matches:
            result['vendor_phone'] = matches[0].strip()
            break
    
    # Invoice Number extraction
    for pattern in patterns['invoice_number']:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        if matches:
            result['invoice_number'] = matches[0].strip()
            break
    
    # Customer Number extraction
    for pattern in patterns['customer_number']:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        if matches:
            result['customer_number'] = matches[0].strip()
            break
    
    # VAT Number extraction
    for pattern in patterns['vat_number']:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        if matches:
            result['vat_number'] = matches[0].strip()
            break
    
    # Total Amount extraction
    for pattern in patterns['total_amount']:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        if matches:
            # Clean up the amount (remove commas, etc.)
            amount = matches[0].replace(',', '')
            result['total_amount'] = f"${amount}"
            break
    
    # Date extraction
    all_dates = []
    for pattern in patterns['dates']:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        all_dates.extend(matches)
    
    # Remove duplicates and filter valid dates
    unique_dates = list(set(all_dates))
    result['dates_found'] = unique_dates[:5]  # Limit to 5 dates max
    
    return result

def parse_invoice_text(text: str) -> Dict:
    """
    Main parsing function that coordinates the extraction
    This is the function that process_invoice.py is trying to import
    """
    if not text or len(text.strip()) < 10:
        return {
            "error": "Text too short or empty for processing",
            "vendor_name": None,
            "vendor_email": None,
            "vendor_phone": None,
            "vendor_address": None,
            "invoice_number": None,
            "invoice_date": None,
            "due_date": None,
            "customer_name": None,
            "customer_number": None,
            "vat_number": None,
            "total_amount": None,
            "subtotal": None,
            "tax_amount": None,
            "currency": None,
            "payment_terms": None,
            "description": None,
            "dates_found": []
        }
    
    try:
        extracted_data = extract_structured_data(text)
        return extracted_data
        
    except Exception as e:
        return {
            "error": f"Error parsing invoice text: {str(e)}",
            "vendor_name": None,
            "vendor_email": None,
            "vendor_phone": None,
            "vendor_address": None,
            "invoice_number": None,
            "invoice_date": None,
            "due_date": None,
            "customer_name": None,
            "customer_number": None,
            "vat_number": None,
            "total_amount": None,
            "subtotal": None,
            "tax_amount": None,
            "currency": None,
            "payment_terms": None,
            "description": None,
            "dates_found": []
        }
