from fastapi import FastAPI, Request, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from test import run_test
from text_extractor import TextExtractor
from keras_OCR import KerasOCR
from utils import crop_ROI, decode_document, extract_fields, export_to_json, load_templates_yaml
import base64
import shutil
import os
import traceback

app = FastAPI()

# Mount the static files directory to serve CSS, JS, and images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Jinja2 templates for HTML rendering
templates = Jinja2Templates(directory="templates")

# Define Pydantic model for requests with base64-encoded documents
class ExtractionRequest(BaseModel):
    document: str  # Base64-encoded document
    template_name: str
    checkboxAI: bool

def process_document(base64_encoded_content, template_name, checkboxAI):
    """
    Process the document by decoding, extracting regions, extracting text, and running tests.
    """
    templates_coord = load_templates_yaml(r'../templates.yaml')
    image = decode_document(base64_encoded_content, template_name)
    selected_template_coord = extract_fields(template_name, templates_coord)
    regions = crop_ROI(image, selected_template_coord)
    if checkboxAI:
        keras_extractor = KerasOCR()
        extracted_text= keras_extractor.perform_OCR(regions)
    else:
        extractor = TextExtractor()
        extracted_text= extractor.perform_OCR(regions)

    output_json_path= export_to_json(extracted_text)
    groundtruth_json_path = os.path.join(r'../ground_truth', f'{template_name}.json')
    test_results = run_test(output_json_path, groundtruth_json_path)

    return extracted_text, test_results

# Route to render the main page where users can upload documents
@app.get("/")
async def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Route to handle document upload and text extraction
@app.post("/upload-file")
async def upload_file(request: Request, document: UploadFile = File(...), template_name: str = Form(...), checkboxAI: str = Form("false")):
    try:
        # Read and encode the uploaded file content to base64
        file_content = await document.read()

        base64_encoded_content = base64.b64encode(file_content).decode()

        checkboxAI_bool = checkboxAI.lower() in ["true", "on", "1"]

        extracted_text, test_results = process_document(base64_encoded_content, template_name, checkboxAI_bool)
        
        # Render the results page with extracted text and test results
        return templates.TemplateResponse("results.html", {
            "request": request,
            "message": "Processed file upload",
            "extracted_text": extracted_text,
            "test_results": test_results
        })
    except Exception as e:
        # Handle exceptions by returning an HTTP error response
        # print exception
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Ensure the uploaded file is closed
        await document.close()

# Route to handle requests with base64-encoded document content
@app.post("/upload-base64")
async def upload_base64(request_data: ExtractionRequest):
    try:
        base64_encoded_content = request_data.document
        template_name = request_data.template_name
        enableAI = request_data.checkboxAI

        extracted_text, test_results = process_document(base64_encoded_content, template_name, enableAI)

        # Return a JSON response with the processing results
        return {"message": "Processed base64 submission", "extracted_text": extracted_text, "test_results": test_results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Entry point to run the application when executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)

