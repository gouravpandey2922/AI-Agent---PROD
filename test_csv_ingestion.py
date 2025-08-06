#!/usr/bin/env python3
"""
Test script to verify CSV ingestion is working correctly
"""

import os
import sys
import pandas as pd

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_processor import DataProcessor

def test_csv_ingestion():
    """Test CSV ingestion to ensure all rows are being processed"""
    print("Testing CSV Ingestion")
    print("=" * 50)
    
    # Initialize data processor
    processor = DataProcessor()
    
    # Test with the quality systems CSV file
    csv_path = "Knowledge Bases/Company Quality System Agent/Final_Updated_Deviation_Sheet_-_11_Records.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return
    
    print(f"📁 Testing file: {csv_path}")
    
    # Read the CSV with pandas to get actual row count
    df = pd.read_csv(csv_path)
    actual_rows = len(df)
    print(f"📊 Actual rows in CSV: {actual_rows}")
    
    # Extract content using our processor
    extracted_content = processor._extract_csv_content(csv_path)
    
    # Count the number of data rows in the extracted content
    # Look for the "Complete Data:" section and count lines
    if "Complete Data:" in extracted_content:
        data_section = extracted_content.split("Complete Data:")[1].split("Total Records:")[0]
        data_lines = [line.strip() for line in data_section.split('\n') if line.strip()]
        
        # Count actual data rows (excluding header and empty lines)
        data_rows = len(data_lines) - 1  # Subtract 1 for header
        
        print(f"📈 Rows extracted by processor: {data_rows}")
        print(f"✅ Match: {'Yes' if data_rows == actual_rows else 'No'}")
        
        if data_rows != actual_rows:
            print(f"❌ MISMATCH: Expected {actual_rows} rows, got {data_rows} rows")
        else:
            print(f"✅ SUCCESS: All {actual_rows} rows were ingested correctly!")
            
        # Show sample of extracted content
        print(f"\n📋 Sample of extracted content:")
        print("-" * 30)
        print(extracted_content[:500] + "..." if len(extracted_content) > 500 else extracted_content)
        
    else:
        print("❌ Could not find 'Complete Data:' section in extracted content")
        print("📋 Extracted content:")
        print(extracted_content)

def test_multiple_csv_files():
    """Test multiple CSV files in the knowledge bases"""
    print("\nTesting Multiple CSV Files")
    print("=" * 50)
    
    processor = DataProcessor()
    
    # Find all CSV files in knowledge bases
    knowledge_base_paths = [
        "Knowledge Bases/Company Quality System Agent",
        "Knowledge Bases/Audit SOP Agent"
    ]
    
    for base_path in knowledge_base_paths:
        if os.path.exists(base_path):
            print(f"\n📁 Checking: {base_path}")
            
            for file in os.listdir(base_path):
                if file.endswith('.csv'):
                    csv_path = os.path.join(base_path, file)
                    print(f"  📄 {file}")
                    
                    # Get actual row count
                    df = pd.read_csv(csv_path)
                    actual_rows = len(df)
                    print(f"    📊 Actual rows: {actual_rows}")
                    
                    # Extract content
                    extracted_content = processor._extract_csv_content(csv_path)
                    
                    # Count extracted rows
                    if "Complete Data:" in extracted_content:
                        data_section = extracted_content.split("Complete Data:")[1].split("Total Records:")[0]
                        data_lines = [line.strip() for line in data_section.split('\n') if line.strip()]
                        data_rows = len(data_lines) - 1
                        
                        print(f"    📈 Extracted rows: {data_rows}")
                        print(f"    ✅ Match: {'Yes' if data_rows == actual_rows else 'No'}")
                        
                        if data_rows != actual_rows:
                            print(f"    ❌ MISMATCH: Expected {actual_rows}, got {data_rows}")
                    else:
                        print(f"    ❌ Could not parse extracted content")

if __name__ == "__main__":
    test_csv_ingestion()
    test_multiple_csv_files() 