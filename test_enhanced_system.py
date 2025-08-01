#!/usr/bin/env python3
"""
Test script for the Enhanced Smart Audit Orchestrator Agent System
Demonstrates key capabilities and functionality
"""

import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.smart_orchestrator_agent import SmartOrchestratorAgent
from utils.audit_logger import AuditLogger, RiskLevel, ObservationType
from utils.checklist_generator import AuditChecklistGenerator

def test_smart_orchestrator():
    """Test the Smart Orchestrator Agent"""
    print("🧠 Testing Smart Orchestrator Agent...")
    
    # Initialize the agent
    orchestrator = SmartOrchestratorAgent()
    
    # Test queries
    test_queries = [
        "Generate a checklist for Hovione sterile manufacturing audit",
        "Provide 360° health status for Boehringer Ingelheim",
        "What changed since our last audit?",
        "Create a report from these audit notes",
        "Show relevant new regulations since last audit"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test Query {i}: {query}")
        try:
            response = orchestrator.process_query(query)
            print(f"✅ Response generated successfully")
            print(f"   Intent: {response.get('intent', 'unknown')}")
            print(f"   Involved Agents: {response.get('involved_agents', [])}")
            print(f"   Response Length: {len(response.get('response', ''))} characters")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def test_checklist_generator():
    """Test the Checklist Generator"""
    print("\n📋 Testing Checklist Generator...")
    
    # Initialize the generator
    generator = AuditChecklistGenerator()
    
    # Test checklist generation
    test_cases = [
        {
            "company": "Hovione",
            "audit_type": "supplier",
            "product_modality": "sterile_manufacturing",
            "risk_factors": ["sterility concerns", "data integrity issues"]
        },
        {
            "company": "Boehringer Ingelheim",
            "audit_type": "internal",
            "product_modality": "oral_solid",
            "risk_factors": ["validation gaps", "cross-contamination"]
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {case['company']} - {case['audit_type']}")
        try:
            checklist = generator.generate_checklist(
                audit_type=case['audit_type'],
                company_name=case['company'],
                product_modality=case['product_modality'],
                risk_factors=case['risk_factors']
            )
            print(f"✅ Checklist generated successfully")
            print(f"   Total Items: {checklist['total_items']}")
            print(f"   Critical: {checklist['priority_breakdown']['Critical']}")
            print(f"   Standard: {checklist['priority_breakdown']['Standard']}")
            print(f"   Watchlist: {checklist['priority_breakdown']['Watchlist']}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def test_audit_logger():
    """Test the Audit Logger"""
    print("\n📝 Testing Audit Logger...")
    
    # Initialize the logger
    logger = AuditLogger()
    
    # Test observation creation
    test_observations = [
        {
            "area": "Warehouse",
            "finding": "Missing temperature records for Freezer #2 during March 3-10, 2025",
            "risk_level": RiskLevel.MAJOR,
            "evidence": "No entries present in the freezer log for that date range",
            "reference": "21 CFR 211.68",
            "observation_type": ObservationType.ON_SITE_OBSERVATION,
            "auditor": "John Smith",
            "company": "Hovione",
            "audit_type": "supplier",
            "corrective_action": "Implement automated temperature monitoring system"
        },
        {
            "area": "Document Control",
            "finding": "Outdated version of SOP QA-008 found in use at packaging line",
            "risk_level": RiskLevel.MINOR,
            "evidence": "Line staff had Revision 5 in their binder, while Revision 6 is current",
            "reference": "Internal SOP Management Policy",
            "observation_type": ObservationType.DOCUMENT_REVIEW,
            "auditor": "Jane Doe",
            "company": "Boehringer Ingelheim",
            "audit_type": "internal",
            "corrective_action": "Immediate removal of obsolete SOPs and retraining"
        }
    ]
    
    for i, obs_data in enumerate(test_observations, 1):
        print(f"\n📝 Test Observation {i}: {obs_data['area']}")
        try:
            observation = logger.create_observation(**obs_data)
            print(f"✅ Observation logged successfully")
            print(f"   ID: {observation.id}")
            print(f"   Risk Level: {observation.risk_level.value}")
            print(f"   Priority Label: {observation.priority_label}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    # Test summary generation
    try:
        summary = logger.generate_observation_summary()
        print(f"\n📊 Summary Statistics:")
        print(f"   Total Observations: {summary['total_observations']}")
        print(f"   Critical: {summary['by_risk_level']['Critical']}")
        print(f"   Major: {summary['by_risk_level']['Major']}")
        print(f"   Minor: {summary['by_risk_level']['Minor']}")
    except Exception as e:
        print(f"❌ Error generating summary: {str(e)}")

def test_live_audit_support():
    """Test live audit support functionality"""
    print("\n🎯 Testing Live Audit Support...")
    
    # Initialize the orchestrator
    orchestrator = SmartOrchestratorAgent()
    
    # Test live audit support
    meeting_context = "Currently discussing environmental monitoring procedures during sterile manufacturing audit"
    current_topic = "Environmental monitoring alert/action limits"
    
    try:
        support_response = orchestrator.generate_live_audit_support(meeting_context, current_topic)
        print(f"✅ Live audit support generated")
        print(f"   Response Length: {len(support_response)} characters")
        print(f"   Sample: {support_response[:200]}...")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_observation_logging():
    """Test structured observation logging"""
    print("\n📋 Testing Structured Observation Logging...")
    
    # Initialize the logger
    logger = AuditLogger()
    
    # Test creating observation with all fields
    try:
        observation = logger.create_observation(
            area="QC Laboratory",
            finding="Analytical method validation not completed for new stability testing method",
            risk_level=RiskLevel.CRITICAL,
            evidence="Method validation protocol exists but execution not completed, no validation report available",
            reference="21 CFR 211.165, ICH Q2",
            observation_type=ObservationType.DOCUMENT_REVIEW,
            auditor="Lead Auditor",
            company="Test Company",
            audit_type="regulatory",
            corrective_action="Complete method validation within 30 days and provide validation report"
        )
        
        print(f"✅ Critical observation created")
        print(f"   ID: {observation.id}")
        print(f"   Priority: {observation.priority_label}")
        print(f"   Status: {observation.status}")
        
        # Test status update
        logger.update_observation_status(observation.id, "In Progress")
        print(f"   Status Updated: {observation.status}")
        
        # Test adding corrective action
        logger.add_corrective_action(observation.id, "Validation completed and report submitted")
        print(f"   Corrective Action Added: {observation.corrective_action}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Run all tests"""
    print("🚀 Enhanced Smart Audit Orchestrator Agent - System Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run tests
    test_smart_orchestrator()
    test_checklist_generator()
    test_audit_logger()
    test_live_audit_support()
    test_observation_logging()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 