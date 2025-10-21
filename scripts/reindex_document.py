"""
RAG Reindexing Script

This script helps reindex specific documents in your RAG system.
It can:
1. Remove all documents with a specific source_file
2. Reindex a document with new metadata structure
"""

import os
import sys
import asyncio
from qdrant_client import QdrantClient, models
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.indexing import process_and_embed_document

# Setup
collection_name = "document_chunks"
client = QdrantClient("localhost", port=6333)

def remove_document(source_file):
    """Remove all records for a specific source file"""
    print(f"🗑️ Removing all records for source file: '{source_file}'")
    
    try:
        # Try with source_file field
        points_ids = client.scroll(
            collection_name=collection_name,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="source_file",
                        match=models.MatchValue(value=source_file)
                    )
                ]
            ),
            with_payload=False,
            with_vectors=False,
        )[0]
        
        # Also try with doc_id field
        points_ids_doc_id = client.scroll(
            collection_name=collection_name,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="doc_id",
                        match=models.MatchValue(value=source_file)
                    )
                ]
            ),
            with_payload=False,
            with_vectors=False,
        )[0]
        
        # Combine both result sets
        all_points = points_ids + points_ids_doc_id
        
        if all_points:
            # Extract IDs
            ids_to_delete = [point.id for point in all_points]
            
            # Delete points
            client.delete(
                collection_name=collection_name,
                points_selector=models.PointIdsList(
                    points=ids_to_delete
                )
            )
            print(f"✅ Successfully removed {len(ids_to_delete)} records")
        else:
            print("ℹ️ No records found for this source file")
    
    except Exception as e:
        print(f"❌ Error removing records: {e}")

async def reindex_document(source_file, smart_indexing=True):
    """Reindex a document with the latest code"""
    print(f"🔄 Reindexing document: '{source_file}' with smart_indexing={smart_indexing}")
    
    try:
        # First remove existing records
        remove_document(source_file)
        
        # Then reindex
        await process_and_embed_document(source_file, smart_indexing=smart_indexing)
        print(f"✅ Document successfully reindexed: {source_file}")
    
    except Exception as e:
        print(f"❌ Error reindexing document: {e}")

async def main():
    parser = argparse.ArgumentParser(description="Reindex documents in RAG system")
    parser.add_argument("--file", required=True, help="Source file to reindex")
    parser.add_argument("--remove-only", action="store_true", help="Only remove the document without reindexing")
    parser.add_argument("--no-smart", action="store_true", help="Disable smart indexing for tables")
    
    args = parser.parse_args()
    
    if args.remove_only:
        remove_document(args.file)
    else:
        await reindex_document(args.file, smart_indexing=not args.no_smart)

if __name__ == "__main__":
    asyncio.run(main())