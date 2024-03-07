import base64
import io
import json
import pytesseract # Importing the pytesseract library for OCR capabilities.
import tempfile
import yaml

from pdf2image import convert_from_path
from PIL import Image, ImageEnhance

class TextExtractor:
    """
    A class to extract text from documents using Optical Character Recognition (OCR).
    
    This class supports extracting text from images or PDF documents. It utilizes the pytesseract library
    to perform OCR on images. For PDF documents, it first converts them into images using the pdf2image library.
    
    Attributes:
        document (str): A base64 encoded string of the document image or the path to a PDF file.
        template_name (str): The name of the template to use for targeted text extraction. Templates define specific
                             areas of the document to extract text from.
    """
    def __init__(self, document, template_name):
        """
        Initializes the TextExtractor with the document and template name.
        
        Parameters:
            document (str): The document to extract text from. Can be a base64 encoded string of an image or a PDF file path.
            template_name (str): The template name for targeted text extraction.
        """
        self.document = document
        self.template_name = template_name
        self.templates_coord = self.load_templates_yaml('../templates.yaml')

    def extract_text(self):
        """
        Main method to extract text from the document. It decodes the document,
        applies template-based cropping if necessary, performs OCR, and exports results to JSON.
        
        Returns:
        Tuple containing the OCR results as a dictionary and the path to the output JSON file.
        """
        image = self.decode_document()
        if image is None:
            print("Unsupported document format")
            return {}

        self.extract_fields()
        regions = self.crop_ROI(image)
        ocr_results = self.perform_OCR(regions)
        
        # Export OCR results to JSON
        output_json_path = self.export_to_json(ocr_results)

        return ocr_results, output_json_path

    def decode_document(self):
        """
        Decodes the base64 encoded document into an image object or handles PDF conversion.

        Returns:
        Image object ready for OCR processing or None if unsupported format.
        """
        if self.document.startswith("/9j"):  # JPEG
            return self.decode_base64_to_image(self.document, 'jpeg')
        elif self.document.startswith("JVB"):  # PDF
            return self.decode_base64_to_image(self.document, 'pdf')
        return None

    def decode_base64_to_image(self, data, doc_type):
        """
        Helper method to decode base64 data to an image, handling JPEG and PDF.

        Returns:
        An image object or the first page of a PDF as an image.
        """
        img_data = base64.b64decode(data)
        if doc_type == 'jpeg':
            image = Image.open(io.BytesIO(img_data)).convert('L')
            return self.image_preprocessing(image) if self.template_name == 'tnb_physical' else image
        elif doc_type == 'pdf':
            with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp_pdf:
                tmp_pdf.write(img_data)
                images = convert_from_path(tmp_pdf.name)
            return images[0] if images else None

    def perform_OCR(self, regions):
        """
        Performs OCR on specified regions of an image.

        Returns:
        A dictionary with OCR results keyed by field names.
        """
        return {field: pytesseract.image_to_string(region, lang='eng') for field, region in regions.items()}

    def crop_ROI(self, image):
        """
        Crops regions of interest from the image based on template coordinates.

        Returns:
        A dictionary with cropped image regions keyed by field names.
        """
        padding = 3
        return {
            field: image.crop((coords['x1']-padding, coords['y1']-padding, coords['x2']+padding, coords['y2']+padding))
            for field, coords in self.templates_coord.items()
        }

    def extract_fields(self):
        """
        Updates the template coordinates based on the selected template.
        """
        self.templates_coord = {field: coords['bounding_box_actual'] for field, coords in self.templates_coord[self.template_name].items()}

    @staticmethod
    def load_templates_yaml(file_path):
        """
        Loads template definitions from a YAML file.

        Returns:
        A dictionary of template coordinates and settings.
        """
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)

    @staticmethod
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
    
    def export_to_json(self, results, file_path='../output.json'):
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

    
