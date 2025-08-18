import datetime
import click
import functools
import keyring
from ciphervault.core.vault import PasswordVault
from ciphervault.core.utils import resolve_vault_path

def sessionTimeoutCheck(f):
    """
    Check vault idle timeout and lock vault if idle too long.
    """
    @functools.wraps(f)
    @click.pass_context
    def wrapper(ctx, *args, **kwargs):
        if keyring.get_password("database_key","db_key") is None:
            click.echo("Vault is logged out. Please login again to access CipherVault")
            raise click.Abort()
        vault = PasswordVault(db_path = resolve_vault_path(ctx.obj['db']))
        # Get session timeout from config (default 60s)
        timeout_str = vault.db.get_config("session_timeout")
        timeout_seconds = int(timeout_str) if timeout_str else 60

        now = datetime.datetime.utcnow()
        last_used_str = vault.db.get_config("last_used")
        if last_used_str:
            last_used = datetime.datetime.fromisoformat(last_used_str)
            idle_time = (now - last_used).total_seconds()
            if idle_time > timeout_seconds:
                vault.update_config("last_used", now.isoformat())
                vault.close()
                click.echo(f"Vault locked due to inactivity ({int(idle_time)} seconds idle). Please log in again.")
                raise click.Abort()

        # Update last_used timestamp
        vault.update_config("last_used", now.isoformat())
        return f(*args, **kwargs)
    return wrapper