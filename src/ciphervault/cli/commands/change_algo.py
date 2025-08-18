import click
from ciphervault.core.vault import PasswordVault
from ciphervault.cli.utils import sessionTimeoutCheck
from ciphervault.core.utils import resolve_vault_path

@click.command('change-algo')
@sessionTimeoutCheck
@click.option('--master-password', prompt='For security reasons, please enter your master password to proceed with this critical operation', hide_input=True, help='Master password for the vault.')
@click.option('--new-algo', type=click.Choice(['aes', 'chacha', 'hybrid']), prompt=True, help='New encryption algorithm.')
@click.pass_context
def change_algo_cmd(ctx, master_password, new_algo):
    """Change the encryption algorithm for the vault."""
    vault = PasswordVault(db_path = resolve_vault_path(ctx.obj['db']))
    if not vault.verify_master_password(master_password):
        click.echo("Incorrect master password. Please try again!")
        vault.close()
        return
    try:
        vault.change_algorithm(new_algo)
        if vault.algorithm != new_algo.lower():
            click.echo(f"Algorithm changed from {vault.algorithm} to {new_algo}.")
        else:
            click.echo(f"Current Algorithm : {vault.algorithm}, Hence no changes made. Exiting!")
    except Exception as e:
        click.echo(f"Error: {e}")
    finally:
        vault.close()