import streamlit as st
import pandas as pd
from typing import Dict, List, Any
import json
from datetime import datetime
import time

# Import our custom modules
from agents.orchestrator_agent import OrchestratorAgent
from database.vector_db import VectorDatabaseManager
from database.graph_db import GraphDatabaseManager
from utils.data_processor import DataProcessor
from config import OUTPUT_TYPES

class AuditIntelligenceApp:
    def __init__(self):
        # Initialize components only when needed for better performance
        self._orchestrator = None
        self._vector_db = None
        self._graph_db = None
        self._data_processor = None
        
    @property
    def orchestrator(self):
        if self._orchestrator is None:
            self._orchestrator = OrchestratorAgent()
        return self._orchestrator
    
    @property
    def vector_db(self):
        if self._vector_db is None:
            self._vector_db = VectorDatabaseManager()
        return self._vector_db
    
    @property
    def graph_db(self):
        if self._graph_db is None:
            self._graph_db = GraphDatabaseManager()
        return self._graph_db
    
    @property
    def data_processor(self):
        if self._data_processor is None:
            self._data_processor = DataProcessor()
        return self._data_processor
        
    def run(self):
        st.set_page_config(
            page_title="Takeda AI Audit Intelligence",
            page_icon="📋",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS for better performance and styling
        st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: bold;
        }
        .agent-status {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px;
            border-radius: 5px;
            margin: 5px 0;
            background-color: #f8f9fa;
        }
        .agent-loading {
            color: #007bff;
        }
        .agent-success {
            color: #28a745;
        }
        .agent-error {
            color: #dc3545;
        }
        .source-item {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            margin: 5px 0;
            border-left: 4px solid #007bff;
        }
        .response-container {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .file-upload-area {
            border: 2px dashed #ccc;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            background-color: #fafafa;
            margin: 20px 0;
        }
        .stButton > button {
            width: 100%;
            background-color: #007bff;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
        }
        .stButton > button:hover {
            background-color: #0056b3;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Header
        st.markdown('<h1 class="main-header">Takeda AI Audit Intelligence</h1>', unsafe_allow_html=True)
        
        # Sidebar
        self._create_sidebar()
        
        # Main content
        self._create_main_content()
        
    def _create_sidebar(self):
        """Create the simplified sidebar"""
        st.sidebar.title("AI Agents")
        
        # Agent status display
        st.sidebar.markdown("### Agent Status")
        
        # Initialize agent status in session state
        if 'agent_status' not in st.session_state:
            st.session_state.agent_status = {
                'web_scraper': 'idle',
                'internal_audit': 'idle', 
                'external_conference': 'idle',
                'quality_systems': 'idle',
                'sop': 'idle'
            }
        
        # Display agent status with icons
        for agent_name, status in st.session_state.agent_status.items():
            display_name = agent_name.replace('_', ' ').title()
            
            if status == 'idle':
                st.sidebar.markdown(f"⭕ {display_name} Agent")
            elif status == 'running':
                st.sidebar.markdown(f"🔄 {display_name} Agent")
            elif status == 'completed':
                st.sidebar.markdown(f"✅ {display_name} Agent")
            elif status == 'error':
                st.sidebar.markdown(f"❌ {display_name} Agent")
        
        st.sidebar.markdown("---")
        
        # Document upload section (frontend only)
        st.sidebar.markdown("### 📁 Document Upload")
        st.sidebar.markdown("*(Coming Soon)*")
        
        uploaded_files = st.sidebar.file_uploader(
            "Upload documents for analysis",
            type=['pdf', 'csv', 'docx', 'txt'],
            accept_multiple_files=True,
            disabled=True
        )
        
        if uploaded_files:
            st.sidebar.info("Document processing will be available in a future update.")
                    
    def _create_main_content(self):
        """Create the main content area"""
        
        # Query input
        st.markdown("### Ask Your Question")
        query = st.text_area(
            "Enter your audit-related question:",
            placeholder="e.g., Create an audit checklist for Hovione, or What are the quality issues for Boehringer Ingelheim?",
            height=100
        )
        
        # Single submit button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit_button = st.button("Submit Query", type="primary")
        
        # Process query
        if submit_button and query.strip():
            self._process_query(query.strip())
    
    def _process_query(self, query: str):
        """Process the user query with intelligent routing"""
        
        # Reset agent status
        for agent_name in st.session_state.agent_status:
            st.session_state.agent_status[agent_name] = 'idle'
        
        # Determine intent and route
        intent = self._determine_intent(query)
        
        # Create progress container
        progress_container = st.container()
        
        with progress_container:
            st.markdown("### 🤖 AI Analysis in Progress")
            
            # Show which agents will be used
            agents_to_use = self._get_relevant_agents(query, intent)
            
            # Create columns for agent status
            cols = st.columns(len(agents_to_use))
            
            # Initialize agent status
            for i, agent_name in enumerate(agents_to_use):
                with cols[i]:
                    st.markdown(f"**{agent_name.replace('_', ' ').title()}**")
                    status_placeholder = st.empty()
                    st.session_state.agent_status[agent_name] = 'running'
                    status_placeholder.markdown("🔄 Running...")
        
        # Process with orchestrator
        try:
            # Get response from orchestrator
            response = self.orchestrator.process_query(query, intent=intent)
            
            # Update agent status to completed
            for agent_name in agents_to_use:
                st.session_state.agent_status[agent_name] = 'completed'
            
            # Display response
            self._display_response(response, query)
            
        except Exception as e:
            # Update agent status to error
            for agent_name in agents_to_use:
                st.session_state.agent_status[agent_name] = 'error'
            
            st.error(f"An error occurred while processing your query: {str(e)}")
    
    def _determine_intent(self, query: str) -> str:
        """Determine the user's intent from the query"""
        query_lower = query.lower()
        
        # Check for checklist intent
        if any(word in query_lower for word in ['checklist', 'list', 'steps', 'procedures']):
            return 'checklist'
        
        # Check for report intent
        if any(word in query_lower for word in ['report', 'analysis', 'summary', 'overview']):
            return 'report'
        
        # Check for insights intent
        if any(word in query_lower for word in ['insights', 'trends', 'patterns', 'analysis']):
            return 'insights'
        
        # Default to general
        return 'general'
    
    def _get_relevant_agents(self, query: str, intent: str) -> List[str]:
        """Determine which agents are relevant for the query"""
        query_lower = query.lower()
        relevant_agents = []
        
        # Always include orchestrator
        relevant_agents.append('orchestrator')
        
        # Check for company-specific queries
        if any(word in query_lower for word in ['hovione', 'boehringer', 'thermo fisher', 'company']):
            relevant_agents.extend(['quality_systems', 'external_conference'])
        
        # Check for audit-related queries
        if any(word in query_lower for word in ['audit', 'compliance', 'checklist']):
            relevant_agents.extend(['internal_audit', 'sop'])
        
        # Check for quality-related queries
        if any(word in query_lower for word in ['quality', 'snc', 'deviation']):
            relevant_agents.append('quality_systems')
        
        # Check for conference-related queries
        if any(word in query_lower for word in ['conference', 'event', 'meeting']):
            relevant_agents.append('external_conference')
        
        # Check for web scraping related queries
        if any(word in query_lower for word in ['fda', 'warning', 'due diligence']):
            relevant_agents.append('web_scraper')
        
        # If no specific agents identified, use all
        if len(relevant_agents) <= 1:
            relevant_agents = ['web_scraper', 'internal_audit', 'external_conference', 'quality_systems', 'sop']
        
        return relevant_agents
    
    def _display_response(self, response: Dict, query: str):
        """Display the response with proper formatting and source attribution"""
        
        st.markdown("---")
        st.markdown("### 📋 Response")
        
        # Create response container
        with st.container():
            st.markdown('<div class="response-container">', unsafe_allow_html=True)
            
            # Display main response
            if 'response' in response:
                st.markdown(response['response'])
            
            # Display sources with better formatting
            if 'sources' in response and response['sources']:
                st.markdown("---")
                st.markdown("### 📚 Sources")
                
                for i, source in enumerate(response['sources'], 1):
                    with st.expander(f"Source {i}: {source.get('title', 'Unknown Document')}"):
                        st.markdown(f"**Document:** {source.get('title', 'Unknown')}")
                        st.markdown(f"**Agent:** {source.get('agent', 'Unknown')}")
                        st.markdown(f"**Relevance:** {source.get('score', 0):.3f}")
                        
                        if 'content' in source:
                            st.markdown("**Content:**")
                            st.markdown(f"*{source['content'][:300]}...*")
                        
                        if 'metadata' in source:
                            st.markdown("**Metadata:**")
                            for key, value in source['metadata'].items():
                                st.markdown(f"- **{key}:** {value}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Display processing summary
        st.markdown("---")
        st.markdown("### ⚡ Processing Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Query Type", self._determine_intent(query).title())
        
        with col2:
            st.metric("Agents Used", len([s for s in st.session_state.agent_status.values() if s == 'completed']))
        
        with col3:
            st.metric("Sources Found", len(response.get('sources', [])))

def main():
    app = AuditIntelligenceApp()
    app.run()

if __name__ == "__main__":
    main() 