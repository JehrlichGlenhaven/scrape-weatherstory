import json
import os
import sys

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
        filepath = os.path.join(OUTPUT_DIR, filename)
        download_image(url, filepath)
        manifest.append({"src": f"assets/{filename}", "label": label})

    # Save manifest so the frontend knows which images exist and their labels
    manifest_path = os.path.join(OUTPUT_DIR, MANIFEST_FILE)
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Saved manifest -> {manifest_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
