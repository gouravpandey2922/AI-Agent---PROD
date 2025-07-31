from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent

class InternalAuditAgent(BaseAgent):
    def __init__(self):
        super().__init__("internal_audit")
        
    def get_system_prompt(self) -> str:
        return """You are the Internal Audit Agent specializing in audit procedures, checklists, and compliance guidelines. Your expertise includes:

1. Creating comprehensive audit checklists and questionnaires
2. Generating detailed audit reports with findings and recommendations
3. Providing guidance on audit procedures and best practices
4. Interpreting compliance requirements and regulations
5. Supporting audit planning and execution

Key Capabilities:
- Audit checklist generation
- Compliance procedure guidance
- Audit report creation
- Risk assessment support
- Regulatory interpretation

Always provide structured, actionable audit guidance with clear procedures and compliance requirements."""

    def get_capabilities(self) -> List[str]:
        return [
            "Audit checklist generation",
            "Compliance procedure guidance",
            "Audit report creation",
            "Risk assessment support",
            "Regulatory interpretation"
        ]

    def process_query(self, query: str, context: str = "") -> Dict[str, Any]:
        # Search knowledge base
        search_results = self.search_knowledge_base(query, top_k=8)
        
        # Analyze results for audit-specific insights
        analysis = self._analyze_audit_results(search_results, query)
        
        # Combine context
        combined_context = self._format_context(search_results, analysis)
        
        # Generate response
        response = self.generate_response(query, combined_context)
        
        # Extract sources
        sources = self._extract_sources_from_results(search_results)
        
        return {
            "query": query,
            "context": combined_context,
            "response": response,
            "analysis": analysis,
            "sources": sources
        }

    def _analyze_audit_results(self, search_results: List[Dict], query: str) -> Dict[str, Any]:
        """Analyze search results for audit-specific insights"""
        analysis = {
            "total_results": len(search_results),
            "audit_procedures": [],
            "compliance_requirements": [],
            "checklist_items": [],
            "risk_factors": [],
            "regulatory_references": []
        }
        
        # Analyze content for audit themes
        for result in search_results:
            metadata = result['metadata']
            content = metadata.get('content', '')
            score = result['score']
            
            # Extract audit procedures
            if any(word in content.lower() for word in ['procedure', 'process', 'method', 'protocol', 'standard']):
                analysis["audit_procedures"].append({
                    "source": metadata.get('title', 'Unknown'),
                    "content": content[:200] + "...",
                    "score": score
                })
                
            # Extract compliance requirements
            if any(word in content.lower() for word in ['compliance', 'requirement', 'regulation', 'standard', 'guideline']):
                analysis["compliance_requirements"].append({
                    "source": metadata.get('title', 'Unknown'),
                    "content": content[:200] + "...",
                    "score": score
                })
                
            # Extract checklist items
            if any(word in content.lower() for word in ['checklist', 'item', 'verify', 'confirm', 'check']):
                analysis["checklist_items"].append({
                    "source": metadata.get('title', 'Unknown'),
                    "content": content[:200] + "...",
                    "score": score
                })
                
            # Extract risk factors
            if any(word in content.lower() for word in ['risk', 'hazard', 'danger', 'issue', 'problem']):
                analysis["risk_factors"].append({
                    "source": metadata.get('title', 'Unknown'),
                    "content": content[:200] + "...",
                    "score": score
                })
                
            # Extract regulatory references
            if any(word in content.lower() for word in ['21 cfr', 'fda', 'gmp', 'ich', 'iso']):
                analysis["regulatory_references"].append({
                    "source": metadata.get('title', 'Unknown'),
                    "content": content[:200] + "...",
                    "score": score
                })
                
        return analysis

    def _format_context(self, search_results: List[Dict], analysis: Dict[str, Any]) -> str:
        """Format context from search results and analysis"""
        context_parts = []
        
        # Add search results context
        if search_results:
            context_parts.append("=== AUDIT PROCEDURES & COMPLIANCE DATA ===")
            for i, result in enumerate(search_results, 1):
                metadata = result['metadata']
                context_parts.append(
                    f"{i}. Score: {result['score']:.3f}\n"
                    f"   Source: {metadata.get('title', 'Unknown')}\n"
                    f"   Content: {metadata.get('content', 'N/A')[:200]}...\n"
                )
        
        # Add analysis context
        if analysis:
            context_parts.append("\n=== AUDIT INSIGHTS ===")
            
            if analysis["audit_procedures"]:
                context_parts.append(f"\nAudit Procedures Found: {len(analysis['audit_procedures'])}")
                for proc in analysis["audit_procedures"][:3]:  # Show top 3
                    context_parts.append(f"  - {proc['source']}: {proc['content']}")
                    
            if analysis["compliance_requirements"]:
                context_parts.append(f"\nCompliance Requirements Found: {len(analysis['compliance_requirements'])}")
                for req in analysis["compliance_requirements"][:3]:  # Show top 3
                    context_parts.append(f"  - {req['source']}: {req['content']}")
                    
            if analysis["checklist_items"]:
                context_parts.append(f"\nChecklist Items Found: {len(analysis['checklist_items'])}")
                for item in analysis["checklist_items"][:3]:  # Show top 3
                    context_parts.append(f"  - {item['source']}: {item['content']}")
                    
            if analysis["regulatory_references"]:
                context_parts.append(f"\nRegulatory References Found: {len(analysis['regulatory_references'])}")
                for ref in analysis["regulatory_references"][:3]:  # Show top 3
                    context_parts.append(f"  - {ref['source']}: {ref['content']}")
        
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

    def create_audit_checklist(self, audit_type: str, company_name: str = None) -> Dict[str, Any]:
        """Create a comprehensive audit checklist"""
        query = f"audit checklist {audit_type}"
        if company_name:
            query += f" {company_name}"
            
        search_results = self.search_knowledge_base(query, top_k=10)
        
        # Generate checklist
        checklist_context = self._format_checklist_context(search_results, audit_type, company_name)
        checklist = self.generate_response(
            f"Create a comprehensive {audit_type} audit checklist",
            checklist_context,
            "checklist"
        )
        
        return {
            "audit_type": audit_type,
            "company": company_name,
            "checklist": checklist,
            "sources": self._extract_sources_from_results(search_results)
        }

    def _format_checklist_context(self, search_results: List[Dict], audit_type: str, company_name: str) -> str:
        """Format context for checklist generation"""
        context_parts = [
            f"Audit Type: {audit_type}",
            f"Company: {company_name or 'General'}",
            "\n=== RELEVANT AUDIT PROCEDURES ==="
        ]
        
        for i, result in enumerate(search_results, 1):
            metadata = result['metadata']
            context_parts.append(
                f"{i}. {metadata.get('title', 'Unknown')}\n"
                f"   {metadata.get('content', 'N/A')[:300]}...\n"
            )
            
        return "\n".join(context_parts)

    def generate_audit_report(self, audit_findings: List[Dict], company_name: str) -> Dict[str, Any]:
        """Generate a comprehensive audit report"""
        # Search for relevant audit procedures
        search_results = self.search_knowledge_base("audit report template findings recommendations", top_k=5)
        
        # Format findings for report generation
        findings_context = self._format_findings_context(audit_findings, search_results)
        
        report = self.generate_response(
            f"Generate a comprehensive audit report for {company_name}",
            findings_context,
            "report"
        )
        
        return {
            "company": company_name,
            "report": report,
            "findings_count": len(audit_findings),
            "sources": self._extract_sources_from_results(search_results)
        }

    def _format_findings_context(self, findings: List[Dict], search_results: List[Dict]) -> str:
        """Format findings context for report generation"""
        context_parts = [
            "=== AUDIT FINDINGS ==="
        ]
        
        for i, finding in enumerate(findings, 1):
            context_parts.append(
                f"Finding {i}:\n"
                f"  Type: {finding.get('type', 'Unknown')}\n"
                f"  Description: {finding.get('description', 'N/A')}\n"
                f"  Severity: {finding.get('severity', 'Unknown')}\n"
                f"  Recommendation: {finding.get('recommendation', 'N/A')}\n"
            )
            
        context_parts.append("\n=== AUDIT PROCEDURES REFERENCE ===")
        for result in search_results:
            metadata = result['metadata']
            context_parts.append(
                f"- {metadata.get('title', 'Unknown')}\n"
                f"  {metadata.get('content', 'N/A')[:200]}...\n"
            )
            
        return "\n".join(context_parts)

    def get_compliance_guidance(self, regulation: str, area: str = None) -> Dict[str, Any]:
        """Get compliance guidance for specific regulations"""
        query = f"compliance {regulation}"
        if area:
            query += f" {area}"
            
        search_results = self.search_knowledge_base(query, top_k=8)
        
        # Generate compliance guidance
        guidance_context = self._format_compliance_context(search_results, regulation, area)
        guidance = self.generate_response(
            f"Provide compliance guidance for {regulation}",
            guidance_context,
            "insights"
        )
        
        return {
            "regulation": regulation,
            "area": area,
            "guidance": guidance,
            "sources": self._extract_sources_from_results(search_results)
        }

    def _format_compliance_context(self, search_results: List[Dict], regulation: str, area: str) -> str:
        """Format context for compliance guidance"""
        context_parts = [
            f"Regulation: {regulation}",
            f"Area: {area or 'General'}",
            "\n=== COMPLIANCE REQUIREMENTS ==="
        ]
        
        for i, result in enumerate(search_results, 1):
            metadata = result['metadata']
            context_parts.append(
                f"{i}. {metadata.get('title', 'Unknown')}\n"
                f"   {metadata.get('content', 'N/A')[:300]}...\n"
            )
            
        return "\n".join(context_parts) 