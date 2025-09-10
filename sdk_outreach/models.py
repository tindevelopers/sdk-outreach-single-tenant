"""
Data models for the SDK Outreach system.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, EmailStr, HttpUrl, validator
import uuid


class LeadStatus(str, Enum):
    """Lead processing status."""
    NEW = "new"
    ENRICHING = "enriching"
    QUALIFIED = "qualified"
    DISQUALIFIED = "disqualified"
    CONTACTED = "contacted"
    RESPONDED = "responded"
    CONVERTED = "converted"
    FAILED = "failed"


class CompanySize(str, Enum):
    """Company size categories."""
    STARTUP = "startup"  # 1-10 employees
    SMALL = "small"      # 11-50 employees
    MEDIUM = "medium"    # 51-200 employees
    LARGE = "large"      # 201-1000 employees
    ENTERPRISE = "enterprise"  # 1000+ employees


class Industry(str, Enum):
    """Industry categories."""
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    EDUCATION = "education"
    REAL_ESTATE = "real_estate"
    CONSULTING = "consulting"
    MARKETING = "marketing"
    OTHER = "other"


class ContactRole(str, Enum):
    """Contact role types."""
    CEO = "ceo"
    CTO = "cto"
    DEVELOPER = "developer"
    PRODUCT_MANAGER = "product_manager"
    MARKETING = "marketing"
    SALES = "sales"
    OTHER = "other"


class SocialProfile(BaseModel):
    """Social media profile information."""
    platform: str
    url: HttpUrl
    followers: Optional[int] = None
    verified: Optional[bool] = None
    last_updated: Optional[datetime] = None


class Contact(BaseModel):
    """Contact information model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[ContactRole] = None
    title: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None
    social_profiles: List[SocialProfile] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit():
            raise ValueError('Invalid phone number format')
        return v


class Company(BaseModel):
    """Company information model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    domain: Optional[str] = None
    website: Optional[HttpUrl] = None
    description: Optional[str] = None
    industry: Optional[Industry] = None
    size: Optional[CompanySize] = None
    employee_count: Optional[int] = None
    founded_year: Optional[int] = None
    headquarters: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None
    social_profiles: List[SocialProfile] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    funding_info: Optional[Dict[str, Any]] = None
    annual_revenue: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('employee_count')
    def validate_employee_count(cls, v):
        if v is not None and v < 0:
            raise ValueError('Employee count must be non-negative')
        return v

    @validator('founded_year')
    def validate_founded_year(cls, v):
        if v is not None and (v < 1800 or v > datetime.now().year):
            raise ValueError('Founded year must be reasonable')
        return v


class LeadScore(BaseModel):
    """Lead scoring information."""
    overall_score: float = Field(ge=0, le=100)
    company_fit_score: float = Field(ge=0, le=100)
    contact_quality_score: float = Field(ge=0, le=100)
    engagement_potential_score: float = Field(ge=0, le=100)
    technology_fit_score: float = Field(ge=0, le=100)
    scoring_factors: Dict[str, Any] = Field(default_factory=dict)
    scored_at: datetime = Field(default_factory=datetime.utcnow)


class Lead(BaseModel):
    """Main lead model combining company and contact information."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company: Company
    contacts: List[Contact] = Field(default_factory=list)
    status: LeadStatus = LeadStatus.NEW
    score: Optional[LeadScore] = None
    source: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    qualification_notes: Optional[str] = None
    last_contacted: Optional[datetime] = None
    next_follow_up: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def get_primary_contact(self) -> Optional[Contact]:
        """Get the primary contact for this lead."""
        if not self.contacts:
            return None
        
        # Prioritize by role
        priority_roles = [ContactRole.CTO, ContactRole.CEO, ContactRole.DEVELOPER, ContactRole.PRODUCT_MANAGER]
        for role in priority_roles:
            for contact in self.contacts:
                if contact.role == role:
                    return contact
        
        # Return first contact if no priority role found
        return self.contacts[0]

    def add_tag(self, tag: str) -> None:
        """Add a tag to the lead."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()

    def update_status(self, status: LeadStatus, notes: Optional[str] = None) -> None:
        """Update lead status."""
        self.status = status
        self.updated_at = datetime.utcnow()
        if notes:
            self.notes = notes


class CampaignType(str, Enum):
    """Campaign types."""
    EMAIL = "email"
    LINKEDIN = "linkedin"
    PHONE = "phone"
    MULTI_CHANNEL = "multi_channel"


class CampaignStatus(str, Enum):
    """Campaign status."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MessageTemplate(BaseModel):
    """Message template for campaigns."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    subject: Optional[str] = None
    content: str
    variables: List[str] = Field(default_factory=list)
    channel: CampaignType
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Campaign(BaseModel):
    """Outreach campaign model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    type: CampaignType
    status: CampaignStatus = CampaignStatus.DRAFT
    target_leads: List[str] = Field(default_factory=list)  # Lead IDs
    message_templates: List[MessageTemplate] = Field(default_factory=list)
    schedule: Optional[Dict[str, Any]] = None
    settings: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class EnrichmentResult(BaseModel):
    """Result of data enrichment process."""
    lead_id: str
    source: str
    success: bool
    data: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    enriched_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time: Optional[float] = None


class APIResponse(BaseModel):
    """Standard API response model."""
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    errors: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)