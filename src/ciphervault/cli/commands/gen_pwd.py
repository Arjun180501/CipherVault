import click
from ciphervault.core.utils import generate_password, copy_clipboard
from ciphervault.cli.utils import sessionTimeoutCheck

@click.command('gen-pwd')
@sessionTimeoutCheck
@click.option('--length', default=16, help='Length of password.', type=int)
@click.option('--no-uppercase', is_flag=True, help='Exclude uppercase letters.')
@click.option('--no-digits', is_flag=True, help='Exclude digits.')
@click.option('--no-symbols', is_flag=True, help='Exclude symbols.')
@click.option('--copy', is_flag=True, help='Copy the password to clipboard.')
@click.option('--timeout', type=int, default=30, show_default=True, help='Seconds before clearing the clipboard.')
@click.pass_context
def gen_pwd_cmd(ctx, length, no_uppercase, no_digits, no_symbols, copy, timeout):
    """
    Generate a secure random password.
    """
    password = generate_password(
        length=length,
        use_uppercase=not no_uppercase,
        use_digits=not no_digits,
        use_symbols=not no_symbols
    )
    click.echo(f"Generated password:\n{password}")
    if copy:
        copy_clipboard(password)
        click.echo(f"Password copied to clipboard. Set to disappear in {timeout} seconds")