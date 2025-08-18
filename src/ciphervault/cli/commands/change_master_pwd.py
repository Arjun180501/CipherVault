import click
from getpass import getpass
from ciphervault.core.vault import PasswordVault
from ciphervault.cli.utils import sessionTimeoutCheck
from ciphervault.core.utils import is_password_pwned, resolve_vault_path

@click.command('change-master-pwd')
@sessionTimeoutCheck
@click.option('--current_master_password', prompt='For security reasons, please enter your current master password to proceed with this critical operation', hide_input=True, help='Current Master password for the vault.')
@click.pass_context
def change_master_pwd_cmd(ctx, current_master_password):
    """Change the master password for your vault."""
    try:
        vault = PasswordVault(db_path = resolve_vault_path(ctx.obj['db']))
        if not vault.verify_master_password(current_master_password):
            click.echo("Incorrect existing master password. Please try again!")
            vault.close()
            return
        
        # Prompt for new password (with confirmation)
        while True:
            new_password = getpass("New master password: ")
            confirm_password = getpass("Confirm new master password: ")
            if new_password != confirm_password:
                click.echo("Passwords do not match. Please try again.")
            elif not new_password:
                click.echo("Password cannot be empty. Please try again.")
            breach_cnt = is_password_pwned(new_password)
            if breach_cnt:
                click.secho(f"The new master password has been seen {breach_cnt:,} times in data breaches. Avoid using it.", fg='red')
            else:
                click.secho("The new master password has not been found in known data breaches. Continuing with master password change", fg='green')
                break


        # Change password in the vault
        vault.change_master_password(new_password)
        vault.close()

        click.echo("Master password changed successfully. Please log in again with your new password.")
    except Exception as e:
        click.echo(f"Failed to change master password: {e}")