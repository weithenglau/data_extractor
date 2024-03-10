from pdf2image import convert_from_bytes
from PIL import Image, ImageEnhance

import base64
import io
import json
import yaml

def crop_ROI(image, templates_coord):
    """
    Crops regions of interest from the image based on template coordinates.

    Returns:
    A dictionary with cropped image regions keyed by field names.
    """
    padding = 3
    return {
        field: image.crop((coords['x1']-padding, coords['y1']-padding, coords['x2']+padding, coords['y2']+padding))
        for field, coords in templates_coord.items()
    }

def decode_base64_to_image(data, doc_type, template_name):
    """
    Helper method to decode base64 data to an image, handling JPEG and PDF.

    Returns:
    An image object or the first page of a PDF as an image.
    """
    img_data = base64.b64decode(data)
    if doc_type == 'jpeg':
        image = Image.open(io.BytesIO(img_data)).convert('L')

        return image_preprocessing(image) if template_name == 'tnb_physical' else image
    
    elif doc_type == 'pdf':
        # Decode base64 data
        img_data = base64.b64decode(data)

        # Create a BytesIO object to store PDF content in memory
        pdf_file = io.BytesIO(img_data)

        # Convert the PDF content into an image
        images = convert_from_bytes(pdf_file.read())

        # Return the first image if available
        return images[0] if images else None

def decode_document(base64_encoded_content, template_name):
    """
    Decodes the base64 encoded document into an image object or handles PDF conversion.

    Returns:
    Image object ready for OCR processing or None if unsupported format.
    """
    if base64_encoded_content.startswith("/9j"):  # JPEG
        return decode_base64_to_image(base64_encoded_content, 'jpeg', template_name)
    elif base64_encoded_content.startswith("JVB"):  # PDF
        return decode_base64_to_image(base64_encoded_content, 'pdf', template_name)
    return None

def extract_fields(template_name, templates_coord):
    """
    Updates the template coordinates based on the selected template.
    """
    return {field: coords['bounding_box_actual'] for field, coords in templates_coord[template_name].items()}

def image_preprocessing(image):
    """
    Applies image preprocessing to enhance OCR accuracy.

    Returns:
    The enhanced image.
    """
    enhancers = [
        (ImageEnhance.Contrast, 2),
        (ImageEnhance.Sharpness, 2),
        (ImageEnhance.Brightness, 1.2)
    ]
    for enhancer, factor in enhancers:
        image = enhancer(image).enhance(factor)
    return image

def load_templates_yaml(file_path):
    """
    Loads template definitions from a YAML file.

    Returns:
    A dictionary of template coordinates and settings.
    """
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)
    
def export_to_json(results, file_path='../output.json'):
    """
    Exports OCR results to a JSON file.

    Parameters:
    - results (dict): OCR results to be exported.
    - file_path (str): Path to the output JSON file.
    
    Returns:
    The file path of the exported JSON.
    """
    """Export OCR results to a JSON file."""
    with open(file_path, 'w') as file:
        json.dump(results, file, indent=4, ensure_ascii=False)
    return file_path
# from pdf2image import convert_from_path
# from PIL import Image, ImageEnhance

# import base64
# import io
# import json
# import tempfile
# import yaml

# def crop_ROI(image, templates_coord):
#     """
#     Crops regions of interest from the image based on template coordinates.

#     Returns:
#     A dictionary with cropped image regions keyed by field names.
#     """
#     padding = 3
#     return {
#         field: image.crop((coords['x1']-padding, coords['y1']-padding, coords['x2']+padding, coords['y2']+padding))
#         for field, coords in templates_coord.items()
#     }

# def decode_base64_to_image(data, doc_type, template_name):
#     """
#     Helper method to decode base64 data to an image, handling JPEG and PDF.

#     Returns:
#     An image object or the first page of a PDF as an image.
#     """
#     img_data = base64.b64decode(data)
#     if doc_type == 'jpeg':
#         image = Image.open(io.BytesIO(img_data)).convert('L')
#         return image_preprocessing(image) if template_name == 'tnb_physical' else image
#     elif doc_type == 'pdf':
#         with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp_pdf:
#             tmp_pdf.write(img_data)
#             images = convert_from_path(tmp_pdf.name)
#         return images[0] if images else None

# def decode_document(base64_encoded_content, template_name):
#     """
#     Decodes the base64 encoded document into an image object or handles PDF conversion.

#     Returns:
#     Image object ready for OCR processing or None if unsupported format.
#     """
#     if base64_encoded_content.startswith("/9j"):  # JPEG
#         return decode_base64_to_image(base64_encoded_content, 'jpeg', template_name)
#     elif base64_encoded_content.startswith("JVB"):  # PDF
#         return decode_base64_to_image(base64_encoded_content, 'pdf', template_name)
#     return None

# def extract_fields(template_name, templates_coord):
#     """
#     Updates the template coordinates based on the selected template.
#     """
#     return {field: coords['bounding_box_actual'] for field, coords in templates_coord[template_name].items()}

# def image_preprocessing(image):
#     """
#     Applies image preprocessing to enhance OCR accuracy.

#     Returns:
#     The enhanced image.
#     """
#     enhancers = [
#         (ImageEnhance.Contrast, 2),
#         (ImageEnhance.Sharpness, 2),
#         (ImageEnhance.Brightness, 1.2)
#     ]
#     for enhancer, factor in enhancers:
#         image = enhancer(image).enhance(factor)
#     return image

# def load_templates_yaml(file_path):
#     """
#     Loads template definitions from a YAML file.

#     Returns:
#     A dictionary of template coordinates and settings.
#     """
#     with open(file_path, 'r') as file:
#         return yaml.safe_load(file)
    
# def export_to_json(results, file_path='../output.json'):
#     """
#     Exports OCR results to a JSON file.

#     Parameters:
#     - results (dict): OCR results to be exported.
#     - file_path (str): Path to the output JSON file.
    
#     Returns:
#     The file path of the exported JSON.
#     """
#     """Export OCR results to a JSON file."""
#     with open(file_path, 'w') as file:
#         json.dump(results, file, indent=4, ensure_ascii=False)
#     return file_path