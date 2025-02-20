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
        
        # Variable type
        var_type = schema["type"]
        console.print(f"Type: {var_type}")

        # Default value
        if questionary.confirm(
            f"Set default value for {var_name}?",
            default=False
        ).ask():
            if var_type == "string":
                default = questionary.text(
                    "Default value:"
                ).ask()
            elif var_type == "number":
                default = questionary.text(
                    "Default value:",
                    validate=lambda text: text.replace(".", "").isdigit()
                ).ask()
            elif var_type == "date":
                default = questionary.text(
                    "Default value (YYYY-MM-DD):",
                    validate=lambda text: len(text.split("-")) == 3
                ).ask()
            elif var_type == "array":
                default = []
            elif var_type == "object":
                default = {}
            
            config[var_name] = {
                "type": var_type,
                "required": schema["required"],
                "default": default
            }
        else:
            config[var_name] = {
                "type": var_type,
                "required": schema["required"]
            }

        # Validation
        if questionary.confirm(
            f"Add validation for {var_name}?",
            default=False
        ).ask():
            validation = {}
            
            if var_type == "string":
                if questionary.confirm("Add minimum length?").ask():
                    validation["min_length"] = int(questionary.text(
                        "Minimum length:",
                        validate=lambda text: text.isdigit()
                    ).ask())
                
                if questionary.confirm("Add maximum length?").ask():
                    validation["max_length"] = int(questionary.text(
                        "Maximum length:",
                        validate=lambda text: text.isdigit()
                    ).ask())
                
                if questionary.confirm("Add pattern match?").ask():
                    validation["pattern"] = questionary.text(
                        "Regex pattern:"
                    ).ask()
            
            elif var_type == "number":
                if questionary.confirm("Add minimum value?").ask():
                    validation["min_value"] = float(questionary.text(
                        "Minimum value:",
                        validate=lambda text: text.replace(".", "").isdigit()
                    ).ask())
                
                if questionary.confirm("Add maximum value?").ask():
                    validation["max_value"] = float(questionary.text(
                        "Maximum value:",
                        validate=lambda text: text.replace(".", "").isdigit()
                    ).ask())
            
            if validation:
                config[var_name]["validation"] = validation

    return config

def get_example_content(type_id: str) -> str:
    """Get example template content."""
    if type_id == "email":
        return """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .header { background: #f5f5f5; padding: 20px; }
        .content { padding: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ subject }}</h1>
    </div>
    <div class="content">
        <p>Dear {{ recipient_name }},</p>
        
        {{ content }}
        
        <p>Best regards,<br>{{ sender_name }}</p>
    </div>
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
    elif type_id == "document":
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
    else:
        return ""

def save_template(info: Dict[str, Any], variables: Dict[str, Any], path: str):
    """Save template configuration."""
    config = {
        "type": info["type"],
        "name": info["name"],
        "description": info["description"],
        "content": info["content"],
        "variables": variables
    }

    # Create directory if needed
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Save config
    with open(path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    console.print(f"\n[green]Template saved to {path}[/green]")

    # Show preview
    console.print("\n[bold]Template Preview:[/bold]")
    console.print(Syntax(
        yaml.dump(config, default_flow_style=False),
        "yaml",
        theme="monokai"
    ))

@click.command()
@click.option(
    "--output",
    default="templates/new.yaml",
    help="Output file path"
)
def create_template(output: str):
    """Create a new template interactively."""
    # Show template types
    show_template_info()

    # Select type
    type_id = select_template_type()

    # Collect information
    info = collect_template_info(type_id)
    info["type"] = type_id

    # Configure variables
    variables = configure_variables(type_id)

    # Save template
    save_template(info, variables, output)

    console.print("\n[bold green]Template created successfully![/bold green]")

if __name__ == "__main__":
    create_template()