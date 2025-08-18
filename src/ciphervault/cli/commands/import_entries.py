import os
import shutil
import click
from ciphervault.core.utils import get_vaults_dir

@click.command('import')
@click.argument('src_folder', type=click.Path(exists=True, file_okay=False, readable=True))
def import_cmd(src_folder):
    """
    Import vault(s) from source folder into the local vaults directory.
    Supports importing multiple vault files, salts, and single vaults.json metadata.
    """

    vaults_dir = get_vaults_dir()

    vault_files = [f for f in os.listdir(src_folder) if f.endswith('.db')]
    salt_files = [f for f in os.listdir(src_folder) if f.endswith('.salt')]

    for db_file in vault_files:
        base_name = os.path.splitext(db_file)[0]
        salt_file = next((s for s in salt_files if s.startswith(base_name)), None)
        if not salt_file:
            click.echo(f"Warning: No salt file found for vault '{db_file}'. Skipping import.")
            continue

        dest_db = os.path.join(vaults_dir, db_file)
        dest_salt = os.path.join(vaults_dir, salt_file)

        if os.path.exists(dest_db) or os.path.exists(dest_salt):
            click.echo(f"Vault or salt file '{db_file}' or '{salt_file}' already exists.")
            rename = click.prompt(f"Type new vault name to rename imported vault or leave blank to overwrite existing", default="", show_default=False)
            if rename:
                dest_db = os.path.join(vaults_dir, rename + os.path.splitext(db_file)[1])
                dest_salt = os.path.join(vaults_dir, rename + '.salt')
            else:
                click.echo("Overwriting existing vault files.")

        shutil.copy2(os.path.join(src_folder, db_file), dest_db)
        shutil.copy2(os.path.join(src_folder, salt_file), dest_salt)

        click.echo(f"Imported vault '{base_name}'")

    click.echo(f"Vault metadata updated, import complete.")
