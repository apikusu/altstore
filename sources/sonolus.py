import requests, json, re, ast

source = {
    "name": "Sonolus",
    "subtitle": "Next Generation Mobile Rhythm Game",
    "description": "An AltStore and derivatives source for the rhythm game Sonolus.\n\nSource made by apix and hosted at https://apikusu.github.io/altstore.\n\nUpdated daily at 04:30 UTC.\n",
    "iconURL": "https://sonolus.com/icon.png",
    "website": "https://wiki.sonolus.com/",
    "featuredApps": [
        "com.FosFenes.Sonolus"
    ],
    "apps": [],
    "news": [],
}

app_info = {
    "name": "Sonolus",
    "bundleIdentifier": "com.FosFenes.Sonolus",
    "developerName": "NonSpicyBurrito",
    "iconURL": "https://sonolus.com/icon.png",
    "tintColor": "2D2D47",
    "category": "games",
    "subtitle": "Next Generation Mobile Rhythm Game",
    "localizedDescription": "Sonolus is a next generation Mobile Rhythm Game that aims to provide maximum freedom to players and level makers.\n\nWith a powerful and performant scripting system, you can create any rhythm game engine imaginable.\nWhether it's to replicate an existing game or to create an entirely different engine, you can do it all.",
    "screenshots": [
        "https://apikusu.github.io/altstore/sonolus/screenshots/iphone-1.jpg",
        "https://apikusu.github.io/altstore/sonolus/screenshots/iphone-2.jpg",
        "https://apikusu.github.io/altstore/sonolus/screenshots/iphone-3.jpg",
        "https://apikusu.github.io/altstore/sonolus/screenshots/iphone-4.jpg",
    ],
    "versions": []
}

def get_last_version():
    response = requests.get("https://raw.githubusercontent.com/Sonolus/wiki/refs/heads/main/.vitepress/version.ts")
    if response.status_code != 200:
        print(f"Failed to fetch version file: {response.status_code}")
        exit(1)

    content = response.text
    match = re.search(r'export\s+const\s+version\s*=\s*({[^}]*})', content, re.DOTALL)
    if not match:
        print("Could not find 'version' object in the file.")
        exit(1)

    js_obj = match.group(1)
    js_obj_clean = re.sub(r'(\w+):', r'"\1":', js_obj)  # key: -> "key":
    version_dict = ast.literal_eval(js_obj_clean)
    print("Last release is", version_dict["title"])

    download_url = "https://download.sonolus.com/Sonolus_" + version_dict["link"] + ".ipa"
    size = int(requests.head(download_url).headers.get('Content-Length', '0'))

    return {
        "version": version_dict['title'].split(' ')[0],
        "buildVersion": "1",
        "marketingVersion": version_dict["title"],
        "date": get_change_time(),
        "downloadURL": download_url,
        "size": size,
        "minOSVersion": "12.0",
        "localizedDescription": get_changelog(version_dict["link"]),
        "appPermissions": {
            "entitlements": [],
            "privacy": {
                "NSPhotoLibraryAddUsageDescription": "Sonolus requires access to gallery to read QR codes.",
                "NSPhotoLibraryUsageDescription": "Sonolus requires access to gallery to read QR codes.",
                "NSCameraUsageDescription": "Sonolus requires access to camera to read QR codes."
            }
        }
    }

def get_change_time():
    response = requests.get("https://api.github.com/repos/Sonolus/wiki/commits?path=.vitepress/version.ts&page=1&per_page=1")
    if response.status_code != 200:
        print(f"Failed to fetch commit history: {response.status_code}")
        return None
    return response.json()[0]["commit"]["committer"]["date"]

def get_changelog(link_id):
    response = requests.get(f"https://raw.githubusercontent.com/Sonolus/wiki/refs/heads/main/src/en/release-notes/versions/{link_id}.md")
    if response.status_code != 200:
        print(f"Failed to fetch changelog: {response.status_code}")
        return None
    content = response.text
    # remove the 3 first lines
    content = '\n'.join(content.splitlines()[4:])

    return content

app_info["versions"].append(get_last_version())
source["apps"].append(app_info)

with open('res/sonolus/index.json', 'w') as file:
    json.dump(source, file)
    print("Created source file")