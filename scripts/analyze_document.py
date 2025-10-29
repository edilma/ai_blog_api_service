"""
Document Analysis Script

This script analyzes a processed JSON file before indexing to help
identify potential issues with the content.
"""

import os
import json
import sys
import argparse
from collections import Counter

# Constants
PROCESSED_DATA_DIR = "data/processed"

def analyze_document(json_filename):
    """Analyze a processed JSON document and print statistics"""
    file_path = os.path.join(PROCESSED_DATA_DIR, json_filename)
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            elements = json.load(f)
    except FileNotFoundError:
        print(f"❌ ERROR: File not found at '{file_path}'")
        return
    except json.JSONDecodeError:
        print(f"❌ ERROR: Invalid JSON file at '{file_path}'")
        return
    
    print(f"\n📊 Analysis for: {json_filename}")
    print(f"📄 Total elements: {len(elements)}")
    
    # Count element types
    element_types = Counter([el.get("type", "unknown") for el in elements])
    
    print("\n📋 Element types:")
    for element_type, count in element_types.most_common():
        print(f"  - {element_type}: {count}")
    
    # Check for empty text
    empty_elements = [el for el in elements if not el.get("text", "").strip()]
    if empty_elements:
        print(f"\n⚠️ Warning -ojo: Found {len(empty_elements)} elements with empty text")
    
    # Analyze pages
    pages = Counter([el.get("metadata", {}).get("page_number", "unknown") for el in elements])
    
    print("\n📑 Page distribution:")
    for page, count in sorted(pages.items()):
        if page != "unknown":
            print(f"  - Page {page}: {count} elements")
    
    if "unknown" in pages:
        print(f"  - Unknown page: {pages['unknown']} elements")
    
    # Show sample of each type
    print("\n🔍 Sample of each element type:")
    for element_type in element_types.keys():
        samples = [el for el in elements if el.get("type") == element_type]
        if samples:
            sample = samples[0]
            text = sample.get("text", "")
            preview = (text[:100] + "...") if len(text) > 100 else text
            print(f"\n  {element_type} example:")
            print(f"  {preview}")
    
    # Check for potential issues
    print("\n🚨 Potential issues:")
    
    # Check if there are tables but no Table elements
    if "Table" not in element_types and any("<table" in el.get("text", "").lower() for el in elements):
        print("  - Document contains HTML tables but no Table elements were detected")
    
    # Check if there are titles but no Title elements
    if "Title" not in element_types:
        print("  - No Title elements detected - this might affect section organization")
    
    # Check for very large elements
    large_elements = [el for el in elements if len(el.get("text", "")) > 10000]
    if large_elements:
        print(f"  - Found {len(large_elements)} very large elements (>10K chars) which might affect embedding quality")
    
    # Check for duplicate content
    text_counts = Counter([el.get("text", "") for el in elements])
    duplicates = {text: count for text, count in text_counts.items() if count > 1 and text.strip()}
    if duplicates:
        print(f"  - Found {len(duplicates)} duplicate text elements")
    
    print("\n✅ Analysis complete")

def main():
    parser = argparse.ArgumentParser(description="Analyze processed JSON files")
    parser.add_argument("--file", help="Specific JSON file to analyze")
    parser.add_argument("--list", action="store_true", help="List all available JSON files")
    
    args = parser.parse_args()
    
    if args.list:
        try:
            files = [f for f in os.listdir(PROCESSED_DATA_DIR) if f.endswith('.json')]
            files.sort(key=lambda x: os.path.getmtime(os.path.join(PROCESSED_DATA_DIR, x)), reverse=True)
            
            print("\n📁 Available JSON files:")
            for i, file in enumerate(files, 1):
                file_size = os.path.getsize(os.path.join(PROCESSED_DATA_DIR, file)) / 1024
                print(f"  {i}. {file} ({file_size:.1f} KB)")
            
            return
        except FileNotFoundError:
            print(f"❌ ERROR: Directory '{PROCESSED_DATA_DIR}' not found")
            return
    
    if args.file:
        analyze_document(args.file)
    else:
        parser.print_help()
        print("\nExamples:")
        print("  python analyze_document.py --list")
        print("  python analyze_document.py --file 20251020-182510_Kholer.json")

if __name__ == "__main__":
    main()