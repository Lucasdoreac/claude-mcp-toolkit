"""
Webhook management commands.
"""
import click
import httpx
import json
from rich.table import Table
from rich.syntax import Syntax
from rich.prompt import Confirm

from ..main import pass_config, Config, print_error, print_success, spinner, console

@click.group()
def webhooks():
    """Manage webhooks."""
    pass

@webhooks.command()
@pass_config
def list(config: Config):
    """List webhooks."""
    with spinner("Loading webhooks") as progress:
        try:
            response = httpx.get(
                f"{config.api_url}/api/webhooks",
                headers={"Authorization": f"Bearer {config.token}"}
            )
            response.raise_for_status()
            webhooks = response.json()

            table = Table(show_header=True)
            table.add_column("ID")
            table.add_column("Name")
            table.add_column("URL")
            table.add_column("Events")
            table.add_column("Active")

            for webhook in webhooks:
                table.add_row(
                    str(webhook["id"]),
                    webhook["name"],
                    webhook["url"],
                    ", ".join(webhook["events"]),
                    "✓" if webhook["is_active"] else "✗"
                )

            console.print(table)

        except Exception as e:
            print_error(f"Failed to list webhooks: {str(e)}")

@webhooks.command()
@click.argument("name")
@click.argument("url")
@click.option("--events", required=True, help="Event types (comma-separated)")
@click.option("--headers", type=click.Path(exists=True), help="Headers JSON file")
@click.option("--secret", help="Webhook secret for signature")
@click.option("--description", help="Webhook description")
@click.option("--retries", type=int, default=3, help="Number of retry attempts")
@pass_config
def create(
    config: Config,
    name: str,
    url: str,
    events: str,
    headers: str,
    secret: str,
    description: str,
    retries: int
):
    """Create a new webhook."""
    try:
        # Parse events
        event_list = [e.strip() for e in events.split(",")]

        # Load headers if provided
        headers_data = None
        if headers:
            with open(headers, "r") as f:
                headers_data = json.load(f)

        # Create webhook
        with spinner("Creating webhook") as progress:
            response = httpx.post(
                f"{config.api_url}/api/webhooks",
                headers={"Authorization": f"Bearer {config.token}"},
                json={
                    "name": name,
                    "url": url,
                    "events": event_list,
                    "headers": headers_data,
                    "secret_key": secret,
                    "description": description,
                    "retry_count": retries
                }
            )
            response.raise_for_status()
            webhook = response.json()
            print_success(f"Webhook created with ID {webhook['id']}")

    except Exception as e:
        print_error(f"Failed to create webhook: {str(e)}")

@webhooks.command()
@click.argument("id", type=int)
@pass_config
def show(config: Config, id: int):
    """Show webhook details."""
    with spinner("Loading webhook") as progress:
        try:
            response = httpx.get(
                f"{config.api_url}/api/webhooks/{id}",
                headers={"Authorization": f"Bearer {config.token}"}
            )
            response.raise_for_status()
            webhook = response.json()

            # Show metadata
            table = Table(show_header=False)
            table.add_row("ID", str(webhook["id"]))
            table.add_row("Name", webhook["name"])
            table.add_row("URL", webhook["url"])
            table.add_row("Events", ", ".join(webhook["events"]))
            table.add_row("Description", webhook["description"] or "")
            table.add_row("Active", "✓" if webhook["is_active"] else "✗")
            table.add_row("Retries", str(webhook["retry_count"]))
            console.print(table)
            console.print()

            # Show headers if present
            if webhook["headers"]:
                console.print("[bold]Headers:[/bold]")
                console.print(Syntax(
                    json.dumps(webhook["headers"], indent=2),
                    "json",
                    theme="monokai"
                ))

        except Exception as e:
            print_error(f"Failed to show webhook: {str(e)}")

