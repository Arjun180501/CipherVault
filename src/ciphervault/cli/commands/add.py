import click
from getpass import getpass
from ciphervault.core.vault import PasswordVault
from ciphervault.cli.utils import sessionTimeoutCheck
from ciphervault.core.utils import resolve_vault_path

@click.command('add')
@sessionTimeoutCheck
@click.option('--service', prompt=True, help='Service name.')
@click.option('--username', prompt=True, help='Username.')
@click.option('--notes', default='', prompt=True, help='Notes (optional).')
@click.pass_context
def add_cmd(ctx, service, username, notes):
    """Add a new password entry."""
    password = getpass("Password: ")
    vault = PasswordVault(db_path = resolve_vault_path(ctx.obj['db']))
    vault.add_password_entry(service, username, password, notes)
    click.echo(f"Added entry for (service: {service} and username: {username})")
    vault.lock()
