import base64
import io
import json
import pytesseract # Importing the pytesseract library for OCR capabilities.
import tempfile
import yaml

from pdf2image import convert_from_path
from PIL import Image, ImageEnhance


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



    
