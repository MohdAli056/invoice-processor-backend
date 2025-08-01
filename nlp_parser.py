import re
from datetime import datetime
from typing import Dict, List, Optional

class InvoiceParser:
    def __init__(self):
        # Regex patterns for common invoice fields
        self.patterns = {
            'invoice_number': [
                r'Invoice\s*(?:No\.?|Number)?\s*:?\s*([A-Z0-9\-_/]+)',
                r'Invoice\s+([A-Z0-9\-_/]+)',
                r'INV[-_]?(\d+)',
                r'#\s*([A-Z0-9\-_/]+)'
            ],
            'customer_number': [
                r'Customer\s*(?:No\.?|Number)?\s*:?\s*([A-Z0-9\-_/]+)',
                r'Cust\.?\s*(?:No\.?)?\s*:?\s*([A-Z0-9\-_/]+)'
            ],
            'vat_number': [
                r'VAT\s*(?:No\.?|Number)?\s*:?\s*([A-Z0-9\s]+)',
                r'Tax\s*(?:ID|No\.?)\s*:?\s*([A-Z0-9\s]+)'
            ],
            'total_amount': [
                r'Total\s*:?\s*([€$£¥]?[\d,]+\.?\d*)',
                r'Amount\s*:?\s*([€$£¥]?[\d,]+\.?\d*)',
                r'Sum\s*:?\s*([€$£¥]?[\d,]+\.?\d*)',
                r'([€$£¥])\s*([\d,]+\.?\d*)\s*Total'
            ],
            'dates': [
                r'(\d{1,2}[./\-]\d{1,2}[./\-]\d{4})',
                r'(\d{4}[./\-]\d{1,2}[./\-]\d{1,2})',
                r'Date\s*:?\s*(\d{1,2}[./\-]\d{1,2}[./\-]\d{4})'
            ]
        }
    
    def extract_vendor_info(self, text: str) -> Dict[str, str]:
        """Extract vendor name and address from invoice text"""
        lines = text.split('\n')[:10]  # Check first 10 lines typically
        
        vendor_info = {
            'vendor_name': '',
            'vendor_address': '',
            'vendor_email': '',
            'vendor_phone': ''
        }
        
        # Look for company name (usually first non-empty line or line with GmbH, LLC, etc.)
        for line in lines:
            line = line.strip()
            if line and any(keyword in line.upper() for keyword in ['GMBH', 'LLC', 'INC', 'LTD', 'CORP']):
                vendor_info['vendor_name'] = line
                break
            elif line and not re.search(r'^\d+', line) and len(line.split()) >= 2:
                if not vendor_info['vendor_name']:
                    vendor_info['vendor_name'] = line
        
        # Extract email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match:
            vendor_info['vendor_email'] = email_match.group()
        
        # Extract phone
        phone_match = re.search(r'[\+]?[\d\s\-\(\)]{10,}', text)
        if phone_match:
            vendor_info['vendor_phone'] = phone_match.group().strip()
        
        return vendor_info
    
    def extract_field(self, text: str, field_name: str) -> Optional[str]:
        """Extract a specific field using regex patterns"""
        if field_name not in self.patterns:
            return None
        
        for pattern in self.patterns[field_name]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def extract_dates(self, text: str) -> List[str]:
        """Extract all dates from the text"""
        dates = []
        for pattern in self.patterns['dates']:
            matches = re.findall(pattern, text)
            for match in matches:
                dates.append(match)
        
        return list(set(dates))  # Remove duplicates
    
    def parse_invoice(self, ocr_text: str) -> Dict:
        """Main parsing function - extracts all key fields from OCR text"""
        
        # Extract vendor information
        vendor_info = self.extract_vendor_info(ocr_text)
        
        # Extract basic fields
        invoice_data = {
            'vendor_name': vendor_info['vendor_name'],
            'vendor_email': vendor_info['vendor_email'],
            'vendor_phone': vendor_info['vendor_phone'],
            'invoice_number': self.extract_field(ocr_text, 'invoice_number'),
            'customer_number': self.extract_field(ocr_text, 'customer_number'),
            'vat_number': self.extract_field(ocr_text, 'vat_number'),
            'total_amount': self.extract_field(ocr_text, 'total_amount'),
            'dates_found': self.extract_dates(ocr_text),
            'raw_text': ocr_text
        }
        
        return invoice_data

def test_parser():
    """Test function to demonstrate the parser"""
    # Sample OCR text for testing
    sample_text = """
    CPB SOFTWARE (GERMANY) GMBH
    Im Bruch 3, 63897 Miltenberg
    Telefon: +49 9371 9786 0
    germany@cpb-software.com
    
    Invoice WMACCESS Internet
    VAT No. DE199378386
    Customer No: 12345
    Date: 01.02.2024
    Total: €150.50
    """
    
    parser = InvoiceParser()
    result = parser.parse_invoice(sample_text)
    
    print("=== Invoice Parser Test Results ===")
    for key, value in result.items():
        if key != 'raw_text':  # Don't print the full raw text
            print(f"{key}: {value}")

if __name__ == "__main__":
    test_parser()
