import requests, json, re

repo_author = "ppy"
repo_name = "osu"

source = {
    "name": "osu!",
    "subtitle": "rhythm is just a *click* away!",
    "description": "An AltStore and derivatives source for the rhythm game osu!.\n\nSource made by apix and hosted at https://apikusu.github.io/altstore.\n\nUpdated daily at 04:30 UTC.\n",
    "iconURL": "https://apikusu.github.io/altstore/osu/logo.png",
    "website": "https://osu.ppy.sh",
    "featuredApps": [
        "sh.ppy.osulazer"
    ],
    "apps": [],
    "news": [],
}

app_info = {
    "name": "osu!",
    "bundleIdentifier": "sh.ppy.osulazer",
    "developerName": "osu! team & contributors",
    "iconURL": "https://raw.githubusercontent.com/ppy/osu/refs/heads/master/osu.iOS/Assets.xcassets/AppIcon.appiconset/300076680-5cbe0121-ed68-414f-9ddc-dd993ac97e62.png",
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
    "versions": []
}

def get_last_release():
    response = requests.get(f"https://api.github.com/repos/{repo_author}/{repo_name}/releases/latest")
    if response.status_code == 200:
        latest_release = response.json()
        version = latest_release["tag_name"]
        # find osu.iOS.ipa in assets
        for asset in latest_release["assets"]:
            if "osu.iOS.ipa" in asset["name"]:
                download_url = asset["browser_download_url"]
                size = asset["size"]
                update_time = asset["updated_at"]
                changelog = latest_release["body"]
                break
        else:
            print("osu.iOS.ipa not found in the latest release assets.")
            exit(1)
        print("Last release is", version)
        return {
            "version": "1.0",
            "buildVersion": version,
            "marketingVersion": version,
            "date": update_time,
            "downloadURL": download_url,
            "size": size,
            "minOSVersion": "13.4",
            "localizedDescription": changelog,
            # "appPermissions": {
            #     "entitlements": ["beta-reports-active", "get-task-allow"],
            #     "privacy": {
            #         "NSCameraUsageDescription": "osu! doesn't require camera access.",
            #         "NSMicrophoneUsageDescription": "osu! doesn't require microphone access.",
            #         "NSBluetoothAlwaysUsageDescription": "osu! doesn't require Bluetooth access.",
            #     }
            # }
        }
    else:
        print(f"Failed to fetch the latest release: {response.status_code}")
        exit(1)

def get_news():
    response = requests.get("https://osu.ppy.sh/api/v2/news?limit=8")
    if response.status_code == 200:
        news = response.json()
        news_items = source["news"]
        for item in news["news_posts"]:
            url = "https://osu.ppy.sh/home/news/" + item["slug"]
            news_items.append({
                "identifier": str(item["id"]),
                "title": item["title"],
                "caption": item["preview"],
                "date": item["published_at"],
                "imageURL": item.get("first_image@2x", item["first_image"]),
                "appID": "sh.ppy.osulazer",
                "url": url,
                "tintColor": "302e38",
            })
        print("Got", len(news_items), "news")
        return news_items
    else:
        print(f"Failed to fetch news: {response.status_code}")
        return []

def get_random_background():
    # Fetch seasonal backgrounds from osu! API
    import random
    response = requests.get("https://osu.ppy.sh/api/v2/seasonal-backgrounds")
    if response.status_code == 200:
        rjson = response.json()
        backgrounds_list = rjson["backgrounds"]
        chosen_background = backgrounds_list[random.randint(0, len(backgrounds_list) - 1)]
        data = {
            "url": chosen_background["url"],
            "artist_username": chosen_background["user"]["username"],
            "artist_profile_link": "https://osu.ppy.sh/users/" + re.search(r'\/(\d+)\?', chosen_background["user"]["avatar_url"]).group(1)
        }

        source["headerURL"] = data["url"]
        source["description"] += f"\nBanner/header:\n- Artist: {data["artist_username"]} ({data["artist_profile_link"]})\n- URL: {data['url']}"
    else:
        print(f"Failed to fetch seasonal backgrounds: {response.status_code}")
    print("Got background", data["url"], "of user", data["artist_username"], data["artist_profile_link"])

app_info["versions"].append(get_last_release())
source["apps"].append(app_info)

try:
    get_random_background()
    get_news()
except Exception as e:
    print(f"Failed querying osu!web API services: {e}")

with open('res/osu/index.html', 'w') as file:
    json.dump(source, file)
    print("Created source file")