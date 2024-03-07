# FastAPI Document Processing Application

This application provides a web interface for uploading documents (images and PDFs), extracting text from them using OCR (Optical Character Recognition), and running predefined tests against the extracted text. It utilizes FastAPI for the backend, integrating file handling, text extraction, and results presentation through HTML templates.

## Features

- **File Upload**: Supports uploading of JPG and PDF files for text extraction.
- **Text Extraction**: Utilizes `pytesseract` for OCR to extract text from uploaded documents.
- **Template-based Extraction**: Supports extracting text from specific document areas defined by templates.
- **Test Results**: Compares extracted text against predefined ground truths and presents test results.

## Requirements

- Python 3.9+
- FastAPI
- PyTesseract
- pdf2image
- PIL (Python Imaging Library)
- YAML for Python (PyYAML)
- Poppler for Windows/Linux/macOS

## Setup

1. **Clone the repository**:
git clone <repository-url>
cd <repository-directory>

2. **Install dependencies**:
pip install fastapi uvicorn pytesseract pdf2image pillow pyyaml


3. **Install Poppler**:
- For Windows, download binaries from [Poppler Windows](http://blog.alivate.com.au/poppler-windows/), and add the `bin` directory to your PATH.
- For Ubuntu/Debian, install Poppler using:
  ```
  sudo apt-get install poppler-utils
  ```
- For macOS, you can use Homebrew:
  ```
  brew install poppler
  ```

Poppler is required for `pdf2image` to convert PDF files into images for OCR processing.

4. **Run the application**:
uvicorn main:app --reload


This command starts the FastAPI server. Access the web interface at `http://127.0.0.1:8000`.

## How to Use

- Navigate to `http://127.0.0.1:8000` in your web browser to access the file upload interface.
- Select a JPG or PDF file to upload and choose a template_name for text extraction if necessary.
- Submit the form to process the document. The extracted text and any test results will be displayed on a new page.

## Using CURL to Post Requests with Base64-Encoded Document

If you prefer to send the document as a base64-encoded string, you can use `curl` to post the request. This method is useful for scenarios where direct file uploads are not feasible or when embedding document data directly within the request payload is preferred.

### Encoding Your Document

First, encode your document to a base64 string. 

On Linux or macOS, you can use the following command:

```bash
base64 /path/to/your/document.pdf > document_base64.txt

curl -X POST "http://127.0.0.1:8000/upload-base64" \
     -H "Content-Type: application/json" \
     -d '{"document": "$(cat document_base64.txt)", "template_name": "your_template_name"}'
```

On Windows, you can use PowerShell to encode the document. Open PowerShell and run:

```bash
[Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\path\to\your\document.pdf")) | Out-File document_base64.txt

curl.exe -X POST "http://127.0.0.1:8000/upload-base64" `
     -H "Content-Type: application/json" `
     -d '{"document": "'$(Get-Content document_base64.txt -Raw)'", "template_name": "your_template_name"}'
```

## Structure

- `main.py`: The FastAPI application setup, routes, and logic for handling requests.
- `text_extractor.py`: Defines the `TextExtractor` class for handling OCR and template-based text extraction.
- `test.py`: Contains logic for preprocessing text and comparing extracted text against a ground truth.
- `templates/`: Directory containing HTML templates for the UI.
- `static/css/`: Contains CSS files for styling the web interface.

## Notes

- Ensure `tesseract-ocr` is installed on your system for `pytesseract` to work properly.
- Adjust the path to `tesseract` in `text_extractor.py` if necessary, depending on your installation.

## Contributing

Contributions to improve the application are welcome. Please fork the repository and submit a pull request with your changes.