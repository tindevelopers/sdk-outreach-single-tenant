"""
Configuration management for the SDK Outreach system.
"""

import os
from typing import Optional, Dict, Any, List
from pydantic import BaseSettings, Field, validator
from functools import lru_cache


class DatabaseConfig(BaseSettings):
    """Database configuration."""
    url: str = Field(default="sqlite:///./sdk_outreach.db", env="DATABASE_URL")
    echo: bool = Field(default=False, env="DATABASE_ECHO")
    pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")


class RedisConfig(BaseSettings):
    """Redis configuration."""
    url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    max_connections: int = Field(default=10, env="REDIS_MAX_CONNECTIONS")
    socket_timeout: int = Field(default=30, env="REDIS_SOCKET_TIMEOUT")


class APIConfig(BaseSettings):
    """External API configuration."""
    outscraper_api_key: Optional[str] = Field(default=None, env="OUTSCRAPER_API_KEY")
    openrouter_api_key: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    
    # Google Services
    google_sheets_credentials_path: Optional[str] = Field(
        default=None, env="GOOGLE_SHEETS_CREDENTIALS_PATH"
    )
    google_sheets_spreadsheet_id: Optional[str] = Field(
        default=None, env="GOOGLE_SHEETS_SPREADSHEET_ID"
    )
    
    # Email Services
    sendgrid_api_key: Optional[str] = Field(default=None, env="SENDGRID_API_KEY")
    mailgun_api_key: Optional[str] = Field(default=None, env="MAILGUN_API_KEY")
    mailgun_domain: Optional[str] = Field(default=None, env="MAILGUN_DOMAIN")
    
    # LinkedIn (Optional)
    linkedin_username: Optional[str] = Field(default=None, env="LINKEDIN_USERNAME")
    linkedin_password: Optional[str] = Field(default=None, env="LINKEDIN_PASSWORD")


class AIConfig(BaseSettings):
    """AI configuration."""
    default_model: str = Field(default="anthropic/claude-3.5-sonnet", env="DEFAULT_AI_MODEL")
    temperature: float = Field(default=0.7, env="AI_TEMPERATURE")
    max_tokens: int = Field(default=4000, env="MAX_TOKENS")
    timeout: int = Field(default=60, env="AI_TIMEOUT")
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if not 0 <= v <= 2:
            raise ValueError('Temperature must be between 0 and 2')
        return v


class RateLimitConfig(BaseSettings):
    """Rate limiting configuration."""
    per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    per_hour: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")
    per_day: int = Field(default=10000, env="RATE_LIMIT_PER_DAY")
    concurrent_requests: int = Field(default=10, env="MAX_CONCURRENT_REQUESTS")


class ScrapingConfig(BaseSettings):
    """Web scraping configuration."""
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")
    retry_attempts: int = Field(default=3, env="RETRY_ATTEMPTS")
    retry_delay: float = Field(default=1.0, env="RETRY_DELAY")
    user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        env="USER_AGENT"
    )
    use_proxy: bool = Field(default=False, env="USE_PROXY")
    proxy_list: List[str] = Field(default_factory=list, env="PROXY_LIST")


class MonitoringConfig(BaseSettings):
    """Monitoring and logging configuration."""
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    prometheus_port: int = Field(default=8000, env="PROMETHEUS_PORT")
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of {valid_levels}')
        return v.upper()


class AppConfig(BaseSettings):
    """Main application configuration."""
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    secret_key: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8080, env="API_PORT")
    
    # Component configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    apis: APIConfig = Field(default_factory=APIConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    rate_limits: RateLimitConfig = Field(default_factory=RateLimitConfig)
    scraping: ScrapingConfig = Field(default_factory=ScrapingConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @validator('environment')
    def validate_environment(cls, v):
        valid_envs = ['development', 'staging', 'production']
        if v.lower() not in valid_envs:
            raise ValueError(f'Environment must be one of {valid_envs}')
        return v.lower()

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"

    def get_api_keys(self) -> Dict[str, Optional[str]]:
        """Get all API keys for validation."""
        return {
            "outscraper": self.apis.outscraper_api_key,
            "openrouter": self.apis.openrouter_api_key,
            "anthropic": self.apis.anthropic_api_key,
            "openai": self.apis.openai_api_key,
            "sendgrid": self.apis.sendgrid_api_key,
            "mailgun": self.apis.mailgun_api_key,
        }

    def validate_required_keys(self, required_keys: List[str]) -> List[str]:
        """Validate that required API keys are present."""
        api_keys = self.get_api_keys()
        missing_keys = []
        
        for key in required_keys:
            if key not in api_keys or not api_keys[key]:
                missing_keys.append(key)
        
        return missing_keys


@lru_cache()
def get_config() -> AppConfig:
    """Get cached application configuration."""
    return AppConfig()


def load_config_from_file(file_path: str) -> AppConfig:
    """Load configuration from a specific file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    
    # Temporarily set the env file path
    original_env_file = AppConfig.Config.env_file
    AppConfig.Config.env_file = file_path
    
    try:
        config = AppConfig()
        return config
    finally:
        # Restore original env file path
        AppConfig.Config.env_file = original_env_file


def validate_configuration(config: AppConfig) -> Dict[str, Any]:
    """Validate configuration and return validation results."""
    results = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "missing_optional_keys": []
    }
    
    # Check required API keys for basic functionality
    required_keys = ["outscraper"]  # Minimum required for basic lead scraping
    missing_required = config.validate_required_keys(required_keys)
    
    if missing_required:
        results["valid"] = False
        results["errors"].extend([
            f"Missing required API key: {key}" for key in missing_required
        ])
    
    # Check optional but recommended keys
    optional_keys = ["openrouter", "anthropic", "sendgrid"]
    missing_optional = config.validate_required_keys(optional_keys)
    results["missing_optional_keys"] = missing_optional
    
    if missing_optional:
        results["warnings"].extend([
            f"Missing optional API key (reduced functionality): {key}" 
            for key in missing_optional
        ])
    
    # Validate database URL format
    if not config.database.url:
        results["valid"] = False
        results["errors"].append("Database URL is required")
    
    # Validate Redis URL format
    if not config.redis.url:
        results["warnings"].append("Redis URL not configured (caching disabled)")
    
    return results