import json
import os
import shutil
import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup

URL = "https://www.weather.gov/phi/weatherstory"
OUTPUT_DIR = "assets"
MANIFEST_FILE = "weatherstory-manifest.json"


def download_image(url: str, path: str) -> None:
    """Download an image and save it to the repo."""
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    with open(path, "wb") as f:
        f.write(response.content)
    print(f"Downloaded {url} -> {path}")


def normalize_url(src: str) -> str:
    """Make a scraped image URL absolute and HTTPS."""
    src = src.strip()
    if src.startswith("/"):
        return f"https://www.weather.gov{src}"
    if src.startswith("http://"):
        return src.replace("http://", "https://", 1)
    return src


def scrape_tab_images(soup: BeautifulSoup) -> list:
    """
    Scrape all images from the NWS Weather Story tabbed interface.
    Returns a list of (label, image_url) tuples in tab order.
    """
    nav_links = soup.select(".c-tabs-nav__link")
    tab_panes = soup.select(".c-tab")

    if len(nav_links) != len(tab_panes):
        raise ValueError(
            f"Mismatched tabs: {len(nav_links)} nav links, {len(tab_panes)} panes"
        )

    results = []
    for nav, pane in zip(nav_links, tab_panes):
        label = nav.get_text(strip=True)
        img = pane.find("img")
        if not img:
            continue
        src = img.get("src", "").strip()
        if not src:
            continue
        results.append((label, normalize_url(src)))

    return results


def main() -> int:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    date_dir = os.path.join(OUTPUT_DIR, today)
    os.makedirs(date_dir, exist_ok=True)

    print(f"Fetching {URL} ...")
    response = requests.get(URL, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    try:
        tab_images = scrape_tab_images(soup)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    if not tab_images:
        print("ERROR: No Weather Story images found", file=sys.stderr)
        return 1

    print(f"Found {len(tab_images)} tab image(s):")
    manifest = []
    for idx, (label, url) in enumerate(tab_images, start=1):
        print(f"  - {label}: {url}")
        filename = f"weatherstory-{idx}.png"

        # Download to the date-stamped archive folder
        date_filepath = os.path.join(date_dir, filename)
        download_image(url, date_filepath)

        # Copy to the root assets folder as the "latest" version for the frontend
        latest_filepath = os.path.join(OUTPUT_DIR, filename)
        shutil.copy2(date_filepath, latest_filepath)

        manifest.append({"src": f"assets/{filename}", "label": label})

    # Save manifest in the date-stamped archive folder
    date_manifest_path = os.path.join(date_dir, MANIFEST_FILE)
    with open(date_manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Saved archive manifest -> {date_manifest_path}")

    # Save manifest in the root assets folder so the frontend finds the latest images
    latest_manifest_path = os.path.join(OUTPUT_DIR, MANIFEST_FILE)
    with open(latest_manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Saved latest manifest -> {latest_manifest_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
