"""
Integration management commands.
"""
import click
import httpx
import json
from rich.table import Table
from rich.syntax import Syntax
from rich.prompt import Confirm

from ..main import pass_config, Config, print_error, print_success, spinner, console

@click.group()
def integrations():
    """Manage integrations."""
    pass

@integrations.command(name="providers")
@click.option("--type", help="Filter by provider type")
@pass_config
def list_providers(config: Config, type: str):
    """List available integration providers."""
    with spinner("Loading providers") as progress:
        try:
            params = {"type": type} if type else {}
            response = httpx.get(
                f"{config.api_url}/api/integrations/providers",
                headers={"Authorization": f"Bearer {config.token}"},
                params=params
            )
            response.raise_for_status()
            providers = response.json()

            table = Table(show_header=True)
            table.add_column("ID")
            table.add_column("Name")
            table.add_column("Type")
            table.add_column("Description")
            table.add_column("Auth Type")

            for provider in providers:
                table.add_row(
                    provider["id"],
                    provider["name"],
                    provider["type"],
                    provider["description"],
                    provider["auth_type"]
                )

            console.print(table)

        except Exception as e:
            print_error(f"Failed to list providers: {str(e)}")

@integrations.command()
@click.option("--type", help="Filter by integration type")
@click.option("--provider", help="Filter by provider")
@pass_config
def list(config: Config, type: str, provider: str):
    """List integrations."""
    with spinner("Loading integrations") as progress:
        try:
            params = {}
            if type:
                params["type"] = type
            if provider:
                params["provider"] = provider

            response = httpx.get(
                f"{config.api_url}/api/integrations",
                headers={"Authorization": f"Bearer {config.token}"},
                params=params
            )
            response.raise_for_status()
            integrations = response.json()

            table = Table(show_header=True)
            table.add_column("ID")
            table.add_column("Name")
            table.add_column("Provider")
            table.add_column("Status")
            table.add_column("Last Sync")

            for integration in integrations:
                table.add_row(
                    str(integration["id"]),
                    integration["name"],
                    integration["provider"],
                    integration["status"],
                    integration["last_sync"] or "Never"
                )

            console.print(table)

        except Exception as e:
            print_error(f"Failed to list integrations: {str(e)}")

@integrations.command()
@click.argument("name")
@click.argument("provider")
@click.option("--config", "config_file", type=click.Path(exists=True), help="Config JSON file")
@click.option("--credentials", type=click.Path(exists=True), help="Credentials JSON file")
@pass_config
def create(
    config: Config,
    name: str,
    provider: str,
    config_file: str,
    credentials: str
):
    """Create a new integration."""
    try:
        # Load config
        if config_file:
            with open(config_file, "r") as f:
                config_data = json.load(f)
        else:
            config_data = {}

        # Load credentials
        if credentials:
            with open(credentials, "r") as f:
                credentials_data = json.load(f)
        else:
            print_error("Credentials file is required")
            return

        # Create integration
        with spinner("Creating integration") as progress:
            response = httpx.post(
                f"{config.api_url}/api/integrations",
                headers={"Authorization": f"Bearer {config.token}"},
                json={
                    "name": name,
                    "provider": provider,
                    "config": config_data,
                    "credentials": credentials_data
                }
            )
            response.raise_for_status()
            integration = response.json()
            print_success(f"Integration created with ID {integration['id']}")

    except Exception as e:
        print_error(f"Failed to create integration: {str(e)}")

@integrations.command()
@click.argument("id", type=int)
@pass_config
def show(config: Config, id: int):
    """Show integration details."""
    with spinner("Loading integration") as progress:
        try:
            response = httpx.get(
                f"{config.api_url}/api/integrations/{id}",
                headers={"Authorization": f"Bearer {config.token}"}
            )
            response.raise_for_status()
            integration = response.json()

            # Show metadata
            table = Table(show_header=False)
            table.add_row("ID", str(integration["id"]))
            table.add_row("Name", integration["name"])
            table.add_row("Provider", integration["provider"])
            table.add_row("Status", integration["status"])
            table.add_row("Last Sync", integration["last_sync"] or "Never")
            table.add_row("Error", integration["error_message"] or "None")
            console.print(table)
            console.print()

            # Show config
            console.print("[bold]Config:[/bold]")
            console.print(Syntax(
                json.dumps(integration["config"], indent=2),
                "json",
                theme="monokai"
            ))

        except Exception as e:
            print_error(f"Failed to show integration: {str(e)}")

