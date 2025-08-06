#!/usr/bin/env python3
"""
Script to load remaining agents (Quality Systems and SOP) into the vector database
"""

import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_processor import DataProcessor
from database.vector_db import VectorDatabaseManager
from config import KNOWLEDGE_BASE_PATHS

def load_remaining_agents():
    """Load Quality Systems and SOP agents"""
    print("Loading Remaining Agents (Quality Systems and SOP)")
    print("=" * 50)
    
    # Initialize components
    data_processor = DataProcessor()
    vector_db = VectorDatabaseManager()
    
    # Only process Quality Systems and SOP
    agents_to_process = ["quality_systems", "sop"]
    
    for agent_name in agents_to_process:
        base_path = KNOWLEDGE_BASE_PATHS[agent_name]
        print(f"\n📁 Processing {agent_name} knowledge base...")
        print(f"   Path: {base_path}")
        
        if not os.path.exists(base_path):
            print(f"   ❌ Path does not exist: {base_path}")
            continue
        
        # Process the knowledge base
        try:
            doc_count = data_processor._process_agent_knowledge_base(agent_name, base_path, vector_db)
            print(f"   ✅ Loaded {doc_count} documents")
        except Exception as e:
            print(f"   ❌ Error processing {agent_name}: {str(e)}")
    
    print("\n🎉 Remaining agents loading complete!")

if __name__ == "__main__":
    load_remaining_agents() 