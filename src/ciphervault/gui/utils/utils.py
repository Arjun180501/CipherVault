import os
from ciphervault.core.utils import get_vaults_dir

def load_vaults():
    vaults_dir = get_vaults_dir()
    vaults = []
    if not os.path.exists(vaults_dir):
        return vaults
    for filename in os.listdir(vaults_dir):
        if filename.endswith(".db"):
            vault_name = os.path.splitext(filename)[0]
            vaults.append({
                "name": vault_name,
                "path": os.path.join(vaults_dir, filename)
            })
    return vaults
