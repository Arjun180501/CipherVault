import click
from ciphervault.core.vault import PasswordVault
from ciphervault.cli.utils import sessionTimeoutCheck
from ciphervault.core.utils import resolve_vault_path

@click.command('list')
@sessionTimeoutCheck
@click.pass_context
def list_cmd(ctx):
    """List all entries."""
    vault = PasswordVault(db_path = resolve_vault_path(ctx.obj['db']))
    entries = vault.list_entries()
    if not entries:
        click.echo("No entries found.")
    for entry in entries:
        click.echo(f"Service: {entry['service']} | Username: {entry['username']} | Notes: {entry['notes']}")
    vault.lock()