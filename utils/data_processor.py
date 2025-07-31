import os
import PyPDF2
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
import re
from config import KNOWLEDGE_BASE_PATHS

class DataProcessor:
    def __init__(self):
        self.supported_extensions = ['.pdf', '.csv', '.docx', '.txt']
        
    def process_knowledge_bases(self, vector_db_manager) -> Dict[str, int]:
        """Process all knowledge bases and upload to vector database"""
        results = {}
        
        for agent_name, base_path in KNOWLEDGE_BASE_PATHS.items():
            if os.path.exists(base_path):
                count = self._process_agent_knowledge_base(agent_name, base_path, vector_db_manager)
                results[agent_name] = count
            else:
                print(f"Warning: Knowledge base path not found: {base_path}")
                results[agent_name] = 0
                
        return results
        
    def _process_agent_knowledge_base(self, agent_name: str, base_path: str, vector_db_manager) -> int:
        """Process a specific agent's knowledge base"""
        processed_count = 0
        
        for root, dirs, files in os.walk(base_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                if file_ext in self.supported_extensions:
                    try:
                        if file_ext == '.pdf':
                            content = self._extract_pdf_content(file_path)
                        elif file_ext == '.csv':
                            content = self._extract_csv_content(file_path)
                        elif file_ext == '.docx':
                            content = self._extract_docx_content(file_path)
                        elif file_ext == '.txt':
                            content = self._extract_txt_content(file_path)
                        else:
                            continue
                            
                        if content:
                            # Extract metadata
                            metadata = self._extract_metadata(file_path, content, agent_name)
                            
                            # Upload to vector database
                            doc_id = vector_db_manager.upsert_document(agent_name, content, metadata)
                            
                            processed_count += 1
                            print(f"Processed: {file} -> {doc_id}")
                            
                    except Exception as e:
                        print(f"Error processing {file}: {str(e)}")
                        
        return processed_count
        
    def _extract_pdf_content(self, file_path: str) -> str:
        """Extract text content from PDF"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                    
                return text.strip()
        except Exception as e:
            print(f"Error extracting PDF content from {file_path}: {str(e)}")
            return ""
            
    def _extract_csv_content(self, file_path: str) -> str:
        """Extract content from CSV file"""
        try:
            df = pd.read_csv(file_path)
            
            # Convert DataFrame to text representation
            content_parts = []
            
            # Add column names
            content_parts.append("Columns: " + ", ".join(df.columns.tolist()))
            
            # Add first few rows as sample
            sample_rows = df.head(10).to_string(index=False)
            content_parts.append(f"Sample Data:\n{sample_rows}")
            
            # Add summary statistics
            if len(df) > 0:
                content_parts.append(f"Total Records: {len(df)}")
                
            return "\n\n".join(content_parts)
            
        except Exception as e:
            print(f"Error extracting CSV content from {file_path}: {str(e)}")
            return ""
            
    def _extract_docx_content(self, file_path: str) -> str:
        """Extract text content from DOCX file"""
        try:
            # For now, return a placeholder - you'd need python-docx library
            return f"DOCX content from {os.path.basename(file_path)}"
        except Exception as e:
            print(f"Error extracting DOCX content from {file_path}: {str(e)}")
            return ""
            
    def _extract_txt_content(self, file_path: str) -> str:
        """Extract text content from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error extracting TXT content from {file_path}: {str(e)}")
            return ""
            
    def _extract_metadata(self, file_path: str, content: str, agent_name: str) -> Dict[str, Any]:
        """Extract metadata from file and content"""
        metadata = {
            "title": os.path.basename(file_path),
            "file_path": file_path,
            "agent": agent_name,
            "file_type": os.path.splitext(file_path)[1].lower(),
            "file_size": os.path.getsize(file_path),
            "processed_date": datetime.now().isoformat(),
            "content_length": len(content)
        }
        
        # Extract additional metadata based on agent type
        if agent_name == "quality_systems":
            metadata.update(self._extract_quality_systems_metadata(content))
        elif agent_name == "external_conference":
            metadata.update(self._extract_conference_metadata(content))
        elif agent_name == "web_scraper":
            metadata.update(self._extract_web_scraper_metadata(content))
        else:
            metadata.update(self._extract_general_metadata(content))
            
        return metadata
        
    def _extract_quality_systems_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata specific to quality systems"""
        metadata = {}
        
        # Extract company names
        companies = self._extract_companies_from_text(content)
        if companies:
            metadata["companies"] = companies
            
        # Extract SNC-related information
        if "SNC" in content or "Supplier Notification" in content:
            metadata["event_type"] = "SNC"
            
        # Extract categories
        categories = ["Biologics", "Formulation", "API", "Small Molecule", "Lab Testing", "Packaging"]
        found_categories = [cat for cat in categories if cat.lower() in content.lower()]
        if found_categories:
            metadata["categories"] = found_categories
            
        return metadata
        
    def _extract_conference_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata specific to conference data"""
        metadata = {}
        
        # Extract dates
        dates = self._extract_dates_from_text(content)
        if dates:
            metadata["dates"] = dates
            metadata["date"] = dates[0]  # Use first date as primary
            
        # Extract companies
        companies = self._extract_companies_from_text(content)
        if companies:
            metadata["companies"] = companies
            
        # Extract topics
        topics = self._extract_topics_from_text(content)
        if topics:
            metadata["topics"] = topics
            
        # Mark as conference event
        metadata["event_type"] = "conference"
        
        return metadata
        
    def _extract_web_scraper_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata specific to web scraper data"""
        metadata = {}
        
        # Extract company names
        companies = self._extract_companies_from_text(content)
        if companies:
            metadata["companies"] = companies
            
        # Extract source information
        if "FDA" in content:
            metadata["source"] = "FDA"
        elif "warning" in content.lower():
            metadata["source"] = "FDA Warning Letters"
        elif "due diligence" in content.lower():
            metadata["source"] = "Due Diligence Report"
            
        # Extract dates
        dates = self._extract_dates_from_text(content)
        if dates:
            metadata["dates"] = dates
            metadata["date"] = dates[0]
            
        return metadata
        
    def _extract_general_metadata(self, content: str) -> Dict[str, Any]:
        """Extract general metadata from content"""
        metadata = {}
        
        # Extract companies
        companies = self._extract_companies_from_text(content)
        if companies:
            metadata["companies"] = companies
            
        # Extract dates
        dates = self._extract_dates_from_text(content)
        if dates:
            metadata["dates"] = dates
            metadata["date"] = dates[0]
            
        # Extract topics
        topics = self._extract_topics_from_text(content)
        if topics:
            metadata["topics"] = topics
            
        return metadata
        
    def _extract_companies_from_text(self, text: str) -> List[str]:
        """Extract company names from text"""
        # Common company names in the dataset
        known_companies = [
            "Boehringer Ingelheim", "Thermo Fisher", "Hovione", "Patheon", 
            "GRAM", "Fisher Clinical", "Lonza", "Pfizer", "BMS", "Vetter",
            "Grand River Aseptic Manufacturing"
        ]
        
        found_companies = []
        for company in known_companies:
            if company.lower() in text.lower():
                found_companies.append(company)
                
        return found_companies
        
    def _extract_dates_from_text(self, text: str) -> List[str]:
        """Extract dates from text"""
        # Common date patterns
        patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
            r'\b\d{4}-\d{1,2}-\d{1,2}\b',  # YYYY-MM-DD
            r'\b\d{1,2}-\d{1,2}-\d{4}\b',  # MM-DD-YYYY
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',  # Month DD, YYYY
        ]
        
        dates = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
            
        return dates
        
    def _extract_topics_from_text(self, text: str) -> List[str]:
        """Extract topics/keywords from text"""
        # Common topics in pharmaceutical/audit context
        topics = [
            "manufacturing", "quality", "compliance", "audit", "FDA", "GMP",
            "validation", "cleaning", "sterilization", "documentation",
            "biologics", "formulation", "API", "packaging", "testing"
        ]
        
        found_topics = []
        for topic in topics:
            if topic.lower() in text.lower():
                found_topics.append(topic)
                
        return found_topics 