import pandas as pd
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
import os
from config import KNOWLEDGE_BASE_PATHS

class QualitySystemsAgent(BaseAgent):
    def __init__(self):
        super().__init__("quality_systems")
        self.snc_data = self._load_snc_data()
        
    def _load_snc_data(self) -> pd.DataFrame:
        """Load SNC data from CSV file"""
        csv_path = os.path.join(KNOWLEDGE_BASE_PATHS["quality_systems"], 
                               "Supplier NOtification of Change Data base.csv")
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            # Clean and process the data
            df = df.dropna()
            return df
        return pd.DataFrame()
        
    def get_system_prompt(self) -> str:
        return """You are the Quality Systems Agent specializing in Supplier Notification of Change (SNC) data and quality events. Your expertise includes:

1. Analyzing SNC entries and their descriptions
2. Tracking quality events over time for specific companies
3. Identifying patterns in quality system changes
4. Providing insights on supplier quality trends
5. Supporting audit planning with quality event data

Key Capabilities:
- Temporal analysis of quality events
- Company-specific quality trend identification
- SNC categorization and analysis
- Quality system change tracking
- Audit support with quality event context

Always provide specific SNC entry details, company information, and temporal context when available."""

    def get_capabilities(self) -> List[str]:
        return [
            "SNC data analysis",
            "Temporal quality event tracking",
            "Company quality trend analysis",
            "Quality system change monitoring",
            "Audit support with quality context"
        ]

    def process_query(self, query: str, context: str = "") -> Dict[str, Any]:
        # Search knowledge base
        search_results = self.search_knowledge_base(query, top_k=10)
        
        # Process SNC data if relevant
        snc_analysis = self._analyze_snc_data(query)
        
        # Combine context
        combined_context = self._format_context(search_results, snc_analysis)
        
        # Generate response
        response = self.generate_response(query, combined_context)
        
        # Extract sources
        sources = self._extract_sources_from_results(search_results)
        
        return {
            "query": query,
            "context": combined_context,
            "response": response,
            "snc_analysis": snc_analysis,
            "sources": sources
        }

    def _analyze_snc_data(self, query: str) -> Dict[str, Any]:
        """Analyze SNC data based on the query"""
        if self.snc_data.empty:
            return {"message": "No SNC data available"}
            
        # Extract company names from query
        companies = self._extract_companies_from_query(query)
        
        analysis = {
            "total_snc_entries": len(self.snc_data),
            "companies_analyzed": companies,
            "company_data": {},
            "temporal_analysis": {},
            "category_analysis": {}
        }
        
        # Analyze by company
        for company in companies:
            company_data = self._get_company_snc_data(company)
            analysis["company_data"][company] = company_data
            
        # Overall category analysis
        analysis["category_analysis"] = self._analyze_categories()
        
        # Temporal analysis if dates are available
        if "date" in self.snc_data.columns:
            analysis["temporal_analysis"] = self._analyze_temporal_trends()
            
        return analysis

    def _extract_companies_from_query(self, query: str) -> List[str]:
        """Extract company names from query"""
        query_lower = query.lower()
        companies = []
        
        # Common companies in the data
        known_companies = [
            "boehringer ingelheim", "thermo fisher", "hovione", "patheon", 
            "gram", "fisher clinical", "lonza", "pfizer", "bms"
        ]
        
        for company in known_companies:
            if company in query_lower:
                companies.append(company)
                
        return companies

    def _get_company_snc_data(self, company_name: str) -> Dict[str, Any]:
        """Get SNC data for a specific company"""
        # Filter data for the company
        company_data = self.snc_data[
            self.snc_data['Assigned CMO'].str.contains(company_name, case=False, na=False)
        ]
        
        if company_data.empty:
            return {"message": f"No SNC data found for {company_name}"}
            
        # Analyze by category
        category_counts = company_data['Assigned Category'].value_counts().to_dict()
        
        # Get recent entries (assuming entries are ordered)
        recent_entries = company_data.head(5).to_dict('records')
        
        # Extract key changes
        key_changes = self._extract_key_changes(company_data)
        
        return {
            "total_entries": len(company_data),
            "categories": category_counts,
            "recent_entries": recent_entries,
            "key_changes": key_changes,
            "all_entries": company_data.to_dict('records')
        }

    def _extract_key_changes(self, company_data: pd.DataFrame) -> List[Dict[str, str]]:
        """Extract key changes from SNC descriptions"""
        key_changes = []
        
        for _, row in company_data.iterrows():
            description = row.get('SNC Description', '')
            if description:
                # Extract the change type from description
                change_type = self._extract_change_type(description)
                key_changes.append({
                    "entry": row.get('SNC Title', ''),
                    "change_type": change_type,
                    "description": description,
                    "category": row.get('Assigned Category', ''),
                    "material_code": self._extract_material_code(description)
                })
                
        return key_changes

    def _extract_change_type(self, description: str) -> str:
        """Extract the type of change from SNC description"""
        description_lower = description.lower()
        
        change_types = [
            "warehouse usage", "label", "excipients", "packaging label",
            "qa leadership", "column name", "raw material supplier",
            "process description", "software system", "batch manufacturing"
        ]
        
        for change_type in change_types:
            if change_type in description_lower:
                return change_type
                
        return "other"

    def _extract_material_code(self, description: str) -> str:
        """Extract material code from description"""
        import re
        # Look for pattern like "Material Code: XXXXX"
        match = re.search(r'Material Code:\s*([A-Z0-9]+)', description)
        if match:
            return match.group(1)
        return ""

    def _analyze_categories(self) -> Dict[str, Any]:
        """Analyze SNC data by category"""
        if self.snc_data.empty:
            return {}
            
        category_counts = self.snc_data['Assigned Category'].value_counts().to_dict()
        total_entries = len(self.snc_data)
        
        return {
            "category_distribution": category_counts,
            "total_entries": total_entries,
            "most_common_category": max(category_counts, key=category_counts.get) if category_counts else None
        }

    def _analyze_temporal_trends(self) -> Dict[str, Any]:
        """Analyze temporal trends in SNC data"""
        # This would be implemented if we had date data
        return {"message": "Temporal analysis requires date data"}

    def _format_context(self, search_results: List[Dict], snc_analysis: Dict[str, Any]) -> str:
        """Format context from search results and SNC analysis"""
        context_parts = []
        
        # Add search results context
        if search_results:
            context_parts.append("=== KNOWLEDGE BASE SEARCH RESULTS ===")
            for i, result in enumerate(search_results, 1):
                metadata = result['metadata']
                context_parts.append(
                    f"{i}. Score: {result['score']:.3f}\n"
                    f"   Content: {metadata.get('content', 'N/A')[:200]}...\n"
                )
        
        # Add SNC analysis context
        if snc_analysis:
            context_parts.append("=== SNC DATA ANALYSIS ===")
            context_parts.append(f"Total SNC Entries: {snc_analysis.get('total_snc_entries', 0)}")
            
            for company, data in snc_analysis.get('company_data', {}).items():
                if isinstance(data, dict) and 'total_entries' in data:
                    context_parts.append(f"\n{company.upper()}:")
                    context_parts.append(f"  Total Entries: {data['total_entries']}")
                    context_parts.append(f"  Categories: {data.get('categories', {})}")
                    
                    # Add recent key changes
                    key_changes = data.get('key_changes', [])
                    if key_changes:
                        context_parts.append("  Recent Key Changes:")
                        for change in key_changes[:3]:  # Show top 3
                            context_parts.append(f"    - {change['change_type']}: {change['description'][:100]}...")
        
        return "\n".join(context_parts)

    def _extract_sources_from_results(self, search_results: List[Dict]) -> List[Dict[str, str]]:
        """Extract source information from search results"""
        sources = []
        for result in search_results:
            metadata = result['metadata']
            sources.append({
                "title": metadata.get('title', 'Unknown'),
                "file_path": metadata.get('file_path', ''),
                "score": result['score'],
                "content_preview": metadata.get('content', '')[:100] + "..."
            })
        return sources

    def get_company_quality_timeline(self, company_name: str) -> Dict[str, Any]:
        """Get a timeline of quality events for a company"""
        company_data = self._get_company_snc_data(company_name)
        
        if "message" in company_data:
            return company_data
            
        # Create timeline from entries
        timeline = []
        for entry in company_data.get('all_entries', []):
            timeline.append({
                "entry": entry.get('SNC Title', ''),
                "category": entry.get('Assigned Category', ''),
                "description": entry.get('SNC Description', ''),
                "change_type": self._extract_change_type(entry.get('SNC Description', ''))
            })
            
        return {
            "company": company_name,
            "timeline": timeline,
            "summary": {
                "total_events": len(timeline),
                "categories": company_data.get('categories', {}),
                "key_changes": company_data.get('key_changes', [])
            }
        }

    def get_quality_trends(self, time_period: str = "all") -> Dict[str, Any]:
        """Get quality trends across all companies"""
        if self.snc_data.empty:
            return {"message": "No SNC data available"}
            
        # Analyze trends by category
        category_trends = self._analyze_categories()
        
        # Analyze by company
        company_trends = {}
        for company in self.snc_data['Assigned CMO'].unique():
            if pd.notna(company):
                company_data = self._get_company_snc_data(company)
                if "message" not in company_data:
                    company_trends[company] = {
                        "total_entries": company_data['total_entries'],
                        "categories": company_data['categories']
                    }
                    
        return {
            "category_trends": category_trends,
            "company_trends": company_trends,
            "overall_summary": {
                "total_companies": len(company_trends),
                "total_entries": len(self.snc_data)
            }
        } 