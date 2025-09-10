# SDK Outreach - Sophisticated B2B Lead Generation & Outreach Automation

A comprehensive Python SDK for automating B2B lead generation, enrichment, qualification, and personalized outreach campaigns. Built with AI-powered insights and multi-source data enrichment.

## 🚀 Features

### Core Capabilities
- **Multi-Source Data Enrichment**: Outscraper, LinkedIn, website analysis, email finding
- **AI-Powered Lead Scoring**: Claude 3.5 Sonnet integration for intelligent qualification
- **Automated Lead Processing**: Complete workflow from raw data to qualified prospects
- **Technology Detection**: Identify tech stacks for better targeting
- **Contact Discovery**: Find decision makers and technical contacts
- **Batch Processing**: Handle large volumes of leads efficiently

### Advanced Features
- **Intelligent Lead Scoring**: 4-factor scoring system (company fit, contact quality, engagement potential, technology fit)
- **AI Insights**: Personalized outreach recommendations and objection handling
- **Rate Limiting**: Built-in API rate limiting and retry logic
- **Error Handling**: Comprehensive error handling with detailed logging
- **Async Architecture**: High-performance async/await throughout
- **Modular Design**: Easily extensible with new data sources and processors

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/tindevelopers/sdk-outreach-single-tenant.git
cd sdk-outreach-single-tenant

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp env.example .env

# Edit .env with your API keys
nano .env
```

## ⚙️ Configuration

### Required API Keys
```bash
# Essential for basic functionality
OUTSCRAPER_API_KEY=your_outscraper_api_key_here

# AI-powered features (choose one)
OPENROUTER_API_KEY=your_openrouter_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Optional enhancements
GOOGLE_SHEETS_CREDENTIALS_PATH=path/to/google/credentials.json
SENDGRID_API_KEY=your_sendgrid_api_key
```

## 🎯 Quick Start

### Basic Lead Processing

```python
import asyncio
from sdk_outreach import OutreachSDK

async def main():
    # Initialize SDK
    async with OutreachSDK() as sdk:
        # Create a lead
        lead = await sdk.create_lead(
            company_name="TechCorp Inc",
            company_data={
                "website": "https://techcorp.com",
                "city": "San Francisco",
                "state": "CA",
                "country": "US"
            },
            source="manual_entry"
        )
        
        # Complete processing (enrich + score)
        processed_lead = await sdk.process_lead_complete(lead.id)
        
        print(f"Lead Score: {processed_lead.score.overall_score}/100")
        print(f"Status: {processed_lead.status}")
        print(f"Technologies: {processed_lead.company.technologies}")

asyncio.run(main())
```

## 🏗️ Architecture

### Core Components

```
┌─────────────────────────────────────┐
│           OutreachSDK               │
│         (Main Client)               │
└─────────────┬───────────────────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
┌───▼───┐ ┌───▼───┐ ┌───▼───┐
│Enrich │ │  AI   │ │Config │
│Engine │ │System │ │ Mgmt  │
└───┬───┘ └───┬───┘ └───────┘
    │         │
┌───▼───┐ ┌───▼───┐
│Sources│ │Scoring│
│& Proc │ │& Qual │
└───────┘ └───────┘
```

## 📊 Lead Scoring System

### Scoring Factors (Weighted)

- **Company Fit (35%)**: Size, industry, digital presence, data completeness
- **Contact Quality (25%)**: Role relevance, data completeness, accessibility
- **Engagement Potential (25%)**: Website activity, social presence, growth signals
- **Technology Fit (15%)**: Tech stack alignment with SDK use cases

### Score Interpretation

- **80-100**: High Priority - Excellent fit, immediate outreach
- **60-79**: Medium Priority - Good fit, standard outreach
- **40-59**: Low Priority - Potential fit, nurture campaign
- **0-39**: Disqualified - Poor fit, exclude from campaigns

## 🚀 Production Deployment

### Docker Setup

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "-m", "sdk_outreach.api"]
```

## 🔧 GitHub Actions CI/CD

This repository includes comprehensive GitHub Actions workflows:

- **CI/CD Pipeline**: Automated testing, linting, security scanning
- **CodeQL Analysis**: Security vulnerability scanning  
- **Dependency Review**: Automated dependency security checks
- **Docker Build**: Automated container builds and publishing
- **Release Management**: Automated releases with semantic versioning

## 📚 API Reference

### Core Methods

#### Lead Management
- `create_lead(company_name, company_data, contacts, source, tags)` → `Lead`
- `get_lead(lead_id)` → `Optional[Lead]`
- `list_leads(status, tags, limit)` → `List[Lead]`
- `update_lead(lead_id, updates)` → `Lead`
- `delete_lead(lead_id)` → `bool`

#### Enrichment
- `enrich_lead(lead_id, sources, force_refresh)` → `Lead`
- `enrich_leads_batch(lead_ids, batch_size, sources)` → `List[Lead]`

#### Scoring
- `score_lead(lead_id)` → `Lead`
- `score_leads_batch(lead_ids)` → `List[Lead]`

#### Workflows
- `process_lead_complete(lead_id, enrich, score, sources)` → `Lead`
- `process_leads_batch_complete(lead_ids, batch_size, enrich, score, sources)` → `List[Lead]`

#### Analytics
- `get_lead_analytics()` → `Dict[str, Any]`
- `health_check()` → `Dict[str, Any]`
- `get_stats()` → `Dict[str, Any]`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Run tests
pytest tests/

# Code formatting
black sdk_outreach/
isort sdk_outreach/

# Type checking
mypy sdk_outreach/
```

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Repository**: https://github.com/tindevelopers/sdk-outreach-single-tenant
- **Issues**: https://github.com/tindevelopers/sdk-outreach-single-tenant/issues
- **Documentation**: See examples/ directory for usage examples

## 🗺️ Roadmap

### v1.1 (Next Release)
- [ ] Campaign management system
- [ ] Email outreach automation
- [ ] LinkedIn outreach integration
- [ ] Advanced analytics dashboard

### v1.2 (Future)
- [ ] CRM integrations (Salesforce, HubSpot)
- [ ] Webhook support
- [ ] Multi-tenant architecture
- [ ] Advanced AI personalization

### v2.0 (Long-term)
- [ ] Real-time lead scoring
- [ ] Predictive analytics
- [ ] Advanced workflow automation
- [ ] Mobile app integration