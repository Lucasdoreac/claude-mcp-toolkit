"""
Template configuration wizard.
"""
import os
import click
import questionary
import yaml
from typing import Dict, Any
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.table import Table

console = Console()

TEMPLATE_TYPES = {
    "email": {
        "name": "Email Template",
        "description": "Email templates with HTML support",
        "variables": {
            "subject": {"type": "string", "required": True},
            "recipient_name": {"type": "string", "required": True},
            "recipient_email": {"type": "string", "required": True},
            "sender_name": {"type": "string", "required": True},
            "content": {"type": "string", "required": True}
        }
    },
    "proposal": {
        "name": "Proposal Template",
        "description": "Sales proposals with markdown support",
        "variables": {
            "client_name": {"type": "string", "required": True},
            "deal_value": {"type": "number", "required": True},
            "valid_until": {"type": "date", "required": True},
            "items": {"type": "array", "required": True},
            "payment_terms": {"type": "string", "required": True}
        }
    },
    "document": {
        "name": "Document Template",
        "description": "Generic document templates",
        "variables": {
            "title": {"type": "string", "required": True},
            "author": {"type": "string", "required": True},
            "content": {"type": "string", "required": True},
            "metadata": {"type": "object", "required": False}
        }
    }
}

def show_template_info():
    """Show available template types."""
    table = Table(title="Available Template Types")
    table.add_column("Type")
    table.add_column("Description")
    table.add_column("Required Variables")

    for type_id, info in TEMPLATE_TYPES.items():
        required_vars = ", ".join(
            name for name, schema in info["variables"].items()
            if schema.get("required")
        )
        table.add_row(type_id, info["description"], required_vars)

    console.print(table)

def select_template_type() -> str:
    """Select template type."""
    choices = [
        {
            "name": f"{info['name']} ({type_id})",
            "value": type_id
        }
        for type_id, info in TEMPLATE_TYPES.items()
    ]

    return questionary.select(
        "Select template type:",
        choices=choices
    ).ask()

def collect_template_info(type_id: str) -> Dict[str, Any]:
    """Collect template information."""
    info = {}

    # Basic info
    info["name"] = questionary.text(
        "Template name:",
        validate=lambda text: len(text) >= 3
    ).ask()

    info["description"] = questionary.text(
        "Template description (optional):"
    ).ask()

    # Content source
    source = questionary.select(
        "Template content source:",
        choices=[
            "Create new",
            "Load from file",
            "Use example"
        ]
    ).ask()

    if source == "Create new":
        info["content"] = click.edit()
    elif source == "Load from file":
        file_path = questionary.text(
            "Template file path:"
        ).ask()
        with open(file_path, "r") as f:
            info["content"] = f.read()
    else:
        info["content"] = get_example_content(type_id)

    return info

def configure_variables(type_id: str) -> Dict[str, Any]:
    """Configure template variables."""
    template_vars = TEMPLATE_TYPES[type_id]["variables"]
    config = {}

    console.print("\n[bold]Variable Configuration[/bold]")
    console.print("Configure how variables will be handled in the template.")

    for var_name, schema in template_vars.items():
        console.print(f"\n[bold]{var_name}[/bold]")
        
        # Basic config
        var_config = {
            "type": schema["type"],
            "required": schema["required"]
        }

        # Default value
        if questionary.confirm(
            f"Set default value for {var_name}?",
            default=False
        ).ask():
            var_config["default"] = questionary.text(
                "Default value:"
            ).ask()

        # Validation
        if questionary.confirm(
            f"Add validation for {var_name}?",
            default=False
        ).ask():
            validation = {}
            
            if schema["type"] == "string":
                validation["min_length"] = questionary.text(
                    "Minimum length:",
                    default="0"
                ).ask()
                validation["max_length"] = questionary.text(
                    "Maximum length:",
                    default="255"
                ).ask()
                validation["pattern"] = questionary.text(
                    "Regex pattern (optional):"
                ).ask()

            elif schema["type"] == "number":
                validation["min_value"] = questionary.text(
                    "Minimum value:",
                    default="0"
                ).ask()
                validation["max_value"] = questionary.text(
                    "Maximum value:"
                ).ask()

            elif schema["type"] == "array":
                validation["min_items"] = questionary.text(
                    "Minimum items:",
                    default="0"
                ).ask()
                validation["max_items"] = questionary.text(
                    "Maximum items:"
                ).ask()

            var_config["validation"] = validation

        # Description
        var_config["description"] = questionary.text(
            f"Description for {var_name} (optional):"
        ).ask()

        config[var_name] = var_config

    return config

def configure_rendering(type_id: str) -> Dict[str, Any]:
    """Configure template rendering options."""
    config = {}

    console.print("\n[bold]Rendering Configuration[/bold]")

    # Cache settings
    config["cache"] = questionary.confirm(
        "Enable template caching?",
        default=True
    ).ask()

    if config["cache"]:
        config["cache_ttl"] = questionary.text(
            "Cache TTL (seconds):",
            default="3600"
        ).ask()

    # Format options
    if type_id == "email":
        config["strip_html"] = questionary.confirm(
            "Strip HTML from plain text version?",
            default=True
        ).ask()

    elif type_id == "proposal":
        config["format"] = questionary.select(
            "Output format:",
            choices=["html", "pdf", "docx"]
        ).ask()

    # Escaping
    config["auto_escape"] = questionary.confirm(
        "Auto-escape variables?",
        default=True
    ).ask()

    return config

def get_example_content(type_id: str) -> str:
    """Get example template content."""
    if type_id == "email":
        return """
<!DOCTYPE html>
<html>
<body>
    <h1>Hello {{ recipient_name }}!</h1>
    <p>{{ content }}</p>
    <br>
    Best regards,<br>
    {{ sender_name }}
</body>
</html>
"""
    elif type_id == "proposal":
        return """
# {{ title }}

**Client:** {{ client_name }}  
**Value:** ${{ deal_value }}  
**Valid Until:** {{ valid_until }}

## Items

{% for item in items %}
- {{ item.name }}: ${{ item.value }}
{% endfor %}

## Payment Terms

{{ payment_terms }}
"""
    else:
        return """
# {{ title }}

Author: {{ author }}

{{ content }}

{% if metadata %}
---
{% for key, value in metadata.items() %}
{{ key }}: {{ value }}
{% endfor %}
{% endif %}
"""

def save_template_config(config: Dict[str, Any], path: str):
    """Save template configuration."""
    # Create directory if needed
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Save config
    with open(path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    console.print(f"\n[green]Template configuration saved to {path}[/green]")

    # Show preview
    console.print("\n[bold]Configuration Preview:[/bold]")
    console.print(Syntax(
        yaml.dump(config, default_flow_style=False),
        "yaml",
        theme="monokai"
    ))

@click.command()
@click.option(
    "--output",
    default="templates/config.yaml",
    help="Output configuration file"
)
def configure(output: str):
    """Configure template interactively."""
    show_template_info()

    # Select template type
    type_id = select_template_type()

    # Collect configuration
    config = {
        "type": type_id,
        **collect_template_info(type_id),
        "variables": configure_variables(type_id),
        "rendering": configure_rendering(type_id)
    }

    # Save configuration
    save_template_config(config, output)

    console.print("\n[bold green]Template configuration complete![/bold green]")

if __name__ == "__main__":
    configure()