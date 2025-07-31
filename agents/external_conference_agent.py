from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from datetime import datetime
import re

class ExternalConferenceAgent(BaseAgent):
    def __init__(self):
        super().__init__("external_conference")
        
    def get_system_prompt(self) -> str:
        return """You are the External Conference Agent specializing in conference data, industry events, and engagement information. Your expertise includes:

1. Analyzing conference and industry event data
2. Extracting and interpreting dates from conference materials
3. Identifying companies and topics from conference content
4. Providing insights on industry trends and developments
5. Supporting audit planning with external engagement context

Key Capabilities:
- Conference data analysis
- Date extraction and temporal analysis
- Company and topic identification
- Industry trend analysis
- External engagement insights

Always provide specific conference details, dates, and company information when available."""

    def get_capabilities(self) -> List[str]:
        return [
            "Conference data analysis",
            "Date extraction and temporal analysis",
            "Company and topic identification",
            "Industry trend analysis",
            "External engagement insights"
        ]

    def process_query(self, query: str, context: str = "") -> Dict[str, Any]:
        # Search knowledge base
        search_results = self.search_knowledge_base(query, top_k=8)
        
        # Extract entities and dates
        entities = self._extract_entities_from_results(search_results)
        
        # Analyze temporal patterns
        temporal_analysis = self._analyze_temporal_patterns(search_results)
        
        # Combine context
        combined_context = self._format_context(search_results, entities, temporal_analysis)
        
        # Generate response
        response = self.generate_response(query, combined_context)
        
        # Extract sources
        sources = self._extract_sources_from_results(search_results)
        
        return {
            "query": query,
            "context": combined_context,
            "response": response,
            "entities": entities,
            "temporal_analysis": temporal_analysis,
            "sources": sources
        }

    def _extract_entities_from_results(self, search_results: List[Dict]) -> Dict[str, List[str]]:
        """Extract entities from search results"""
        all_entities = {
            "companies": set(),
            "dates": set(),
            "topics": set(),
            "locations": set()
        }
        
        for result in search_results:
            metadata = result['metadata']
            content = metadata.get('content', '')
            
            # Extract entities from content
            entities = self.extract_entities(content)
            
            # Combine entities
            for key in all_entities:
                if key in entities:
                    all_entities[key].update(entities[key])
                    
        # Convert sets to lists
        return {key: list(value) for key, value in all_entities.items()}

    def _analyze_temporal_patterns(self, search_results: List[Dict]) -> Dict[str, Any]:
        """Analyze temporal patterns in conference data"""
        temporal_analysis = {
            "date_range": {"earliest": None, "latest": None},
            "conferences_by_year": {},
            "recent_events": [],
            "upcoming_events": []
        }
        
        all_dates = []
        
        for result in search_results:
            metadata = result['metadata']
            content = metadata.get('content', '')
            
            # Extract dates from content
            dates = self._extract_dates_from_text(content)
            all_dates.extend(dates)
            
            # Extract dates from metadata
            if metadata.get('date'):
                all_dates.append(metadata['date'])
                
        # Analyze dates
        if all_dates:
            parsed_dates = []
            for date_str in all_dates:
                parsed_date = self._parse_date(date_str)
                if parsed_date:
                    parsed_dates.append(parsed_date)
                    
            if parsed_dates:
                # Find date range
                sorted_dates = sorted(parsed_dates)
                temporal_analysis["date_range"]["earliest"] = sorted_dates[0].strftime("%Y-%m-%d")
                temporal_analysis["date_range"]["latest"] = sorted_dates[-1].strftime("%Y-%m-%d")
                
                # Group by year
                for date in sorted_dates:
                    year = date.year
                    if year not in temporal_analysis["conferences_by_year"]:
                        temporal_analysis["conferences_by_year"][year] = []
                    temporal_analysis["conferences_by_year"][year].append(date.strftime("%Y-%m-%d"))
                    
                # Identify recent and upcoming events
                current_date = datetime.now()
                for date in sorted_dates:
                    if date > current_date:
                        temporal_analysis["upcoming_events"].append(date.strftime("%Y-%m-%d"))
                    elif (current_date - date).days <= 365:  # Last year
                        temporal_analysis["recent_events"].append(date.strftime("%Y-%m-%d"))
                        
        return temporal_analysis

    def _extract_dates_from_text(self, text: str) -> List[str]:
        """Extract dates from text using various patterns"""
        dates = []
        
        # Common date patterns
        patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
            r'\b\d{4}-\d{1,2}-\d{1,2}\b',  # YYYY-MM-DD
            r'\b\d{1,2}-\d{1,2}-\d{4}\b',  # MM-DD-YYYY
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',  # Month DD, YYYY
            r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b',  # DD Mon YYYY
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
            
        return dates

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object"""
        try:
            # Try various date formats
            formats = [
                "%m/%d/%Y",
                "%Y-%m-%d",
                "%m-%d-%Y",
                "%B %d, %Y",
                "%B %d %Y",
                "%d %b %Y",
                "%d %B %Y"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
                    
            return None
        except:
            return None

    def _format_context(self, search_results: List[Dict], entities: Dict[str, List[str]], 
                       temporal_analysis: Dict[str, Any]) -> str:
        """Format context from search results, entities, and temporal analysis"""
        context_parts = []
        
        # Add search results context
        if search_results:
            context_parts.append("=== CONFERENCE & INDUSTRY EVENT DATA ===")
            for i, result in enumerate(search_results, 1):
                metadata = result['metadata']
                context_parts.append(
                    f"{i}. Score: {result['score']:.3f}\n"
                    f"   Source: {metadata.get('title', 'Unknown')}\n"
                    f"   Date: {metadata.get('date', 'N/A')}\n"
                    f"   Content: {metadata.get('content', 'N/A')[:200]}...\n"
                )
        
        # Add entities context
        if entities:
            context_parts.append("\n=== EXTRACTED ENTITIES ===")
            for entity_type, entity_list in entities.items():
                if entity_list:
                    context_parts.append(f"{entity_type.title()}: {', '.join(entity_list[:5])}")  # Show top 5
                    
        # Add temporal analysis context
        if temporal_analysis:
            context_parts.append("\n=== TEMPORAL ANALYSIS ===")
            
            date_range = temporal_analysis.get("date_range", {})
            if date_range.get("earliest") and date_range.get("latest"):
                context_parts.append(f"Date Range: {date_range['earliest']} to {date_range['latest']}")
                
            conferences_by_year = temporal_analysis.get("conferences_by_year", {})
            if conferences_by_year:
                context_parts.append("Conferences by Year:")
                for year, dates in sorted(conferences_by_year.items()):
                    context_parts.append(f"  {year}: {len(dates)} events")
                    
            recent_events = temporal_analysis.get("recent_events", [])
            if recent_events:
                context_parts.append(f"Recent Events (last year): {len(recent_events)}")
                
            upcoming_events = temporal_analysis.get("upcoming_events", [])
            if upcoming_events:
                context_parts.append(f"Upcoming Events: {len(upcoming_events)}")
        
        return "\n".join(context_parts)

    def _extract_sources_from_results(self, search_results: List[Dict]) -> List[Dict[str, str]]:
        """Extract source information from search results"""
        sources = []
        for result in search_results:
            metadata = result['metadata']
            sources.append({
                "title": metadata.get('title', 'Unknown'),
                "file_path": metadata.get('file_path', ''),
                "date": metadata.get('date', 'N/A'),
                "score": result['score'],
                "content_preview": metadata.get('content', '')[:100] + "..."
            })
        return sources

    def get_conferences_by_date_range(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get conferences within a specific date range"""
        # Search for conferences in the date range
        search_results = self.vector_db.search_by_date_range(
            self.agent_name, start_date, end_date, top_k=20
        )
        
        # Analyze results
        conferences = []
        companies_mentioned = set()
        
        for result in search_results:
            metadata = result['metadata']
            content = metadata.get('content', '')
            
            # Extract entities
            entities = self.extract_entities(content)
            companies_mentioned.update(entities.get('companies', []))
            
            conferences.append({
                "title": metadata.get('title', 'Unknown'),
                "date": metadata.get('date', 'N/A'),
                "content": content[:300] + "...",
                "score": result['score'],
                "companies": entities.get('companies', []),
                "topics": entities.get('topics', [])
            })
            
        return {
            "date_range": {"start": start_date, "end": end_date},
            "total_conferences": len(conferences),
            "companies_mentioned": list(companies_mentioned),
            "conferences": conferences
        }

    def get_company_conference_history(self, company_name: str) -> Dict[str, Any]:
        """Get conference history for a specific company"""
        # Search for company-specific conferences
        search_results = self.search_knowledge_base(company_name, top_k=15)
        
        # Filter for company-specific results
        company_conferences = []
        for result in search_results:
            metadata = result['metadata']
            content = metadata.get('content', '')
            
            # Check if company is mentioned
            if company_name.lower() in content.lower():
                entities = self.extract_entities(content)
                dates = self._extract_dates_from_text(content)
                
                company_conferences.append({
                    "title": metadata.get('title', 'Unknown'),
                    "date": metadata.get('date', dates[0] if dates else 'N/A'),
                    "content": content[:300] + "...",
                    "score": result['score'],
                    "topics": entities.get('topics', [])
                })
                
        # Sort by date
        company_conferences.sort(key=lambda x: x['date'], reverse=True)
        
        return {
            "company": company_name,
            "total_conferences": len(company_conferences),
            "conferences": company_conferences
        }

    def get_industry_trends(self, time_period: str = "recent") -> Dict[str, Any]:
        """Get industry trends from conference data"""
        # Search for recent conference data
        query = "industry trends developments conference"
        search_results = self.search_knowledge_base(query, top_k=10)
        
        # Analyze trends
        trends = {
            "topics": {},
            "companies": {},
            "technologies": {},
            "regulatory_focus": []
        }
        
        for result in search_results:
            metadata = result['metadata']
            content = metadata.get('content', '')
            
            # Extract entities
            entities = self.extract_entities(content)
            
            # Count topics
            for topic in entities.get('topics', []):
                trends["topics"][topic] = trends["topics"].get(topic, 0) + 1
                
            # Count companies
            for company in entities.get('companies', []):
                trends["companies"][company] = trends["companies"].get(company, 0) + 1
                
            # Look for technology mentions
            tech_keywords = ['AI', 'automation', 'digital', 'technology', 'innovation', 'platform']
            for keyword in tech_keywords:
                if keyword.lower() in content.lower():
                    trends["technologies"][keyword] = trends["technologies"].get(keyword, 0) + 1
                    
            # Look for regulatory focus
            reg_keywords = ['FDA', 'compliance', 'regulation', 'guidance', 'standard']
            for keyword in reg_keywords:
                if keyword.lower() in content.lower():
                    trends["regulatory_focus"].append({
                        "keyword": keyword,
                        "source": metadata.get('title', 'Unknown'),
                        "context": content[:200] + "..."
                    })
                    
        return trends 