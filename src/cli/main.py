"""
Command Line Interface (CLI) for Claude MCP Toolkit.
"""
import os
import sys
import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import httpx

console = Console()

def print_error(message: str):
    """Print error message in red."""
    console.print(f"[red]Error:[/red] {message}")

def print_success(message: str):
    """Print success message in green."""
    console.print(f"[green]Success:[/green] {message}")

def print_warning(message: str):
    """Print warning message in yellow."""
    console.print(f"[yellow]Warning:[/yellow] {message}")

def spinner(message: str):
    """Create loading spinner."""
    return Progress(
        SpinnerColumn(),
        TextColumn(f"{message}...")
    )

class Config:
    """CLI configuration."""
    def __init__(self):
        self.api_url = os.getenv("MCP_API_URL", "http://localhost:8000")
        self.token = os.getenv("MCP_TOKEN")

pass_config = click.make_pass_decorator(Config, ensure=True)

@click.group()
@click.option(
    "--api-url",
    envvar="MCP_API_URL",
    help="API URL (default: http://localhost:8000)"
)
@click.option(
    "--token",
    envvar="MCP_TOKEN",
    help="Authentication token"
)
@click.version_option()
def cli(api_url: Optional[str], token: Optional[str]):
    """Claude MCP Toolkit CLI."""
    ctx = click.get_current_context()
    config = ctx.ensure_object(Config)
    
    if api_url:
        config.api_url = api_url
    if token:
        config.token = token

    # Check token if required
    if not config.token and not ctx.command.name in ["login", "help"]:
        print_error("Authentication required. Please login first.")
        sys.exit(1)

@cli.command()
@click.option("--username", prompt=True)
@click.option("--password", prompt=True, hide_input=True)
@pass_config
def login(config: Config, username: str, password: str):
    """Login to get authentication token."""
    with spinner("Logging in") as progress:
        try:
            response = httpx.post(
                f"{config.api_url}/auth/token",
                data={
                    "username": username,
                    "password": password
                }
            )
            response.raise_for_status()
            token = response.json()["access_token"]
            
            # Save token
            with open(os.path.expanduser("~/.mcp_token"), "w") as f:
                f.write(token)
            
            print_success("Login successful")
            console.print("Token saved to ~/.mcp_token")
            
        except Exception as e:
            print_error(f"Login failed: {str(e)}")
            sys.exit(1)

@cli.command()
@pass_config
def whoami(config: Config):
    """Show current user info."""
    with spinner("Getting user info") as progress:
        try:
            response = httpx.get(
                f"{config.api_url}/auth/users/me",
                headers={"Authorization": f"Bearer {config.token}"}
            )
            response.raise_for_status()
            user = response.json()
            
            table = Table(show_header=False)
            table.add_row("Username", user["username"])
            table.add_row("Email", user["email"])
            table.add_row("Role", "Admin" if user["is_superuser"] else "User")
            console.print(table)
            
        except Exception as e:
            print_error(f"Failed to get user info: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    cli()