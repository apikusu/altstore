import requests
import json

repo_author = "ppy"
repo_name = "osu"

source = {
    "name": "osu!",
    "subtitle": "rhythm is just a *click* away!",
    "description": "An AltStore and derivatives source for the rhythm game osu!.\n\nSource hosted at https://apikusu.github.io/altstore.\n\nUpdated daily at 00:30 and 12:30 UTC.\n",
    "iconURL": "https://apikusu.github.io/altstore/osu/logo.png",
    "website": "https://osu.ppy.sh",
    "featuredApps": [
        "sh.ppy.osulazer"
    ],
    "apps": [],
    "news": [],
    "header_url": "https://raw.githubusercontent.com/ppy/osu-resources/refs/heads/master/osu.Game.Resources/Textures/Menu/menu-background-1.jpg"
}

app_info = {
    "name": "osu!",
    "bundleIdentifier": "sh.ppy.osulazer",
    "developerName": "osu! team & contributors",
    "iconURL": "https://apikusu.github.io/altstore/osu/AppIcon.png",
    "tintColor": "F964A7",
    "category": "games",
    "subtitle": "A free-to-win rhythm game. Rhythm is just a *click* away!",
    "localizedDescription": "This is the future – and final – iteration of the osu! game client which marks the beginning of an open era!\n\nCurrently known by and released under the release codename \"lazer\". As in sharper than cutting-edge.",
    "screenshots": [
        "https://apikusu.github.io/altstore/osu/screenshots/iphone-1.jpg",
        "https://apikusu.github.io/altstore/osu/screenshots/iphone-2.jpg",
        "https://apikusu.github.io/altstore/osu/screenshots/iphone-3.jpg",
        "https://apikusu.github.io/altstore/osu/screenshots/iphone-4.jpg",
    ],
    "appPermissions": {
        "entitlements": ["beta-reports-active", "get-task-allow"],
        "privacy": {
            "NSCameraUsageDescription": "osu! doesn't require camera access.",
            "NSMicrophoneUsageDescription": "osu! doesn't require microphone access.",
            "NSBluetoothAlwaysUsageDescription": "osu! doesn't require Bluetooth access.",
        }
    },
    "versions": []
}

def get_last_release_and_versions():
    versions = []
    # Try to read old versions from the existing index.json
    try:
        with open('res/osu/index.json', 'r', encoding="utf-8") as file:
            local_source = json.load(file)
            if local_source["apps"] and local_source["apps"][0]["versions"]:
                versions = local_source["apps"][0]["versions"]
    except Exception:
        pass  # No old file or error reading, just start with empty

    response = requests.get(f"https://api.github.com/repos/{repo_author}/{repo_name}/releases/latest")
    if response.status_code == 200:
        latest_release = response.json()
        version = latest_release["tag_name"]
        for asset in latest_release["assets"]:
            if "osu.iOS.ipa" in asset["name"]:
                download_url = asset["browser_download_url"]
                size = asset["size"]
                update_time = asset["updated_at"]
                changelog = latest_release["body"]
                print("Last release is", version)
                new_version = {
                    "version": "1.0",
                    "buildVersion": version.replace("-lazer", ""),
                    "marketingVersion": version,
                    "date": update_time,
                    "downloadURL": download_url,
                    "size": size,
                    "minOSVersion": "13.4",
                    "localizedDescription": changelog,
                }
                # Only prepend if not already present
                if not any(v.get("buildVersion") == version.replace("-lazer", "") for v in versions):
                    versions.insert(0, new_version)
                return versions
        # If no iOS release found, just return old versions
        print("osu.iOS.ipa not found in the latest release assets, checking local file...")
        return versions
    else:
        print(f"Failed to fetch the latest release: {response.status_code}")
        return versions

app_info["versions"] = get_last_release_and_versions()
source["apps"].append(app_info)

with open('res/osu/index.json', 'w', encoding="utf-8") as file:
    json.dump(source, file, ensure_ascii=False)
    print("Created source file")
