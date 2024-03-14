from dotenv import load_dotenv
import os
import pytesseract # Importing the pytesseract library for OCR capabilities.

load_dotenv()
pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_EXE_PATH")

class TextExtractor:
    def __init__(self, language='eng'):
        self.language = language

    def perform_OCR(self, regions):
        """
        Performs OCR on specified regions of an image.

        Returns:
        A dictionary with OCR results keyed by field names.
        """
        return {field: pytesseract.image_to_string(region, lang='eng') for field, region in regions.items()}



    
