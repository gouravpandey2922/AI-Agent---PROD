from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from .web_scraper_agent import WebScraperAgent
from .internal_audit_agent import InternalAuditAgent
from .external_conference_agent import ExternalConferenceAgent
from .quality_systems_agent import QualitySystemsAgent
from .sop_agent import SOPAgent

class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__("orchestrator")
        # Initialize all other agents
        self.agents = {
            "web_scraper": WebScraperAgent(),
            "internal_audit": InternalAuditAgent(),
            "external_conference": ExternalConferenceAgent(),
            "quality_systems": QualitySystemsAgent(),
            "sop": SOPAgent()
        }
        
    def get_system_prompt(self) -> str:
        return """You are the Orchestrator Agent for an Audit Intelligence Platform. Your role is to:

1. Analyze user queries and determine which specialized agents need to be involved
2. Coordinate between agents to gather comprehensive information
3. Synthesize responses from multiple agents into coherent, actionable insights
4. Determine the appropriate output format (report, checklist, insights, or general answer)

Available Agents:
- Web Scraper Agent: Due diligence reports, FDA warning letters, company reviews
- Internal Audit Agent: Audit procedures, checklists, compliance guidelines
- External Conference Agent: Conference data, industry events, engagement information
- Quality Systems Agent: Supplier notifications, quality events, SNC data
- SOP Agent: Standard operating procedures, audit protocols

You can route queries to multiple agents and combine their responses. Always provide source references and file paths when possible."""

    def get_capabilities(self) -> List[str]:
        return [
            "Query routing and orchestration",
            "Multi-agent coordination", 
            "Response synthesis",
            "Output format determination",
            "Cross-agent insights generation"
        ]

    def process_query(self, query: str, context: str = "", intent: str = None) -> Dict[str, Any]:
        # First, determine which agents to involve
        agent_selection = self._determine_agent_involvement(query)
        
        # Use provided intent or determine output type
        output_type = intent if intent else self._determine_output_type(query)
        
        # Collect responses from relevant agents
        agent_responses = {}
        all_sources = []
        
        for agent_name, should_involve in agent_selection.items():
            if should_involve:
                agent = self.agents[agent_name]
                response = agent.process_query(query, context)
                agent_responses[agent_name] = response
                
                # Extract sources from this agent's response
                if 'sources' in response:
                    for source in response['sources']:
                        source['agent'] = agent_name
                        all_sources.append(source)
        
        # Synthesize final response
        final_response = self._synthesize_responses(query, agent_responses, output_type)
        
        return {
            "query": query,
            "response": final_response,
            "involved_agents": [name for name, involved in agent_selection.items() if involved],
            "output_type": output_type,
            "agent_responses": agent_responses,
            "sources": all_sources
        }

    def _determine_agent_involvement(self, query: str) -> Dict[str, bool]:
        """Determine which agents should be involved based on the query"""
        prompt = f"""
        Analyze this query and determine which agents should be involved:
        
        Query: {query}
        
        Available agents:
        - web_scraper: Due diligence reports, FDA warnings, company reviews
        - internal_audit: Audit procedures, checklists, compliance
        - external_conference: Conference data, industry events
        - quality_systems: Supplier notifications, quality events, SNC data
        - sop: Standard operating procedures, audit protocols
        
        Return JSON with boolean values for each agent:
        {{
            "web_scraper": true/false,
            "internal_audit": true/false,
            "external_conference": true/false,
            "quality_systems": true/false,
            "sop": true/false
        }}
        
        Consider the query content and keywords to determine relevance.
        """
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a query routing specialist. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=200
        )
        
        try:
            import json
            result = json.loads(response.choices[0].message.content)
            return result
        except:
            # Default to involving all agents if parsing fails
            return {
                "web_scraper": True,
                "internal_audit": True,
                "external_conference": True,
                "quality_systems": True,
                "sop": True
            }

    def _determine_output_type(self, query: str) -> str:
        """Determine the appropriate output type based on the query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['checklist', 'list', 'steps', 'procedures']):
            return 'checklist'
        elif any(word in query_lower for word in ['report', 'analysis', 'summary', 'overview']):
            return 'report'
        elif any(word in query_lower for word in ['insights', 'trends', 'patterns']):
            return 'insights'
        else:
            return 'general'

    def _synthesize_responses(self, query: str, agent_responses: Dict[str, Any], output_type: str) -> str:
        """Synthesize responses from multiple agents into a coherent response"""
        
        # Collect all agent responses
        responses = []
        for agent_name, response in agent_responses.items():
            if 'response' in response:
                responses.append(f"**{agent_name.replace('_', ' ').title()} Agent:**\n{response['response']}")
        
        if not responses:
            return "I couldn't find relevant information for your query. Please try rephrasing or ask about a different topic."
        
        # Create synthesis prompt
        separator = "\n\n"
        synthesis_prompt = f"""
        Synthesize the following agent responses into a coherent answer for the user's query.
        
        User Query: {query}
        Output Type: {output_type}
        
        Agent Responses:
        {separator.join(responses)}
        
        Instructions:
        1. Create a comprehensive, well-structured response
        2. If this is a checklist request, format as a numbered or bulleted list
        3. If this is a report request, provide a detailed analysis with sections
        4. If this is an insights request, focus on patterns and trends
        5. Always reference specific sources when possible
        6. Make the response actionable and informative
        
        Response:
        """
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert audit intelligence analyst. Provide clear, actionable insights."},
                {"role": "user", "content": synthesis_prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        return response.choices[0].message.content

    def _extract_sources(self, agent_responses: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract and format sources from agent responses"""
        all_sources = []
        
        for agent_name, response in agent_responses.items():
            if 'sources' in response:
                for source in response['sources']:
                    # Add agent information to source
                    source['agent'] = agent_name
                    all_sources.append(source)
        
        # Sort by relevance score if available
        all_sources.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return all_sources

    def get_cross_agent_insights(self, company_name: str) -> Dict[str, Any]:
        """Get insights about a company across all agents"""
        insights = {}
        
        # Get insights from each agent
        for agent_name, agent in self.agents.items():
            try:
                if hasattr(agent, 'get_company_insights'):
                    agent_insights = agent.get_company_insights(company_name)
                    insights[agent_name] = agent_insights
            except Exception as e:
                insights[agent_name] = {"error": str(e)}
        
        return insights

    def create_audit_plan(self, company_name: str, audit_type: str = "comprehensive") -> Dict[str, Any]:
        """Create a comprehensive audit plan for a company"""
        
        # Get relevant information from all agents
        audit_info = {}
        
        # Get audit procedures from internal audit agent
        if "internal_audit" in self.agents:
            audit_info["procedures"] = self.agents["internal_audit"].get_audit_procedures()
        
        # Get company-specific information from quality systems agent
        if "quality_systems" in self.agents:
            audit_info["quality_events"] = self.agents["quality_systems"].get_company_quality_timeline(company_name)
        
        # Get SOP information from SOP agent
        if "sop" in self.agents:
            audit_info["sop_references"] = self.agents["sop"].get_relevant_sops(audit_type)
        
        # Create audit plan
        plan_prompt = f"""
        Create a comprehensive audit plan for {company_name} based on the following information:
        
        Audit Type: {audit_type}
        Available Information: {audit_info}
        
        The plan should include:
        1. Pre-audit preparation
        2. Audit scope and objectives
        3. Key areas to focus on
        4. Required documentation
        5. Risk assessment
        6. Timeline and milestones
        
        Format as a structured document with clear sections.
        """
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert audit planner with deep knowledge of pharmaceutical compliance."},
                {"role": "user", "content": plan_prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        return {
            "company": company_name,
            "audit_type": audit_type,
            "plan": response.choices[0].message.content,
            "supporting_data": audit_info
        } 