import requests
import zipfile
import os
import json
import yaml
import re

# === Prompt for API key if not already saved or is empty ===
token_file = "token.yml"
api_key = None

if os.path.exists(token_file):
    with open(token_file, "r") as f:
        try:
            token_data = yaml.safe_load(f) or {}
            api_key = token_data.get("curseforge_api_key", "").strip()
        except yaml.YAMLError:
            print("⚠️ Failed to parse token.yml. Deleting and starting fresh.")
            os.remove(token_file)
            api_key = ""

if not api_key:
    api_key = input("🔑 Enter your CurseForge API token: ").strip()
    with open(token_file, "w") as f:
        yaml.dump({"curseforge_api_key": api_key}, f)

headers = {"x-api-key": api_key}

# === Ask for modpack ZIP file path ===
zip_path = input("📦 Drag your modpack .zip file here and press Enter: ").strip('"')

if not zip_path.lower().endswith(".zip") or not os.path.exists(zip_path):
    print("❌ Invalid zip file. Please try again.")
    exit(1)

# === Extract manifest.json ===
extract_dir = "modpack_temp"
os.makedirs(extract_dir, exist_ok=True)

try:
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
except zipfile.BadZipFile:
    print("❌ Error: Not a valid ZIP file.")
    exit(1)

manifest_path = os.path.join(extract_dir, "manifest.json")
if not os.path.exists(manifest_path):
    print("❌ No manifest.json found inside ZIP.")
    exit(1)

with open(manifest_path, "r") as f:
    manifest = json.load(f)

project_ids = [entry["projectID"] for entry in manifest.get("files", [])]

# === Download mod logos ===
logo_dir = "mod_logos"
os.makedirs(logo_dir, exist_ok=True)

def safe_filename(text):
    return re.sub(r'[\\/:*?"<>|]', '-', text)

print(f"🎯 Fetching info for {len(project_ids)} mods...")

for mod_id in project_ids:
    res = requests.get(f"https://api.curseforge.com/v1/mods/{mod_id}", headers=headers)
    if res.status_code == 200:
        data = res.json()["data"]
        name = safe_filename(data["name"])
        author = safe_filename(data["authors"][0]["name"])
        logo_url = data["logo"]["url"]

        img = requests.get(logo_url).content
        filename = f"{name} - {author}.png"
        with open(os.path.join(logo_dir, filename), "wb") as f:
            f.write(img)

        print(f"✅ Saved: {filename}")
    else:
        print(f"❌ Failed to get mod info for ID {mod_id} (HTTP {res.status_code})")

print("🏁 Done. Logos saved to 'mod_logos/' folder.")
