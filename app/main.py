from fastapi import FastAPI, Request, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from test import run_test
from text_extractor import TextExtractor
import base64
import shutil
import os

app = FastAPI()

# Mount the static files directory to serve CSS, JS, and images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Jinja2 templates for HTML rendering
templates = Jinja2Templates(directory="templates")

# Define Pydantic model for request data validation
class RequestData(BaseModel):
    document: str
    template_name: str

# Route to render the main page where users can upload documents
@app.get("/")
async def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Route to handle document upload and text extraction
@app.post("/upload-file")
async def upload_file(request: Request, document: UploadFile = File(...), template_name: str = Form(...)):
    try:
        # Read and encode the uploaded file content to base64
        file_content = await document.read()
        base64_encoded_content = base64.b64encode(file_content).decode()

        # Initialize the text extractor with the encoded content and template name
        extractor = TextExtractor(base64_encoded_content, template_name)
        # Extract text from the document
        extracted_text, output_json_path = extractor.extract_text()

        # Generate path for ground truth JSON for comparison
        groundtruth_json_path = os.path.join('../ground_truth', f'{template_name}.json')
        # Compare extracted text against ground truth
        test_results = run_test(output_json_path, groundtruth_json_path)

        # Render the results page with extracted text and test results
        return templates.TemplateResponse("results.html", {
            "request": request,
            "message": "Processed file upload",
            "extracted_text": extracted_text,
            "test_results": test_results
        })
    except Exception as e:
        # Handle exceptions by returning an HTTP error response
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Ensure the uploaded file is closed
        await document.close()

# Define Pydantic model for requests with base64-encoded documents
class ExtractionRequest(BaseModel):
    document: str  # Base64-encoded document
    template_name: str

# Route to handle requests with base64-encoded document content
@app.post("/upload-base64")
async def upload_base64(request_data: ExtractionRequest):
    try:
        base64_encoded_content = request_data.document
        template_name = request_data.template_name

        # Process the document and extract text as before
        extractor = TextExtractor(base64_encoded_content, template_name)
        extracted_text, output_json_path = extractor.extract_text()
        groundtruth_json_path = os.path.join('../ground_truth', f'{template_name}.json')
        test_results = run_test(output_json_path, groundtruth_json_path)

        # Return a JSON response with the processing results
        return {"message": "Processed base64 submission", "extracted_text": extracted_text, "test_results": test_results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Entry point to run the application when executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


# from fastapi import FastAPI, Request, File, UploadFile, Form, HTTPException
# from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from pydantic import BaseModel
# from test import run_test
# from text_extractor import TextExtractor
# import base64
# import shutil
# import os

# app = FastAPI()

# # Mount the static files directory
# app.mount("/static", StaticFiles(directory="static"), name="static")

# # Initialize Jinja2 templates
# templates = Jinja2Templates(directory="templates")

# class RequestData(BaseModel):
#     document: str
#     template_name: str

# @app.get("/")
# async def main(request: Request):
#     # Use TemplateResponse to render HTML templates
#     return templates.TemplateResponse("index.html", {"request": request})

# @app.post("/upload-file")
# async def upload_file(request: Request, document: UploadFile = File(...), template_name: str = Form(...), ):
#     try:
#         file_content = await document.read()
#         base64_encoded_content = base64.b64encode(file_content).decode()
#         extractor = TextExtractor(base64_encoded_content, template_name)
#         extracted_text, output_json_path = extractor.extract_text()
#         groundtruth_json_path = os.path.join('../ground_truth', f'{template_name}.json')
#         test_results = run_test(output_json_path, groundtruth_json_path)
        
#         return templates.TemplateResponse("results.html",{"request": request, "message": "Processed file upload", "extracted_text": extracted_text, "test_results": test_results})
    
#         # Your processing logic here
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#     finally:
#         await document.close()
    

# class ExtractionRequest(BaseModel):
#     document: str  # Base64-encoded document
#     template_name: str

# @app.post("/upload-base64")
# async def upload_base64(request_data: ExtractionRequest):
#     try:
#         base64_encoded_content = request_data.document
#         template_name = request_data.template_name
#         extractor = TextExtractor(base64_encoded_content, template_name)
#         extracted_text, output_json_path = extractor.extract_text()
#         groundtruth_json_path = os.path.join('../ground_truth', f'{template_name}.json')
#         test_results = run_test(output_json_path, groundtruth_json_path)
#         # Your processing logic here
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#     return {"message": "Processed base64 submission", "extracted_text": extracted_text, "test_results": test_results}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)


