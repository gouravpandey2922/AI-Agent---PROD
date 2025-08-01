from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import uuid
from dataclasses import dataclass, asdict
from enum import Enum

class RiskLevel(Enum):
    CRITICAL = "Critical"
    MAJOR = "Major"
    MINOR = "Minor"

class ObservationType(Enum):
    DOCUMENT_REVIEW = "Document Review"
    INTERVIEW = "Interview"
    ON_SITE_OBSERVATION = "On-site Observation"
    SYSTEM_REVIEW = "System Review"
    FACILITY_TOUR = "Facility Tour"

@dataclass
class AuditObservation:
    """Structured audit observation entry"""
    id: str
    area: str
    finding: str
    risk_level: RiskLevel
    evidence: str
    reference: str
    observation_type: ObservationType
    priority_label: str
    timestamp: datetime
    auditor: str
    company: str
    audit_type: str
    corrective_action: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str = "Open"
    attachments: List[str] = None
    
    def __post_init__(self):
        if self.attachments is None:
            self.attachments = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['risk_level'] = self.risk_level.value
        data['observation_type'] = self.observation_type.value
        data['timestamp'] = self.timestamp.isoformat()
        if self.due_date:
            data['due_date'] = self.due_date.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditObservation':
        """Create from dictionary"""
        data['risk_level'] = RiskLevel(data['risk_level'])
        data['observation_type'] = ObservationType(data['observation_type'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        if data.get('due_date'):
            data['due_date'] = datetime.fromisoformat(data['due_date'])
        return cls(**data)

class AuditLogger:
    """Comprehensive audit logging system"""
    
    def __init__(self, storage_path: str = "audit_logs"):
        self.storage_path = storage_path
        self.observations: List[AuditObservation] = []
        self.priority_labels = {
            "critical": "🔥 Priority",
            "major": "🔥 Priority", 
            "minor": "✅ Standard",
            "watchlist": "⚠️ Watchlist"
        }
    
    def create_observation(self, 
                          area: str,
                          finding: str,
                          risk_level: RiskLevel,
                          evidence: str,
                          reference: str,
                          observation_type: ObservationType,
                          auditor: str,
                          company: str,
                          audit_type: str,
                          corrective_action: Optional[str] = None,
                          due_date: Optional[datetime] = None) -> AuditObservation:
        """Create a new audit observation"""
        
        observation = AuditObservation(
            id=str(uuid.uuid4()),
            area=area,
            finding=finding,
            risk_level=risk_level,
            evidence=evidence,
            reference=reference,
            observation_type=observation_type,
            priority_label=self.priority_labels.get(risk_level.value.lower(), "✅ Standard"),
            timestamp=datetime.now(),
            auditor=auditor,
            company=company,
            audit_type=audit_type,
            corrective_action=corrective_action,
            due_date=due_date
        )
        
        self.observations.append(observation)
        return observation
    
    def get_observations_by_company(self, company: str) -> List[AuditObservation]:
        """Get all observations for a specific company"""
        return [obs for obs in self.observations if obs.company.lower() == company.lower()]
    
    def get_observations_by_risk_level(self, risk_level: RiskLevel) -> List[AuditObservation]:
        """Get observations by risk level"""
        return [obs for obs in self.observations if obs.risk_level == risk_level]
    
    def get_observations_by_area(self, area: str) -> List[AuditObservation]:
        """Get observations by area"""
        return [obs for obs in self.observations if area.lower() in obs.area.lower()]
    
    def get_open_observations(self) -> List[AuditObservation]:
        """Get all open observations"""
        return [obs for obs in self.observations if obs.status == "Open"]
    
    def get_overdue_observations(self) -> List[AuditObservation]:
        """Get overdue observations"""
        now = datetime.now()
        return [obs for obs in self.observations 
                if obs.due_date and obs.due_date < now and obs.status == "Open"]
    
    def update_observation_status(self, observation_id: str, status: str) -> bool:
        """Update observation status"""
        for obs in self.observations:
            if obs.id == observation_id:
                obs.status = status
                return True
        return False
    
    def add_corrective_action(self, observation_id: str, action: str, due_date: Optional[datetime] = None) -> bool:
        """Add or update corrective action for an observation"""
        for obs in self.observations:
            if obs.id == observation_id:
                obs.corrective_action = action
                if due_date:
                    obs.due_date = due_date
                return True
        return False
    
    def generate_observation_summary(self, company: str = None) -> Dict[str, Any]:
        """Generate summary statistics for observations"""
        observations = self.observations
        if company:
            observations = self.get_observations_by_company(company)
        
        summary = {
            "total_observations": len(observations),
            "by_risk_level": {
                "Critical": len([obs for obs in observations if obs.risk_level == RiskLevel.CRITICAL]),
                "Major": len([obs for obs in observations if obs.risk_level == RiskLevel.MAJOR]),
                "Minor": len([obs for obs in observations if obs.risk_level == RiskLevel.MINOR])
            },
            "by_status": {
                "Open": len([obs for obs in observations if obs.status == "Open"]),
                "Closed": len([obs for obs in observations if obs.status == "Closed"]),
                "In Progress": len([obs for obs in observations if obs.status == "In Progress"])
            },
            "overdue": len(self.get_overdue_observations()) if not company else len([obs for obs in observations if obs.due_date and obs.due_date < datetime.now() and obs.status == "Open"])
        }
        
        return summary
    
    def generate_observation_report(self, company: str = None, format_type: str = "structured") -> str:
        """Generate a formatted observation report"""
        observations = self.observations
        if company:
            observations = self.get_observations_by_company(company)
        
        if format_type == "structured":
            return self._generate_structured_report(observations)
        elif format_type == "summary":
            return self._generate_summary_report(observations)
        else:
            return self._generate_detailed_report(observations)
    
    def _generate_structured_report(self, observations: List[AuditObservation]) -> str:
        """Generate structured observation report"""
        if not observations:
            return "No observations found."
        
        # Group by risk level
        critical_obs = [obs for obs in observations if obs.risk_level == RiskLevel.CRITICAL]
        major_obs = [obs for obs in observations if obs.risk_level == RiskLevel.MAJOR]
        minor_obs = [obs for obs in observations if obs.risk_level == RiskLevel.MINOR]
        
        report = f"""
# Audit Observations Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Total Observations: {len(observations)}
- Critical: {len(critical_obs)}
- Major: {len(major_obs)}
- Minor: {len(minor_obs)}

"""
        
        # Critical Observations
        if critical_obs:
            report += "## 🔥 Critical Observations\n\n"
            for obs in critical_obs:
                report += self._format_observation(obs)
        
        # Major Observations
        if major_obs:
            report += "## ⚠️ Major Observations\n\n"
            for obs in major_obs:
                report += self._format_observation(obs)
        
        # Minor Observations
        if minor_obs:
            report += "## ✅ Minor Observations\n\n"
            for obs in minor_obs:
                report += self._format_observation(obs)
        
        return report
    
    def _format_observation(self, obs: AuditObservation) -> str:
        """Format individual observation for report"""
        return f"""
### {obs.area} - {obs.observation_type.value}

**Finding:** {obs.finding}

**Risk Level:** {obs.risk_level.value} {obs.priority_label}

**Evidence:** {obs.evidence}

**Reference:** {obs.reference}

**Status:** {obs.status}

**Auditor:** {obs.auditor}

**Date:** {obs.timestamp.strftime('%Y-%m-%d')}

"""
    
    def _generate_summary_report(self, observations: List[AuditObservation]) -> str:
        """Generate summary report"""
        summary = self.generate_observation_summary()
        
        return f"""
# Audit Observations Summary

## Statistics
- Total Observations: {summary['total_observations']}
- Critical: {summary['by_risk_level']['Critical']}
- Major: {summary['by_risk_level']['Major']}
- Minor: {summary['by_risk_level']['Minor']}

## Status
- Open: {summary['by_status']['Open']}
- In Progress: {summary['by_status']['In Progress']}
- Closed: {summary['by_status']['Closed']}
- Overdue: {summary['overdue']}
"""
    
    def _generate_detailed_report(self, observations: List[AuditObservation]) -> str:
        """Generate detailed report with all information"""
        report = self._generate_structured_report(observations)
        
        # Add additional details
        report += "\n## Detailed Information\n\n"
        
        for obs in observations:
            report += f"""
### Observation ID: {obs.id}

**Company:** {obs.company}
**Audit Type:** {obs.audit_type}
**Area:** {obs.area}
**Finding:** {obs.finding}
**Risk Level:** {obs.risk_level.value}
**Evidence:** {obs.evidence}
**Reference:** {obs.reference}
**Type:** {obs.observation_type.value}
**Status:** {obs.status}
**Auditor:** {obs.auditor}
**Date:** {obs.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

"""
            
            if obs.corrective_action:
                report += f"**Corrective Action:** {obs.corrective_action}\n"
            
            if obs.due_date:
                report += f"**Due Date:** {obs.due_date.strftime('%Y-%m-%d')}\n"
            
            if obs.attachments:
                report += f"**Attachments:** {', '.join(obs.attachments)}\n"
            
            report += "\n---\n"
        
        return report
    
    def export_observations(self, format_type: str = "json") -> str:
        """Export observations to different formats"""
        if format_type == "json":
            return json.dumps([obs.to_dict() for obs in self.observations], indent=2)
        elif format_type == "csv":
            return self._export_to_csv()
        else:
            return json.dumps([obs.to_dict() for obs in self.observations], indent=2)
    
    def _export_to_csv(self) -> str:
        """Export observations to CSV format"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Company', 'Audit Type', 'Area', 'Finding', 'Risk Level',
            'Evidence', 'Reference', 'Type', 'Status', 'Auditor', 'Date',
            'Corrective Action', 'Due Date'
        ])
        
        # Write data
        for obs in self.observations:
            writer.writerow([
                obs.id, obs.company, obs.audit_type, obs.area, obs.finding,
                obs.risk_level.value, obs.evidence, obs.reference,
                obs.observation_type.value, obs.status, obs.auditor,
                obs.timestamp.strftime('%Y-%m-%d'),
                obs.corrective_action or '', obs.due_date.strftime('%Y-%m-%d') if obs.due_date else ''
            ])
        
        return output.getvalue()
    
    def save_observations(self, filename: str = None) -> str:
        """Save observations to file"""
        if not filename:
            filename = f"audit_observations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump([obs.to_dict() for obs in self.observations], f, indent=2)
        
        return filename
    
    def load_observations(self, filename: str) -> bool:
        """Load observations from file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.observations = [AuditObservation.from_dict(obs_data) for obs_data in data]
            return True
        except Exception as e:
            print(f"Error loading observations: {e}")
            return False 