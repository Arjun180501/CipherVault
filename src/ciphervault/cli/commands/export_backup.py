import os
import shutil
import click
from ciphervault.core.utils import get_vaults_dir

@click.command('export-bkp')
@click.option('--dest', 'dest_folder', required=True, type=click.Path(file_okay=False, writable=True), help="Destination folder to export full backup")
def export_bkp_cmd(dest_folder):
    """Export all vaults (db + salt + vaults.json combined metadata) to destination folder."""

    vaults_dir = get_vaults_dir()

    if not os.path.exists(vaults_dir):
        click.echo(f"Vaults directory not found: {vaults_dir}")
        return

    os.makedirs(dest_folder, exist_ok=True)

    # Copy all vault files and salts
    for item in os.listdir(vaults_dir):
        s = os.path.join(vaults_dir, item)
        d = os.path.join(dest_folder, item)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)

    click.echo(f"Full vault backup successfully exported to '{dest_folder}'.")
