# Invoice Processor Backend

This is the backend service for the Invoice Processor application, which provides OCR (Optical Character Recognition) and AI-powered invoice processing capabilities.

## Features

- Dual processing methods:
  - Traditional OCR using Tesseract
  - AI-powered processing using Google Gemini
- PDF and image support
- Automatic data extraction
- REST API endpoints

## Prerequisites

Before running the application, ensure you have the following installed:

- Python 3.12+
- Tesseract OCR 5.4.0+
- Poppler Utils
- Required Python packages (see `requirements.txt`)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/MohdAli056/invoice-processor-backend.git
cd invoice-processor-backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Tesseract OCR:
- Windows: Download and install from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- Linux: `sudo apt-get install tesseract-ocr`

4. Install Poppler:
- Windows: Download from [poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases/)
- Linux: `sudo apt-get install poppler-utils`

5. Set up environment variables:
Create a `.env` file with the following:
```env
GEMINI_API_KEY=your_gemini_api_key
TESSERACT_PATH=/path/to/tesseract
POPPLER_PATH=/path/to/poppler/bin
```

## Running the Application

1. Start the FastAPI server:
```bash
python app.py
```

2. The server will start at `http://localhost:8000`

## API Endpoints

- `POST /process-invoice`: Process invoice using traditional OCR
- `POST /process-invoice-ai`: Process invoice using Gemini AI
- `GET /health`: Health check endpoint

## Deployment

### Render Deployment

1. Add the following environment variables:
```
GEMINI_API_KEY=your_gemini_api_key
TESSERACT_PATH=/usr/bin/tesseract
POPPLER_PATH=/usr/bin
```

2. Add build commands:
```bash
apt-get update && apt-get install -y tesseract-ocr poppler-utils
```

## Testing

Run the test suite:
```bash
python test_ocr_setup.py
```

## Directory Structure

```
backend/
├── app.py              # Main FastAPI application
├── ai_processor.py     # Gemini AI processing logic
├── ocr.py             # Traditional OCR processing
├── process_invoice.py  # Invoice processing utilities
├── requirements.txt    # Python dependencies
└── test_ocr_setup.py  # Setup verification script
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.
