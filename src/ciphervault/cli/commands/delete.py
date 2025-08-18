import click
from ciphervault.core.vault import PasswordVault
from ciphervault.cli.utils import sessionTimeoutCheck
from ciphervault.core.utils import resolve_vault_path

@click.command('delete')
@sessionTimeoutCheck
@click.option('--master-password', prompt='For security reasons, please enter your master password to proceed with this critical operation', hide_input=True, help='Master password for the vault.')
@click.option('--service', help='Service name of the entry to delete.')
@click.option('--username', help='Username of the entry to delete.')
@click.pass_context
def delete_cmd(ctx, master_password, service, username):
    """Delete an entry by specifying service and username."""
    vault = PasswordVault(db_path = resolve_vault_path(ctx.obj['db']))
    if not vault.verify_master_password(master_password):
        click.echo("Incorrect master password. Please try again!")
        vault.lock()
        return
    try:
        # If both service and username are provided, try direct deletion
        if service and username:
            entry = vault.find_entry(service, username)
            if not entry:
                click.echo(f"No entry found for service '{service}' and username '{username}'.")
                return
            click.echo(f"Entry found: {entry['service']} ({entry['username']})")
            if click.confirm(f"Are you sure you want to delete this entry?", default=False):
                vault.delete_entry(entry['id'])
                click.echo("Entry deleted.")
            else:
                click.echo("Deletion cancelled.")
            return

        # If not, list entries for interactive selection
        entries = vault.list_entries()
        if not entries:
            click.echo("No entries found.")
            return

        click.echo("Your entries:")
        for idx, entry in enumerate(entries, 1):
            click.echo(f"{idx}: {entry['service']} ({entry['username']})")

        choice = click.prompt("Enter the number of the entry to delete", type=int)
        if not (1 <= choice <= len(entries)):
            click.echo("Invalid selection.")
            return

        entry = entries[choice - 1]
        if click.confirm(f"Are you sure you want to delete '{entry['service']}' ({entry['username']})?", default=False):
            vault.delete_entry(entry['id'])
            click.echo("Entry deleted.")
        else:
            click.echo("Deletion cancelled.")

    except Exception as e:
        click.echo(f"Error: {e}")
    finally:
        vault.lock()
