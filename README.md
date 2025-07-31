# 🔍 Audit Intelligence Platform

A comprehensive multi-agent system for pharmaceutical audit intelligence, combining specialized AI agents with vector and graph databases to provide deep insights into quality systems, compliance, and audit procedures.

## 🏗️ Architecture Overview

The platform consists of 6 specialized AI agents working together through an orchestrator:

### 🤖 Agents

1. **Orchestrator Agent** - Coordinates all other agents and synthesizes responses
2. **Web Scraper Agent** - Analyzes due diligence reports and FDA warning letters
3. **Internal Audit Agent** - Handles audit procedures, checklists, and compliance guidelines
4. **External Conference Agent** - Processes conference data and industry events with temporal analysis
5. **Quality Systems Agent** - Manages SNC data and quality events with temporal tracking
6. **SOP Agent** - Interprets standard operating procedures and creates audit protocols

### 🗄️ Data Storage

- **Vector Database (Pinecone)** - Semantic search across all knowledge bases
- **Graph Database (Neo4j)** - Relationship mapping between companies, events, and documents
- **PostgreSQL** - Structured data storage (optional)

## 🚀 Features

### Multi-Agent Coordination
- Intelligent query routing to relevant agents
- Cross-agent insights and synthesis
- Temporal analysis of quality events
- Company-specific audit planning

### Knowledge Management
- PDF processing and text extraction
- Metadata extraction (companies, dates, topics)
- Entity relationship mapping
- Source tracking and references

### Output Types
- **Reports** - Comprehensive analysis and findings
- **Checklists** - Structured audit questionnaires
- **Insights** - Trend analysis and patterns
- **General** - Direct question answering

## 📁 Project Structure

```
takeda_upwork/
├── agents/                     # AI Agent implementations
│   ├── base_agent.py          # Base agent class
│   ├── orchestrator_agent.py  # Main orchestrator
│   ├── web_scraper_agent.py   # Due diligence analysis
│   ├── internal_audit_agent.py # Audit procedures
│   ├── external_conference_agent.py # Conference data
│   ├── quality_systems_agent.py # SNC and quality events
│   └── sop_agent.py           # SOP interpretation
├── database/                   # Database managers
│   ├── vector_db.py           # Pinecone vector database
│   └── graph_db.py            # Neo4j graph database
├── utils/                      # Utilities
│   └── data_processor.py      # PDF processing and data ingestion
├── Knowledge Bases/            # Knowledge base folders
│   ├── Web Scraper Agent/     # Due diligence reports
│   ├── Internal Audit Agent/  # Audit procedures
│   ├── External Engagement Conferences DATA/ # Conference data
│   ├── Company Quality System Agent/ # SNC data
│   └── Audit SOP Agent/       # SOP documents
├── config.py                   # Configuration settings
├── app.py                     # Main Streamlit application
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🛠️ Installation

### Prerequisites

1. **Python 3.8+**
2. **Neo4j Database** (local or cloud)
3. **Pinecone Account** (for vector database)
4. **OpenAI API Key**

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd takeda_upwork
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   Create a `.env` file with:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_password
   RENDER_DB_URL=your_postgresql_url
   ```

4. **Initialize Databases**
   - Set up Neo4j database
   - Create Pinecone indexes (automatically handled by the app)

## 🚀 Usage

### Running the Application

```bash
streamlit run app.py
```

### Main Interface

The application provides four main sections:

1. **Chat Interface** - Main query interface with multi-agent responses
2. **Data Management** - Process knowledge bases and manage databases
3. **Agent Analysis** - Company-specific analysis and insights
4. **System Status** - Monitor system health and agent capabilities

### Example Queries

- "Create an audit checklist for Hovione"
- "What are the quality issues for Boehringer Ingelheim?"
- "Generate a report on FDA compliance trends"
- "Show me the quality timeline for Thermo Fisher"
- "What conferences discussed biologics manufacturing?"

## 🔧 Configuration

### Agent Configuration

Edit `config.py` to customize:
- Model parameters (temperature, max tokens)
- Pinecone index names
- Knowledge base paths
- Output type preferences

### Database Configuration

- **Pinecone**: Configure indexes for each agent
- **Neo4j**: Set up constraints and relationship types
- **PostgreSQL**: Optional for structured data storage

## 📊 Data Processing

### Knowledge Base Ingestion

The system automatically processes:
- **PDFs** - Text extraction and metadata parsing
- **CSVs** - Structured data with column analysis
- **DOCX** - Document content extraction
- **TXT** - Plain text processing

### Metadata Extraction

For each document, the system extracts:
- **Companies** - Named entity recognition
- **Dates** - Temporal information
- **Topics** - Key themes and subjects
- **Categories** - Document classification

### Graph Relationships

The system creates relationships between:
- Companies ↔ Documents
- Companies ↔ Events (SNCs, Conferences)
- Documents ↔ Events
- Temporal sequences of quality events

## 🤖 Agent Capabilities

### Orchestrator Agent
- Query routing and agent selection
- Response synthesis and formatting
- Cross-agent coordination
- Output type determination

### Web Scraper Agent
- Due diligence report analysis
- FDA warning letter processing
- Manufacturing site assessment
- Risk identification

### Internal Audit Agent
- Audit checklist generation
- Compliance procedure guidance
- Audit report creation
- Regulatory interpretation

### External Conference Agent
- Conference data analysis
- Date extraction and temporal analysis
- Company and topic identification
- Industry trend analysis

### Quality Systems Agent
- SNC data analysis
- Temporal quality event tracking
- Company quality trend analysis
- Quality system change monitoring

### SOP Agent
- SOP interpretation and explanation
- Audit protocol creation
- Procedure compliance guidance
- SOP change tracking

## 🔍 Advanced Features

### Temporal Analysis
- Track quality events over time
- Identify trends and patterns
- Historical compliance analysis
- Future risk prediction

### Cross-Agent Insights
- Company-specific comprehensive analysis
- Multi-source data synthesis
- Relationship mapping
- Risk assessment across domains

### Graph Analytics
- Company relationship networks
- Event correlation analysis
- Temporal event sequences
- Risk propagation patterns

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check Neo4j connection settings
   - Verify Pinecone API key
   - Ensure database services are running

2. **PDF Processing Errors**
   - Install PyPDF2 correctly
   - Check file permissions
   - Verify PDF file integrity

3. **Agent Import Errors**
   - Ensure all `__init__.py` files exist
   - Check Python path configuration
   - Verify module dependencies

### Performance Optimization

- Use appropriate Pinecone index sizes
- Optimize Neo4j queries with indexes
- Implement caching for frequent queries
- Monitor API rate limits

## 🔮 Future Enhancements

### Planned Features
- Real-time document upload
- Advanced graph analytics
- Machine learning model integration
- API endpoints for external integration
- Mobile application support

### Scalability Improvements
- Microservices architecture
- Load balancing for agents
- Distributed database setup
- Caching layer implementation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For questions and support:
- Create an issue in the repository
- Contact the development team
- Check the documentation

---

**Built with ❤️ for pharmaceutical audit intelligence**