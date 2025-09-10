"""
Custom exceptions for the SDK Outreach system.
"""

from typing import Optional, Dict, Any


class OutreachSDKError(Exception):
    """Base exception for all SDK Outreach errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class APIError(OutreachSDKError):
    """Raised when an external API call fails."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        api_name: Optional[str] = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}
        self.api_name = api_name


class RateLimitError(APIError):
    """Raised when API rate limits are exceeded."""
    
    def __init__(
        self, 
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        api_name: Optional[str] = None
    ):
        super().__init__(message, status_code=429, api_name=api_name)
        self.retry_after = retry_after


class ValidationError(OutreachSDKError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message)
        self.field = field


class DataEnrichmentError(OutreachSDKError):
    """Raised when data enrichment processes fail."""
    
    def __init__(
        self, 
        message: str, 
        source: Optional[str] = None,
        lead_id: Optional[str] = None
    ):
        super().__init__(message)
        self.source = source
        self.lead_id = lead_id


class DatabaseError(OutreachSDKError):
    """Raised when database operations fail."""
    pass


class ConfigurationError(OutreachSDKError):
    """Raised when configuration is invalid or missing."""
    pass


class AIProcessingError(OutreachSDKError):
    """Raised when AI processing fails."""
    
    def __init__(
        self, 
        message: str, 
        model: Optional[str] = None,
        prompt: Optional[str] = None
    ):
        super().__init__(message)
        self.model = model
        self.prompt = prompt


class ScrapingError(OutreachSDKError):
    """Raised when web scraping fails."""
    
    def __init__(
        self, 
        message: str, 
        url: Optional[str] = None,
        status_code: Optional[int] = None
    ):
        super().__init__(message)
        self.url = url
        self.status_code = status_code