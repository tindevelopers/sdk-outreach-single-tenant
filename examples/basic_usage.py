"""
Basic usage example for the SDK Outreach system.

This example demonstrates:
1. Creating leads
2. Enriching lead data
3. Scoring leads
4. Analyzing results
"""

import asyncio
import logging
from datetime import datetime
from sdk_outreach import OutreachSDK, LeadStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def basic_lead_processing():
    """Demonstrate basic lead processing workflow."""
    print("🚀 Starting SDK Outreach Basic Example")
    print("=" * 50)
    
    async with OutreachSDK() as sdk:
        # Check SDK health
        health = await sdk.health_check()
        print(f"SDK Status: {health['status']}")
        
        if health['status'] != 'healthy':
            print("⚠️  SDK not fully healthy, some features may be limited")
        
        print("\n1. Creating sample leads...")
        
        # Sample companies to process
        sample_companies = [
            {
                "name": "TechStart Solutions",
                "website": "https://techstart.io",
                "city": "San Francisco",
                "state": "CA",
                "country": "US",
                "description": "AI-powered development tools for modern teams"
            },
            {
                "name": "DevTools Inc",
                "website": "https://devtools.com",
                "city": "Austin",
                "state": "TX", 
                "country": "US",
                "description": "Cloud-native development platform"
            },
            {
                "name": "API Solutions Ltd",
                "website": "https://apisolutions.net",
                "city": "London",
                "country": "UK",
                "description": "Enterprise API management and integration"
            }
        ]
        
        # Create leads
        lead_ids = []
        for company_data in sample_companies:
            try:
                lead = await sdk.create_lead(
                    company_name=company_data["name"],
                    company_data={
                        "website": company_data["website"],
                        "city": company_data["city"],
                        "state": company_data.get("state"),
                        "country": company_data["country"],
                        "description": company_data["description"]
                    },
                    source="example_script",
                    tags=["demo", "tech_company"]
                )
                
                lead_ids.append(lead.id)
                print(f"✅ Created lead: {lead.company.name} (ID: {lead.id[:8]}...)")
                
            except Exception as e:
                print(f"❌ Error creating lead for {company_data['name']}: {str(e)}")
        
        if not lead_ids:
            print("❌ No leads created successfully")
            return
        
        print(f"\n2. Processing {len(lead_ids)} leads...")
        
        # Process leads individually to show progress
        processed_leads = []
        for i, lead_id in enumerate(lead_ids, 1):
            try:
                print(f"   Processing lead {i}/{len(lead_ids)}...")
                
                # Complete processing (enrich + score)
                processed_lead = await sdk.process_lead_complete(
                    lead_id=lead_id,
                    enrich=True,
                    score=True
                )
                
                processed_leads.append(processed_lead)
                
                # Show immediate results
                score = processed_lead.score.overall_score if processed_lead.score else 0
                print(f"   ✅ {processed_lead.company.name}: {score:.1f}/100 ({processed_lead.status.value})")
                
            except Exception as e:
                print(f"   ❌ Error processing lead {lead_id[:8]}...: {str(e)}")
        
        print(f"\n3. Analysis Results")
        print("-" * 30)
        
        if processed_leads:
            # Show detailed results
            for lead in processed_leads:
                print(f"\n🏢 {lead.company.name}")
                print(f"   Score: {lead.score.overall_score:.1f}/100" if lead.score else "   Score: Not available")
                print(f"   Status: {lead.status.value}")
                print(f"   Industry: {lead.company.industry.value if lead.company.industry else 'Unknown'}")
                print(f"   Size: {lead.company.size.value if lead.company.size else 'Unknown'}")
                print(f"   Technologies: {', '.join(lead.company.technologies[:5]) if lead.company.technologies else 'None detected'}")
                print(f"   Contacts: {len(lead.contacts)}")
                
                # Show primary contact if available
                primary_contact = lead.get_primary_contact()
                if primary_contact:
                    print(f"   Primary Contact: {primary_contact.full_name or 'Unknown'}")
                    print(f"   Contact Role: {primary_contact.role.value if primary_contact.role else 'Unknown'}")
                    print(f"   Contact Email: {primary_contact.email or 'Not found'}")
                
                # Show AI insights if available
                if lead.score and 'ai_insights' in lead.score.scoring_factors:
                    insights = lead.score.scoring_factors['ai_insights']
                    if 'outreach_approach' in insights:
                        print(f"   💡 AI Recommendation: {insights['outreach_approach']}")
        
        print(f"\n4. Overall Analytics")
        print("-" * 30)
        
        # Get analytics
        analytics = await sdk.get_lead_analytics()
        
        print(f"Total Leads: {analytics['total_leads']}")
        print(f"Average Score: {analytics['average_score']:.1f}/100")
        
        if analytics['status_breakdown']:
            print("Status Breakdown:")
            for status, count in analytics['status_breakdown'].items():
                print(f"  - {status.title()}: {count}")
        
        if analytics['score_distribution']:
            print("Score Distribution:")
            for range_name, count in analytics['score_distribution'].items():
                print(f"  - {range_name}: {count}")
        
        if analytics['top_industries']:
            print("Top Industries:")
            for industry, count in analytics['top_industries'][:3]:
                print(f"  - {industry.title()}: {count}")
        
        if analytics['top_technologies']:
            print("Top Technologies:")
            for tech, count in analytics['top_technologies'][:5]:
                print(f"  - {tech}: {count}")
        
        print(f"\n5. High-Priority Leads")
        print("-" * 30)
        
        # Find high-priority leads
        high_priority_leads = [
            lead for lead in processed_leads 
            if lead.score and lead.score.overall_score >= 70
        ]
        
        if high_priority_leads:
            print(f"Found {len(high_priority_leads)} high-priority leads:")
            for lead in high_priority_leads:
                print(f"  🎯 {lead.company.name} ({lead.score.overall_score:.1f}/100)")
                
                # Show key strengths
                if lead.score and 'ai_insights' in lead.score.scoring_factors:
                    insights = lead.score.scoring_factors['ai_insights']
                    if 'strengths' in insights and insights['strengths']:
                        print(f"     Strengths: {', '.join(insights['strengths'][:2])}")
        else:
            print("No high-priority leads found in this batch")
        
        print(f"\n✅ Example completed successfully!")
        print(f"Processed {len(processed_leads)} leads in total")


