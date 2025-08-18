import click

@click.group()
@click.option('--db', help='Path to the vault database file.')
@click.pass_context
def cli(ctx, db):
    """CipherVault: Secure Password Manager CLI"""
    ctx.ensure_object(dict)
    ctx.obj['db'] = db

from ciphervault.cli.commands.add import add_cmd
from ciphervault.cli.commands.login import login_cmd
from ciphervault.cli.commands.list import list_cmd
from ciphervault.cli.commands.retrieve import retrieve_cmd
from ciphervault.cli.commands.update import update_cmd
from ciphervault.cli.commands.delete import delete_cmd
from ciphervault.cli.commands.change_algo import change_algo_cmd
from ciphervault.cli.commands.change_master_pwd import change_master_pwd_cmd
from ciphervault.cli.commands.init import init_cmd
from ciphervault.cli.commands.lock import lock_cmd
from ciphervault.cli.commands.gen_pwd import gen_pwd_cmd
from ciphervault.cli.commands.breach_check import breach_status_cmd
from ciphervault.cli.commands.export_entries import export_cmd
from ciphervault.cli.commands.export_backup import export_bkp_cmd
from ciphervault.cli.commands.import_entries import import_cmd

cli.add_command(init_cmd)
cli.add_command(add_cmd)
cli.add_command(login_cmd)
cli.add_command(list_cmd)
cli.add_command(retrieve_cmd)
cli.add_command(update_cmd)
cli.add_command(delete_cmd)
cli.add_command(change_algo_cmd)
cli.add_command(change_master_pwd_cmd)
cli.add_command(lock_cmd)
cli.add_command(gen_pwd_cmd)
cli.add_command(breach_status_cmd)
cli.add_command(import_cmd)
cli.add_command(export_cmd)
cli.add_command(export_bkp_cmd)

if __name__ == '__main__':
    cli()