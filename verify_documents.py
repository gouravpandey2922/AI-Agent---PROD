#!/usr/bin/env python3
"""
Script to verify documents loaded in the vector database
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.vector_db import VectorDatabaseManager
from config import KNOWLEDGE_BASE_PATHS

def verify_documents_loaded():
    """Verify that documents are loaded in the vector database"""
    print("Verifying Documents in Vector Database")
    print("=" * 50)
    
    vector_db = VectorDatabaseManager()
    
    for agent_name in KNOWLEDGE_BASE_PATHS.keys():
        print(f"\n📊 {agent_name.replace('_', ' ').title()}:")
        try:
            documents = vector_db.list_documents(agent_name, limit=100)
            print(f"   Documents found: {len(documents)}")
            
            if documents:
                print("   Sample documents:")
                for i, doc in enumerate(documents[:5], 1):
                    title = doc.get('metadata', {}).get('title', 'Unknown')
                    file_type = doc.get('metadata', {}).get('file_type', 'Unknown')
                    print(f"     {i}. {title} ({file_type})")
            else:
                print("   No documents found")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

if __name__ == "__main__":
    verify_documents_loaded() 