"""
SDK Outreach - Sophisticated B2B Lead Generation and Outreach Automation

A comprehensive SDK for automating lead generation, enrichment, qualification,
and personalized outreach campaigns.
"""

__version__ = "1.0.0"
__author__ = "TIN Developers"
__email__ = "contact@tindevelopers.com"

from .client import OutreachSDK
from .models import Lead, Company, Contact, Campaign
from .exceptions import (
    OutreachSDKError,
    APIError,
    RateLimitError,
    ValidationError,
    DataEnrichmentError,
)

__all__ = [
    "OutreachSDK",
    "Lead",
    "Company", 
    "Contact",
    "Campaign",
    "OutreachSDKError",
    "APIError",
    "RateLimitError",
    "ValidationError",
    "DataEnrichmentError",
]