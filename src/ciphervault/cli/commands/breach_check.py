import click
from ciphervault.core.utils import is_password_pwned, resolve_vault_path
from ciphervault.core.vault import PasswordVault
from ciphervault.cli.utils import sessionTimeoutCheck

@click.command('breach-status')
@sessionTimeoutCheck
@click.option("--only-breached", is_flag=True, help="Show only breached entries")
@click.pass_context
def breach_status_cmd(ctx, only_breached):
    """List all password entries with breach status from HIBP"""
    try:
        vault_obj = PasswordVault(db_path = resolve_vault_path(ctx.obj['db']))
        entries = vault_obj.list_entries()

        if not entries:
            click.echo("No entries found in the vault.")
            return

        click.echo(f"\n{'Service':<20} {'Username':<30} {'Breach Status'}")
        click.echo("-" * 60)

        for e in entries:
            try:
                details = vault_obj.get_entry_details(e['id'])
                breached = is_password_pwned(details['password'])

                if only_breached and not breached:
                    continue  # skip safe entries

                status = "Breached" if breached else "Safe"
                color = "red" if breached else "green"
                click.secho(f"{e['service']:<20} {e['username']:<30} {status}", fg=color)

            except Exception as err:
                click.secho(f"{e['service']:<20} {e['username']:<30} ERROR: {err}", fg="yellow")

    except Exception as e:
        click.secho(f"[ERROR] Could not complete breach check: {e}", fg="red")