"""
Interactive setup wizard for Claude MCP Toolkit.
"""
import os
import click
import questionary
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from typing import Dict, Any

console = Console()

def print_welcome():
    """Print welcome message."""
    console.print(Panel(
        """[bold blue]Welcome to Claude MCP Toolkit![/bold blue]

This wizard will help you set up and configure your environment.
We'll go through:
- API configuration
- Database setup
- Redis cache
- Email settings
- Integration providers
- Initial templates""",
        title="Setup Wizard"
    ))

def collect_api_config() -> Dict[str, Any]:
    """Collect API configuration."""
    console.print("\n[bold]API Configuration[/bold]")
    
    config = {}
    
    # API URL
    config["api_url"] = questionary.text(
        "API URL:",
        default="http://localhost:8000"
    ).ask()
    
    # Environment
    config["environment"] = questionary.select(
        "Select environment:",
        choices=["development", "staging", "production"]
    ).ask()
    
    # Debug mode
    if config["environment"] != "production":
        config["debug"] = questionary.confirm(
            "Enable debug mode?",
            default=True
        ).ask()
    
    return config

def collect_database_config() -> Dict[str, Any]:
    """Collect database configuration."""
    console.print("\n[bold]Database Configuration[/bold]")
    
    config = {}
    
    # Database type
    db_type = questionary.select(
        "Select database type:",
        choices=["PostgreSQL", "SQLite"]
    ).ask()
    
    config["db_type"] = db_type.lower()
    
    if db_type == "PostgreSQL":
        # PostgreSQL config
        config["db_host"] = questionary.text(
            "Database host:",
            default="localhost"
        ).ask()
        
        config["db_port"] = questionary.text(
            "Database port:",
            default="5432"
        ).ask()
        
        config["db_name"] = questionary.text(
            "Database name:",
            default="claude_mcp"
        ).ask()
        
        config["db_user"] = questionary.text(
            "Database user:",
            default="postgres"
        ).ask()
        
        config["db_password"] = questionary.password(
            "Database password:"
        ).ask()
    else:
        # SQLite config
        config["db_path"] = questionary.text(
            "Database file path:",
            default="db.sqlite3"
        ).ask()
    
    return config

def collect_redis_config() -> Dict[str, Any]:
    """Collect Redis configuration."""
    console.print("\n[bold]Redis Configuration[/bold]")
    
    config = {}
    
    # Enable Redis
    if not questionary.confirm(
        "Do you want to use Redis for caching?",
        default=True
    ).ask():
        return None
    
    config["redis_host"] = questionary.text(
        "Redis host:",
        default="localhost"
    ).ask()
    
    config["redis_port"] = questionary.text(
        "Redis port:",
        default="6379"
    ).ask()
    
    config["redis_db"] = questionary.text(
        "Redis database number:",
        default="0"
    ).ask()
    
    # Redis password
    if questionary.confirm(
        "Does Redis require authentication?",
        default=False
    ).ask():
        config["redis_password"] = questionary.password(
            "Redis password:"
        ).ask()
    
    return config

def collect_email_config() -> Dict[str, Any]:
    """Collect email configuration."""
    console.print("\n[bold]Email Configuration[/bold]")
    
    config = {}
    
    # Email provider
    provider = questionary.select(
        "Select email provider:",
        choices=["SMTP", "SendGrid", "None"]
    ).ask()
    
    if provider == "None":
        return None
    
    config["email_provider"] = provider.lower()
    
    if provider == "SMTP":
        # SMTP config
        config["smtp_host"] = questionary.text(
            "SMTP host:"
        ).ask()
        
        config["smtp_port"] = questionary.text(
            "SMTP port:",
            default="587"
        ).ask()
        
        config["smtp_user"] = questionary.text(
            "SMTP username:"
        ).ask()
        
        config["smtp_password"] = questionary.password(
            "SMTP password:"
        ).ask()
        
        config["smtp_tls"] = questionary.confirm(
            "Use TLS?",
            default=True
        ).ask()
    
    elif provider == "SendGrid":
        # SendGrid config
        config["sendgrid_api_key"] = questionary.password(
            "SendGrid API key:"
        ).ask()
    
    # Default from email
    config["default_from_email"] = questionary.text(
        "Default from email:"
    ).ask()
    
    return config

