"""
Integration providers configuration.
"""
from src.api.models.integration import IntegrationProvider

PROVIDERS = {
    # CRM Providers
    "hubspot": IntegrationProvider(
        id="hubspot",
        name="HubSpot",
        type="crm",
        description="Integrate with HubSpot CRM",
        auth_type="oauth2",
        config_schema={
            "sync_contacts": {"type": "boolean", "default": True},
            "sync_deals": {"type": "boolean", "default": True},
            "sync_interval": {"type": "number", "default": 3600}
        },
        credentials_schema={
            "client_id": {"type": "string", "required": True},
            "client_secret": {"type": "string", "required": True},
            "refresh_token": {"type": "string", "required": True}
        },
        features=["contacts", "deals", "tasks"],
        docs_url="https://developers.hubspot.com/"
    ),

    "pipedrive": IntegrationProvider(
        id="pipedrive",
        name="Pipedrive",
        type="crm",
        description="Integrate with Pipedrive CRM",
        auth_type="api_key",
        config_schema={
            "sync_persons": {"type": "boolean", "default": True},
            "sync_deals": {"type": "boolean", "default": True},
            "sync_interval": {"type": "number", "default": 3600}
        },
        credentials_schema={
            "api_token": {"type": "string", "required": True}
        },
        features=["contacts", "deals", "activities"],
        docs_url="https://developers.pipedrive.com/"
    ),

    # Payment Providers
    "stripe": IntegrationProvider(
        id="stripe",
        name="Stripe",
        type="payment",
        description="Process payments with Stripe",
        auth_type="api_key",
        config_schema={
            "webhook_enabled": {"type": "boolean", "default": True},
            "automatic_tax": {"type": "boolean", "default": False},
            "currency": {"type": "string", "default": "USD"}
        },
        credentials_schema={
            "publishable_key": {"type": "string", "required": True},
            "secret_key": {"type": "string", "required": True},
            "webhook_secret": {"type": "string", "required": False}
        },
        features=["payments", "subscriptions", "refunds"],
        docs_url="https://stripe.com/docs/api"
    ),

    # Email Providers
    "sendgrid": IntegrationProvider(
        id="sendgrid",
        name="SendGrid",
        type="email",
        description="Send emails via SendGrid",
        auth_type="api_key",
        config_schema={
            "from_email": {"type": "string", "required": True},
            "from_name": {"type": "string", "required": True},
            "track_opens": {"type": "boolean", "default": True},
            "track_clicks": {"type": "boolean", "default": True}
        },
        credentials_schema={
            "api_key": {"type": "string", "required": True}
        },
        features=["send", "templates", "analytics"],
        docs_url="https://docs.sendgrid.com/"
    ),

    # Calendar Providers
    "google_calendar": IntegrationProvider(
        id="google_calendar",
        name="Google Calendar",
        type="calendar",
        description="Integrate with Google Calendar",
        auth_type="oauth2",
        config_schema={
            "calendar_id": {"type": "string", "required": True},
            "sync_events": {"type": "boolean", "default": True},
            "sync_interval": {"type": "number", "default": 900}
        },
        credentials_schema={
            "client_id": {"type": "string", "required": True},
            "client_secret": {"type": "string", "required": True},
            "refresh_token": {"type": "string", "required": True}
        },
        features=["events", "attendees", "reminders"],
        docs_url="https://developers.google.com/calendar"
    ),

    # Storage Providers
    "aws_s3": IntegrationProvider(
        id="aws_s3",
        name="Amazon S3",
        type="storage",
        description="Store files in Amazon S3",
        auth_type="api_key",
        config_schema={
            "bucket_name": {"type": "string", "required": True},
            "region": {"type": "string", "required": True},
            "path_prefix": {"type": "string", "default": ""}
        },
        credentials_schema={
            "access_key_id": {"type": "string", "required": True},
            "secret_access_key": {"type": "string", "required": True}
        },
        features=["upload", "download", "delete"],
        docs_url="https://docs.aws.amazon.com/s3/"
    )
}

# Validation functions
def get_provider(provider_id: str) -> IntegrationProvider:
    """Get provider by ID."""
    if provider_id not in PROVIDERS:
        raise ValueError(f"Unknown provider: {provider_id}")
    return PROVIDERS[provider_id]

def get_providers_by_type(type: str) -> list[IntegrationProvider]:
    """Get all providers of a specific type."""
    return [p for p in PROVIDERS.values() if p.type == type]

def validate_config(provider: IntegrationProvider, config: dict) -> bool:
    """Validate provider configuration."""
    schema = provider.config_schema
    for key, field in schema.items():
        if field.get("required", False) and key not in config:
            return False
    return True

def validate_credentials(provider: IntegrationProvider, credentials: dict) -> bool:
    """Validate provider credentials."""
    schema = provider.credentials_schema
    for key, field in schema.items():
        if field.get("required", False) and key not in credentials:
            return False
    return True