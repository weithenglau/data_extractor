import argparse
import difflib
import json
import re

def preprocess_text(text):
    """Preprocesses the text by removing newlines, and leading/trailing/extra spaces."""
    # Remove newlines
    text = text.replace('\n', ' ')
    # Remove Space
    text = text.replace(' ', '')
    # Remove leading and trailing spaces
    text = text.strip()
    # Replace multiple spaces with a single space
    text = re.sub(' +', ' ', text)
    # Convert dates from DD.MM.YYYY to YYMMDD
    text = re.sub(r'(\d{2})\.(\d{2})\.(\d{4})', lambda x: x.group(3)[2:] + x.group(2) + x.group(1), text)
    # Convert dates from 13Jul2022 to 220713
    month_map = {
        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", 
        "May": "05", "Jun": "06", "Jul": "07", "Aug": "08", 
        "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
    }
    text = re.sub(r'(\d{2})(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(\d{4})', 
                  lambda x: x.group(3)[2:] + month_map[x.group(2)] + x.group(1), text)
    # Remove square and curly brackets, commas, and dots
    text = re.sub(r'[\[\]{},.]', '', text)
    return text

def load_json(file_path):
    """Loads JSON data from a file with error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file), None
    except json.decoder.JSONDecodeError as e:
        error_msg = f"Error decoding JSON from {file_path}: {e.msg}. " \
                    f"Check JSON format. Error at line {e.lineno}, column {e.colno}."
    except FileNotFoundError:
        error_msg = f"File not found: {file_path}."
    except Exception as e:
        error_msg = f"An unexpected error occurred while loading {file_path}: {e}."
    return None, error_msg

def compute_similarity(str1, str2):
    """Compute the similarity between two strings using SequenceMatcher."""
    return difflib.SequenceMatcher(None, str1, str2).ratio()

def compare_jsons(output_data, ground_truth_data):
    """Compares two JSON objects and computes accuracy based on text similarity."""
    exact_matches = 0
    total_fields = 0
    similarity_scores = []

    for key, ground_truth_value in ground_truth_data.items():
        if key in output_data:
            # Preprocess: normalize the string to improve its accuracy
            output_value = preprocess_text(output_data[key])
            ground_truth_value = preprocess_text(ground_truth_value)
            # output_value = output_data[key]
            if output_value == ground_truth_value:
                exact_matches += 1
                similarity_scores.append(1)  # Exact match
            else:
                # Compute and store the similarity score for non-exact matches
                similarity = compute_similarity(output_value, ground_truth_value)
                similarity_scores.append(similarity)
        else:
            similarity_scores.append(0)  # Key not found in output
        total_fields += 1
    
    overall_similarity = sum(similarity_scores) / total_fields if total_fields > 0 else 0
    accuracy = exact_matches / total_fields if total_fields > 0 else 0

    return {
        "exact_matches": exact_matches,
        "total_fields": total_fields,
        "overall_similarity": overall_similarity,
        "accuracy": accuracy
    }

def run_test(output_file_path='../output.json', ground_truth_file_path='ground_truth.json'):
    output_data, error = load_json(output_file_path)
    if error:
        print(f"Error loading output JSON: {error}")
        return
    
    ground_truth_data, error = load_json(ground_truth_file_path)
    if error:
        print(f"Error loading ground truth JSON: {error}")
        return
    
    results = compare_jsons(output_data, ground_truth_data)
    print(f"Test Results: {results}")
    return results

if __name__ == "__main__":
    # Create the parser
    parser = argparse.ArgumentParser(description="Compare JSON output to ground truth for accuracy.")

    # Add arguments
    parser.add_argument('-o', '--output', default='../output.json', help='Path to the output JSON file. Default is "output.json".')
    parser.add_argument('-g', '--ground_truth', default='../ground_truth.json', help='Path to the ground truth JSON file. Default is "ground_truth.json".')

    # Parse the arguments
    args = parser.parse_args()

    # Run the test with the specified or default file paths
    run_test(args.output, args.ground_truth)

