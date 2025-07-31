from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent

class WebScraperAgent(BaseAgent):
    def __init__(self):
        super().__init__("web_scraper")
        
    def get_system_prompt(self) -> str:
        return """You are the Web Scraper Agent specializing in due diligence reports, FDA warning letters, and company reviews. Your expertise includes:

1. Analyzing due diligence reports for manufacturing sites
2. Processing FDA warning letters and compliance data
3. Reviewing company manufacturing capabilities and history
4. Identifying operational challenges and risks
5. Supporting audit planning with external data

Key Capabilities:
- Due diligence report analysis
- FDA compliance data interpretation
- Manufacturing site assessment
- Risk identification and analysis
- Company capability evaluation

Always provide specific details from reports, include file references, and highlight key findings and risks."""

    def get_capabilities(self) -> List[str]:
        return [
            "Due diligence report analysis",
            "FDA warning letter processing",
            "Manufacturing site assessment",
            "Risk identification",
            "Company capability evaluation"
        ]

    def process_query(self, query: str, context: str = "") -> Dict[str, Any]:
        """Process query using the enhanced source tracking method"""
        return self.process_query_with_sources(query, context, "general")

    def _analyze_search_results(self, search_results: List[Dict], query: str) -> Dict[str, Any]:
        """Analyze search results for key insights"""
        analysis = {
            "total_results": len(search_results),
            "companies_mentioned": [],
            "risk_factors": [],
            "compliance_issues": [],
            "manufacturing_capabilities": [],
            "key_findings": []
        }
        
        # Extract companies mentioned
        companies = set()
        for result in search_results:
            metadata = result['metadata']
            company = metadata.get('company', '')
            if company:
                companies.add(company)
        analysis["companies_mentioned"] = list(companies)
        
        # Analyze content for key themes
        for result in search_results:
            metadata = result['metadata']
            content = metadata.get('content', '')
            score = result['score']
            
            # Extract risk factors
            if any(word in content.lower() for word in ['risk', 'warning', 'violation', 'issue', 'problem']):
                analysis["risk_factors"].append({
                    "source": metadata.get('title', 'Unknown'),
                    "content": content[:200] + "...",
                    "score": score
                })
                
            # Extract compliance issues
            if any(word in content.lower() for word in ['fda', 'compliance', 'warning letter', '483', 'violation']):
                analysis["compliance_issues"].append({
                    "source": metadata.get('title', 'Unknown'),
                    "content": content[:200] + "...",
                    "score": score
                })
                
            # Extract manufacturing capabilities
            if any(word in content.lower() for word in ['manufacturing', 'facility', 'capacity', 'capability', 'production']):
                analysis["manufacturing_capabilities"].append({
                    "source": metadata.get('title', 'Unknown'),
                    "content": content[:200] + "...",
                    "score": score
                })
                
            # Extract key findings
            if score > 0.7:  # High relevance threshold
                analysis["key_findings"].append({
                    "source": metadata.get('title', 'Unknown'),
                    "content": content[:300] + "...",
                    "score": score
                })
        
        return analysis

    def _format_context(self, search_results: List[Dict], analysis: Dict[str, Any]) -> str:
        """Format search results into context for response generation"""
        context_parts = []
        
        # Add analysis summary
        context_parts.append("=== ANALYSIS SUMMARY ===")
        context_parts.append(f"Total Results: {analysis['total_results']}")
        context_parts.append(f"Companies Mentioned: {', '.join(analysis['companies_mentioned'])}")
        
        # Add key findings
        if analysis['key_findings']:
            context_parts.append("\n=== KEY FINDINGS ===")
            for finding in analysis['key_findings'][:3]:  # Top 3 findings
                context_parts.append(f"Source: {finding['source']}")
                context_parts.append(f"Relevance: {finding['score']:.3f}")
                context_parts.append(f"Content: {finding['content']}\n")
        
        # Add risk factors
        if analysis['risk_factors']:
            context_parts.append("=== RISK FACTORS ===")
            for risk in analysis['risk_factors'][:3]:  # Top 3 risks
                context_parts.append(f"Source: {risk['source']}")
                context_parts.append(f"Content: {risk['content']}\n")
        
        # Add compliance issues
        if analysis['compliance_issues']:
            context_parts.append("=== COMPLIANCE ISSUES ===")
            for issue in analysis['compliance_issues'][:3]:  # Top 3 issues
                context_parts.append(f"Source: {issue['source']}")
                context_parts.append(f"Content: {issue['content']}\n")
        
        # Add detailed search results
        context_parts.append("=== DETAILED SEARCH RESULTS ===")
        for result in search_results:
            metadata = result['metadata']
            context_parts.append(f"Document: {metadata.get('title', 'Unknown')}")
            context_parts.append(f"Relevance: {result['score']:.3f}")
            context_parts.append(f"Content: {metadata.get('content', '')[:500]}...\n")
        
        return "\n".join(context_parts)

    def _extract_sources_from_results(self, search_results: List[Dict]) -> List[Dict[str, str]]:
        """Extract source information from search results"""
        sources = []
        
        for result in search_results:
            metadata = result['metadata']
            source = {
                'title': metadata.get('title', 'Unknown Document'),
                'score': result['score'],
                'agent': self.agent_name,
                'content': metadata.get('content', '')[:300] + '...' if metadata.get('content') else '',
                'metadata': {
                    'file_path': metadata.get('file_path', ''),
                    'source_type': 'web_scraper',
                    'date': metadata.get('date', ''),
                    'company': metadata.get('company', ''),
                    'category': metadata.get('category', '')
                }
            }
            sources.append(source)
        
        return sources

    def get_company_due_diligence(self, company_name: str) -> Dict[str, Any]:
        """Get comprehensive due diligence information for a company"""
        query = f"due diligence {company_name} manufacturing site assessment"
        
        # Search for company-specific information
        search_results = self.search_knowledge_base(query, top_k=10)
        
        # Analyze results
        analysis = self._analyze_company_data(search_results, company_name)
        
        # Generate response
        context = self._format_context(search_results, analysis)
        response = self.generate_response(
            f"Provide a comprehensive due diligence assessment for {company_name}",
            context,
            "report"
        )
        
        return {
            "company": company_name,
            "assessment": response,
            "analysis": analysis,
            "sources": self._extract_sources_from_results(search_results)
        }

    def _analyze_company_data(self, results: List[Dict], company_name: str) -> Dict[str, Any]:
        """Analyze company-specific data from search results"""
        analysis = {
            "company_name": company_name,
            "total_documents": len(results),
            "risk_assessment": "Low",
            "compliance_status": "Unknown",
            "manufacturing_capabilities": [],
            "key_concerns": [],
            "positive_factors": []
        }
        
        # Analyze each result
        for result in results:
            metadata = result['metadata']
            content = metadata.get('content', '').lower()
            score = result['score']
            
            # Assess risk level
            risk_keywords = ['warning', 'violation', '483', 'fda', 'compliance issue', 'problem']
            if any(keyword in content for keyword in risk_keywords):
                analysis["key_concerns"].append({
                    "source": metadata.get('title', 'Unknown'),
                    "issue": "Compliance concern identified",
                    "score": score
                })
                if analysis["risk_assessment"] == "Low":
                    analysis["risk_assessment"] = "Medium"
                elif analysis["risk_assessment"] == "Medium":
                    analysis["risk_assessment"] = "High"
            
            # Identify positive factors
            positive_keywords = ['approved', 'compliant', 'successful', 'capable', 'qualified']
            if any(keyword in content for keyword in positive_keywords):
                analysis["positive_factors"].append({
                    "source": metadata.get('title', 'Unknown'),
                    "factor": "Positive assessment identified",
                    "score": score
                })
            
            # Extract manufacturing capabilities
            if 'manufacturing' in content or 'facility' in content:
                analysis["manufacturing_capabilities"].append({
                    "source": metadata.get('title', 'Unknown'),
                    "capability": content[:100] + "...",
                    "score": score
                })
        
        return analysis

    def get_fda_compliance_data(self, company_name: str = None) -> Dict[str, Any]:
        """Get FDA compliance data, optionally filtered by company"""
        if company_name:
            query = f"FDA compliance {company_name} warning letter 483"
        else:
            query = "FDA compliance warning letter 483 inspection"
        
        # Search for FDA-related information
        search_results = self.search_knowledge_base(query, top_k=8)
        
        # Analyze results
        analysis = {
            "total_fda_documents": len(search_results),
            "warning_letters": [],
            "483_observations": [],
            "compliance_trends": []
        }
        
        for result in search_results:
            metadata = result['metadata']
            content = metadata.get('content', '').lower()
            score = result['score']
            
            if 'warning letter' in content:
                analysis["warning_letters"].append({
                    "source": metadata.get('title', 'Unknown'),
                    "content": metadata.get('content', '')[:300] + "...",
                    "score": score
                })
            
            if '483' in content or 'observation' in content:
                analysis["483_observations"].append({
                    "source": metadata.get('title', 'Unknown'),
                    "content": metadata.get('content', '')[:300] + "...",
                    "score": score
                })
        
        # Generate response
        context = f"FDA Compliance Analysis:\n{str(analysis)}"
        response = self.generate_response(
            f"Provide FDA compliance analysis{f' for {company_name}' if company_name else ''}",
            context,
            "report"
        )
        
        return {
            "company": company_name,
            "compliance_analysis": response,
            "analysis": analysis,
            "sources": self._extract_sources_from_results(search_results)
        } 