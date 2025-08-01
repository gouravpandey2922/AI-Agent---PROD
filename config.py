import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("RENDER_DB_URL")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Pinecone Index Names - Optimized for 5-index limit
PINECONE_INDEXES = {
    "web_scraper": "audit-intelligence-web",
    "internal_audit": "audit-intelligence-audit", 
    "external_conference": "audit-intelligence-conference",
    "quality_systems": "audit-intelligence-quality",
    "sop": "audit-intelligence-sop"
}

# Namespace mapping for better organization
PINECONE_NAMESPACES = {
    "web_scraper": "web-scraper",
    "internal_audit": "internal-audit", 
    "external_conference": "external-conference",
    "quality_systems": "quality-systems",
    "sop": "sop"
}

# Agent Configuration
AGENT_CONFIGS = {
    "orchestrator": {
        "model": "gpt-4o-mini",
        "temperature": 0.1,
        "max_tokens": 2000
    },
    "smart_orchestrator": {
        "model": "gpt-4o-mini",
        "temperature": 0.2,
        "max_tokens": 3000
    },
    "web_scraper": {
        "model": "gpt-4o-mini", 
        "temperature": 0.1,
        "max_tokens": 1500
    },
    "internal_audit": {
        "model": "gpt-4o-mini",
        "temperature": 0.1, 
        "max_tokens": 2000
    },
    "external_conference": {
        "model": "gpt-4o-mini",
        "temperature": 0.1,
        "max_tokens": 1500
    },
    "quality_systems": {
        "model": "gpt-4o-mini",
        "temperature": 0.1,
        "max_tokens": 1500
    },
    "sop": {
        "model": "gpt-4o-mini",
        "temperature": 0.1,
        "max_tokens": 1500
    }
}

# Knowledge Base Paths
KNOWLEDGE_BASE_PATHS = {
    "web_scraper": "Knowledge Bases/Web Scraper Agent",
    "internal_audit": "Knowledge Bases/Internal Audit Agent",
    "external_conference": "Knowledge Bases/External Engagement Conferences DATA", 
    "quality_systems": "Knowledge Bases/Company Quality System Agent",
    "sop": "Knowledge Bases/Audit SOP Agent"
}

# Output Types
OUTPUT_TYPES = {
    "report": "Generate a comprehensive report",
    "checklist": "Create a checklist or questionnaire", 
    "insights": "Provide insights and analysis",
    "general": "Answer general questions"
} 