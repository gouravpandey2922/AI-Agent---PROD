from neo4j import GraphDatabase
from typing import Dict, List, Optional
import logging
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

class GraphDatabaseManager:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
    def close(self):
        self.driver.close()
        
    def create_constraints(self):
        """Create unique constraints for better performance"""
        with self.driver.session() as session:
            # Company constraints
            session.run("CREATE CONSTRAINT company_name IF NOT EXISTS FOR (c:Company) REQUIRE c.name IS UNIQUE")
            # Document constraints  
            session.run("CREATE CONSTRAINT document_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE")
            # Event constraints
            session.run("CREATE CONSTRAINT event_id IF NOT EXISTS FOR (e:Event) REQUIRE e.id IS UNIQUE")
            
    def create_company_node(self, company_name: str, metadata: Dict = None):
        """Create or merge a company node"""
        with self.driver.session() as session:
            query = """
            MERGE (c:Company {name: $name})
            SET c += $metadata
            RETURN c
            """
            session.run(query, name=company_name, metadata=metadata or {})
            
    def create_document_node(self, doc_id: str, doc_type: str, title: str, 
                           file_path: str, metadata: Dict = None):
        """Create a document node"""
        with self.driver.session() as session:
            query = """
            MERGE (d:Document {id: $id})
            SET d.type = $type, d.title = $title, d.file_path = $file_path
            SET d += $metadata
            RETURN d
            """
            session.run(query, id=doc_id, type=doc_type, title=title, 
                       file_path=file_path, metadata=metadata or {})
            
    def create_event_node(self, event_id: str, event_type: str, title: str, 
                         date: str, metadata: Dict = None):
        """Create an event node (SNC, Conference, etc.)"""
        with self.driver.session() as session:
            query = """
            MERGE (e:Event {id: $id})
            SET e.type = $type, e.title = $title, e.date = $date
            SET e += $metadata
            RETURN e
            """
            session.run(query, id=event_id, type=event_type, title=title,
                       date=date, metadata=metadata or {})
            
    def link_company_to_document(self, company_name: str, doc_id: str, relationship_type: str = "MENTIONED_IN"):
        """Link a company to a document"""
        with self.driver.session() as session:
            query = """
            MATCH (c:Company {name: $company_name})
            MATCH (d:Document {id: $doc_id})
            MERGE (c)-[r:$relationship_type]->(d)
            RETURN r
            """
            session.run(query, company_name=company_name, doc_id=doc_id, 
                       relationship_type=relationship_type)
            
    def link_company_to_event(self, company_name: str, event_id: str, relationship_type: str = "INVOLVED_IN"):
        """Link a company to an event"""
        with self.driver.session() as session:
            query = """
            MATCH (c:Company {name: $company_name})
            MATCH (e:Event {id: $event_id})
            MERGE (c)-[r:$relationship_type]->(e)
            RETURN r
            """
            session.run(query, company_name=company_name, event_id=event_id,
                       relationship_type=relationship_type)
            
    def link_document_to_event(self, doc_id: str, event_id: str, relationship_type: str = "DOCUMENTS"):
        """Link a document to an event"""
        with self.driver.session() as session:
            query = """
            MATCH (d:Document {id: $doc_id})
            MATCH (e:Event {id: $event_id})
            MERGE (d)-[r:$relationship_type]->(e)
            RETURN r
            """
            session.run(query, doc_id=doc_id, event_id=event_id,
                       relationship_type=relationship_type)
            
    def get_company_relationships(self, company_name: str) -> Dict:
        """Get all relationships for a company"""
        with self.driver.session() as session:
            query = """
            MATCH (c:Company {name: $company_name})-[r]-(related)
            RETURN type(r) as relationship_type, labels(related) as node_type, 
                   related.name as name, related.title as title, related.date as date
            """
            result = session.run(query, company_name=company_name)
            relationships = {
                "documents": [],
                "events": [],
                "quality_events": [],
                "conferences": []
            }
            
            for record in result:
                rel_type = record["relationship_type"]
                node_type = record["node_type"][0] if record["node_type"] else "Unknown"
                name = record["name"] or record["title"]
                date = record["date"]
                
                if node_type == "Document":
                    relationships["documents"].append({
                        "name": name,
                        "date": date,
                        "relationship": rel_type
                    })
                elif node_type == "Event":
                    if "conference" in rel_type.lower():
                        relationships["conferences"].append({
                            "name": name,
                            "date": date,
                            "relationship": rel_type
                        })
                    else:
                        relationships["events"].append({
                            "name": name,
                            "date": date,
                            "relationship": rel_type
                        })
                        
            return relationships
            
    def get_temporal_analysis(self, company_name: str, start_date: str = None, end_date: str = None) -> Dict:
        """Get temporal analysis of events for a company"""
        with self.driver.session() as session:
            date_filter = ""
            if start_date and end_date:
                date_filter = "WHERE e.date >= $start_date AND e.date <= $end_date"
            elif start_date:
                date_filter = "WHERE e.date >= $start_date"
            elif end_date:
                date_filter = "WHERE e.date <= $end_date"
                
            query = f"""
            MATCH (c:Company {{name: $company_name}})-[r]-(e:Event)
            {date_filter}
            RETURN e.type as event_type, e.title as title, e.date as date, 
                   e.metadata as metadata, type(r) as relationship
            ORDER BY e.date
            """
            
            params = {"company_name": company_name}
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
                
            result = session.run(query, **params)
            
            events = []
            for record in result:
                events.append({
                    "type": record["event_type"],
                    "title": record["title"],
                    "date": record["date"],
                    "metadata": record["metadata"],
                    "relationship": record["relationship"]
                })
                
            return {"company": company_name, "events": events}
            
    def get_cross_agent_insights(self, company_name: str) -> Dict:
        """Get insights across all agents for a company"""
        with self.driver.session() as session:
            query = """
            MATCH (c:Company {name: $company_name})-[r]-(related)
            WITH c, collect({node: related, rel: type(r)}) as connections
            MATCH (c)-[r1]-(d:Document)
            MATCH (c)-[r2]-(e:Event)
            RETURN 
                count(d) as document_count,
                count(e) as event_count,
                collect(distinct d.type) as document_types,
                collect(distinct e.type) as event_types,
                collect(distinct type(r1)) as document_relationships,
                collect(distinct type(r2)) as event_relationships
            """
            
            result = session.run(query, company_name=company_name)
            record = result.single()
            
            return {
                "company": company_name,
                "document_count": record["document_count"],
                "event_count": record["event_count"],
                "document_types": list(set(record["document_types"])),
                "event_types": list(set(record["event_types"])),
                "document_relationships": list(set(record["document_relationships"])),
                "event_relationships": list(set(record["event_relationships"]))
            } 