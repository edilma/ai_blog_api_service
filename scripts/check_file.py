"""
Simple Check Script for Qdrant

This script checks if a specific file is indexed in your Qdrant database.
"""

from qdrant_client import QdrantClient
import sys

# Connect to your running Qdrant instance
client = QdrantClient("localhost", port=6333)
collection_name = "document_chunks"

# Get the collection info
try:
    collection_info = client.get_collection(collection_name)
    print(f"Collection '{collection_name}' exists with {collection_info.points_count} points")
except Exception as e:
    print(f"Error getting collection: {e}")
    sys.exit(1)

# Check if there are any points with metadata for a specific source file
source_file = "20251020-182510_Kholer bathtub UNI-PS18310_Spec.json"

# First try exact match on source_file field
try:
    count = client.count(
        collection_name=collection_name,
        count_filter={
            "must": [
                {
                    "key": "source_file",
                    "match": {"value": source_file}
                }
            ]
        }
    ).count
    print(f"Found {count} records with exact match on source_file: {source_file}")
except Exception as e:
    print(f"Error searching with exact match: {e}")

# Try text match on source_file field (more flexible)
try:
    count = client.count(
        collection_name=collection_name,
        count_filter={
            "must": [
                {
                    "key": "text",
                    "match": {"text": "Kholer bathtub"}
                }
            ]
        }
    ).count
    print(f"Found {count} records with text match for 'Kholer bathtub'")
except Exception as e:
    print(f"Error searching with text match: {e}")

# List some files that ARE in the database
try:
    # Get a sample of records
    results = client.scroll(
        collection_name=collection_name,
        with_payload=["source_file"],
        limit=10
    )
    
    source_files = set()
    for point in results[0]:
        if "source_file" in point.payload:
            source_files.add(point.payload["source_file"])
    
    print("\nSource files found in database:")
    for file in source_files:
        print(f"  - {file}")
except Exception as e:
    print(f"Error listing files: {e}")