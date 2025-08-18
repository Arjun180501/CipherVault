import click
from ciphervault.core.vault import PasswordVault
from ciphervault.core.utils import resolve_vault_path

@click.command('lock')
@click.pass_context
def lock_cmd(ctx):
    """
    Lock (logout of) the vault.
    """
    try:
        vault = PasswordVault(db_path = resolve_vault_path(ctx.obj['db']))
        vault.close()
        click.echo("Vault locked and session ended.")
    except Exception as e:
        click.echo(f"Error locking vault: {e}")