async def demonstrate_batch_processing():
    """Demonstrate batch processing capabilities."""
    print("\n" + "=" * 50)
    print("🔄 Batch Processing Example")
    print("=" * 50)
    
    async with OutreachSDK() as sdk:
        # Create multiple leads quickly
        companies = [
            f"TechCorp {i}" for i in range(1, 6)
        ]
        
        print(f"Creating {len(companies)} leads for batch processing...")
        
        lead_ids = []
        for company_name in companies:
            lead = await sdk.create_lead(
                company_name=company_name,
                company_data={
                    "website": f"https://{company_name.lower().replace(' ', '')}.com",
                    "city": "San Francisco",
                    "state": "CA",
                    "country": "US"
                },
                source="batch_demo",
                tags=["batch", "demo"]
            )
            lead_ids.append(lead.id)
        
        print(f"✅ Created {len(lead_ids)} leads")
        
        # Process in batch
        print("Processing leads in batch...")
        start_time = datetime.now()
        
        processed_leads = await sdk.process_leads_batch_complete(
            lead_ids=lead_ids,
            batch_size=3,  # Process 3 at a time
            enrich=True,
            score=True
        )
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        print(f"✅ Batch processing completed in {processing_time:.2f} seconds")
        print(f"Average time per lead: {processing_time/len(processed_leads):.2f} seconds")
        
        # Show results summary
        scores = [lead.score.overall_score for lead in processed_leads if lead.score]
        if scores:
            print(f"Score range: {min(scores):.1f} - {max(scores):.1f}")
            print(f"Average score: {sum(scores)/len(scores):.1f}")


async def main():
    """Main example function."""
    try:
        await basic_lead_processing()
        await demonstrate_batch_processing()
        
    except KeyboardInterrupt:
        print("\n⏹️  Example interrupted by user")
    except Exception as e:
        print(f"\n❌ Example failed with error: {str(e)}")
        logger.exception("Example failed")


if __name__ == "__main__":
    print("SDK Outreach - Basic Usage Example")
    print("Make sure you have configured your API keys in .env file")
    print()
    
    asyncio.run(main())