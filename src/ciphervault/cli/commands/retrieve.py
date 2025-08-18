import click
from getpass import getpass
from ciphervault.core.vault import PasswordVault
from ciphervault.cli.utils import sessionTimeoutCheck
from ciphervault.core.utils import resolve_vault_path

@click.command('get')
@sessionTimeoutCheck
@click.pass_context
def retrieve_cmd(ctx):
    """
    Retrieve an entry by service and (optionally) account.
    Guides the user to select a service, then an account if multiple exists.
    """
    vault = PasswordVault(db_path = resolve_vault_path(ctx.obj['db']))

    # Step 1: List all unique services
    entries = vault.list_entries()
    services = sorted(set(entry['service'] for entry in entries))
    if not services:
        click.echo("No entries found in the vault.")
        vault.lock()
        return

    # Step 2: Prompt user to select a service
    click.echo("Available services:")
    for idx, service in enumerate(services, 1):
        click.echo(f"{idx}. {service}")
    while True:
        try:
            service_choice = int(click.prompt("Select a service by number"))
            if 1 <= service_choice <= len(services):
                selected_service = services[service_choice - 1]
                break
            else:
                click.echo("Invalid selection. Please try again.")
        except ValueError:
            click.echo("Please enter a valid number.")

    # Step 3: Get all entries for the selected service
    service_entries = vault.get_entries_by_service(selected_service)
    if not service_entries:
        click.echo("No entries found for the selected service.")
        vault.close()
        return

    # Step 4: If multiple entries, prompt for entry selection
    if len(service_entries) == 1:
        entry = service_entries[0]
    else:
        click.echo(f"Multiple accounts found for '{selected_service}':")
        for idx, entry in enumerate(service_entries, 1):
            username = entry.get('username', 'N/A')
            notes = entry.get('notes', '')
            click.echo(f"Choice: {idx} Username: {username} | Notes: {notes}")
        while True:
            try:
                entry_choice = int(click.prompt("Select the required choice"))
                if 1 <= entry_choice <= len(service_entries):
                    entry = service_entries[entry_choice - 1]
                    break
                else:
                    click.echo("Invalid selection. Please try again.")
            except ValueError:
                click.echo("Please enter a valid number.")

    # Step 5: Display the entry details
    entry_details = vault.get_entry_details(entry['id'])
    if entry_details:
        click.echo(f"\nService: {entry_details['service']}")
        click.echo(f"Username: {entry_details['username']}")
        click.echo(f"Password: {entry_details['password']}")
        click.echo(f"Notes: {entry_details['notes']}")
    else:
        click.echo("Entry not found.")
    vault.lock()
