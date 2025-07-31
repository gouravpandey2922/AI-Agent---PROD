from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent

class SOPAgent(BaseAgent):
    def __init__(self):
        super().__init__("sop")
        
    def get_system_prompt(self) -> str:
        return """You are the SOP Agent specializing in standard operating procedures and audit protocols. Your expertise includes:

1. Interpreting and explaining standard operating procedures
2. Creating audit protocols and checklists based on SOPs
3. Identifying SOP updates and changes over time
4. Providing guidance on procedure compliance
5. Supporting audit planning with SOP-based requirements

Key Capabilities:
- SOP interpretation and explanation
- Audit protocol creation
- Procedure compliance guidance
- SOP change tracking
- Audit checklist generation

Always provide structured, step-by-step guidance based on SOPs and include specific procedure references."""

    def get_capabilities(self) -> List[str]:
        return [
            "SOP interpretation and explanation",
            "Audit protocol creation",
            "Procedure compliance guidance",
            "SOP change tracking",
            "Audit checklist generation"
        ]

    def process_query(self, query: str, context: str = "") -> Dict[str, Any]:
        # Search knowledge base
        search_results = self.search_knowledge_base(query, top_k=8)
        
        # Analyze results for SOP-specific insights
        analysis = self._analyze_sop_results(search_results, query)
        
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

    def _analyze_sop_results(self, search_results: List[Dict], query: str) -> Dict[str, Any]:
        """Analyze search results for SOP-specific insights"""
        analysis = {
            "total_results": len(search_results),
            "sop_procedures": [],
            "audit_protocols": [],
            "compliance_requirements": [],
            "checklist_items": [],
            "procedure_steps": [],
            "sop_versions": []
        }
        
        # Analyze content for SOP themes
        for result in search_results:
            metadata = result['metadata']
            content = metadata.get('content', '')
            score = result['score']
            
            # Extract SOP procedures
            if any(word in content.lower() for word in ['procedure', 'process', 'method', 'protocol', 'standard']):
                analysis["sop_procedures"].append({
                    "source": metadata.get('title', 'Unknown'),
                    "content": content[:200] + "...",
                    "score": score
                })
                
            # Extract audit protocols
            if any(word in content.lower() for word in ['audit', 'inspection', 'review', 'assessment']):
                analysis["audit_protocols"].append({
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
                
            # Extract procedure steps
            if any(word in content.lower() for word in ['step', 'stage', 'phase', 'sequence']):
                analysis["procedure_steps"].append({
                    "source": metadata.get('title', 'Unknown'),
                    "content": content[:200] + "...",
                    "score": score
                })
                
            # Extract SOP versions
            if any(word in content.lower() for word in ['version', 'revision', 'update', 'change']):
                analysis["sop_versions"].append({
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
            context_parts.append("=== STANDARD OPERATING PROCEDURES ===")
            for i, result in enumerate(search_results, 1):
                metadata = result['metadata']
                context_parts.append(
                    f"{i}. Score: {result['score']:.3f}\n"
                    f"   Source: {metadata.get('title', 'Unknown')}\n"
                    f"   Content: {metadata.get('content', 'N/A')[:200]}...\n"
                )
        
        # Add analysis context
        if analysis:
            context_parts.append("\n=== SOP INSIGHTS ===")
            
            if analysis["sop_procedures"]:
                context_parts.append(f"\nSOP Procedures Found: {len(analysis['sop_procedures'])}")
                for proc in analysis["sop_procedures"][:3]:  # Show top 3
                    context_parts.append(f"  - {proc['source']}: {proc['content']}")
                    
            if analysis["audit_protocols"]:
                context_parts.append(f"\nAudit Protocols Found: {len(analysis['audit_protocols'])}")
                for protocol in analysis["audit_protocols"][:3]:  # Show top 3
                    context_parts.append(f"  - {protocol['source']}: {protocol['content']}")
                    
            if analysis["compliance_requirements"]:
                context_parts.append(f"\nCompliance Requirements Found: {len(analysis['compliance_requirements'])}")
                for req in analysis["compliance_requirements"][:3]:  # Show top 3
                    context_parts.append(f"  - {req['source']}: {req['content']}")
                    
            if analysis["checklist_items"]:
                context_parts.append(f"\nChecklist Items Found: {len(analysis['checklist_items'])}")
                for item in analysis["checklist_items"][:3]:  # Show top 3
                    context_parts.append(f"  - {item['source']}: {item['content']}")
                    
            if analysis["sop_versions"]:
                context_parts.append(f"\nSOP Versions/Updates Found: {len(analysis['sop_versions'])}")
                for version in analysis["sop_versions"][:3]:  # Show top 3
                    context_parts.append(f"  - {version['source']}: {version['content']}")
        
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

    def create_sop_based_checklist(self, sop_topic: str, audit_type: str = "general") -> Dict[str, Any]:
        """Create a checklist based on specific SOPs"""
        query = f"SOP {sop_topic} checklist audit"
        search_results = self.search_knowledge_base(query, top_k=10)
        
        # Generate checklist
        checklist_context = self._format_sop_checklist_context(search_results, sop_topic, audit_type)
        checklist = self.generate_response(
            f"Create a comprehensive checklist based on SOPs for {sop_topic}",
            checklist_context,
            "checklist"
        )
        
        return {
            "sop_topic": sop_topic,
            "audit_type": audit_type,
            "checklist": checklist,
            "sources": self._extract_sources_from_results(search_results)
        }

    def _format_sop_checklist_context(self, search_results: List[Dict], sop_topic: str, audit_type: str) -> str:
        """Format context for SOP-based checklist generation"""
        context_parts = [
            f"SOP Topic: {sop_topic}",
            f"Audit Type: {audit_type}",
            "\n=== RELEVANT SOPs ==="
        ]
        
        for i, result in enumerate(search_results, 1):
            metadata = result['metadata']
            context_parts.append(
                f"{i}. {metadata.get('title', 'Unknown')}\n"
                f"   {metadata.get('content', 'N/A')[:300]}...\n"
            )
            
        return "\n".join(context_parts)

    def get_sop_procedure(self, procedure_name: str) -> Dict[str, Any]:
        """Get detailed procedure information from SOPs"""
        query = f"procedure {procedure_name} SOP"
        search_results = self.search_knowledge_base(query, top_k=5)
        
        # Generate procedure explanation
        procedure_context = self._format_procedure_context(search_results, procedure_name)
        procedure = self.generate_response(
            f"Explain the {procedure_name} procedure based on SOPs",
            procedure_context,
            "general"
        )
        
        return {
            "procedure_name": procedure_name,
            "procedure": procedure,
            "sources": self._extract_sources_from_results(search_results)
        }

    def _format_procedure_context(self, search_results: List[Dict], procedure_name: str) -> str:
        """Format context for procedure explanation"""
        context_parts = [
            f"Procedure: {procedure_name}",
            "\n=== RELEVANT SOPs ==="
        ]
        
        for i, result in enumerate(search_results, 1):
            metadata = result['metadata']
            context_parts.append(
                f"{i}. {metadata.get('title', 'Unknown')}\n"
                f"   {metadata.get('content', 'N/A')[:400]}...\n"
            )
            
        return "\n".join(context_parts)

    def get_sop_compliance_guidance(self, area: str) -> Dict[str, Any]:
        """Get compliance guidance based on SOPs for a specific area"""
        query = f"compliance {area} SOP procedure"
        search_results = self.search_knowledge_base(query, top_k=8)
        
        # Generate compliance guidance
        compliance_context = self._format_compliance_context(search_results, area)
        guidance = self.generate_response(
            f"Provide compliance guidance for {area} based on SOPs",
            compliance_context,
            "insights"
        )
        
        return {
            "area": area,
            "guidance": guidance,
            "sources": self._extract_sources_from_results(search_results)
        }

    def _format_compliance_context(self, search_results: List[Dict], area: str) -> str:
        """Format context for compliance guidance"""
        context_parts = [
            f"Area: {area}",
            "\n=== RELEVANT SOPs ==="
        ]
        
        for i, result in enumerate(search_results, 1):
            metadata = result['metadata']
            context_parts.append(
                f"{i}. {metadata.get('title', 'Unknown')}\n"
                f"   {metadata.get('content', 'N/A')[:300]}...\n"
            )
            
        return "\n".join(context_parts)

    def track_sop_changes(self, sop_name: str = None) -> Dict[str, Any]:
        """Track changes and updates to SOPs"""
        if sop_name:
            query = f"version revision update {sop_name} SOP"
        else:
            query = "SOP version revision update change"
            
        search_results = self.search_knowledge_base(query, top_k=10)
        
        # Analyze for changes
        changes = []
        for result in search_results:
            metadata = result['metadata']
            content = metadata.get('content', '')
            
            # Look for version/revision information
            if any(word in content.lower() for word in ['version', 'revision', 'update', 'change', 'modified']):
                changes.append({
                    "title": metadata.get('title', 'Unknown'),
                    "content": content[:300] + "...",
                    "score": result['score']
                })
                
        return {
            "sop_name": sop_name,
            "total_changes": len(changes),
            "changes": changes,
            "sources": self._extract_sources_from_results(search_results)
        }

    def get_audit_protocols(self, audit_area: str) -> Dict[str, Any]:
        """Get audit protocols based on SOPs for a specific area"""
        query = f"audit protocol {audit_area} SOP"
        search_results = self.search_knowledge_base(query, top_k=8)
        
        # Generate audit protocol
        protocol_context = self._format_audit_protocol_context(search_results, audit_area)
        protocol = self.generate_response(
            f"Create an audit protocol for {audit_area} based on SOPs",
            protocol_context,
            "checklist"
        )
        
        return {
            "audit_area": audit_area,
            "protocol": protocol,
            "sources": self._extract_sources_from_results(search_results)
        }

    def _format_audit_protocol_context(self, search_results: List[Dict], audit_area: str) -> str:
        """Format context for audit protocol generation"""
        context_parts = [
            f"Audit Area: {audit_area}",
            "\n=== RELEVANT SOPs ==="
        ]
        
        for i, result in enumerate(search_results, 1):
            metadata = result['metadata']
            context_parts.append(
                f"{i}. {metadata.get('title', 'Unknown')}\n"
                f"   {metadata.get('content', 'N/A')[:300]}...\n"
            )
            
        return "\n".join(context_parts) 