@integrations.command()
@click.argument("id", type=int)
@click.option("--name", help="New integration name")
@click.option("--config", type=click.Path(exists=True), help="New config JSON file")
@click.option("--credentials", type=click.Path(exists=True), help="New credentials JSON file")
@click.option("--enabled/--disabled", help="Enable or disable integration")
@pass_config
def update(
    config: Config,
    id: int,
    name: str,
    config_file: str,
    credentials: str,
    enabled: bool
):
    """Update an integration."""
    try:
        # Build update data
        update_data = {}
        if name:
            update_data["name"] = name
        if enabled is not None:
            update_data["is_enabled"] = enabled

        # Update config if provided
        if config_file:
            with open(config_file, "r") as f:
                update_data["config"] = json.load(f)

        # Update credentials if provided
        if credentials:
            with open(credentials, "r") as f:
                update_data["credentials"] = json.load(f)

        # Send update
        with spinner("Updating integration") as progress:
            response = httpx.put(
                f"{config.api_url}/api/integrations/{id}",
                headers={"Authorization": f"Bearer {config.token}"},
                json=update_data
            )
            response.raise_for_status()
            print_success("Integration updated")

    except Exception as e:
        print_error(f"Failed to update integration: {str(e)}")

@integrations.command()
@click.argument("id", type=int)
@click.option("--force/--no-force", help="Force delete without confirmation")
@pass_config
def delete(config: Config, id: int, force: bool):
    """Delete an integration."""
    if not force and not Confirm.ask(f"Delete integration {id}?"):
        return

    with spinner("Deleting integration") as progress:
        try:
            response = httpx.delete(
                f"{config.api_url}/api/integrations/{id}",
                headers={"Authorization": f"Bearer {config.token}"}
            )
            response.raise_for_status()
            print_success("Integration deleted")

        except Exception as e:
            print_error(f"Failed to delete integration: {str(e)}")

@integrations.command()
@click.argument("id", type=int)
@pass_config
def sync(config: Config, id: int):
    """Trigger integration sync."""
    with spinner("Syncing integration") as progress:
        try:
            response = httpx.post(
                f"{config.api_url}/api/integrations/{id}/sync",
                headers={"Authorization": f"Bearer {config.token}"}
            )
            response.raise_for_status()
            result = response.json()
            
            print_success(f"""
            Sync completed:
            - Items processed: {result['items_processed']}
            - Succeeded: {result['items_succeeded']}
            - Failed: {result['items_failed']}
            """)

        except Exception as e:
            print_error(f"Failed to sync integration: {str(e)}")

@integrations.command()
@click.argument("id", type=int)
@click.option("--limit", type=int, default=100, help="Number of logs to show")
@pass_config
def logs(config: Config, id: int, limit: int):
    """Show integration sync logs."""
    with spinner("Loading sync logs") as progress:
        try:
            response = httpx.get(
                f"{config.api_url}/api/integrations/{id}/sync-logs",
                headers={"Authorization": f"Bearer {config.token}"},
                params={"limit": limit}
            )
            response.raise_for_status()
            logs = response.json()

            table = Table(show_header=True)
            table.add_column("ID")
            table.add_column("Status")
            table.add_column("Items")
            table.add_column("Success")
            table.add_column("Failed")
            table.add_column("Started")
            table.add_column("Completed")

            for log in logs:
                table.add_row(
                    str(log["id"]),
                    log["status"],
                    str(log["items_processed"]),
                    str(log["items_succeeded"]),
                    str(log["items_failed"]),
                    log["started_at"],
                    log["completed_at"] or "In Progress"
                )

            console.print(table)

        except Exception as e:
            print_error(f"Failed to show sync logs: {str(e)}")

if __name__ == "__main__":
    integrations()