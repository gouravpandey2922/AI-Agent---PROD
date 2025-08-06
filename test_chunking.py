#!/usr/bin/env python3
"""
Test script to verify chunking functionality for large documents
"""

import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_processor import DataProcessor

def test_chunking():
    """Test the chunking functionality"""
    print("Testing Document Chunking Functionality")
    print("=" * 50)
    
    processor = DataProcessor()
    
    # Test with a large text sample
    large_text = """
    This is a test document with many sentences. 
    We want to see if the chunking works properly. 
    Each sentence should be properly separated. 
    The chunking should respect sentence boundaries. 
    This helps maintain context within each chunk. 
    Large documents will be split into manageable pieces. 
    Each chunk should stay within token limits. 
    This prevents OpenAI API errors. 
    The chunking algorithm uses sentence boundaries. 
    This ensures logical breaks in the content. 
    """ * 100  # Repeat to make it large
    
    print(f"Original text length: {len(large_text)} characters")
    
    # Test chunking
    chunks = processor._chunk_content(large_text, max_tokens=1000)
    
    print(f"Number of chunks created: {len(chunks)}")
    
    for i, chunk in enumerate(chunks, 1):
        print(f"Chunk {i}: {len(chunk)} characters")
        print(f"  Preview: {chunk[:100]}...")
        print()
    
    # Test with a smaller text
    small_text = "This is a small document that should not be chunked."
    small_chunks = processor._chunk_content(small_text, max_tokens=1000)
    
    print(f"Small text chunks: {len(small_chunks)} (should be 1)")
    print(f"Small text chunked: {'Yes' if len(small_chunks) > 1 else 'No'}")

def test_file_processing():
    """Test file processing with chunking"""
    print("\nTesting File Processing with Chunking")
    print("=" * 50)
    
    processor = DataProcessor()
    
    # Test with a CSV file
    csv_path = "Knowledge Bases/Company Quality System Agent/Final_Updated_Deviation_Sheet_-_11_Records.csv"
    
    if os.path.exists(csv_path):
        print(f"Testing CSV file: {csv_path}")
        
        # Extract content
        content = processor._extract_csv_content(csv_path)
        print(f"CSV content length: {len(content)} characters")
        
        # Test chunking
        chunks = processor._chunk_content(content, max_tokens=2000)
        print(f"CSV chunks created: {len(chunks)}")
        
        for i, chunk in enumerate(chunks, 1):
            print(f"  Chunk {i}: {len(chunk)} characters")
    else:
        print(f"CSV file not found: {csv_path}")

if __name__ == "__main__":
    test_chunking()
    test_file_processing() 