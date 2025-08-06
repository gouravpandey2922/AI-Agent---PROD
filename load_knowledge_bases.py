#!/usr/bin/env python3
"""
Script to load all knowledge base documents into the vector database
"""

import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_processor import DataProcessor
from database.vector_db import VectorDatabaseManager
from config import KNOWLEDGE_BASE_PATHS

def load_all_knowledge_bases():
    """Load all knowledge base documents into the vector database"""
    print("Loading Knowledge Bases into Vector Database")
    print("=" * 50)
    
    # Initialize components
    data_processor = DataProcessor()
    vector_db = VectorDatabaseManager()
    
    total_documents = 0
    
    for agent_name, base_path in KNOWLEDGE_BASE_PATHS.items():
        print(f"\n📁 Processing {agent_name} knowledge base...")
        print(f"   Path: {base_path}")
        
        if not os.path.exists(base_path):
            print(f"   ❌ Path does not exist: {base_path}")
            continue
        
        # Process the knowledge base
        try:
            doc_count = data_processor._process_agent_knowledge_base(agent_name, base_path, vector_db)
            print(f"   ✅ Loaded {doc_count} documents")
            total_documents += doc_count
        except Exception as e:
            print(f"   ❌ Error processing {agent_name}: {str(e)}")
    
    print(f"\n🎉 Total documents loaded: {total_documents}")
    print("Knowledge base loading complete!")

def verify_documents_loaded():
    """Verify that documents are loaded in the vector database"""
    print("\nVerifying Documents in Vector Database")
    print("=" * 50)
    
    vector_db = VectorDatabaseManager()
    
    for agent_name in KNOWLEDGE_BASE_PATHS.keys():
        print(f"\n📊 {agent_name.replace('_', ' ').title()}:")
        try:
            documents = vector_db.list_documents(agent_name, limit=100)
            print(f"   Documents found: {len(documents)}")
            
            if documents:
                print("   Sample documents:")
                for i, doc in enumerate(documents[:3], 1):
                    title = doc.get('metadata', {}).get('title', 'Unknown')
                    print(f"     {i}. {title}")
            else:
                print("   No documents found")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

if __name__ == "__main__":
    load_all_knowledge_bases()
    verify_documents_loaded() 