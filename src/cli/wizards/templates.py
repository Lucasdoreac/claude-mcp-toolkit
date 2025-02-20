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
        
        var_config = {}
        
        # Required/optional
        if not schema.get("required"):
            var_config["required"] = questionary.confirm(
                "Make this variable required?",
                default=False
            ).ask()
        
        # Default value
        if questionary.confirm(
            "Set default value?",
            default=False
        ).ask():
            var_config["default"] = questionary.text(
                "Default value:"
            ).ask()
        
        # Validation
        if questionary.confirm(
            "Add validation?",
            default=False
        ).ask():
            var_config["validation"] = configure_validation(schema["type"])
        
        config[var_name] = var_config

    return config

def configure_validation(var_type: str) -> Dict[str, Any]:
    """Configure variable validation."""
    validation = {}

    if var_type == "string":
        if questionary.confirm("Add minimum length?", default=False).ask():
            validation["min_length"] = int(questionary.text(
                "Minimum length:",
                validate=lambda text: text.isdigit()
            ).ask())

        if questionary.confirm("Add maximum length?", default=False).ask():
            validation["max_length"] = int(questionary.text(
                "Maximum length:",
                validate=lambda text: text.isdigit()
            ).ask())

        if questionary.confirm("Add regex pattern?", default=False).ask():
            validation["pattern"] = questionary.text(
                "Regex pattern:"
            ).ask()

    elif var_type == "number":
        if questionary.confirm("Add minimum value?", default=False).ask():
            validation["min_value"] = float(questionary.text(
                "Minimum value:",
                validate=lambda text: text.replace(".", "").isdigit()
            ).ask())

        if questionary.confirm("Add maximum value?", default=False).ask():
            validation["max_value"] = float(questionary.text(
                "Maximum value:",
                validate=lambda text: text.replace(".", "").isdigit()
            ).ask())

    elif var_type == "array":
        if questionary.confirm("Add minimum items?", default=False).ask():
            validation["min_items"] = int(questionary.text(
                "Minimum items:",
                validate=lambda text: text.isdigit()
            ).ask())

        if questionary.confirm("Add maximum items?", default=False).ask():
            validation["max_items"] = int(questionary.text(
                "Maximum items:",
                validate=lambda text: text.isdigit()
            ).ask())

    return validation

def configure_rendering() -> Dict[str, Any]:
    """Configure template rendering."""
    config = {}

    console.print("\n[bold]Rendering Configuration[/bold]")

    # Cache settings
    config["cache"] = questionary.confirm(
        "Enable result caching?",
        default=True
    ).ask()

    if config["cache"]:
        config["cache_ttl"] = int(questionary.text(
            "Cache TTL in seconds:",
            default="3600",
            validate=lambda text: text.isdigit()
        ).ask())

    # Format settings
    config["strip_whitespace"] = questionary.confirm(
        "Strip extra whitespace?",
        default=True
    ).ask()

    config["escape_html"] = questionary.confirm(
        "Escape HTML in variables?",
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
            <p>Dear {{recipient_name}},</p>
            
            <p>{{content}}</p>
            
            <p>Best regards,<br>
            {{sender_name}}</p>
        </body>
        </html>
        """
    elif type_id == "proposal":
        return """
        # {{title}}

        Dear {{client_name}},

        Thank you for your interest. Here is our proposal:

        ## Items
        {% for item in items %}
        - {{item.name}}: ${{item.price}}
        {% endfor %}

        **Total Value:** ${{deal_value}}

        ## Payment Terms
        {{payment_terms}}

        Valid until: {{valid_until}}
        """
    else:
        return """
        # {{title}}

        Author: {{author}}

        {{content}}

        {% if metadata %}
        ## Metadata
        {% for key, value in metadata.items() %}
        - {{key}}: {{value}}
        {% endfor %}
        {% endif %}
        """

def save_template_config(config: Dict[str, Any], path: str):
    """Save template configuration."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    with open(path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    
    console.print(f"\n[green]Template configuration saved to {path}[/green]")
    
    console.print("\n[bold]Configuration Preview:[/bold]")
    console.print(Syntax(
        yaml.dump(config, default_flow_style=False),
        "yaml",
        theme="monokai"
    ))

@click.command()
@click.option(
    "--config",
    default="templates/config.yaml",
    help="Configuration file path"
)
def setup_template(config: str):
    """Run template setup wizard."""
    console.print(Panel(
        "[bold blue]Template Configuration Wizard[/bold blue]\n\n"
        "This wizard will help you configure a new template."
    ))

    # Show available types
    show_template_info()

    # Collect configuration
    template_type = select_template_type()
    template_info = collect_template_info(template_type)
    variables_config = configure_variables(template_type)
    rendering_config = configure_rendering()

    # Build config
    config_data = {
        "type": template_type,
        "info": template_info,
        "variables": variables_config,
        "rendering": rendering_config
    }

    # Save configuration
    save_template_config(config_data, config)

if __name__ == "__main__":
    setup_template()