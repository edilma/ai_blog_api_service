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
try:
    # Count how many records match the filter
    count_response = client.count(
        collection_name=collection_name,
        count_filter={
            "must": [
                {
                    "key": "source_file",
                    "match": {"value": source_file}
                }
            ]
        }
    )
    print(f"Found {count_response.count} records for source file: {source_file}")
    
    # Get some example records
    search_response = client.scroll(
        collection_name=collection_name,
        scroll_filter={
            "must": [
                {
                    "key": "source_file",
                    "match": {"value": source_file}
                }
            ]
        },
        limit=3,
        with_payload=True
    )
    
    if search_response[0]:  # Check if any results were returned
        print("\nExample records:")
        for point in search_response[0]:
            print(f"ID: {point.id}")
            print(f"Type: {point.payload.get('type', 'unknown')}")
            print(f"Section: {point.payload.get('section', 'unknown')}")
            print(f"Text length: {len(point.payload.get('text', ''))}")
            print("-" * 40)
    else:
        print("No records found for this source file")
except Exception as e:
    print(f"Error searching collection: {e}")