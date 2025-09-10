"""
Main SDK client for lead generation and outreach automation.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import uuid

from .config import get_config, validate_configuration
from .models import Lead, Company, Contact, Campaign, LeadStatus, APIResponse
from .enrichment import EnrichmentEngine
from .ai import LeadScorer, create_ai_client
from .exceptions import (
    OutreachSDKError, 
    ValidationError, 
    ConfigurationError,
    DataEnrichmentError
)

logger = logging.getLogger(__name__)


class OutreachSDK:
    """
    Main SDK client for B2B lead generation and outreach automation.
    
    This client provides a high-level interface for:
    - Lead creation and management
    - Data enrichment from multiple sources
    - AI-powered lead scoring and qualification
    - Outreach campaign management
    - Analytics and reporting
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the Outreach SDK.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.config = get_config()
        self._validate_configuration()
        
        # Initialize components
        self.enrichment_engine = EnrichmentEngine()
        self.ai_client = create_ai_client()
        self.lead_scorer = LeadScorer(self.ai_client)
        
        # Internal state
        self._leads: Dict[str, Lead] = {}
        self._campaigns: Dict[str, Campaign] = {}
        
        logger.info("OutreachSDK initialized successfully")
    
    def _validate_configuration(self) -> None:
        """Validate SDK configuration."""
        validation_results = validate_configuration(self.config)
        
        if not validation_results["valid"]:
            error_msg = "Configuration validation failed: " + "; ".join(validation_results["errors"])
            raise ConfigurationError(error_msg)
        
        if validation_results["warnings"]:
            for warning in validation_results["warnings"]:
                logger.warning(warning)
    
    # Lead Management Methods
    
    async def create_lead(
        self, 
        company_name: str,
        company_data: Optional[Dict[str, Any]] = None,
        contacts: Optional[List[Dict[str, Any]]] = None,
        source: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Lead:
        """
        Create a new lead.
        
        Args:
            company_name: Name of the company
            company_data: Additional company information
            contacts: List of contact information
            source: Source of the lead
            tags: Tags to associate with the lead
            
        Returns:
            Created Lead object
        """
        try:
            # Create company object
            company = Company(name=company_name)
            
            if company_data:
                # Update company with provided data
                for key, value in company_data.items():
                    if hasattr(company, key) and value is not None:
                        setattr(company, key, value)
            
            # Create contact objects
            contact_objects = []
            if contacts:
                for contact_data in contacts:
                    contact = Contact(**contact_data)
                    contact_objects.append(contact)
            
            # Create lead
            lead = Lead(
                company=company,
                contacts=contact_objects,
                source=source,
                tags=tags or []
            )
            
            # Store lead
            self._leads[lead.id] = lead
            
            logger.info(f"Created lead {lead.id} for company {company_name}")
            return lead
            
        except Exception as e:
            logger.error(f"Error creating lead: {str(e)}")
            raise ValidationError(f"Failed to create lead: {str(e)}")
    
    async def get_lead(self, lead_id: str) -> Optional[Lead]:
        """Get a lead by ID."""
        return self._leads.get(lead_id)
    
    async def list_leads(
        self, 
        status: Optional[LeadStatus] = None,
        tags: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> List[Lead]:
        """
        List leads with optional filtering.
        
        Args:
            status: Filter by lead status
            tags: Filter by tags
            limit: Maximum number of leads to return
            
        Returns:
            List of matching leads
        """
        leads = list(self._leads.values())
        
        # Apply filters
        if status:
            leads = [lead for lead in leads if lead.status == status]
        
        if tags:
            leads = [lead for lead in leads if any(tag in lead.tags for tag in tags)]
        
        # Sort by creation date (newest first)
        leads.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply limit
        if limit:
            leads = leads[:limit]
        
        return leads
    
    async def update_lead(self, lead_id: str, updates: Dict[str, Any]) -> Lead:
        """
        Update a lead.
        
        Args:
            lead_id: ID of the lead to update
            updates: Dictionary of updates to apply
            
        Returns:
            Updated Lead object
        """
        lead = self._leads.get(lead_id)
        if not lead:
            raise ValidationError(f"Lead {lead_id} not found")
        
        try:
            # Apply updates
            for key, value in updates.items():
                if hasattr(lead, key):
                    setattr(lead, key, value)
            
            lead.updated_at = datetime.utcnow()
            
            logger.info(f"Updated lead {lead_id}")
            return lead
            
        except Exception as e:
            logger.error(f"Error updating lead {lead_id}: {str(e)}")
            raise ValidationError(f"Failed to update lead: {str(e)}")
    
    async def delete_lead(self, lead_id: str) -> bool:
        """Delete a lead."""
        if lead_id in self._leads:
            del self._leads[lead_id]
            logger.info(f"Deleted lead {lead_id}")
            return True
        return False
    
    # Lead Enrichment Methods
    
    async def enrich_lead(
        self, 
        lead_id: str,
        sources: Optional[List[str]] = None,
        force_refresh: bool = False
    ) -> Lead:
        """
        Enrich a lead with data from external sources.
        
        Args:
            lead_id: ID of the lead to enrich
            sources: Specific sources to use for enrichment
            force_refresh: Whether to refresh existing data
            
        Returns:
            Enriched Lead object
        """
        lead = self._leads.get(lead_id)
        if not lead:
            raise ValidationError(f"Lead {lead_id} not found")
        
        try:
            enriched_lead = await self.enrichment_engine.enrich_lead(
                lead, sources, force_refresh
            )
            
            # Update stored lead
            self._leads[lead_id] = enriched_lead
            
            logger.info(f"Enriched lead {lead_id}")
            return enriched_lead
            
        except Exception as e:
            logger.error(f"Error enriching lead {lead_id}: {str(e)}")
            raise DataEnrichmentError(f"Lead enrichment failed: {str(e)}", lead_id=lead_id)
    
    async def enrich_leads_batch(
        self, 
        lead_ids: List[str],
        batch_size: int = 10,
        sources: Optional[List[str]] = None
    ) -> List[Lead]:
        """
        Enrich multiple leads in batches.
        
        Args:
            lead_ids: List of lead IDs to enrich
            batch_size: Number of leads to process concurrently
            sources: Specific sources to use for enrichment
            
        Returns:
            List of enriched leads
        """
        leads = []
        for lead_id in lead_ids:
            lead = self._leads.get(lead_id)
            if lead:
                leads.append(lead)
            else:
                logger.warning(f"Lead {lead_id} not found, skipping")
        
        if not leads:
            return []
        
        try:
            enriched_leads = await self.enrichment_engine.enrich_leads_batch(
                leads, batch_size, sources
            )
            
            # Update stored leads
            for enriched_lead in enriched_leads:
                self._leads[enriched_lead.id] = enriched_lead
            
            logger.info(f"Enriched {len(enriched_leads)} leads in batch")
            return enriched_leads
            
        except Exception as e:
            logger.error(f"Error in batch enrichment: {str(e)}")
            raise DataEnrichmentError(f"Batch enrichment failed: {str(e)}")
    
    # Lead Scoring Methods
    
    async def score_lead(self, lead_id: str) -> Lead:
        """
        Score a lead using AI-powered analysis.
        
        Args:
            lead_id: ID of the lead to score
            
        Returns:
            Lead with updated score
        """
        lead = self._leads.get(lead_id)
        if not lead:
            raise ValidationError(f"Lead {lead_id} not found")
        
        try:
            score = await self.lead_scorer.score_lead(lead)
            lead.score = score
            lead.updated_at = datetime.utcnow()
            
            # Update lead status based on score
            if score.overall_score >= 80:
                lead.status = LeadStatus.QUALIFIED
                lead.add_tag("high-priority")
            elif score.overall_score >= 60:
                lead.status = LeadStatus.QUALIFIED
                lead.add_tag("medium-priority")
            elif score.overall_score >= 40:
                lead.status = LeadStatus.NEW
                lead.add_tag("low-priority")
            else:
                lead.status = LeadStatus.DISQUALIFIED
                lead.add_tag("disqualified")
            
            logger.info(f"Scored lead {lead_id}: {score.overall_score:.2f}/100")
            return lead
            
        except Exception as e:
            logger.error(f"Error scoring lead {lead_id}: {str(e)}")
            raise DataEnrichmentError(f"Lead scoring failed: {str(e)}", lead_id=lead_id)
    
    async def score_leads_batch(self, lead_ids: List[str]) -> List[Lead]:
        """Score multiple leads."""
        leads = []
        for lead_id in lead_ids:
            lead = self._leads.get(lead_id)
            if lead:
                leads.append(lead)
        
        if not leads:
            return []
        
        try:
            scores = await self.lead_scorer.score_leads_batch(leads)
            
            # Apply scores to leads
            for lead, score in zip(leads, scores):
                lead.score = score
                lead.updated_at = datetime.utcnow()
                
                # Update status based on score
                if score.overall_score >= 80:
                    lead.status = LeadStatus.QUALIFIED
                    lead.add_tag("high-priority")
                elif score.overall_score >= 60:
                    lead.status = LeadStatus.QUALIFIED
                    lead.add_tag("medium-priority")
                elif score.overall_score >= 40:
                    lead.status = LeadStatus.NEW
                    lead.add_tag("low-priority")
                else:
                    lead.status = LeadStatus.DISQUALIFIED
                    lead.add_tag("disqualified")
            
            logger.info(f"Scored {len(leads)} leads in batch")
            return leads
            
        except Exception as e:
            logger.error(f"Error in batch scoring: {str(e)}")
            raise DataEnrichmentError(f"Batch scoring failed: {str(e)}")
    
    # Workflow Methods
    
    async def process_lead_complete(
        self, 
        lead_id: str,
        enrich: bool = True,
        score: bool = True,
        sources: Optional[List[str]] = None
    ) -> Lead:
        """
        Complete lead processing workflow (enrich + score).
        
        Args:
            lead_id: ID of the lead to process
            enrich: Whether to enrich the lead
            score: Whether to score the lead
            sources: Specific sources for enrichment
            
        Returns:
            Fully processed Lead object
        """
        lead = self._leads.get(lead_id)
        if not lead:
            raise ValidationError(f"Lead {lead_id} not found")
        
        try:
            logger.info(f"Starting complete processing for lead {lead_id}")
            
            # Enrichment phase
            if enrich:
                lead = await self.enrich_lead(lead_id, sources)
            
            # Scoring phase
            if score:
                lead = await self.score_lead(lead_id)
            
            logger.info(f"Completed processing for lead {lead_id}")
            return lead
            
        except Exception as e:
            logger.error(f"Error in complete processing for lead {lead_id}: {str(e)}")
            raise OutreachSDKError(f"Complete processing failed: {str(e)}")
    
    async def process_leads_batch_complete(
        self, 
        lead_ids: List[str],
        batch_size: int = 10,
        enrich: bool = True,
        score: bool = True,
        sources: Optional[List[str]] = None
    ) -> List[Lead]:
        """
        Complete batch processing workflow.
        
        Args:
            lead_ids: List of lead IDs to process
            batch_size: Batch size for processing
            enrich: Whether to enrich leads
            score: Whether to score leads
            sources: Specific sources for enrichment
            
        Returns:
            List of fully processed leads
        """
        try:
            logger.info(f"Starting batch processing for {len(lead_ids)} leads")
            
            # Enrichment phase
            if enrich:
                await self.enrich_leads_batch(lead_ids, batch_size, sources)
            
            # Scoring phase
            if score:
                await self.score_leads_batch(lead_ids)
            
            # Return processed leads
            processed_leads = []
            for lead_id in lead_ids:
                lead = self._leads.get(lead_id)
                if lead:
                    processed_leads.append(lead)
            
            logger.info(f"Completed batch processing for {len(processed_leads)} leads")
            return processed_leads
            
        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
            raise OutreachSDKError(f"Batch processing failed: {str(e)}")
    
    # Analytics Methods
    
    async def get_lead_analytics(self) -> Dict[str, Any]:
        """Get analytics about leads."""
        leads = list(self._leads.values())
        
        if not leads:
            return {
                "total_leads": 0,
                "status_breakdown": {},
                "average_score": 0,
                "top_industries": [],
                "top_technologies": []
            }
        
        # Status breakdown
        status_counts = {}
        for lead in leads:
            status = lead.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Score statistics
        scores = [lead.score.overall_score for lead in leads if lead.score]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Industry breakdown
        industries = {}
        for lead in leads:
            if lead.company.industry:
                industry = lead.company.industry.value
                industries[industry] = industries.get(industry, 0) + 1
        
        top_industries = sorted(industries.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Technology breakdown
        tech_counts = {}
        for lead in leads:
            for tech in lead.company.technologies:
                tech_counts[tech] = tech_counts.get(tech, 0) + 1
        
        top_technologies = sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_leads": len(leads),
            "status_breakdown": status_counts,
            "average_score": round(avg_score, 2),
            "score_distribution": {
                "high (80+)": len([s for s in scores if s >= 80]),
                "medium (60-79)": len([s for s in scores if 60 <= s < 80]),
                "low (40-59)": len([s for s in scores if 40 <= s < 60]),
                "very_low (<40)": len([s for s in scores if s < 40])
            },
            "top_industries": top_industries,
            "top_technologies": top_technologies,
            "enrichment_stats": self._get_enrichment_stats(leads),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _get_enrichment_stats(self, leads: List[Lead]) -> Dict[str, Any]:
        """Get enrichment statistics."""
        enriched_count = 0
        total_sources = 0
        source_success = {}
        
        for lead in leads:
            if 'enrichment' in lead.metadata:
                enriched_count += 1
                enrichment_data = lead.metadata['enrichment']
                
                sources_used = enrichment_data.get('sources_used', [])
                total_sources += len(sources_used)
                
                for source in sources_used:
                    if source not in source_success:
                        source_success[source] = 0
                    source_success[source] += 1
        
        return {
            "enriched_leads": enriched_count,
            "enrichment_rate": round(enriched_count / len(leads) * 100, 2) if leads else 0,
            "avg_sources_per_lead": round(total_sources / enriched_count, 2) if enriched_count else 0,
            "source_usage": source_success
        }
    
    # Utility Methods
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on SDK components."""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {}
        }
        
        # Check AI client
        try:
            from .ai.clients import test_ai_client
            ai_healthy = await test_ai_client(self.ai_client)
            health_status["components"]["ai_client"] = "healthy" if ai_healthy else "unhealthy"
        except Exception as e:
            health_status["components"]["ai_client"] = f"error: {str(e)}"
        
        # Check enrichment sources
        try:
            available_sources = list(self.enrichment_engine.sources.keys())
            health_status["components"]["enrichment_sources"] = {
                "available": available_sources,
                "count": len(available_sources)
            }
        except Exception as e:
            health_status["components"]["enrichment_sources"] = f"error: {str(e)}"
        
        # Check configuration
        validation_results = validate_configuration(self.config)
        health_status["components"]["configuration"] = {
            "valid": validation_results["valid"],
            "warnings": len(validation_results["warnings"]),
            "errors": len(validation_results["errors"])
        }
        
        # Overall status
        component_statuses = [
            status for status in health_status["components"].values() 
            if isinstance(status, str)
        ]
        
        if any("error" in status or status == "unhealthy" for status in component_statuses):
            health_status["status"] = "degraded"
        
        return health_status
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get general SDK statistics."""
        return {
            "leads_count": len(self._leads),
            "campaigns_count": len(self._campaigns),
            "config_valid": validate_configuration(self.config)["valid"],
            "available_sources": list(self.enrichment_engine.sources.keys()),
            "sdk_version": "1.0.0",
            "uptime": datetime.utcnow().isoformat()
        }
    
    # Context manager support
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # Cleanup resources if needed
        if hasattr(self.enrichment_engine, 'cleanup'):
            await self.enrichment_engine.cleanup()
        
        logger.info("OutreachSDK session ended")