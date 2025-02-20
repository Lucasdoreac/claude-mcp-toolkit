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
        if schema["type"] == "string":
            config[var_name] = configure_string_var(var_name, schema)
        elif schema["type"] == "number":
            config[var_name] = configure_number_var(var_name, schema)
        elif schema["type"] == "date":
            config[var_name] = configure_date_var(var_name, schema)
        elif schema["type"] == "array":
            config[var_name] = configure_array_var(var_name, schema)
        elif schema["type"] == "object":
            config[var_name] = configure_object_var(var_name, schema)

    return config

def configure_string_var(name: str, schema: Dict) -> Dict[str, Any]:
    """Configure string variable."""
    config = {"type": "string"}

    # Validation
    if questionary.confirm(
        "Add validation?",
        default=False
    ).ask():
        config["min_length"] = questionary.text(
            "Minimum length (optional):",
            validate=lambda text: text.isdigit() or text == ""
        ).ask()

        config["max_length"] = questionary.text(
            "Maximum length (optional):",
            validate=lambda text: text.isdigit() or text == ""
        ).ask()

        config["pattern"] = questionary.text(
            "Regex pattern (optional):"
        ).ask()

    # Default value
    if questionary.confirm(
        "Add default value?",
        default=False
    ).ask():
        config["default"] = questionary.text(
            "Default value:"
        ).ask()

    return config

def configure_number_var(name: str, schema: Dict) -> Dict[str, Any]:
    """Configure number variable."""
    config = {"type": "number"}

    # Validation
    if questionary.confirm(
        "Add validation?",
        default=False
    ).ask():
        config["min"] = questionary.text(
            "Minimum value (optional):",
            validate=lambda text: text.replace(".", "").isdigit() or text == ""
        ).ask()

        config["max"] = questionary.text(
            "Maximum value (optional):",
            validate=lambda text: text.replace(".", "").isdigit() or text == ""
        ).ask()

        config["integer"] = questionary.confirm(
            "Integer only?",
            default=False
        ).ask()

    # Default value
    if questionary.confirm(
        "Add default value?",
        default=False
    ).ask():
        config["default"] = questionary.text(
            "Default value:",
            validate=lambda text: text.replace(".", "").isdigit()
        ).ask()

    return config

def configure_date_var(name: str, schema: Dict) -> Dict[str, Any]:
    """Configure date variable."""
    config = {"type": "date"}

    # Format
    config["format"] = questionary.select(
        "Date format:",
        choices=[
            "YYYY-MM-DD",
            "DD/MM/YYYY",
            "MM/DD/YYYY",
            "Custom"
        ]
    ).ask()

    if config["format"] == "Custom":
        config["format"] = questionary.text(
            "Custom format:"
        ).ask()

    # Validation
    if questionary.confirm(
        "Add validation?",
        default=False
    ).ask():
        config["min_date"] = questionary.text(
            "Minimum date (optional, YYYY-MM-DD):"
        ).ask()

        config["max_date"] = questionary.text(
            "Maximum date (optional, YYYY-MM-DD):"
        ).ask()

    return config

def configure_array_var(name: str, schema: Dict) -> Dict[str, Any]:
    """Configure array variable."""
    config = {"type": "array"}

    # Item type
    config["item_type"] = questionary.select(
        "Array item type:",
        choices=["string", "number", "object"]
    ).ask()

    # Validation
    if questionary.confirm(
        "Add validation?",
        default=False
    ).ask():
        config["min_items"] = questionary.text(
            "Minimum items (optional):",
            validate=lambda text: text.isdigit() or text == ""
        ).ask()

        config["max_items"] = questionary.text(
            "Maximum items (optional):",
            validate=lambda text: text.isdigit() or text == ""
        ).ask()

        config["unique"] = questionary.confirm(
            "Require unique items?",
            default=False
        ).ask()

    return config

def configure_object_var(name: str, schema: Dict) -> Dict[str, Any]:
    """Configure object variable."""
    config = {"type": "object"}

    # Properties
    if questionary.confirm(
        "Define object properties?",
        default=True
    ).ask():
        config["properties"] = {}
        
        while True:
            prop_name = questionary.text(
                "Property name (empty to finish):"
            ).ask()
            
            if not prop_name:
                break
            
            prop_type = questionary.select(
                f"Type for {prop_name}:",
                choices=["string", "number", "date", "boolean"]
            ).ask()
            
            required = questionary.confirm(
                f"Is {prop_name} required?",
                default=False
            ).ask()
            
            config["properties"][prop_name] = {
                "type": prop_type,
                "required": required
            }

    return config

def get_example_content(type_id: str) -> str:
    """Get example template content."""
    if type_id == "email":
        return """<!DOCTYPE html>
<html>
<body>
    <p>Dear {{ recipient_name }},</p>
    
    <p>{{ content }}</p>
    
    <p>Best regards,<br>
    {{ sender_name }}</p>
</body>
</html>"""

    elif type_id == "proposal":
        return """# {{ title }}

## Client Information
**Client:** {{ client_name }}
**Date:** {{ date }}
**Valid Until:** {{ valid_until }}

## Items
{% for item in items %}
- {{ item.name }}: ${{ item.value }}
{% endfor %}

**Total:** ${{ deal_value }}

## Payment Terms
{{ payment_terms }}"""

    else:
        return """# {{ title }}

**Author:** {{ author }}
**Date:** {{ date }}

{{ content }}

{% if metadata %}
## Metadata
{% for key, value in metadata.items() %}
- {{ key }}: {{ value }}
{% endfor %}
{% endif %}"""

def save_template(template_info: Dict[str, Any], config: Dict[str, Any], path: str):
    """Save template configuration."""
    # Create template directory if needed
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Combine info and config
    template_data = {
        "info": template_info,
        "variables": config
    }

    # Save template
    with open(path, "w") as f:
        yaml.dump(template_data, f, default_flow_style=False)

    console.print(f"\n[green]Template saved to {path}[/green]")

    # Show preview
    console.print("\n[bold]Template Preview:[/bold]")
    console.print(Syntax(
        yaml.dump(template_data, default_flow_style=False),
        "yaml",
        theme="monokai"
    ))

@click.command()
@click.option(
    "--output",
    default="templates/template.yaml",
    help="Output file path"
)
def setup_template(output: str):
    """Run template setup wizard."""
    show_template_info()

    type_id = select_template_type()
    template_info = collect_template_info(type_id)
    variable_config = configure_variables(type_id)

    save_template(template_info, variable_config, output)

if __name__ == "__main__":
    setup_template()