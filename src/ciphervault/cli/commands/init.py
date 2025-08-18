import os
import click
import pyotp
from getpass import getpass
from ciphervault.core.vault import PasswordVault
from ciphervault.core.utils import resolve_vault_path

@click.command('init')
@click.option('--algo', type=click.Choice(['aes', 'chacha', 'hybrid']), default='hybrid', help='Encryption algorithm.')
@click.option('--db', help='Full Path to the vault database file.')
@click.option('--enable-mfa/--disable-mfa', default=None, help='Enable or disable TOTP. If not set, will prompt interactively.')
def init_cmd(algo, db, enable_mfa):
    """Initialize a new vault."""
    db_path = resolve_vault_path(db)
    
    if os.path.exists(db_path):
        click.confirm(f"Vault file '{db}' already exists. Overwrite?", abort=True)
        os.remove(db_path)
        salt_path = resolve_vault_path(f"{os.path.splitext(db)[0]}.salt")
        if os.path.exists(salt_path):
            os.remove(salt_path)
    
    while True:
        master_password = getpass("Set a new master password: ")
        confirm_password = getpass("Confirm master password: ")
        if master_password == confirm_password:
            break
        click.echo("Passwords do not match. Please try again.")
    
    if enable_mfa is None:
        enable_mfa = click.confirm("Do you want to enable Two-Factor Authentication (TOTP)?", default=True)
    
    if enable_mfa:
        totp_secret = pyotp.random_base32()
        totp_uri = pyotp.TOTP(totp_secret).provisioning_uri(name="User", issuer_name="CipherVault")
        click.secho(f"Secret (enter this in your authenticator app): ", fg="yellow", nl=False)
        click.secho(totp_secret, fg="green")
        click.echo()
        click.secho("Or, use this URI (you can paste it into some apps, or generate a QR code online):", fg="yellow")
        click.secho(totp_uri, fg="cyan")
        totp_code = input("Enter the 6-digit TOTP code from your app: ").strip()
        if not pyotp.TOTP(totp_secret).verify(totp_code):
            click.echo("TOTP code is incorrect. Please try again!")
            return
    else:
        totp_secret = None
    
    vault = PasswordVault(master_password, db_path=db, algorithm=algo)
    vault.db.set_config("totp_key", totp_secret)
    click.echo(f"Vault registered and initialized at '{db_path}' with algorithm: {algo}")
    vault.lock()