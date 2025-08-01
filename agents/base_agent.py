from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import os
from openai import OpenAI
from database.vector_db import VectorDatabaseManager
from database.graph_db import GraphDatabaseManager
from config import AGENT_CONFIGS, OPENAI_API_KEY

class BaseAgent(ABC):
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.config = AGENT_CONFIGS.get(agent_name, AGENT_CONFIGS["orchestrator"])
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        self.vector_db = VectorDatabaseManager()
        self.graph_db = GraphDatabaseManager()
        
    @property
    def model(self) -> str:
        """Get the model name for this agent"""
        return self.config["model"]
        
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent"""
        pass
        
    @abstractmethod
    def process_query(self, query: str, context: str = "") -> Dict[str, Any]:
        """Process a query and return results"""
        pass
        
    def search_knowledge_base(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search this agent's knowledge base"""
        return self.vector_db.search_documents(self.agent_name, query, top_k)
        
    def generate_response(self, query: str, context: str = "", 
                         response_type: str = "general") -> str:
        """Generate a response using OpenAI"""
        system_prompt = self.get_system_prompt()
        
        # Add response type specific instructions
        if response_type == "report":
            system_prompt += "\n\nGenerate a comprehensive audit report with clear sections, findings, and recommendations."
        elif response_type == "checklist":
            system_prompt += "\n\nGenerate a structured checklist or questionnaire with clear items and categories."
        elif response_type == "insights":
            system_prompt += "\n\nProvide detailed insights and analysis with supporting evidence from the context."
            
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuery: {query}"}
        ]
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.config["temperature"],
            max_tokens=self.config["max_tokens"]
        )
        
        return response.choices[0].message.content
        
    def process_query_with_sources(self, query: str, context: str = "", 
                                 response_type: str = "general") -> Dict[str, Any]:
        """Process a query and return results with detailed source information and document citations"""
        
        # Search knowledge base
        search_results = self.search_knowledge_base(query, top_k=8)
        
        # Extract context from search results
        context_parts = []
        sources = []
        document_citations = []
        
        for i, result in enumerate(search_results, 1):
            metadata = result.get('metadata', {})
            
            # Add to context
            if 'content' in metadata:
                context_parts.append(f"[Document {i}]: {metadata['content']}")
            
            # Create detailed source entry with enhanced metadata
            source = {
                'title': metadata.get('title', 'Unknown Document'),
                'score': result.get('score', 0),
                'agent': self.agent_name,
                'content': metadata.get('content', '')[:500] + '...' if metadata.get('content') else '',
                'document_id': f"DOC_{i:03d}",
                'metadata': {
                    'file_path': metadata.get('file_path', ''),
                    'file_name': self._extract_filename(metadata.get('file_path', '')),
                    'file_extension': self._get_file_extension(metadata.get('file_path', '')),
                    'source_type': metadata.get('source_type', ''),
                    'date': metadata.get('date', ''),
                    'company': metadata.get('company', ''),
                    'category': metadata.get('category', ''),
                    'page_number': metadata.get('page_number', ''),
                    'section': metadata.get('section', ''),
                    'relevance_score': result.get('score', 0)
                }
            }
            sources.append(source)
            
            # Create citation entry
            citation = {
                'document_id': f"DOC_{i:03d}",
                'title': metadata.get('title', 'Unknown Document'),
                'file_name': self._extract_filename(metadata.get('file_path', '')),
                'file_extension': self._get_file_extension(metadata.get('file_path', '')),
                'relevance_score': result.get('score', 0),
                'agent': self.agent_name
            }
            document_citations.append(citation)
        
        # Combine context with document references
        combined_context = "\n\n".join(context_parts) if context_parts else context
        
        # Generate response with citation instructions
        citation_instructions = self._generate_citation_instructions(document_citations)
        enhanced_context = f"{combined_context}\n\n{citation_instructions}"
        
        response_text = self.generate_response(query, enhanced_context, response_type)
        
        return {
            'response': response_text,
            'sources': sources,
            'document_citations': document_citations,
            'context': combined_context,
            'agent': self.agent_name,
            'total_documents': len(sources)
        }
    
    def _extract_filename(self, file_path: str) -> str:
        """Extract filename from file path"""
        if not file_path:
            return "Unknown"
        return os.path.basename(file_path)
    
    def _get_file_extension(self, file_path: str) -> str:
        """Get file extension from file path"""
        if not file_path:
            return "Unknown"
        return os.path.splitext(file_path)[1].lower()
    
    def _generate_citation_instructions(self, citations: List[Dict]) -> str:
        """Generate citation instructions for the AI model"""
        if not citations:
            return ""
        
        citation_text = "\n\nDOCUMENT CITATIONS:\n"
        for citation in citations:
            citation_text += f"- {citation['document_id']}: {citation['title']} ({citation['file_name']})\n"
        
        citation_text += "\nINSTRUCTIONS: When referencing information in your response, cite the specific document using the format [DOC_XXX] where XXX is the document ID. Always provide detailed, comprehensive responses with proper document citations."
        
        return citation_text
        
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities from text using OpenAI"""
        prompt = f"""
        Extract the following entities from the text:
        - Companies
        - Dates
        - Topics/Keywords
        - Locations
        
        Return as JSON format:
        {{
            "companies": ["company1", "company2"],
            "dates": ["date1", "date2"],
            "topics": ["topic1", "topic2"],
            "locations": ["location1", "location2"]
        }}
        
        Text: {text}
        """
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts entities from text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        try:
            import json
            return json.loads(response.choices[0].message.content)
        except:
            return {"companies": [], "dates": [], "topics": [], "locations": []}
            
    def create_graph_relationships(self, doc_id: str, metadata: Dict[str, Any]):
        """Create graph relationships for a document"""
        # Create document node
        self.graph_db.create_document_node(
            doc_id=doc_id,
            doc_type=self.agent_name,
            title=metadata.get('title', 'Unknown'),
            file_path=metadata.get('file_path', ''),
            metadata=metadata
        )
        
        # Extract entities and create relationships
        if 'content' in metadata:
            entities = self.extract_entities(metadata['content'])
            
            # Create company relationships
            for company in entities.get('companies', []):
                self.graph_db.create_company_relationship(
                    doc_id=doc_id,
                    company_name=company,
                    relationship_type="MENTIONED_IN"
                )
                
    def get_agent_capabilities(self) -> Dict[str, Any]:
        """Get detailed capabilities of this agent"""
        return {
            "agent_name": self.agent_name,
            "capabilities": self.get_capabilities(),
            "model": self.model,
            "temperature": self.config["temperature"],
            "max_tokens": self.config["max_tokens"]
        }
        
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return a list of capabilities for this agent"""
        pass 