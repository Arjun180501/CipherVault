import os
import json
import shutil
import click
from ciphervault.core.utils import get_vaults_dir

@click.command('export')
@click.option('--vaults', 'vault_filenames', multiple=True, required=True, help="Vault filenames to export (e.g., arjun.db)")
@click.option('--dest', 'dest_folder', required=True, type=click.Path(file_okay=False, writable=True), help="Destination folder to export vaults and metadata")
def export_cmd(vault_filenames, dest_folder):
    """Export selected vaults (db + salt + combined vaults.json metadata) to destination folder."""

    vaults_dir = get_vaults_dir()
    os.makedirs(dest_folder, exist_ok=True)

    exported_meta = {'vaults': []}
    for vault_filename in vault_filenames:

        source_db_path = os.path.join(vaults_dir, vault_filename)
        source_salt_path = os.path.join(vaults_dir, vault_filename + ".salt")

        if not os.path.exists(source_db_path):
            click.echo(f"Vault file not found: {source_db_path}")
            continue
        if not os.path.exists(source_salt_path):
            click.echo(f"Salt file not found: {source_salt_path}")
            continue

        # Copy vault files
        shutil.copy2(source_db_path, os.path.join(dest_folder, vault_filename))
        shutil.copy2(source_salt_path, os.path.join(dest_folder, vault_filename + ".salt"))

    click.echo(f"Exported {len(exported_meta['vaults'])} vault(s) to '{dest_folder}'")
