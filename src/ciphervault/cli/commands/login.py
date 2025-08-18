import os
import click
from getpass import getpass
import keyring
import base64
import pyotp
import datetime
from ciphervault.core.vault import PasswordVault
from ciphervault.core.utils import is_password_pwned
from ciphervault.core.utils import resolve_vault_path

@click.command('login')
@click.pass_context
def login_cmd(ctx):
    """Login to the vault"""
    db_path = resolve_vault_path(ctx.obj['db'])
    print(ctx.obj['db'])
    if not os.path.exists(db_path):
        click.echo(f"Vault file '{db_path}' does not exist.")
        click.echo("Please initialize a new vault first using 'cvault init'.")
        return
    master_password = getpass("Master password: ")
    breach_cnt = is_password_pwned(master_password)
    if breach_cnt:
        click.secho(f"The master password has been seen {breach_cnt:,} times in data breaches. Please plan to update it as soon as possible!", fg='red')
    else:
        click.secho("The master password has not been found in known data breaches. Continuing with logging in to the vault", fg='green')

    try:
        vault = PasswordVault(master_password, db_path=db_path)
        if vault.get_config("totp_key"):
            totp_code = getpass("TOTP Code: ")
            totp_key = vault.db.get_config("totp_key")
            if not totp_key:
                click.echo("TOTP not configured. Please reinitialize the vault if totp should be enabled.")
                return
            if not pyotp.TOTP(totp_key).verify(totp_code.strip()):
                click.echo("Invalid TOTP code. Access denied.")
                return
        b64_key = base64.b64encode(vault.db_key).decode()  # bytes → base64 string
        keyring.set_password("database_key", "db_key", b64_key)
        now = datetime.datetime.utcnow()
        vault.update_config("last_used", now.isoformat())
        click.echo("Login successful. Welcome to CipherVault CLI!")
        vault.lock()
    except Exception as e:
        click.echo(f"Login failed: {e}")
