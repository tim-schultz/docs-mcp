#!/usr/bin/env python3
"""
Simple script to query the vector database and check its contents.
Useful for debugging and testing the ingested data.
"""
from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

from config import VECTOR_STORE_DIR
from vectordb.vector_store import load_vector_store

# Load environment variables
load_dotenv()


def list_collections() -> list[str]:
    """List all available collections in the vector store."""
    if not VECTOR_STORE_DIR.exists():
        print("❌ Vector store directory not found. Run ingestion first.")
        return []
    
    collections = [d.name for d in VECTOR_STORE_DIR.iterdir() if d.is_dir()]
    return collections


def query_collection(collection: str, query: str, k: int = 5) -> None:
    """Query a specific collection and display results."""
    try:
        vectorstore = load_vector_store(collection)
        if vectorstore is None:
            print(f"❌ Collection '{collection}' not found.")
            return
        
        print(f"🔍 Querying collection '{collection}' with: '{query}'")
        print("-" * 60)
        
        results = vectorstore.similarity_search(query, k=k)
        
        if not results:
            print("No results found.")
            return
        
        for i, doc in enumerate(results, 1):
            print(f"\n📄 Result {i}:")
            print(f"Source: {doc.metadata.get('source_type', 'unknown')}")
            if doc.metadata.get('path'):
                print(f"Path: {doc.metadata['path']}")
            if doc.metadata.get('source'):
                print(f"URL: {doc.metadata['source']}")
            print(f"Content preview: {doc.page_content[:200]}...")
            if len(doc.page_content) > 200:
                print("(truncated)")
            
    except Exception as e:
        print(f"❌ Error querying collection: {e}")


def show_collection_stats(collection: str) -> None:
    """Show statistics about a collection."""
    try:
        vectorstore = load_vector_store(collection)
        if vectorstore is None:
            print(f"❌ Collection '{collection}' not found.")
            return
        
        # Get a sample of documents to analyze
        sample_docs = vectorstore.similarity_search("", k=100)
        
        print(f"📊 Collection '{collection}' Statistics:")
        print(f"Total documents (sample): {len(sample_docs)}")
        
        # Count by source type
        source_types = {}
        paths = set()
        
        for doc in sample_docs:
            source_type = doc.metadata.get('source_type', 'unknown')
            source_types[source_type] = source_types.get(source_type, 0) + 1
            
            if doc.metadata.get('path'):
                paths.add(doc.metadata['path'])
        
        print("Source types:")
        for source_type, count in source_types.items():
            print(f"  - {source_type}: {count} documents")
        
        if paths:
            print(f"Unique file paths: {len(paths)}")
            
    except Exception as e:
        print(f"❌ Error getting collection stats: {e}")


def main() -> None:
    """Main interactive query interface."""
    collections = list_collections()
    
    if not collections:
        print("No collections found. Run 'uv run python main.py ingest --repo <url>' first.")
        return
    
    print("📚 Available collections:")
    for i, collection in enumerate(collections, 1):
        print(f"  {i}. {collection}")
    
    # If only one collection, use it
    if len(collections) == 1:
        selected_collection = collections[0]
        print(f"\n🎯 Using collection: {selected_collection}")
    else:
        try:
            choice = input(f"\nSelect collection (1-{len(collections)}): ").strip()
            if not choice.isdigit() or not (1 <= int(choice) <= len(collections)):
                print("Invalid selection.")
                return
            selected_collection = collections[int(choice) - 1]
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            return
    
    # Show collection stats
    show_collection_stats(selected_collection)
    
    print(f"\n🔍 Query interface for collection '{selected_collection}'")
    print("Commands:")
    print("  - Type a query to search")
    print("  - 'stats' to show collection statistics")
    print("  - 'quit' or Ctrl+C to exit")
    
    while True:
        try:
            query = input("\n> ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            elif query.lower() == 'stats':
                show_collection_stats(selected_collection)
            elif query:
                query_collection(selected_collection, query)
            
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break


if __name__ == "__main__":
    main()