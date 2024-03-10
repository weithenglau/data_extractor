import keras_ocr
import base64
from io import BytesIO
from PIL import Image

class KerasOCR:
    def perform_OCR(self, regions):
        """
        Perform Optical Character Recognition (OCR) on the given regions.
        
        Args:
            regions (dict): A dictionary containing regions to perform OCR on.
        
        Returns:
            dict: A dictionary containing OCR results with fields as keys and merged texts as values.
        """

        output_dict = {}
        for field, region in regions.items():
            prediction_groups = keras_ocr.pipeline.Pipeline().recognize([region])
            merged_texts = self.merge_predictions(prediction_groups)
            output_dict[field] = merged_texts

        return output_dict

    def merge_predictions(self, prediction_groups):
        """
        Merge OCR predictions that share the same y-level.

        Args:
            prediction_groups (list): A list of OCR prediction groups for a single region.

        Returns:
            list: A list of merged texts.
        """
        merged_predictions = {}
        for text, box in prediction_groups[0]:
            added = False
            for key, value in merged_predictions.items():
                if self.share_same_y(value['box'], box):
                    value['texts'].append(text)
                    value['box'] = [value['box'][0], box[1], box[2], value['box'][3]]
                    added = True
                    break
            if not added:
                merged_predictions[len(merged_predictions)] = {'texts': [text], 'box': box}

        merged_texts = [' '.join(data['texts']) for data in merged_predictions.values()]
        return merged_texts

    def share_same_y(self, box1, box2, threshold=5):
        """
        Check if two bounding boxes share the same y-level within a threshold.

        Args:
            box1 (list): Bounding box coordinates of the first box.
            box2 (list): Bounding box coordinates of the second box.
            threshold (int): Maximum allowed difference in y-level.

        Returns:
            bool: True if boxes share the same y-level, False otherwise.
        """
        y1 = [y for x, y in box1]
        y2 = [y for x, y in box2]
        return abs(min(y1) - min(y2)) < threshold and abs(max(y1) - max(y2)) < threshold



