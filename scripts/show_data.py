import json
import os
from bs4 import BeautifulSoup

# --- Configuration ---
# CHANGE THIS to the name of the file you want to inspect
# You can copy the full name from your data/processed folder
FILENAME_TO_INSPECT = "20250812-073410_embed-tables-sample.json"
# -------------------

PROCESSED_DATA_DIR = "data/processed"
file_path = os.path.join(PROCESSED_DATA_DIR, FILENAME_TO_INSPECT)

def display_table_data(file_path):
    """
    Reads a processed JSON file and prints the content of any Table elements.
    """
    print(f"--- Inspecting file: {file_path} ---\n")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found at '{file_path}'")
        print("Please make sure FILENAME_TO_INSPECT is correct.")
        return

    table_found = False
    for element in data:
        if element.get("type") == "Table":
            table_found = True
            print("--- Found a Table Element ---")
            
            # The 'text' field contains HTML for the table
            html_content = element.get("text", "")
            
            # Use BeautifulSoup to parse the HTML and extract clean text
            soup = BeautifulSoup(html_content, 'html.parser')
            print(soup.get_text(separator="\n", strip=True))
            print("\n" + "="*30 + "\n")

    if not table_found:
        print("--- No 'Table' elements were found in this file. ---")

if __name__ == "__main__":
    display_table_data(file_path)