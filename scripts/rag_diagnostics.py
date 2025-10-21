"""
RAG Diagnostics Script

This script helps diagnose issues with the RAG system by:
1. Listing all indexed documents in Qdrant
2. Searching for specific files
3. Testing different query formats
4. Displaying detailed metadata about the indexed chunks
"""

import os
import sys
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
import argparse

# Setup
collection_name = "document_chunks"
client = QdrantClient("localhost", port=6333)
embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

def check_collection_exists():
    """Check if the collection exists and print stats"""
    try:
        collection_info = client.get_collection(collection_name)
        print(f"✅ Collection '{collection_name}' exists with {collection_info.points_count} points")
        return True
    except Exception as e:
        print(f"❌ Error: Collection '{collection_name}' not found: {e}")
        return False

def list_all_source_files():
    """List all unique source files in the database"""
    try:
        # Use scroll to get all records
        results = client.scroll(
            collection_name=collection_name,
            scroll_filter=None,
            limit=100,
            with_payload=["source_file", "doc_id"],
        )
        
        # Extract unique source files
        source_files = set()
        for point in results[0]:
            if "source_file" in point.payload:
                source_files.add(point.payload["source_file"])
            elif "doc_id" in point.payload:
                source_files.add(point.payload["doc_id"])
                
        print(f"\n📁 Found {len(source_files)} unique source files:")
        for i, file in enumerate(sorted(source_files), 1):
            print(f"  {i}. {file}")
            
        return source_files
    
    except Exception as e:
        print(f"❌ Error listing source files: {e}")
        return set()

def check_specific_file(filename):
    """Check if a specific file exists in the database and show details"""
    print(f"\n🔍 Checking for records with source file: '{filename}'")
    
    # Try different ways of finding the file
    for field in ["source_file", "doc_id"]:
        for match_type in ["exact", "text"]:
            if match_type == "exact":
                filter_condition = models.FieldCondition(
                    key=field,
                    match=models.MatchValue(value=filename)
                )
            else:
                filter_condition = models.FieldCondition(
                    key=field,
                    match=models.MatchText(text=filename)
                )
            
            count_filter = models.Filter(
                must=[filter_condition]
            )
            
            try:
                count_response = client.count(
                    collection_name=collection_name,
                    count_filter=count_filter
                )
                
                if count_response.count > 0:
                    print(f"✅ Found {count_response.count} records using {field} with {match_type} match")
                    
                    # Get sample records
                    scroll_response = client.scroll(
                        collection_name=collection_name,
                        scroll_filter=count_filter,
                        limit=3,
                        with_payload=True
                    )
                    
                    print("\n📄 Sample records:")
                    for i, point in enumerate(scroll_response[0], 1):
                        print(f"  Record {i}:")
                        print(f"    ID: {point.id}")
                        print(f"    Type: {point.payload.get('type', 'unknown')}")
                        print(f"    Section: {point.payload.get('section', 'unknown')}")
                        text_preview = point.payload.get('text', '')[:100] + "..." if len(point.payload.get('text', '')) > 100 else point.payload.get('text', '')
                        print(f"    Text preview: {text_preview}")
                        print(f"    Source file: {point.payload.get('source_file', 'unknown')}")
                        print(f"    Doc ID: {point.payload.get('doc_id', 'unknown')}")
                        print()
                    
                    return True
            except Exception as e:
                print(f"❌ Error during search with {field} ({match_type}): {e}")
    
    print("❌ No records found for this file using any search method")
    return False

def test_semantic_search(query, source_file=None):
    """Test semantic search with the given query and optional source file filter"""
    print(f"\n🔎 Testing semantic search for: '{query}'")
    
    query_vector = embedding_model.encode(query).tolist()
    
    # Build filter if source file is provided
    query_filter = None
    if source_file:
        query_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="source_file",
                    match=models.MatchValue(value=source_file)
                )
            ]
        )
    
    try:
        search_results = client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=5
        )
        
        if search_results:
            print(f"✅ Found {len(search_results)} results for semantic search")
            
            print("\n📄 Results:")
            for i, result in enumerate(search_results, 1):
                print(f"  Result {i} (score: {result.score:.4f}):")
                print(f"    Source: {result.payload.get('source_file', 'unknown')}")
                print(f"    Type: {result.payload.get('type', 'unknown')}")
                print(f"    Section: {result.payload.get('section', 'unknown')}")
                text_preview = result.payload.get('text', '')[:100] + "..." if len(result.payload.get('text', '')) > 100 else result.payload.get('text', '')
                print(f"    Text preview: {text_preview}")
                print()
        else:
            print("❌ No results found for semantic search")
    
    except Exception as e:
        print(f"❌ Error during semantic search: {e}")

def main():
    parser = argparse.ArgumentParser(description="Diagnose RAG system issues")
    parser.add_argument("--file", help="Check for specific file in the database")
    parser.add_argument("--query", help="Test semantic search with a query")
    parser.add_argument("--list", action="store_true", help="List all source files")
    parser.add_argument("--all", action="store_true", help="Run all diagnostics")
    
    args = parser.parse_args()
    
    # Check if collection exists
    if not check_collection_exists():
        return
    
    if args.list or args.all:
        list_all_source_files()
    
    if args.file or args.all:
        file_to_check = args.file if args.file else input("\nEnter filename to check: ")
        check_specific_file(file_to_check)
    
    if args.query or args.all:
        query = args.query if args.query else input("\nEnter search query: ")
        test_semantic_search(query)
        
        if args.file:
            print("\nTesting semantic search with file filter...")
            test_semantic_search(query, args.file)
    
    # If no arguments provided, provide usage info
    if not (args.list or args.file or args.query or args.all):
        parser.print_help()
        print("\nExamples:")
        print("  python rag_diagnostics.py --list")
        print("  python rag_diagnostics.py --file 20251020-182510_Kholer.json")
        print("  python rag_diagnostics.py --query \"bathtub specifications\"")
        print("  python rag_diagnostics.py --all")
        print("  python rag_diagnostics.py --query \"bathtub specifications\" --file 20251020-182510_Kholer.json")

if __name__ == "__main__":
    main()