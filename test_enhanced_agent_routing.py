#!/usr/bin/env python3
"""
Test script for Enhanced Agent Routing and Document Citation System
Demonstrates advanced agent routing, cross-agent communication, and document citation capabilities
"""

import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.smart_orchestrator_agent import SmartOrchestratorAgent

def test_advanced_agent_routing():
    """Test advanced agent routing with different query types"""
    print("Advanced Agent Routing Test")
    print("=" * 50)
    
    # Initialize the Smart Orchestrator Agent
    orchestrator = SmartOrchestratorAgent()
    
    # Test queries with different intents and expected agent combinations
    test_cases = [
        {
            "query": "Generate a comprehensive audit checklist for Hovione sterile manufacturing facility",
            "expected_intent": "audit_checklist",
            "expected_agents": ["internal_audit", "sop", "quality_systems"],
            "description": "Sterile manufacturing audit checklist"
        },
        {
            "query": "What are the recent quality deviations and CAPAs for Boehringer Ingelheim?",
            "expected_intent": "quality_analysis",
            "expected_agents": ["quality_systems", "internal_audit"],
            "description": "Quality systems analysis"
        },
        {
            "query": "Review SOP compliance with current FDA regulations and EU GMP guidelines",
            "expected_intent": "sop_review",
            "expected_agents": ["sop", "web_scraper"],
            "description": "SOP regulatory compliance review"
        },
        {
            "query": "Provide 360-degree health status assessment for Thermo Fisher CDMO",
            "expected_intent": "health_assessment",
            "expected_agents": ["quality_systems", "web_scraper", "external_conference"],
            "description": "Comprehensive health assessment"
        },
        {
            "query": "What changed in our quality systems since the last audit?",
            "expected_intent": "delta_analysis",
            "expected_agents": ["quality_systems", "sop", "external_conference"],
            "description": "Delta analysis of changes"
        },
        {
            "query": "Research recent FDA warning letters and regulatory updates",
            "expected_intent": "regulatory_research",
            "expected_agents": ["web_scraper", "sop"],
            "description": "Regulatory research"
        },
        {
            "query": "Analyze industry trends from recent conferences and external engagements",
            "expected_intent": "conference_analysis",
            "expected_agents": ["external_conference", "quality_systems"],
            "description": "Conference and industry analysis"
        },
        {
            "query": "Create a detailed audit report with findings and recommendations",
            "expected_intent": "audit_report",
            "expected_agents": ["internal_audit", "quality_systems", "sop"],
            "description": "Audit report generation"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['description']}")
        print(f"Query: {test_case['query']}")
        
        try:
            # Process the query
            response = orchestrator.process_query(test_case['query'])
            
            # Analyze results
            actual_intent = response.get('intent', 'unknown')
            actual_agents = response.get('involved_agents', [])
            agent_communications = response.get('agent_communications', [])
            document_citations = response.get('document_citations', [])
            document_summary = response.get('document_summary', {})
            
            # Display results
            print(f"✅ Intent Detected: {actual_intent}")
            print(f"✅ Agents Involved: {actual_agents}")
            print(f"✅ Agent Communications: {len(agent_communications)}")
            print(f"✅ Document Citations: {len(document_citations)}")
            
            # Check intent accuracy
            if actual_intent == test_case['expected_intent']:
                print("✅ Intent Detection: PASSED")
            else:
                print(f"❌ Intent Detection: FAILED (Expected: {test_case['expected_intent']}, Got: {actual_intent})")
            
            # Check agent selection
            expected_agents_set = set(test_case['expected_agents'])
            actual_agents_set = set(actual_agents)
            
            if expected_agents_set.issubset(actual_agents_set):
                print("✅ Agent Selection: PASSED")
            else:
                missing_agents = expected_agents_set - actual_agents_set
                extra_agents = actual_agents_set - expected_agents_set
                print(f"❌ Agent Selection: PARTIAL (Missing: {missing_agents}, Extra: {extra_agents})")
            
            # Display agent communication details
            if agent_communications:
                print("   Agent Communication Details:")
                for comm in agent_communications:
                    status = "✅" if comm.get('status') == 'completed' else "❌"
                    docs_found = comm.get('documents_found', 0)
                    score = comm.get('relevance_score', 0)
                    print(f"   {status} {comm['agent']}: {docs_found} docs (score: {score:.2f})")
            
            # Display document summary
            if document_summary:
                print(f"   Document Summary: {document_summary.get('total_documents', 0)} total documents")
                print(f"   Document Types: {list(document_summary.get('document_types', {}).keys())}")
                print(f"   Agents Used: {document_summary.get('agents_used', [])}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 50)

def test_document_citation_enhancement():
    """Test enhanced document citation capabilities"""
    print("\nDocument Citation Enhancement Test")
    print("=" * 50)
    
    orchestrator = SmartOrchestratorAgent()
    
    # Test queries that should generate document citations
    citation_test_queries = [
        "What SOPs are available for sterile manufacturing processes?",
        "Show me quality deviation reports for the last quarter",
        "What FDA guidance documents are relevant to our operations?",
        "Review audit procedures and compliance requirements",
        "Analyze supplier quality data and performance metrics"
    ]
    
    for i, query in enumerate(citation_test_queries, 1):
        print(f"\nCitation Test {i}: {query}")
        
        try:
            response = orchestrator.process_query(query)
            
            # Analyze document citations
            document_citations = response.get('document_citations', [])
            document_summary = response.get('document_summary', {})
            sources = response.get('sources', [])
            
            print(f"✅ Document Citations: {len(document_citations)}")
            print(f"✅ Total Sources: {len(sources)}")
            print(f"✅ Document Summary: {document_summary.get('total_documents', 0)} documents")
            
            # Display high relevance documents
            high_relevance_docs = document_summary.get('high_relevance_documents', [])
            if high_relevance_docs:
                print("   High Relevance Documents:")
                for doc in high_relevance_docs[:3]:  # Show top 3
                    print(f"   - {doc.get('document_id')}: {doc.get('title')} (Score: {doc.get('relevance_score', 0):.3f})")
            
            # Display document types
            doc_types = document_summary.get('document_types', {})
            if doc_types:
                print(f"   Document Types: {list(doc_types.keys())}")
            
            # Display agent breakdown
            agent_breakdown = document_summary.get('document_breakdown', {})
            if agent_breakdown:
                print("   Documents by Agent:")
                for agent, docs in agent_breakdown.items():
                    print(f"   - {agent}: {len(docs)} documents")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 30)

def test_cross_agent_communication():
    """Test cross-agent communication and insights generation"""
    print("\nCross-Agent Communication Test")
    print("=" * 50)
    
    orchestrator = SmartOrchestratorAgent()
    
    # Test queries that should trigger cross-agent communication
    communication_test_queries = [
        "Analyze quality system effectiveness and audit findings correlation",
        "Review SOP compliance with current regulatory requirements",
        "Assess supplier quality performance and regulatory status",
        "Evaluate internal audit results against quality metrics"
    ]
    
    for i, query in enumerate(communication_test_queries, 1):
        print(f"\nCommunication Test {i}: {query}")
        
        try:
            response = orchestrator.process_query(query)
            
            # Analyze cross-agent insights
            cross_agent_insights = response.get('cross_agent_insights', {})
            agent_communications = response.get('agent_communications', [])
            
            print(f"✅ Agent Communications: {len(agent_communications)}")
            print(f"✅ Cross-Agent Insights: {len([k for k, v in cross_agent_insights.items() if v])}")
            
            # Display cross-agent insights
            if cross_agent_insights:
                print("   Cross-Agent Insights Generated:")
                for insight_type, insight_content in cross_agent_insights.items():
                    if insight_content:
                        print(f"   - {insight_type}: {len(insight_content)} characters")
            
            # Display agent communication details
            if agent_communications:
                print("   Agent Communication Status:")
                for comm in agent_communications:
                    status = "✅" if comm.get('status') == 'completed' else "❌"
                    docs_found = comm.get('documents_found', 0)
                    print(f"   {status} {comm['agent']}: {docs_found} documents")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 30)