def collect_integration_config() -> Dict[str, Any]:
    """Collect integration configuration."""
    console.print("\n[bold]Integration Configuration[/bold]")
    
    config = {}
    
    # Available integrations
    integrations = {
        "hubspot": "HubSpot CRM",
        "stripe": "Stripe Payments",
        "google_calendar": "Google Calendar",
        "aws_s3": "AWS S3 Storage"
    }
    
    # Select integrations
    selected = questionary.checkbox(
        "Select integrations to configure:",
        choices=list(integrations.values())
    ).ask()
    
    for name, label in integrations.items():
        if label in selected:
            config[name] = collect_provider_config(name)
    
    return config

def collect_provider_config(provider: str) -> Dict[str, Any]:
    """Collect provider-specific configuration."""
    console.print(f"\n[bold]{provider.title()} Configuration[/bold]")
    
    config = {}
    
    if provider == "hubspot":
        config["client_id"] = questionary.password(
            "HubSpot client ID:"
        ).ask()
        config["client_secret"] = questionary.password(
            "HubSpot client secret:"
        ).ask()
    
    elif provider == "stripe":
        config["publishable_key"] = questionary.password(
            "Stripe publishable key:"
        ).ask()
        config["secret_key"] = questionary.password(
            "Stripe secret key:"
        ).ask()
        config["webhook_secret"] = questionary.password(
            "Stripe webhook secret:"
        ).ask()
    
    elif provider == "google_calendar":
        config["client_id"] = questionary.password(
            "Google client ID:"
        ).ask()
        config["client_secret"] = questionary.password(
            "Google client secret:"
        ).ask()
    
    elif provider == "aws_s3":
        config["access_key_id"] = questionary.password(
            "AWS access key ID:"
        ).ask()
        config["secret_access_key"] = questionary.password(
            "AWS secret access key:"
        ).ask()
        config["region"] = questionary.text(
            "AWS region:",
            default="us-east-1"
        ).ask()
        config["bucket"] = questionary.text(
            "S3 bucket name:"
        ).ask()
    
    return config

def collect_template_config() -> Dict[str, Any]:
    """Collect template configuration."""
    console.print("\n[bold]Template Configuration[/bold]")
    
    config = {}
    
    # Enable templates
    if not questionary.confirm(
        "Do you want to set up default templates?",
        default=True
    ).ask():
        return None
    
    # Template directory
    config["template_dir"] = questionary.text(
        "Template directory:",
        default="templates"
    ).ask()
    
    # Cache templates
    config["cache_templates"] = questionary.confirm(
        "Cache rendered templates?",
        default=True
    ).ask()
    
    if config["cache_templates"]:
        config["template_cache_ttl"] = questionary.text(
            "Template cache TTL (seconds):",
            default="3600"
        ).ask()
    
    return config

def generate_config(config: Dict[str, Any]) -> str:
    """Generate configuration file content."""
    return yaml.dump(config, default_flow_style=False)

def save_config(config: Dict[str, Any], path: str):
    """Save configuration to file."""
    # Create config directory if needed
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    # Save config
    with open(path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    
    console.print(f"\n[green]Configuration saved to {path}[/green]")
    
    # Show config preview
    console.print("\n[bold]Configuration Preview:[/bold]")
    console.print(Syntax(
        yaml.dump(config, default_flow_style=False),
        "yaml",
        theme="monokai"
    ))

@click.command()
@click.option(
    "--config",
    default="~/.mcp/config.yaml",
    help="Configuration file path"
)
def setup(config: str):
    """Run interactive setup."""
    print_welcome()
    
    config_data = {}
    
    # Collect configuration
    config_data["api"] = collect_api_config()
    config_data["database"] = collect_database_config()
    
    redis_config = collect_redis_config()
    if redis_config:
        config_data["redis"] = redis_config
    
    email_config = collect_email_config()
    if email_config:
        config_data["email"] = email_config
    
    integration_config = collect_integration_config()
    if integration_config:
        config_data["integrations"] = integration_config
    
    template_config = collect_template_config()
    if template_config:
        config_data["templates"] = template_config
    
    # Save configuration
    config_path = os.path.expanduser(config)
    save_config(config_data, config_path)
    
    console.print("\n[bold green]Setup complete![/bold green]")
    console.print(
        "\nYou can now start using Claude MCP Toolkit. "
        "Run 'mcp --help' to see available commands."
    )

if __name__ == "__main__":
    setup()