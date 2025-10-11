import requests, json, re, datetime, random
from bs4 import BeautifulSoup

source = {
    "name": "Sonolus",
    "subtitle": "Next Generation Mobile Rhythm Game",
    "description": "An AltStore and derivatives source for the rhythm game Sonolus.\n\nSource made by apix and hosted at https://apikusu.github.io/altstore.\n\nThis source will not be updated.\n",
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
    "appPermissions": {
        "entitlements": [
             "com.apple.developer.associated-domains",
             "com.apple.developer.ubiquity-container-identifiers",
             "com.apple.developer.icloud-container-environment",
             "com.apple.developer.icloud-container-identifiers",
             "com.apple.developer.icloud-services",
             "beta-reports-active"
        ],
        "privacy": {
            "NSPhotoLibraryAddUsageDescription": "Sonolus requires access to gallery to read QR codes.",
            "NSPhotoLibraryUsageDescription": "Sonolus requires access to gallery to read QR codes.",
            "NSCameraUsageDescription": "Sonolus requires access to camera to read QR codes."
        }
    },
    "versions": []
}

def get_last_version_and_versions():
    versions = []
    # Try to read old versions from the existing index.json
    try:
        with open('res/sonolus/index.json', 'r', encoding="utf-8") as file:
            local_source = json.load(file)
            if local_source["apps"] and local_source["apps"][0]["versions"]:
                versions = local_source["apps"][0]["versions"]
    except Exception:
        pass  # No old file or error reading, just start with empty

    response = requests.get("https://wiki.sonolus.com/release-notes/")
    if response.status_code != 200:
        print(f"Failed to fetch version file: {response.status_code}")
        return versions
    content = response.text
    soup = BeautifulSoup(content, 'html.parser')
    version_link = soup.find('a', href=re.compile(r'^/release-notes/versions/'))
    version_dict = {}
    version_dict["link"] = version_link['href'].split('/')[-1]
    version_dict["title"] = version_link.text.strip()

    print("Last release is", version_dict["title"], "with id", version_dict["link"])

    download_url = "https://download.sonolus.com/Sonolus_" + version_dict["link"] + ".ipa"
    size = int(requests.head(download_url).headers.get('Content-Length', '0'))

    new_version = {
        "version": version_dict['title'].split(' ')[0],
        "buildVersion": "2",
        "marketingVersion": version_dict["title"],
        "date": get_change_time(),
        "downloadURL": download_url,
        "size": size,
        "minOSVersion": "13.0",
        "localizedDescription": get_changelog(version_dict["link"]),
    }
    # Only prepend if not already present (by marketingVersion)
    if not any(v.get("marketingVersion") == new_version["marketingVersion"] for v in versions):
        versions.insert(0, new_version)
    return versions

def get_change_time():
    try:
        response = requests.get("https://api.github.com/repos/Sonolus/wiki/commits?path=.vitepress/version.ts&page=1&per_page=1&sha=prod")
        if response.status_code != 200:
            print(f"Failed to fetch commit history: {response.status_code}")
        return response.json()[0]["commit"]["committer"]["date"]
    except Exception as e:
        print(f"Exception occurred: {e}")
        return datetime.datetime.now().isoformat()

def get_changelog(link_id):
    response = requests.get(f"https://raw.githubusercontent.com/Sonolus/wiki/refs/heads/prod/src/en/release-notes/versions/{link_id}.md")
    if response.status_code != 200:
        print(f"Failed to fetch changelog: {response.status_code}")
        return None
    content = response.text
    # remove the 3 first lines
    content = '\n'.join(content.splitlines()[4:])

    return content

def get_random_theme_background():
    response = requests.get("https://content.sonolus.com/info.json")
    if response.status_code == 200:
        rjson = response.json()
        backgrounds = [
            theme["background"]["url"]
            for theme in rjson.get("themes", [])
            if "background" in theme and "url" in theme["background"]
        ]
        if backgrounds:
            chosen_url = random.choice(backgrounds)
            print("Random background URL:", chosen_url)
            source["headerURL"] = 'https://content.sonolus.com' + chosen_url
        else:
            print("No backgrounds found in themes.")
            return None
    else:
        print(f"Failed to fetch themes: {response.status_code}")
        return None

try:
    get_random_theme_background()
except Exception as e:
    print(f"Failed querying Sonolus API: {e}")

app_info["versions"] = get_last_version_and_versions()
source["apps"].append(app_info)

with open('res/sonolus/index.json', 'w', encoding="utf-8") as file:
    json.dump(source, file, ensure_ascii=False)
    print("Created source file")