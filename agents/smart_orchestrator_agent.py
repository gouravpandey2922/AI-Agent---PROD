from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
from .base_agent import BaseAgent
from .web_scraper_agent import WebScraperAgent
from .internal_audit_agent import InternalAuditAgent
from .external_conference_agent import ExternalConferenceAgent
from .quality_systems_agent import QualitySystemsAgent
from .sop_agent import SOPAgent

class SmartOrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__("smart_orchestrator")
        # Initialize all specialized agents
        self.agents = {
            "web_scraper": WebScraperAgent(),
            "internal_audit": InternalAuditAgent(),
            "external_conference": ExternalConferenceAgent(),
            "quality_systems": QualitySystemsAgent(),
            "sop": SOPAgent()
        }
        
        # Risk priority labels
        self.priority_labels = {
            "critical": "🔥 Priority",
            "standard": "✅ Standard", 
            "watchlist": "⚠️ Watchlist"
        }
        
    def get_system_prompt(self) -> str:
        return """You are a centralized Smart Audit Orchestrator Agent for quality audits. Your role is to support both internal audits and external CDMO/supplier audits by coordinating multiple specialized sub-agents. Acting as a virtual Lead Auditor, you leverage each sub-agent's data to plan audits, identify risks, and compile findings.

You must simulate the knowledge, skills, and behavior of a qualified auditor with at least five years of relevant GMP experience, completed basic auditor training, documented on-the-job participation in two audits (one as co-lead), and formal requalification every three years.

Your expertise includes:
- Global regulations: 21 CFR Parts 210-211, EU GMP Part I Chapters 1-9, ICH Q7-Q10, WHO TRS 957 Annex 2, PIC/S PE 009-17 Part I, Health Canada C.02, PMDA GMP Ordinance, TGA PIC/S adoption, NMPA Annex 1, and ASEAN GMP
- Risk-based thinking and objective evidence review
- Clear communication for audit preparation and reporting

Key Outputs:
1. Audit Agenda Insights: Analyze existing agendas, highlight changes, suggest additions
2. Intelligent Audit Checklists: Tailor risk-based checklists for each audit type
3. Observation Logs: Structured entries with area, finding, risk level, evidence, references
4. Structured Audit Reports: Comprehensive reports aligned with company templates
5. Regulatory & SOP Delta Summaries: Changes since last audit with impact assessment

Risk-Based Focus:
- 🔥 Priority: Critical or high-risk areas requiring immediate investigation
- ✅ Standard: Regular checkpoints essential to compliance
- ⚠️ Watchlist: Emerging or potential risks requiring monitoring

Always maintain professional audit standards, use evidence-based findings, and provide actionable recommendations."""

    def get_capabilities(self) -> List[str]:
        return [
            "Audit agenda analysis and enhancement",
            "Risk-based checklist generation",
            "Structured observation logging",
            "Comprehensive audit reporting",
            "Regulatory delta analysis",
            "Live audit participation support",
            "Multi-agent orchestration",
            "Quality event trend analysis",
            "SOP change tracking",
            "Supplier health assessment"
        ]

    def process_query(self, query: str, context: str = "", intent: str = None) -> Dict[str, Any]:
        """Process audit-related queries with intelligent routing, agent communication, and comprehensive synthesis"""
        
        # Determine user intent and required agents
        intent = intent or self._determine_audit_intent(query)
        required_agents = self._determine_required_agents(query, intent)
        
        # Collect data from relevant agents with enhanced source processing
        agent_data = {}
        all_sources = []
        all_document_citations = []
        agent_communications = []
        
        # First pass: Collect initial data from all agents
        for agent_name in required_agents:
            if agent_name in self.agents:
                try:
                    # Use enhanced source processing
                    agent_response = self.agents[agent_name].process_query_with_sources(query, context)
                    agent_data[agent_name] = agent_response
                    
                    # Collect sources and document citations
                    if 'sources' in agent_response:
                        for source in agent_response['sources']:
                            source['agent'] = agent_name
                            all_sources.append(source)
                    
                    if 'document_citations' in agent_response:
                        for citation in agent_response['document_citations']:
                            citation['agent'] = agent_name
                            all_document_citations.append(citation)
                    
                    # Record agent communication
                    agent_communications.append({
                        'agent': agent_name,
                        'status': 'completed',
                        'documents_found': len(agent_response.get('sources', [])),
                        'relevance_score': sum(s.get('score', 0) for s in agent_response.get('sources', []))
                    })
                    
                except Exception as e:
                    agent_data[agent_name] = {"error": str(e)}
                    agent_communications.append({
                        'agent': agent_name,
                        'status': 'error',
                        'error': str(e)
                    })
        
        # Second pass: Agent cross-communication for enhanced insights
        cross_agent_insights = self._facilitate_agent_communication(agent_data, query, intent)
        
        # Generate comprehensive response based on intent with all collected data
        response = self._generate_audit_response(query, intent, agent_data, cross_agent_insights)
        
        # Compile comprehensive document citation summary
        document_summary = self._compile_document_summary(all_document_citations)
        
        return {
            "query": query,
            "intent": intent,
            "response": response,
            "involved_agents": required_agents,
            "agent_data": agent_data,
            "agent_communications": agent_communications,
            "cross_agent_insights": cross_agent_insights,
            "sources": all_sources,
            "document_citations": all_document_citations,
            "document_summary": document_summary,
            "timestamp": datetime.now().isoformat()
        }

    def _determine_audit_intent(self, query: str) -> str:
        """Determine the specific audit intent from the query using advanced pattern recognition"""
        query_lower = query.lower()
        
        # Define intent patterns with weighted scoring
        intent_patterns = {
            'audit_checklist': {
                'keywords': ['checklist', 'list', 'steps', 'procedures', 'items to check', 'audit items'],
                'weight': 1.0
            },
            'audit_agenda': {
                'keywords': ['agenda', 'schedule', 'plan', 'timeline', 'meeting plan', 'audit plan'],
                'weight': 1.0
            },
            'audit_report': {
                'keywords': ['report', 'findings', 'observations', 'summary', 'conclusion', 'audit report'],
                'weight': 1.0
            },
            'delta_analysis': {
                'keywords': ['changed', 'delta', 'since last', 'updates', 'what changed', 'differences', 'modifications'],
                'weight': 1.0
            },
            'health_assessment': {
                'keywords': ['health', 'status', '360', 'overview', 'assessment', 'evaluation', 'condition'],
                'weight': 1.0
            },
            'trend_analysis': {
                'keywords': ['insights', 'trends', 'patterns', 'analysis', 'statistics', 'metrics', 'performance'],
                'weight': 1.0
            },
            'supplier_audit': {
                'keywords': ['supplier', 'cdmo', 'vendor', 'contractor', 'external', 'third party'],
                'weight': 1.0
            },
            'internal_audit': {
                'keywords': ['internal', 'site', 'facility', 'own', 'company', 'in-house'],
                'weight': 1.0
            },
            'regulatory_audit': {
                'keywords': ['regulatory', 'compliance', 'fda', 'ema', 'gmp', 'inspection', 'regulatory audit'],
                'weight': 1.0
            },
            'quality_analysis': {
                'keywords': ['quality', 'deviations', 'capas', 'non-conformances', 'quality issues', 'quality events'],
                'weight': 1.0
            },
            'sop_review': {
                'keywords': ['sop', 'procedures', 'documentation', 'policies', 'standard operating procedures'],
                'weight': 1.0
            },
            'regulatory_research': {
                'keywords': ['regulations', 'guidelines', 'fda guidance', 'ema guidance', 'regulatory updates'],
                'weight': 1.0
            },
            'conference_analysis': {
                'keywords': ['conference', 'meeting', 'event', 'presentation', 'industry', 'external engagement'],
                'weight': 1.0
            }
        }
        
        # Calculate intent scores
        intent_scores = {}
        for intent, pattern in intent_patterns.items():
            score = 0
            for keyword in pattern['keywords']:
                if keyword in query_lower:
                    score += pattern['weight']
            if score > 0:
                intent_scores[intent] = score
        
        # Return the highest scoring intent, or general_audit if no clear match
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        
        return 'general_audit'

    def _determine_required_agents(self, query: str, intent: str) -> List[str]:
        """Determine which agents are required based on query and intent using advanced routing logic"""
        required_agents = []
        query_lower = query.lower()
        
        # Define agent capabilities and their relevance to different intents
        agent_capabilities = {
            'internal_audit': {
                'primary_intents': ['audit_checklist', 'audit_agenda', 'audit_report', 'internal_audit'],
                'secondary_intents': ['health_assessment', 'trend_analysis', 'general_audit'],
                'keywords': ['audit', 'checklist', 'procedures', 'compliance', 'inspection'],
                'weight': 1.0
            },
            'sop': {
                'primary_intents': ['sop_review', 'audit_checklist', 'audit_agenda'],
                'secondary_intents': ['delta_analysis', 'health_assessment', 'quality_analysis'],
                'keywords': ['sop', 'procedures', 'documentation', 'policies', 'standard operating'],
                'weight': 1.0
            },
            'quality_systems': {
                'primary_intents': ['quality_analysis', 'health_assessment', 'trend_analysis'],
                'secondary_intents': ['delta_analysis', 'audit_report', 'supplier_audit'],
                'keywords': ['quality', 'deviations', 'capas', 'non-conformances', 'quality events'],
                'weight': 1.0
            },
            'web_scraper': {
                'primary_intents': ['regulatory_research', 'regulatory_audit', 'supplier_audit'],
                'secondary_intents': ['health_assessment', 'delta_analysis'],
                'keywords': ['fda', 'warning', '483', 'eir', 'regulatory', 'guidance', 'compliance'],
                'weight': 1.0
            },
            'external_conference': {
                'primary_intents': ['conference_analysis', 'trend_analysis'],
                'secondary_intents': ['health_assessment', 'delta_analysis'],
                'keywords': ['conference', 'meeting', 'event', 'presentation', 'industry', 'external'],
                'weight': 1.0
            }
        }
        
        # Calculate agent relevance scores
        agent_scores = {}
        for agent_name, capabilities in agent_capabilities.items():
            score = 0
            
            # Intent-based scoring
            if intent in capabilities['primary_intents']:
                score += 3.0
            elif intent in capabilities['secondary_intents']:
                score += 1.5
            
            # Keyword-based scoring
            for keyword in capabilities['keywords']:
                if keyword in query_lower:
                    score += capabilities['weight']
            
            # Company-specific scoring
            companies = ['hovione', 'boehringer', 'thermo fisher', 'gram', 'grand river']
            if any(company in query_lower for company in companies):
                if agent_name in ['quality_systems', 'web_scraper']:
                    score += 1.0
            
            if score > 0:
                agent_scores[agent_name] = score
        
        # Select agents based on scores (threshold-based selection)
        threshold = 1.0
        for agent_name, score in agent_scores.items():
            if score >= threshold:
                required_agents.append(agent_name)
        
        # Ensure at least one agent is selected for basic functionality
        if not required_agents:
            required_agents = ['internal_audit']
        
        # Remove duplicates and return
        return list(set(required_agents))

    def _generate_audit_response(self, query: str, intent: str, agent_data: Dict[str, Any], cross_agent_insights: Dict[str, Any] = None) -> str:
        """Generate comprehensive audit response based on intent with cross-agent insights"""
        
        if intent == 'audit_checklist':
            return self._generate_audit_checklist(query, agent_data, cross_agent_insights)
        elif intent == 'audit_agenda':
            return self._generate_agenda_analysis(query, agent_data, cross_agent_insights)
        elif intent == 'audit_report':
            return self._generate_audit_report(query, agent_data, cross_agent_insights)
        elif intent == 'delta_analysis':
            return self._generate_delta_analysis(query, agent_data, cross_agent_insights)
        elif intent == 'health_assessment':
            return self._generate_health_assessment(query, agent_data, cross_agent_insights)
        elif intent == 'trend_analysis':
            return self._generate_trend_analysis(query, agent_data, cross_agent_insights)
        elif intent == 'quality_analysis':
            return self._generate_quality_analysis(query, agent_data, cross_agent_insights)
        elif intent == 'sop_review':
            return self._generate_sop_review(query, agent_data, cross_agent_insights)
        elif intent == 'regulatory_research':
            return self._generate_regulatory_research(query, agent_data, cross_agent_insights)
        elif intent == 'conference_analysis':
            return self._generate_conference_analysis(query, agent_data, cross_agent_insights)
        else:
            return self._generate_general_response(query, agent_data, cross_agent_insights)

    def _generate_audit_checklist(self, query: str, agent_data: Dict[str, Any], cross_agent_insights: Dict[str, Any] = None) -> str:
        """Generate intelligent, risk-based audit checklist"""
        
        # Extract company and audit type from query
        company_name = self._extract_company_name(query)
        audit_type = self._determine_audit_type(query)
        
        # Get relevant data from agents
        sop_data = agent_data.get('sop', {}).get('response', '')
        quality_data = agent_data.get('quality_systems', {}).get('response', '')
        audit_data = agent_data.get('internal_audit', {}).get('response', '')
        
        # Create checklist prompt
        checklist_prompt = f"""
        Create a comprehensive, risk-based audit checklist for {audit_type} audit of {company_name}.
        
        Context:
        - SOP Information: {sop_data[:1000]}...
        - Quality Systems Data: {quality_data[:1000]}...
        - Audit Procedures: {audit_data[:1000]}...
        
        Requirements:
        1. Use risk-based prioritization (🔥 Priority, ✅ Standard, ⚠️ Watchlist)
        2. Include specific areas: Facilities, Systems, Processes, Documentation
        3. Add evidence requirements for each item
        4. Include regulatory references where applicable
        5. Format as a structured table with columns: Area, Checklist Item, Type, Priority, Notes
        
        Generate a professional, comprehensive checklist suitable for a qualified auditor.
        """
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert audit checklist creator with deep GMP knowledge."},
                {"role": "user", "content": checklist_prompt}
            ],
            temperature=0.2,
            max_tokens=3000
        )
        
        return response.choices[0].message.content

    def _generate_agenda_analysis(self, query: str, agent_data: Dict[str, Any], cross_agent_insights: Dict[str, Any] = None) -> str:
        """Analyze and enhance audit agendas"""
        
        # Extract agenda content from query or context
        agenda_content = self._extract_agenda_content(query)
        
        # Get relevant data for agenda enhancement
        sop_changes = agent_data.get('sop', {}).get('response', '')
        quality_events = agent_data.get('quality_systems', {}).get('response', '')
        
        analysis_prompt = f"""
        Analyze this audit agenda and provide insights and recommendations:
        
        Agenda Content: {agenda_content}
        
        Recent Changes:
        - SOP Updates: {sop_changes[:500]}...
        - Quality Events: {quality_events[:500]}...
        
        Provide:
        1. 🔥 Critical areas that need attention
        2. ✅ Standard areas that are well-covered
        3. ⚠️ Watchlist items that should be monitored
        4. Suggested additions based on recent changes
        5. Risk assessment for each agenda item
        
        Format as a structured analysis with clear recommendations.
        """
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert audit agenda analyst."},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.2,
            max_tokens=2500
        )
        
        return response.choices[0].message.content

    def _generate_delta_analysis(self, query: str, agent_data: Dict[str, Any], cross_agent_insights: Dict[str, Any] = None) -> str:
        """Generate delta analysis of changes since last audit"""
        
        # Extract time period and company from query
        time_period = self._extract_time_period(query)
        company_name = self._extract_company_name(query)
        
        # Collect change data from agents
        sop_changes = agent_data.get('sop', {}).get('response', '')
        quality_changes = agent_data.get('quality_systems', {}).get('response', '')
        regulatory_changes = agent_data.get('web_scraper', {}).get('response', '')
        
        delta_prompt = f"""
        Generate a comprehensive delta analysis for {company_name} covering changes since {time_period}:
        
        Changes to Analyze:
        - SOP Updates: {sop_changes[:1000]}...
        - Quality System Changes: {quality_changes[:1000]}...
        - Regulatory Updates: {regulatory_changes[:1000]}...
        
        Provide:
        1. 🔥 Critical Changes (High Impact)
        2. ⚠️ Moderate Changes (Medium Impact)  
        3. ✅ Minor Changes (Low Impact)
        4. Impact assessment for each change
        5. Recommendations for audit focus areas
        
        Format as a structured delta report with clear impact classifications.
        """
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert change management analyst."},
                {"role": "user", "content": delta_prompt}
            ],
            temperature=0.2,
            max_tokens=2500
        )
        
        return response.choices[0].message.content

    def _generate_health_assessment(self, query: str, agent_data: Dict[str, Any], cross_agent_insights: Dict[str, Any] = None) -> str:
        """Generate 360° health assessment for a company/CDMO"""
        
        company_name = self._extract_company_name(query)
        
        # Collect comprehensive data
        quality_data = agent_data.get('quality_systems', {}).get('response', '')
        regulatory_data = agent_data.get('web_scraper', {}).get('response', '')
        audit_data = agent_data.get('internal_audit', {}).get('response', '')
        
        health_prompt = f"""
        Provide a comprehensive 360° health assessment for {company_name}:
        
        Data Sources:
        - Quality Systems: {quality_data[:1000]}...
        - Regulatory Status: {regulatory_data[:1000]}...
        - Audit History: {audit_data[:1000]}...
        
        Assessment Areas:
        1. 🔥 Critical Issues (Immediate attention required)
        2. ⚠️ Risk Areas (Monitor closely)
        3. ✅ Stable Areas (Well-controlled)
        4. 📈 Performance Trends
        5. 🎯 Recommendations
        
        Provide actionable insights and risk-based recommendations.
        """
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert quality systems analyst."},
                {"role": "user", "content": health_prompt}
            ],
            temperature=0.2,
            max_tokens=2500
        )
        
        return response.choices[0].message.content

    def _generate_audit_report(self, query: str, agent_data: Dict[str, Any], cross_agent_insights: Dict[str, Any] = None) -> str:
        """Generate structured audit report"""
        
        # Extract audit findings from query or context
        findings = self._extract_audit_findings(query)
        
        report_prompt = f"""
        Generate a comprehensive audit report following FORM-0046210 template:
        
        Audit Findings: {findings}
        
        Report Structure:
        1. Executive Summary
        2. Audit Scope and Objectives
        3. Audit Team and Methodology
        4. Summary of Audit
        5. Observations (Critical/Major/Minor)
        6. Conclusion
        7. Recommended Actions
        
        Ensure professional tone, clear findings classification, and actionable recommendations.
        """
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert audit report writer."},
                {"role": "user", "content": report_prompt}
            ],
            temperature=0.2,
            max_tokens=3000
        )
        
        return response.choices[0].message.content

    def _generate_trend_analysis(self, query: str, agent_data: Dict[str, Any], cross_agent_insights: Dict[str, Any] = None) -> str:
        """Generate trend analysis and insights"""
        
        quality_data = agent_data.get('quality_systems', {}).get('response', '')
        audit_data = agent_data.get('internal_audit', {}).get('response', '')
        
        trend_prompt = f"""
        Analyze trends and patterns in the audit data:
        
        Quality Systems Data: {quality_data[:1000]}...
        Audit History: {audit_data[:1000]}...
        
        Provide:
        1. 📊 Key Trends Identified
        2. 🔥 Critical Patterns
        3. ⚠️ Emerging Risks
        4. 📈 Performance Metrics
        5. 🎯 Strategic Recommendations
        
        Focus on actionable insights and risk mitigation strategies.
        """
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert trend analyst."},
                {"role": "user", "content": trend_prompt}
            ],
            temperature=0.2,
            max_tokens=2000
        )
        
        return response.choices[0].message.content

    def _generate_general_response(self, query: str, agent_data: Dict[str, Any], cross_agent_insights: Dict[str, Any] = None) -> str:
        """Generate general audit response"""
        
        # Combine all agent responses
        combined_data = ""
        for agent_name, data in agent_data.items():
            if 'response' in data:
                combined_data += f"\n{agent_name.upper()} DATA:\n{data['response'][:500]}...\n"
        
        general_prompt = f"""
        Provide a comprehensive audit intelligence response to: {query}
        
        Available Data: {combined_data}
        
        Provide a well-structured, professional response that addresses the query with actionable insights.
        """
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert audit intelligence analyst."},
                {"role": "user", "content": general_prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        return response.choices[0].message.content

    # Helper methods for data extraction
    def _extract_company_name(self, query: str) -> str:
        """Extract company name from query"""
        # Simple extraction - could be enhanced with NER
        companies = ['Hovione', 'Boehringer', 'Thermo Fisher', 'GRAM', 'Grand River']
        for company in companies:
            if company.lower() in query.lower():
                return company
        return "the company"

    def _determine_audit_type(self, query: str) -> str:
        """Determine audit type from query"""
        query_lower = query.lower()
        if any(word in query_lower for word in ['supplier', 'cdmo', 'vendor']):
            return "supplier"
        elif any(word in query_lower for word in ['internal', 'site']):
            return "internal"
        elif any(word in query_lower for word in ['regulatory', 'compliance']):
            return "regulatory"
        else:
            return "comprehensive"

    def _extract_time_period(self, query: str) -> str:
        """Extract time period from query"""
        if 'last year' in query.lower():
            return "last year"
        elif 'last 6 months' in query.lower():
            return "last 6 months"
        elif 'last quarter' in query.lower():
            return "last quarter"
        else:
            return "last audit"

    def _extract_agenda_content(self, query: str) -> str:
        """Extract agenda content from query"""
        # This would need to be enhanced for actual agenda parsing
        return "Audit agenda content to be analyzed"

    def _extract_audit_findings(self, query: str) -> str:
        """Extract audit findings from query"""
        # This would need to be enhanced for actual findings parsing
        return "Audit findings to be reported"

    # Additional specialized methods
    def create_observation_log(self, area: str, finding: str, risk_level: str, 
                             evidence: str, reference: str) -> Dict[str, Any]:
        """Create structured observation log entry"""
        return {
            "area": area,
            "finding": finding,
            "risk_level": risk_level,
            "evidence": evidence,
            "reference": reference,
            "timestamp": datetime.now().isoformat(),
            "priority_label": self.priority_labels.get(risk_level.lower(), "✅ Standard")
        }

    def generate_live_audit_support(self, meeting_context: str, current_topic: str) -> str:
        """Provide live audit meeting support"""
        support_prompt = f"""
        Provide live audit support for current topic: {current_topic}
        
        Meeting Context: {meeting_context}
        
        Provide:
        1. Relevant questions to ask
        2. Key areas to investigate
        3. Regulatory considerations
        4. Risk assessment for current topic
        
        Keep response concise and actionable for live meeting use.
        """
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a live audit meeting assistant."},
                {"role": "user", "content": support_prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        return response.choices[0].message.content 

    def _facilitate_agent_communication(self, agent_data: Dict[str, Any], query: str, intent: str) -> Dict[str, Any]:
        """Facilitate communication between agents for enhanced insights"""
        cross_agent_insights = {
            'quality_audit_correlation': {},
            'regulatory_compliance_gaps': {},
            'sop_quality_alignment': {},
            'trend_cross_validation': {},
            'risk_factor_identification': {}
        }
        
        # Quality Systems and Internal Audit correlation
        if 'quality_systems' in agent_data and 'internal_audit' in agent_data:
            quality_data = agent_data['quality_systems'].get('response', '')
            audit_data = agent_data['internal_audit'].get('response', '')
            
            if quality_data and audit_data:
                correlation_prompt = f"""
                Analyze the correlation between quality systems data and internal audit findings:
                
                Quality Systems Data: {quality_data[:1000]}...
                Internal Audit Data: {audit_data[:1000]}...
                
                Identify:
                1. Quality issues that align with audit findings
                2. Compliance gaps that need attention
                3. Risk factors that appear in both datasets
                4. Recommendations for coordinated action
                """
                
                try:
                    response = self.openai_client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "You are an expert in correlating quality and audit data."},
                            {"role": "user", "content": correlation_prompt}
                        ],
                        temperature=0.2,
                        max_tokens=1500
                    )
                    cross_agent_insights['quality_audit_correlation'] = response.choices[0].message.content
                except Exception as e:
                    cross_agent_insights['quality_audit_correlation'] = f"Error in correlation analysis: {str(e)}"
        
        # SOP and Regulatory compliance analysis
        if 'sop' in agent_data and 'web_scraper' in agent_data:
            sop_data = agent_data['sop'].get('response', '')
            regulatory_data = agent_data['web_scraper'].get('response', '')
            
            if sop_data and regulatory_data:
                compliance_prompt = f"""
                Analyze SOP compliance with current regulatory requirements:
                
                SOP Data: {sop_data[:1000]}...
                Regulatory Data: {regulatory_data[:1000]}...
                
                Identify:
                1. SOP gaps in regulatory compliance
                2. Outdated procedures that need updating
                3. Regulatory changes requiring SOP updates
                4. Compliance risk areas
                """
                
                try:
                    response = self.openai_client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "You are an expert in regulatory compliance analysis."},
                            {"role": "user", "content": compliance_prompt}
                        ],
                        temperature=0.2,
                        max_tokens=1500
                    )
                    cross_agent_insights['regulatory_compliance_gaps'] = response.choices[0].message.content
                except Exception as e:
                    cross_agent_insights['regulatory_compliance_gaps'] = f"Error in compliance analysis: {str(e)}"
        
        return cross_agent_insights

    def _compile_document_summary(self, document_citations: List[Dict]) -> Dict[str, Any]:
        """Compile comprehensive document citation summary"""
        if not document_citations:
            return {"total_documents": 0, "document_types": {}, "agents_used": []}
        
        summary = {
            "total_documents": len(document_citations),
            "document_types": {},
            "agents_used": [],
            "high_relevance_documents": [],
            "document_breakdown": {}
        }
        
        # Analyze document types and agents
        for citation in document_citations:
            # Document type analysis
            file_ext = citation.get('file_extension', '').lower()
            if file_ext:
                summary['document_types'][file_ext] = summary['document_types'].get(file_ext, 0) + 1
            
            # Agent analysis
            agent = citation.get('agent', 'unknown')
            if agent not in summary['agents_used']:
                summary['agents_used'].append(agent)
            
            # High relevance documents (score > 0.7)
            if citation.get('relevance_score', 0) > 0.7:
                summary['high_relevance_documents'].append({
                    'document_id': citation.get('document_id'),
                    'title': citation.get('title'),
                    'file_name': citation.get('file_name'),
                    'agent': agent,
                    'relevance_score': citation.get('relevance_score', 0)
                })
            
            # Document breakdown by agent
            if agent not in summary['document_breakdown']:
                summary['document_breakdown'][agent] = []
            summary['document_breakdown'][agent].append({
                'document_id': citation.get('document_id'),
                'title': citation.get('title'),
                'file_name': citation.get('file_name'),
                'relevance_score': citation.get('relevance_score', 0)
            })
        
        return summary

    def _generate_quality_analysis(self, query: str, agent_data: Dict[str, Any], cross_agent_insights: Dict[str, Any] = None) -> str:
        """Generate comprehensive quality analysis"""
        quality_data = agent_data.get('quality_systems', {}).get('response', '')
        audit_data = agent_data.get('internal_audit', {}).get('response', '')
        
        analysis_prompt = f"""
        Provide a comprehensive quality analysis based on the following data:
        
        Quality Systems Data: {quality_data[:1500]}...
        Internal Audit Data: {audit_data[:1500]}...
        
        Cross-Agent Insights: {cross_agent_insights.get('quality_audit_correlation', '') if cross_agent_insights else ''}
        
        Provide detailed analysis covering:
        1. Quality system effectiveness
        2. Deviation trends and patterns
        3. CAPA effectiveness and closure rates
        4. Risk areas and compliance gaps
        5. Recommendations for improvement
        6. Regulatory compliance status
        
        Ensure comprehensive coverage with specific examples and actionable recommendations.
        """
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert quality systems analyst with deep GMP knowledge."},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.2,
            max_tokens=2500
        )
        
        return response.choices[0].message.content

    def _generate_sop_review(self, query: str, agent_data: Dict[str, Any], cross_agent_insights: Dict[str, Any] = None) -> str:
        """Generate comprehensive SOP review"""
        sop_data = agent_data.get('sop', {}).get('response', '')
        regulatory_data = agent_data.get('web_scraper', {}).get('response', '')
        
        review_prompt = f"""
        Conduct a comprehensive SOP review and analysis:
        
        SOP Data: {sop_data[:1500]}...
        Regulatory Data: {regulatory_data[:1500]}...
        
        Cross-Agent Insights: {cross_agent_insights.get('regulatory_compliance_gaps', '') if cross_agent_insights else ''}
        
        Provide detailed analysis covering:
        1. SOP completeness and coverage
        2. Regulatory compliance status
        3. Procedure effectiveness and clarity
        4. Training and implementation status
        5. Gap analysis and recommendations
        6. Update requirements and priorities
        
        Ensure comprehensive coverage with specific examples and actionable recommendations.
        """
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert SOP analyst with deep regulatory knowledge."},
                {"role": "user", "content": review_prompt}
            ],
            temperature=0.2,
            max_tokens=2500
        )
        
        return response.choices[0].message.content

    def _generate_regulatory_research(self, query: str, agent_data: Dict[str, Any], cross_agent_insights: Dict[str, Any] = None) -> str:
        """Generate comprehensive regulatory research analysis"""
        regulatory_data = agent_data.get('web_scraper', {}).get('response', '')
        sop_data = agent_data.get('sop', {}).get('response', '')
        
        research_prompt = f"""
        Conduct comprehensive regulatory research and analysis:
        
        Regulatory Data: {regulatory_data[:1500]}...
        SOP Data: {sop_data[:1500]}...
        
        Cross-Agent Insights: {cross_agent_insights.get('regulatory_compliance_gaps', '') if cross_agent_insights else ''}
        
        Provide detailed analysis covering:
        1. Current regulatory landscape
        2. Recent regulatory changes and updates
        3. Compliance requirements and deadlines
        4. Impact on existing procedures
        5. Risk assessment and mitigation strategies
        6. Implementation recommendations
        
        Ensure comprehensive coverage with specific regulatory references and actionable recommendations.
        """
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert regulatory affairs specialist."},
                {"role": "user", "content": research_prompt}
            ],
            temperature=0.2,
            max_tokens=2500
        )
        
        return response.choices[0].message.content

    def _generate_conference_analysis(self, query: str, agent_data: Dict[str, Any], cross_agent_insights: Dict[str, Any] = None) -> str:
        """Generate comprehensive conference and industry analysis"""
        conference_data = agent_data.get('external_conference', {}).get('response', '')
        quality_data = agent_data.get('quality_systems', {}).get('response', '')
        
        analysis_prompt = f"""
        Conduct comprehensive conference and industry analysis:
        
        Conference Data: {conference_data[:1500]}...
        Quality Systems Data: {quality_data[:1500]}...
        
        Provide detailed analysis covering:
        1. Industry trends and developments
        2. Best practices and benchmarking
        3. Emerging technologies and methodologies
        4. Regulatory developments and guidance
        5. Networking and collaboration opportunities
        6. Strategic recommendations for improvement
        
        Ensure comprehensive coverage with specific examples and actionable recommendations.
        """
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert industry analyst with deep pharmaceutical knowledge."},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.2,
            max_tokens=2500
        )
        
        return response.choices[0].message.content 