@webhooks.command()
@click.argument("id", type=int)
@click.option("--name", help="New webhook name")
@click.option("--url", help="New webhook URL")
@click.option("--events", help="New event types (comma-separated)")
@click.option("--headers", type=click.Path(exists=True), help="New headers JSON file")
@click.option("--secret", help="New webhook secret")
@click.option("--description", help="New description")
@click.option("--active/--inactive", help="Set active status")
@click.option("--retries", type=int, help="New retry count")
@pass_config
def update(
    config: Config,
    id: int,
    name: str,
    url: str,
    events: str,
    headers: str,
    secret: str,
    description: str,
    active: bool,
    retries: int
):
    """Update a webhook."""
    try:
        # Build update data
        update_data = {}
        if name:
            update_data["name"] = name
        if url:
            update_data["url"] = url
        if events:
            update_data["events"] = [e.strip() for e in events.split(",")]
        if secret:
            update_data["secret_key"] = secret
        if description:
            update_data["description"] = description
        if active is not None:
            update_data["is_active"] = active
        if retries is not None:
            update_data["retry_count"] = retries

        # Update headers if provided
        if headers:
            with open(headers, "r") as f:
                update_data["headers"] = json.load(f)

        # Send update
        with spinner("Updating webhook") as progress:
            response = httpx.put(
                f"{config.api_url}/api/webhooks/{id}",
                headers={"Authorization": f"Bearer {config.token}"},
                json=update_data
            )
            response.raise_for_status()
            print_success("Webhook updated")

    except Exception as e:
        print_error(f"Failed to update webhook: {str(e)}")

@webhooks.command()
@click.argument("id", type=int)
@click.option("--force/--no-force", help="Force delete without confirmation")
@pass_config
def delete(config: Config, id: int, force: bool):
    """Delete a webhook."""
    if not force and not Confirm.ask(f"Delete webhook {id}?"):
        return

    with spinner("Deleting webhook") as progress:
        try:
            response = httpx.delete(
                f"{config.api_url}/api/webhooks/{id}",
                headers={"Authorization": f"Bearer {config.token}"}
            )
            response.raise_for_status()
            print_success("Webhook deleted")

        except Exception as e:
            print_error(f"Failed to delete webhook: {str(e)}")

@webhooks.command()
@click.argument("id", type=int)
@click.argument("event_type")
@click.argument("payload", type=click.Path(exists=True))
@pass_config
def trigger(config: Config, id: int, event_type: str, payload: str):
    """Trigger a webhook event."""
    try:
        # Load payload
        with open(payload, "r") as f:
            payload_data = json.load(f)

        # Trigger event
        with spinner("Triggering webhook") as progress:
            response = httpx.post(
                f"{config.api_url}/api/webhooks/trigger",
                headers={"Authorization": f"Bearer {config.token}"},
                json={
                    "event_type": event_type,
                    "payload": payload_data
                }
            )
            response.raise_for_status()
            print_success("Webhook triggered")

    except Exception as e:
        print_error(f"Failed to trigger webhook: {str(e)}")

@webhooks.command()
@click.argument("id", type=int)
@click.option("--limit", type=int, default=100, help="Number of deliveries to show")
@pass_config
def deliveries(config: Config, id: int, limit: int):
    """Show webhook delivery history."""
    with spinner("Loading deliveries") as progress:
        try:
            response = httpx.get(
                f"{config.api_url}/api/webhooks/{id}/deliveries",
                headers={"Authorization": f"Bearer {config.token}"},
                params={"limit": limit}
            )
            response.raise_for_status()
            deliveries = response.json()

            table = Table(show_header=True)
            table.add_column("ID")
            table.add_column("Event")
            table.add_column("Status")
            table.add_column("Attempts")
            table.add_column("Created")
            table.add_column("Completed")

            for delivery in deliveries:
                table.add_row(
                    str(delivery["id"]),
                    delivery["event_type"],
                    "✓" if delivery["is_success"] else "✗",
                    str(delivery["attempt_count"]),
                    delivery["created_at"],
                    delivery["completed_at"] or "In Progress"
                )

            console.print(table)

        except Exception as e:
            print_error(f"Failed to show deliveries: {str(e)}")

@webhooks.command()
@click.argument("delivery_id", type=int)
@pass_config
def retry(config: Config, delivery_id: int):
    """Retry a failed webhook delivery."""
    with spinner("Retrying delivery") as progress:
        try:
            response = httpx.post(
                f"{config.api_url}/api/webhooks/deliveries/{delivery_id}/retry",
                headers={"Authorization": f"Bearer {config.token}"}
            )
            response.raise_for_status()
            print_success("Delivery retry initiated")

        except Exception as e:
            print_error(f"Failed to retry delivery: {str(e)}")

if __name__ == "__main__":
    webhooks()