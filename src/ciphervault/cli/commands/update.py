import click
from getpass import getpass
from ciphervault.core.vault import PasswordVault
from ciphervault.cli.utils import sessionTimeoutCheck
from ciphervault.core.utils import resolve_vault_path

@click.command('update')
@sessionTimeoutCheck
@click.option('--service', help='Service name of the entry to update.')
@click.option('--username', help='Username of the entry to update.')
@click.option('--master-password', prompt='For security reasons, please enter your master password to proceed with this critical operation', hide_input=True, help='Master password for the vault.')
@click.pass_context
def update_cmd(ctx, service, username, master_password):
    """Update an existing entry. Leave any field blank to keep its current value."""
    vault = PasswordVault(db_path = resolve_vault_path(ctx.obj['db']))
    if not vault.verify_master_password(master_password):
        click.echo("Incorrect master password. Please try again!")
        vault.lock()
        return
    try:
        # If service and username not provided, let user select entry interactively
        if not service or not username:
            entries = vault.list_entries()
            if not entries:
                click.echo("No entries found.")
                return
            click.echo("Select an entry to update:")
            for idx, entry in enumerate(entries, 1):
                click.echo(f"{idx}: {entry['service']} ({entry['username']})")
            choice = click.prompt("Enter the number of the entry to update", type=int)
            if not (1 <= choice <= len(entries)):
                click.echo("Invalid selection.")
                return
            entry = entries[choice - 1]
        else:
            entry = vault.find_entry(service, username)
            if not entry:
                click.echo(f"No entry found for service '{service}' and username '{username}'.")
                return

        # Fetch full details for update
        entry_details = vault.get_entry_details(entry['id'])

        # Prompt for new values, using current as default
        new_service = click.prompt("New service name(leave blank to keep current):", default=entry_details['service'], show_default=True)
        new_username = click.prompt("New username(leave blank to keep current):", default=entry_details['username'], show_default=True)
        pass_input = getpass("New password(leave blank to keep current): ")
        new_password = pass_input if pass_input else entry_details['password']
        new_notes = click.prompt("New notes(leave blank to keep current):", default=entry_details['notes'], show_default=True)

        # Update the entry
        success = vault.update_entry(entry_details['id'], new_service, new_username, new_password, new_notes)
        if success:
            click.echo("Entry updated.")
        else:
            click.echo("Entry not found or update failed.")
    except Exception as e:
        click.echo(f"Error: {e}")
    finally:
        vault.lock()