def test_comprehensive_response_generation():
    """Test comprehensive response generation with all enhancements"""
    print("\nComprehensive Response Generation Test")
    print("=" * 50)
    
    orchestrator = SmartOrchestratorAgent()
    
    # Test a complex query that should utilize multiple agents and generate comprehensive response
    complex_query = """
    Provide a comprehensive analysis of Hovione's quality systems, including:
    1. Recent quality deviations and CAPAs
    2. SOP compliance with current FDA and EU regulations
    3. Audit findings and recommendations
    4. Industry benchmarking from recent conferences
    5. Risk assessment and mitigation strategies
    """
    
    print(f"Complex Query: {complex_query.strip()}")
    
    try:
        response = orchestrator.process_query(complex_query)
        
        # Analyze comprehensive response
        intent = response.get('intent', 'unknown')
        involved_agents = response.get('involved_agents', [])
        agent_communications = response.get('agent_communications', [])
        document_citations = response.get('document_citations', [])
        document_summary = response.get('document_summary', {})
        cross_agent_insights = response.get('cross_agent_insights', {})
        response_text = response.get('response', '')
        
        print(f"✅ Intent: {intent}")
        print(f"✅ Agents Involved: {involved_agents}")
        print(f"✅ Agent Communications: {len(agent_communications)}")
        print(f"✅ Document Citations: {len(document_citations)}")
        print(f"✅ Total Documents: {document_summary.get('total_documents', 0)}")
        print(f"✅ Cross-Agent Insights: {len([k for k, v in cross_agent_insights.items() if v])}")
        print(f"✅ Response Length: {len(response_text)} characters")
        
        # Display response preview
        if response_text:
            print(f"✅ Response Preview: {response_text[:200]}...")
        
        # Display document breakdown
        if document_summary:
            agent_breakdown = document_summary.get('document_breakdown', {})
            print("   Document Breakdown by Agent:")
            for agent, docs in agent_breakdown.items():
                print(f"   - {agent}: {len(docs)} documents")
        
        # Display cross-agent insights
        if cross_agent_insights:
            print("   Cross-Agent Insights:")
            for insight_type, insight_content in cross_agent_insights.items():
                if insight_content:
                    print(f"   - {insight_type}: Available")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Run all enhanced agent routing tests"""
    print("Enhanced Agent Routing and Document Citation System Test")
    print("=" * 70)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run all tests
    test_advanced_agent_routing()
    test_document_citation_enhancement()
    test_cross_agent_communication()
    test_comprehensive_response_generation()
    
    print("\n" + "=" * 70)
    print("Enhanced Agent Routing Test Completed!")
    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 