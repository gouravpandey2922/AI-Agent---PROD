from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from typing import Dict, List, Optional, Any
import uuid
import hashlib
from config import PINECONE_API_KEY, OPENAI_API_KEY, PINECONE_INDEXES, PINECONE_NAMESPACES

class VectorDatabaseManager:
    def __init__(self):
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        self.indexes = {}
        self._initialize_indexes()
        
    def _initialize_indexes(self):
        """Initialize all Pinecone indexes"""
        for agent_name, index_name in PINECONE_INDEXES.items():
            if not self.pc.has_index(index_name):
                self._create_index(index_name)
            self.indexes[agent_name] = self.pc.Index(index_name)
            
    def _create_index(self, index_name: str):
        """Create a new Pinecone index"""
        self.pc.create_index(
            name=index_name,
            vector_type="dense",
            dimension=1536,  # OpenAI text-embedding-3-small dimension
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            ),
            deletion_protection="disabled",
            tags={
                "environment": "development",
                "project": "audit-intelligence"
            }
        )
        
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI"""
        text = text.replace("\n", " ")
        response = self.openai_client.embeddings.create(
            input=[text], 
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
        
    def upsert_document(self, agent_name: str, text: str, metadata: Dict[str, Any]):
        """Upsert a document into the specified agent's index with namespace"""
        if agent_name not in self.indexes:
            raise ValueError(f"Unknown agent: {agent_name}")
            
        # Generate unique ID
        doc_id = str(uuid.uuid4())
        
        # Get embedding
        embedding = self.get_embedding(text)
        
        # Add text hash for deduplication
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        metadata['text_hash'] = text_hash
        metadata['agent'] = agent_name
        
        # Get namespace for this agent
        namespace = PINECONE_NAMESPACES.get(agent_name, agent_name)
        
        # Upsert to Pinecone with namespace
        self.indexes[agent_name].upsert(
            vectors=[{
                "id": doc_id,
                "values": embedding,
                "metadata": metadata
            }],
            namespace=namespace
        )
        
        return doc_id
        
    def search_documents(self, agent_name: str, query: str, top_k: int = 5, 
                        filter_dict: Dict = None) -> List[Dict]:
        """Search documents in a specific agent's index with namespace"""
        if agent_name not in self.indexes:
            raise ValueError(f"Unknown agent: {agent_name}")
            
        query_embedding = self.get_embedding(query)
        
        # Get namespace for this agent
        namespace = PINECONE_NAMESPACES.get(agent_name, agent_name)
        
        search_kwargs = {
            "vector": query_embedding,
            "top_k": top_k,
            "include_metadata": True,
            "namespace": namespace
        }
        
        if filter_dict:
            search_kwargs["filter"] = filter_dict
            
        results = self.indexes[agent_name].query(**search_kwargs)
        return results['matches']
        
    def search_across_all_agents(self, query: str, top_k_per_agent: int = 3) -> Dict[str, List[Dict]]:
        """Search across all agent indexes"""
        results = {}
        
        for agent_name in self.indexes.keys():
            agent_results = self.search_documents(agent_name, query, top_k_per_agent)
            if agent_results:
                results[agent_name] = agent_results
                
        return results
        
    def search_by_company(self, company_name: str, top_k_per_agent: int = 5) -> Dict[str, List[Dict]]:
        """Search for documents mentioning a specific company across all agents"""
        results = {}
        
        for agent_name in self.indexes.keys():
            # Search with company name filter
            agent_results = self.search_documents(
                agent_name, 
                company_name, 
                top_k_per_agent,
                filter_dict={"company": {"$in": [company_name]}}
            )
            
            if agent_results:
                results[agent_name] = agent_results
                
        return results
        
    def search_by_date_range(self, agent_name: str, start_date: str, end_date: str, 
                           query: str = "", top_k: int = 10) -> List[Dict]:
        """Search documents within a date range"""
        filter_dict = {
            "date": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        
        return self.search_documents(agent_name, query, top_k, filter_dict)
        
    def get_document_by_id(self, agent_name: str, doc_id: str) -> Optional[Dict]:
        """Get a specific document by ID with namespace"""
        if agent_name not in self.indexes:
            raise ValueError(f"Unknown agent: {agent_name}")
            
        namespace = PINECONE_NAMESPACES.get(agent_name, agent_name)
        results = self.indexes[agent_name].fetch(ids=[doc_id], namespace=namespace)
        if doc_id in results['vectors']:
            return results['vectors'][doc_id]
        return None
        
    def delete_document(self, agent_name: str, doc_id: str):
        """Delete a document from the index with namespace"""
        if agent_name not in self.indexes:
            raise ValueError(f"Unknown agent: {agent_name}")
            
        namespace = PINECONE_NAMESPACES.get(agent_name, agent_name)
        self.indexes[agent_name].delete(ids=[doc_id], namespace=namespace)
        
    def get_index_stats(self, agent_name: str) -> Dict:
        """Get statistics for an index"""
        if agent_name not in self.indexes:
            raise ValueError(f"Unknown agent: {agent_name}")
            
        return self.indexes[agent_name].describe_index_stats()
    
    def list_documents(self, agent_name: str, limit: int = 100) -> List[Dict]:
        """List all documents in an agent's index"""
        if agent_name not in self.indexes:
            raise ValueError(f"Unknown agent: {agent_name}")
            
        namespace = PINECONE_NAMESPACES.get(agent_name, agent_name)
        
        # Query with a dummy vector to get all documents
        dummy_vector = [0.0] * 1536  # OpenAI embedding dimension
        
        response = self.indexes[agent_name].query(
            vector=dummy_vector,
            top_k=limit,
            include_metadata=True,
            namespace=namespace
        )
        
        documents = []
        for match in response.matches:
            documents.append({
                "id": match.id,
                "score": match.score,
                "metadata": match.metadata
            })
        
        return documents
        
    def semantic_search_with_context(self, query: str, agent_names: List[str] = None, 
                                   top_k_per_agent: int = 3) -> str:
        """Perform semantic search and return formatted context"""
        if agent_names is None:
            agent_names = list(self.indexes.keys())
            
        all_results = {}
        for agent_name in agent_names:
            if agent_name in self.indexes:
                results = self.search_documents(agent_name, query, top_k_per_agent)
                if results:
                    all_results[agent_name] = results
                    
        # Format context
        context_parts = []
        for agent_name, results in all_results.items():
            context_parts.append(f"=== {agent_name.upper()} AGENT RESULTS ===")
            for i, result in enumerate(results, 1):
                metadata = result['metadata']
                score = result['score']
                
                # Format based on agent type
                if agent_name == "quality_systems":
                    context_parts.append(
                        f"{i}. SNC: {metadata.get('title', 'N/A')} | "
                        f"Company: {metadata.get('company', 'N/A')} | "
                        f"Category: {metadata.get('category', 'N/A')} | "
                        f"Score: {score:.3f}\n"
                        f"Description: {metadata.get('description', 'N/A')}\n"
                    )
                elif agent_name == "external_conference":
                    context_parts.append(
                        f"{i}. Conference: {metadata.get('title', 'N/A')} | "
                        f"Date: {metadata.get('date', 'N/A')} | "
                        f"Companies: {metadata.get('companies', 'N/A')} | "
                        f"Score: {score:.3f}\n"
                        f"Content: {metadata.get('content', 'N/A')[:200]}...\n"
                    )
                else:
                    context_parts.append(
                        f"{i}. Title: {metadata.get('title', 'N/A')} | "
                        f"Source: {metadata.get('source', 'N/A')} | "
                        f"Score: {score:.3f}\n"
                        f"Content: {metadata.get('content', 'N/A')[:200]}...\n"
                    )
                    
        return "\n".join(context_parts) 