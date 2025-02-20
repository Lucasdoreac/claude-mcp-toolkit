"""
Template management commands.
"""
import click
import httpx
from rich.table import Table
from rich.syntax import Syntax
from rich.prompt import Confirm

from ..main import pass_config, Config, print_error, print_success, spinner, console

@click.group()
def templates():
    """Manage templates."""
    pass

@templates.command()
@click.option("--type", help="Filter by template type")
@pass_config
def list(config: Config, type: str):
    """List templates."""
    with spinner("Loading templates") as progress:
        try:
            params = {"type": type} if type else {}
            response = httpx.get(
                f"{config.api_url}/api/templates",
                headers={"Authorization": f"Bearer {config.token}"},
                params=params
            )
            response.raise_for_status()
            templates = response.json()

            table = Table(show_header=True)
            table.add_column("ID")
            table.add_column("Name")
            table.add_column("Type")
            table.add_column("Active")
            table.add_column("Default")

            for template in templates:
                table.add_row(
                    str(template["id"]),
                    template["name"],
                    template["type"],
                    "✓" if template["is_active"] else "✗",
                    "✓" if template["is_default"] else "✗"
                )

            console.print(table)

        except Exception as e:
            print_error(f"Failed to list templates: {str(e)}")

@templates.command()
@click.argument("name")
@click.option("--type", required=True, help="Template type")
@click.option("--file", type=click.Path(exists=True), help="Template content file")
@click.option("--variables", help="Template variables (JSON)")
@click.option("--description", help="Template description")
@click.option("--default/--no-default", default=False, help="Set as default template")
@pass_config
def create(
    config: Config,
    name: str,
    type: str,
    file: str,
    variables: str,
    description: str,
    default: bool
):
    """Create a new template."""
    try:
        # Read template content
        if file:
            with open(file, "r") as f:
                content = f.read()
        else:
            content = click.edit()
            if not content:
                print_error("Template content is required")
                return

        # Parse variables
        import json
        if variables:
            try:
                variables_dict = json.loads(variables)
            except json.JSONDecodeError:
                print_error("Invalid JSON for variables")
                return
        else:
            variables_dict = {}

        # Create template
        with spinner("Creating template") as progress:
            response = httpx.post(
                f"{config.api_url}/api/templates",
                headers={"Authorization": f"Bearer {config.token}"},
                json={
                    "name": name,
                    "type": type,
                    "content": content,
                    "variables": variables_dict,
                    "description": description,
                    "is_default": default
                }
            )
            response.raise_for_status()
            template = response.json()
            print_success(f"Template created with ID {template['id']}")

    except Exception as e:
        print_error(f"Failed to create template: {str(e)}")

@templates.command()
@click.argument("id", type=int)
@pass_config
def show(config: Config, id: int):
    """Show template details."""
    with spinner("Loading template") as progress:
        try:
            response = httpx.get(
                f"{config.api_url}/api/templates/{id}",
                headers={"Authorization": f"Bearer {config.token}"}
            )
            response.raise_for_status()
            template = response.json()

            # Show metadata
            table = Table(show_header=False)
            table.add_row("ID", str(template["id"]))
            table.add_row("Name", template["name"])
            table.add_row("Type", template["type"])
            table.add_row("Description", template["description"] or "")
            table.add_row("Active", "✓" if template["is_active"] else "✗")
            table.add_row("Default", "✓" if template["is_default"] else "✗")
            console.print(table)
            console.print()

            # Show variables
            console.print("[bold]Variables:[/bold]")
            console.print(Syntax(
                json.dumps(template["variables"], indent=2),
                "json",
                theme="monokai"
            ))
            console.print()

            # Show content
            console.print("[bold]Content:[/bold]")
            console.print(Syntax(
                template["content"],
                "html" if template["type"] == "email" else "markdown",
                theme="monokai"
            ))

        except Exception as e:
            print_error(f"Failed to show template: {str(e)}")

@templates.command()
@click.argument("id", type=int)
@click.option("--name", help="New template name")
@click.option("--file", type=click.Path(exists=True), help="New content file")
@click.option("--variables", help="New variables (JSON)")
@click.option("--description", help="New description")
@click.option("--active/--inactive", help="Set active status")
@click.option("--default/--no-default", help="Set as default template")
@pass_config
def update(
    config: Config,
    id: int,
    name: str,
    file: str,
    variables: str,
    description: str,
    active: bool,
    default: bool
):
    """Update a template."""
    try:
        # Build update data
        update_data = {}
        if name:
            update_data["name"] = name
        if description:
            update_data["description"] = description
        if active is not None:
            update_data["is_active"] = active
        if default is not None:
            update_data["is_default"] = default

        # Update content if provided
        if file:
            with open(file, "r") as f:
                update_data["content"] = f.read()

        # Update variables if provided
        if variables:
            try:
                update_data["variables"] = json.loads(variables)
            except json.JSONDecodeError:
                print_error("Invalid JSON for variables")
                return

        # Send update
        with spinner("Updating template") as progress:
            response = httpx.put(
                f"{config.api_url}/api/templates/{id}",
                headers={"Authorization": f"Bearer {config.token}"},
                json=update_data
            )
            response.raise_for_status()
            print_success("Template updated")

    except Exception as e:
        print_error(f"Failed to update template: {str(e)}")

@templates.command()
@click.argument("id", type=int)
@click.option("--force/--no-force", help="Force delete without confirmation")
@pass_config
def delete(config: Config, id: int, force: bool):
    """Delete a template."""
    if not force and not Confirm.ask(f"Delete template {id}?"):
        return

    with spinner("Deleting template") as progress:
        try:
            response = httpx.delete(
                f"{config.api_url}/api/templates/{id}",
                headers={"Authorization": f"Bearer {config.token}"}
            )
            response.raise_for_status()
            print_success("Template deleted")

        except Exception as e:
            print_error(f"Failed to delete template: {str(e)}")

@templates.command()
@click.argument("id", type=int)
@click.argument("variable-values", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file")
@pass_config
def render(config: Config, id: int, variable_values: str, output: str):
    """Render a template."""
    try:
        # Read variables
        with open(variable_values, "r") as f:
            variables = json.load(f)

        # Render template
        with spinner("Rendering template") as progress:
            response = httpx.post(
                f"{config.api_url}/api/templates/{id}/render",
                headers={"Authorization": f"Bearer {config.token}"},
                json=variables
            )
            response.raise_for_status()
            content = response.json()["content"]

        # Output result
        if output:
            with open(output, "w") as f:
                f.write(content)
            print_success(f"Output written to {output}")
        else:
            console.print(content)

    except Exception as e:
        print_error(f"Failed to render template: {str(e)}")

if __name__ == "__main__":
    templates()