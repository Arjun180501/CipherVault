
import os, json

def load_vaults(vaults_path):
    if not os.path.exists(vaults_path):
        return []
    try:
        with open(vaults_path, "r") as f:
            data = json.load(f)
            return data.get("vaults", [])
    except Exception as e:
        print("Error reading vaults.json:", e)
        return []
