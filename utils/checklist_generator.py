from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from dataclasses import dataclass, asdict
from enum import Enum

class ChecklistPriority(Enum):
    CRITICAL = "🔥 Priority"
    STANDARD = "✅ Standard"
    WATCHLIST = "⚠️ Watchlist"

class ChecklistType(Enum):
    DOCUMENT_REVIEW = "Document Review"
    INTERVIEW = "Interview"
    ON_SITE_OBSERVATION = "On-site Observation"
    SYSTEM_REVIEW = "System Review"
    FACILITY_TOUR = "Facility Tour"

@dataclass
class ChecklistItem:
    """Individual checklist item"""
    area: str
    item: str
    checklist_type: ChecklistType
    priority: ChecklistPriority
    notes: str
    evidence_required: str
    regulatory_reference: Optional[str] = None
    sop_reference: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['checklist_type'] = self.checklist_type.value
        data['priority'] = self.priority.value
        return data

class AuditChecklistGenerator:
    """Intelligent audit checklist generator"""
    
    def __init__(self):
        self.priority_labels = {
            "critical": ChecklistPriority.CRITICAL,
            "major": ChecklistPriority.CRITICAL,
            "minor": ChecklistPriority.STANDARD,
            "watchlist": ChecklistPriority.WATCHLIST
        }
        
        # Predefined checklist templates
        self.checklist_templates = {
            "sterile_manufacturing": self._get_sterile_manufacturing_template(),
            "oral_solid": self._get_oral_solid_template(),
            "biotech": self._get_biotech_template(),
            "laboratory": self._get_laboratory_template(),
            "warehouse": self._get_warehouse_template(),
            "quality_systems": self._get_quality_systems_template()
        }
    
    def generate_checklist(self, 
                          audit_type: str,
                          company_name: str,
                          product_modality: str = None,
                          risk_factors: List[str] = None,
                          custom_areas: List[str] = None) -> Dict[str, Any]:
        """Generate comprehensive audit checklist"""
        
        # Determine base template
        base_template = self._get_base_template(audit_type, product_modality)
        
        # Add risk-based items
        risk_items = self._generate_risk_based_items(risk_factors) if risk_factors else []
        
        # Add custom areas
        custom_items = self._generate_custom_items(custom_areas) if custom_areas else []
        
        # Combine all items
        all_items = base_template + risk_items + custom_items
        
        # Sort by priority
        all_items.sort(key=lambda x: self._get_priority_score(x.priority), reverse=True)
        
        # Generate formatted checklist
        formatted_checklist = self._format_checklist(all_items, company_name, audit_type)
        
        return {
            "company": company_name,
            "audit_type": audit_type,
            "product_modality": product_modality,
            "generated_date": datetime.now().isoformat(),
            "total_items": len(all_items),
            "priority_breakdown": self._get_priority_breakdown(all_items),
            "checklist": formatted_checklist,
            "raw_items": [item.to_dict() for item in all_items]
        }
    
    def _get_base_template(self, audit_type: str, product_modality: str) -> List[ChecklistItem]:
        """Get base checklist template"""
        items = []
        
        # Common items for all audits
        items.extend(self._get_common_items())
        
        # Add modality-specific items
        if product_modality:
            modality_template = self.checklist_templates.get(product_modality.lower(), [])
            items.extend(modality_template)
        
        # Add audit type specific items
        if audit_type.lower() == "supplier":
            items.extend(self._get_supplier_specific_items())
        elif audit_type.lower() == "internal":
            items.extend(self._get_internal_specific_items())
        elif audit_type.lower() == "regulatory":
            items.extend(self._get_regulatory_specific_items())
        
        return items
    
    def _get_common_items(self) -> List[ChecklistItem]:
        """Get common checklist items for all audits"""
        return [
            ChecklistItem(
                area="Quality Management System",
                item="Review Quality Manual and organizational structure",
                checklist_type=ChecklistType.DOCUMENT_REVIEW,
                priority=ChecklistPriority.CRITICAL,
                notes="Verify quality unit independence and responsibilities",
                evidence_required="Quality Manual, organizational chart, job descriptions",
                regulatory_reference="21 CFR 211.22, EU GMP Chapter 2"
            ),
            ChecklistItem(
                area="Document Control",
                item="Verify document control system effectiveness",
                checklist_type=ChecklistType.SYSTEM_REVIEW,
                priority=ChecklistPriority.CRITICAL,
                notes="Check SOP management, version control, and accessibility",
                evidence_required="Document control SOP, master list, training records",
                regulatory_reference="21 CFR 211.100, EU GMP Chapter 4"
            ),
            ChecklistItem(
                area="Training",
                item="Review personnel training and qualification records",
                checklist_type=ChecklistType.DOCUMENT_REVIEW,
                priority=ChecklistPriority.STANDARD,
                notes="Verify GMP training, job-specific training, and requalification",
                evidence_required="Training records, qualification files, training matrix",
                regulatory_reference="21 CFR 211.25, EU GMP Chapter 2"
            ),
            ChecklistItem(
                area="Change Control",
                item="Review change control system and recent changes",
                checklist_type=ChecklistType.SYSTEM_REVIEW,
                priority=ChecklistPriority.STANDARD,
                notes="Assess change control procedures and implementation",
                evidence_required="Change control SOP, recent change records, impact assessments",
                regulatory_reference="21 CFR 211.100, ICH Q10"
            ),
            ChecklistItem(
                area="Deviation Management",
                item="Review deviation and CAPA systems",
                checklist_type=ChecklistType.SYSTEM_REVIEW,
                priority=ChecklistPriority.CRITICAL,
                notes="Verify deviation investigation, root cause analysis, and CAPA effectiveness",
                evidence_required="Deviation logs, investigation reports, CAPA records",
                regulatory_reference="21 CFR 211.192, EU GMP Chapter 4"
            )
        ]
    
    def _get_sterile_manufacturing_template(self) -> List[ChecklistItem]:
        """Get sterile manufacturing specific checklist items"""
        return [
            ChecklistItem(
                area="Aseptic Processing",
                item="Review aseptic processing procedures and controls",
                checklist_type=ChecklistType.ON_SITE_OBSERVATION,
                priority=ChecklistPriority.CRITICAL,
                notes="Verify aseptic technique, interventions, and contamination control",
                evidence_required="Aseptic processing SOPs, media fill results, intervention logs",
                regulatory_reference="21 CFR 211.113, EU GMP Annex 1"
            ),
            ChecklistItem(
                area="Environmental Monitoring",
                item="Review environmental monitoring program",
                checklist_type=ChecklistType.DOCUMENT_REVIEW,
                priority=ChecklistPriority.CRITICAL,
                notes="Check EM procedures, alert/action limits, and trend analysis",
                evidence_required="EM SOPs, monitoring data, trend reports, excursion investigations",
                regulatory_reference="21 CFR 211.42, EU GMP Annex 1"
            ),
            ChecklistItem(
                area="Sterilization",
                item="Review sterilization validation and procedures",
                checklist_type=ChecklistType.DOCUMENT_REVIEW,
                priority=ChecklistPriority.CRITICAL,
                notes="Verify sterilization cycle validation and routine monitoring",
                evidence_required="Sterilization validation reports, cycle records, biological indicators",
                regulatory_reference="21 CFR 211.113, EU GMP Annex 1"
            ),
            ChecklistItem(
                area="Gowning",
                item="Observe gowning procedures and qualification",
                checklist_type=ChecklistType.ON_SITE_OBSERVATION,
                priority=ChecklistPriority.STANDARD,
                notes="Verify gowning procedures, qualification, and requalification",
                evidence_required="Gowning SOPs, qualification records, gowning logs",
                regulatory_reference="EU GMP Annex 1"
            )
        ]
    
    def _get_oral_solid_template(self) -> List[ChecklistItem]:
        """Get oral solid dosage form specific checklist items"""
        return [
            ChecklistItem(
                area="Process Validation",
                item="Review process validation for critical unit operations",
                checklist_type=ChecklistType.DOCUMENT_REVIEW,
                priority=ChecklistPriority.CRITICAL,
                notes="Verify validation protocols, execution, and reports",
                evidence_required="Validation protocols, validation reports, batch records",
                regulatory_reference="21 CFR 211.100, ICH Q7"
            ),
            ChecklistItem(
                area="Equipment Qualification",
                item="Review equipment qualification and calibration",
                checklist_type=ChecklistType.SYSTEM_REVIEW,
                priority=ChecklistPriority.STANDARD,
                notes="Check equipment qualification, calibration, and maintenance",
                evidence_required="Qualification protocols, calibration records, maintenance logs",
                regulatory_reference="21 CFR 211.68, EU GMP Chapter 3"
            ),
            ChecklistItem(
                area="Cross-Contamination Control",
                item="Review cross-contamination control measures",
                checklist_type=ChecklistType.FACILITY_TOUR,
                priority=ChecklistPriority.CRITICAL,
                notes="Verify facility design, cleaning procedures, and material flow",
                evidence_required="Facility layout, cleaning validation, material flow diagrams",
                regulatory_reference="21 CFR 211.42, EU GMP Chapter 3"
            )
        ]
    
    def _get_biotech_template(self) -> List[ChecklistItem]:
        """Get biotech/biologics specific checklist items"""
        return [
            ChecklistItem(
                area="Cell Culture",
                item="Review cell culture and fermentation processes",
                checklist_type=ChecklistType.ON_SITE_OBSERVATION,
                priority=ChecklistPriority.CRITICAL,
                notes="Verify cell culture procedures, monitoring, and controls",
                evidence_required="Cell culture SOPs, batch records, monitoring data",
                regulatory_reference="21 CFR 600-680, EU GMP Annex 2"
            ),
            ChecklistItem(
                area="Purification",
                item="Review purification and chromatography processes",
                checklist_type=ChecklistType.DOCUMENT_REVIEW,
                priority=ChecklistPriority.CRITICAL,
                notes="Check purification procedures, column qualification, and cleaning",
                evidence_required="Purification SOPs, column qualification, cleaning validation",
                regulatory_reference="21 CFR 600-680, EU GMP Annex 2"
            ),
            ChecklistItem(
                area="Viral Safety",
                item="Review viral safety testing and clearance",
                checklist_type=ChecklistType.DOCUMENT_REVIEW,
                priority=ChecklistPriority.CRITICAL,
                notes="Verify viral safety testing, clearance studies, and monitoring",
                evidence_required="Viral safety protocols, clearance studies, testing records",
                regulatory_reference="ICH Q5A, EU GMP Annex 2"
            )
        ]
    
    def _get_laboratory_template(self) -> List[ChecklistItem]:
        """Get laboratory operations specific checklist items"""
        return [
            ChecklistItem(
                area="Method Validation",
                item="Review analytical method validation",
                checklist_type=ChecklistType.DOCUMENT_REVIEW,
                priority=ChecklistPriority.CRITICAL,
                notes="Verify method validation protocols, execution, and reports",
                evidence_required="Validation protocols, validation reports, method SOPs",
                regulatory_reference="21 CFR 211.165, ICH Q2"
            ),
            ChecklistItem(
                area="Data Integrity",
                item="Review data integrity controls and systems",
                checklist_type=ChecklistType.SYSTEM_REVIEW,
                priority=ChecklistPriority.CRITICAL,
                notes="Check electronic systems, audit trails, and data controls",
                evidence_required="Data integrity SOPs, system validation, audit trail reviews",
                regulatory_reference="21 CFR Part 11, EU GMP Annex 11"
            ),
            ChecklistItem(
                area="Out of Specification",
                item="Review OOS investigation procedures",
                checklist_type=ChecklistType.DOCUMENT_REVIEW,
                priority=ChecklistPriority.STANDARD,
                notes="Verify OOS investigation procedures and recent investigations",
                evidence_required="OOS SOPs, investigation reports, trend analysis",
                regulatory_reference="FDA OOS Guidance"
            )
        ]
    
    def _get_warehouse_template(self) -> List[ChecklistItem]:
        """Get warehouse operations specific checklist items"""
        return [
            ChecklistItem(
                area="Temperature Control",
                item="Review temperature monitoring and control systems",
                checklist_type=ChecklistType.FACILITY_TOUR,
                priority=ChecklistPriority.CRITICAL,
                notes="Verify temperature monitoring, alarms, and excursion handling",
                evidence_required="Temperature monitoring SOPs, alarm logs, excursion investigations",
                regulatory_reference="21 CFR 211.42, EU GMP Chapter 5"
            ),
            ChecklistItem(
                area="Inventory Control",
                item="Review inventory control and reconciliation",
                checklist_type=ChecklistType.SYSTEM_REVIEW,
                priority=ChecklistPriority.STANDARD,
                notes="Check inventory procedures, reconciliation, and expiry management",
                evidence_required="Inventory SOPs, reconciliation records, expiry logs",
                regulatory_reference="21 CFR 211.142, EU GMP Chapter 5"
            ),
            ChecklistItem(
                area="Security",
                item="Review facility security and access controls",
                checklist_type=ChecklistType.FACILITY_TOUR,
                priority=ChecklistPriority.STANDARD,
                notes="Verify security measures, access controls, and surveillance",
                evidence_required="Security SOPs, access logs, surveillance records",
                regulatory_reference="21 CFR 211.28, EU GMP Chapter 3"
            )
        ]
    
    def _get_quality_systems_template(self) -> List[ChecklistItem]:
        """Get quality systems specific checklist items"""
        return [
            ChecklistItem(
                area="Management Review",
                item="Review management review process and outputs",
                checklist_type=ChecklistType.DOCUMENT_REVIEW,
                priority=ChecklistPriority.STANDARD,
                notes="Verify management review frequency, inputs, and actions",
                evidence_required="Management review SOPs, meeting minutes, action items",
                regulatory_reference="ICH Q10, ISO 9001"
            ),
            ChecklistItem(
                area="Risk Management",
                item="Review risk management processes and tools",
                checklist_type=ChecklistType.SYSTEM_REVIEW,
                priority=ChecklistPriority.STANDARD,
                notes="Check risk assessment procedures and recent assessments",
                evidence_required="Risk management SOPs, risk assessments, mitigation plans",
                regulatory_reference="ICH Q9, ICH Q10"
            ),
            ChecklistItem(
                area="Continuous Improvement",
                item="Review continuous improvement initiatives",
                checklist_type=ChecklistType.INTERVIEW,
                priority=ChecklistPriority.WATCHLIST,
                notes="Assess continuous improvement culture and initiatives",
                evidence_required="Improvement projects, metrics, success stories",
                regulatory_reference="ICH Q10"
            )
        ]
    
    def _get_supplier_specific_items(self) -> List[ChecklistItem]:
        """Get supplier audit specific items"""
        return [
            ChecklistItem(
                area="Supplier Qualification",
                item="Review supplier qualification process",
                checklist_type=ChecklistType.DOCUMENT_REVIEW,
                priority=ChecklistPriority.CRITICAL,
                notes="Verify supplier qualification criteria and process",
                evidence_required="Qualification procedures, assessment reports, approval records",
                regulatory_reference="21 CFR 211.84, EU GMP Chapter 7"
            ),
            ChecklistItem(
                area="Supply Chain",
                item="Review supply chain security and traceability",
                checklist_type=ChecklistType.SYSTEM_REVIEW,
                priority=ChecklistPriority.STANDARD,
                notes="Check supply chain controls, traceability, and security",
                evidence_required="Supply chain procedures, traceability records, security measures",
                regulatory_reference="21 CFR 211.84, EU GMP Chapter 7"
            )
        ]
    
    def _get_internal_specific_items(self) -> List[ChecklistItem]:
        """Get internal audit specific items"""
        return [
            ChecklistItem(
                area="Internal Audit Program",
                item="Review internal audit program effectiveness",
                checklist_type=ChecklistType.SYSTEM_REVIEW,
                priority=ChecklistPriority.STANDARD,
                notes="Verify audit schedule, scope, and follow-up actions",
                evidence_required="Audit schedule, audit reports, follow-up records",
                regulatory_reference="ICH Q10, ISO 19011"
            ),
            ChecklistItem(
                area="Self-Inspection",
                item="Review self-inspection procedures and results",
                checklist_type=ChecklistType.DOCUMENT_REVIEW,
                priority=ChecklistPriority.STANDARD,
                notes="Check self-inspection procedures and recent results",
                evidence_required="Self-inspection SOPs, reports, action items",
                regulatory_reference="EU GMP Chapter 9"
            )
        ]
    
    def _get_regulatory_specific_items(self) -> List[ChecklistItem]:
        """Get regulatory audit specific items"""
        return [
            ChecklistItem(
                area="Regulatory Compliance",
                item="Review regulatory compliance status",
                checklist_type=ChecklistType.DOCUMENT_REVIEW,
                priority=ChecklistPriority.CRITICAL,
                notes="Verify compliance with applicable regulations",
                evidence_required="Compliance assessments, gap analyses, action plans",
                regulatory_reference="21 CFR 210-211, EU GMP"
            ),
            ChecklistItem(
                area="Regulatory Communications",
                item="Review regulatory communication procedures",
                checklist_type=ChecklistType.SYSTEM_REVIEW,
                priority=ChecklistPriority.STANDARD,
                notes="Check procedures for regulatory communications",
                evidence_required="Communication procedures, correspondence logs",
                regulatory_reference="21 CFR 314, EU GMP Chapter 1"
            )
        ]
    
    def _generate_risk_based_items(self, risk_factors: List[str]) -> List[ChecklistItem]:
        """Generate checklist items based on identified risk factors"""
        items = []
        
        for risk_factor in risk_factors:
            if "sterility" in risk_factor.lower():
                items.append(ChecklistItem(
                    area="Sterility Assurance",
                    item=f"Review sterility assurance measures for {risk_factor}",
                    checklist_type=ChecklistType.ON_SITE_OBSERVATION,
                    priority=ChecklistPriority.CRITICAL,
                    notes=f"Focus on sterility controls related to {risk_factor}",
                    evidence_required="Sterility procedures, monitoring data, validation records",
                    regulatory_reference="21 CFR 211.113, EU GMP Annex 1"
                ))
            elif "data integrity" in risk_factor.lower():
                items.append(ChecklistItem(
                    area="Data Integrity",
                    item=f"Review data integrity controls for {risk_factor}",
                    checklist_type=ChecklistType.SYSTEM_REVIEW,
                    priority=ChecklistPriority.CRITICAL,
                    notes=f"Focus on data integrity related to {risk_factor}",
                    evidence_required="Data integrity procedures, system controls, audit trails",
                    regulatory_reference="21 CFR Part 11, EU GMP Annex 11"
                ))
            elif "validation" in risk_factor.lower():
                items.append(ChecklistItem(
                    area="Validation",
                    item=f"Review validation status for {risk_factor}",
                    checklist_type=ChecklistType.DOCUMENT_REVIEW,
                    priority=ChecklistPriority.CRITICAL,
                    notes=f"Focus on validation related to {risk_factor}",
                    evidence_required="Validation protocols, reports, qualification records",
                    regulatory_reference="21 CFR 211.100, ICH Q7"
                ))
        
        return items
    
    def _generate_custom_items(self, custom_areas: List[str]) -> List[ChecklistItem]:
        """Generate checklist items for custom areas"""
        items = []
        
        for area in custom_areas:
            items.append(ChecklistItem(
                area=area,
                item=f"Review {area} procedures and controls",
                checklist_type=ChecklistType.SYSTEM_REVIEW,
                priority=ChecklistPriority.STANDARD,
                notes=f"Assess {area} procedures and implementation",
                evidence_required=f"{area} SOPs, records, and documentation",
                regulatory_reference="Applicable regulations"
            ))
        
        return items
    
    def _get_priority_score(self, priority: ChecklistPriority) -> int:
        """Get numerical score for priority sorting"""
        priority_scores = {
            ChecklistPriority.CRITICAL: 3,
            ChecklistPriority.STANDARD: 2,
            ChecklistPriority.WATCHLIST: 1
        }
        return priority_scores.get(priority, 1)
    
    def _get_priority_breakdown(self, items: List[ChecklistItem]) -> Dict[str, int]:
        """Get breakdown of items by priority"""
        breakdown = {
            "Critical": 0,
            "Standard": 0,
            "Watchlist": 0
        }
        
        for item in items:
            if item.priority == ChecklistPriority.CRITICAL:
                breakdown["Critical"] += 1
            elif item.priority == ChecklistPriority.STANDARD:
                breakdown["Standard"] += 1
            elif item.priority == ChecklistPriority.WATCHLIST:
                breakdown["Watchlist"] += 1
        
        return breakdown
    
    def _format_checklist(self, items: List[ChecklistItem], company_name: str, audit_type: str) -> str:
        """Format checklist for display"""
        
        checklist = f"""
# Audit Checklist - {company_name}
**Audit Type:** {audit_type}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Checklist Items

| Area | Checklist Item | Type | Priority | Notes |
|------|----------------|------|----------|-------|
"""
        
        for item in items:
            checklist += f"| {item.area} | {item.item} | {item.checklist_type.value} | {item.priority.value} | {item.notes} |\n"
        
        checklist += f"""

## Evidence Requirements

"""
        
        for item in items:
            checklist += f"""
### {item.area}
- **Item:** {item.item}
- **Evidence Required:** {item.evidence_required}
"""
            
            if item.regulatory_reference:
                checklist += f"- **Regulatory Reference:** {item.regulatory_reference}\n"
            
            if item.sop_reference:
                checklist += f"- **SOP Reference:** {item.sop_reference}\n"
        
        return checklist 