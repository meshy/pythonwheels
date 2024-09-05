import datetime
import json
import pytz
import requests


BASE_URL = "https://pypi.org/pypi"

DEPRECATED_PACKAGES = {
    "BeautifulSoup",
    "bs4",
    "distribute",
    "django-social-auth",
    "nose",
    "pep8",
    "pycrypto",
    "pypular",
    "sklearn",
}

SESSION = requests.Session()

# Updated ~ when the release candidates start to appear
# Goal: to have as many as possible wheels ready to use from the day it's released
NEWEST_PYTHON_VER = "3.13"
NEWEST_PYTHON_ABI_TAG = "cp313"


def get_json_url(package_name):
    return BASE_URL + "/" + package_name + "/json"


def annotate_wheels(packages):
    print("Getting wheel data...")
    num_packages = len(packages)
    for index, package in enumerate(packages):
        print(index + 1, num_packages, package["name"])
        has_wheel = False
        has_newest_wheel = False
        url = get_json_url(package["name"])
        response = SESSION.get(url)
        if response.status_code != 200:
            print(" ! Skipping " + package["name"])
            continue
        data = response.json()
        for download in data["urls"]:
            if download["packagetype"] == "bdist_wheel":
                has_wheel = True
                abi_tag = download["filename"].split("-")[-2]
                # wheel can be universal or compiled for the specific Python version
                # there can be additional letters at the end of the abi tag
                # e.g. "cp313t" built for free-threading
                if abi_tag in ["none", "abi3"] or abi_tag.startswith(NEWEST_PYTHON_ABI_TAG):
                    has_newest_wheel = True
        package["wheel"] = has_wheel
        package["newest_wheel"] = has_newest_wheel

        # Display logic. I know, I'm sorry.
        package["value"] = 1
        if has_newest_wheel:
            package["css_class"] = "success"
            package["icon"] = "\u2713"  # Check mark
            package["title"] = f"This package provides a wheel compatible with Python {NEWEST_PYTHON_VER}."
        elif has_wheel:
            package["css_class"] = "warning"
            package["icon"] = "\u23FA"  # Circle
            package["title"] = "This package provides a wheel."
        else:
            package["css_class"] = "default"
            package["icon"] = "\u2717"  # Ballot X
            package["title"] = "This package has no wheel archives uploaded " "(yet!)."


def get_top_packages():
    print("Getting packages...")

    with open("top-pypi-packages.json") as data_file:
        packages = json.load(data_file)["rows"]

    # Rename keys
    for package in packages:
        package["downloads"] = package.pop("download_count")
        package["name"] = package.pop("project")

    return packages


def not_deprecated(package):
    return package["name"] not in DEPRECATED_PACKAGES


def remove_irrelevant_packages(packages, limit):
    print("Removing cruft...")
    active_packages = list(filter(not_deprecated, packages))
    return active_packages[:limit]


def save_to_file(packages, file_name):
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    with open(file_name, "w") as f:
        f.write(
            json.dumps(
                {
                    "data": packages,
                    "last_update": now.strftime("%A, %d %B %Y, %X %Z"),
                },
                indent=1,
            )
        )
