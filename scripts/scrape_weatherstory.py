import os
import re
import sys

import requests
from bs4 import BeautifulSoup

URL = "https://www.weather.gov/phi/weatherstory"
OUTPUT_DIR = "assets"


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


def scrape_tab_images(soup: BeautifulSoup) -> dict:
    """
    Scrape the NWS Weather Story tabbed interface.
    Returns a dict mapping topic keywords to image URLs.
    """
    # Tab navigation labels (e.g. "Today's Severe Thunderstorm Potential")
    nav_links = soup.select(".c-tabs-nav__link")
    # Tab content panes (each contains one image)
    tab_panes = soup.select(".c-tab")

    if len(nav_links) != len(tab_panes):
        raise ValueError(
            f"Mismatched tabs: {len(nav_links)} nav links, {len(tab_panes)} panes"
        )

    results = {}
    for nav, pane in zip(nav_links, tab_panes):
        label = nav.get_text(strip=True)
        img = pane.find("img")
        if not img:
            continue
        src = img.get("src", "").strip()
        if not src:
            continue
        results[label] = normalize_url(src)

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

    print("Found tab images:")
    for label, url in tab_images.items():
        print(f"  - {label}: {url}")

    # Map the scraped labels to our output files
    severe_url = None
    flood_url = None
    for label, url in tab_images.items():
        if re.search(r"severe\s+thunderstorm", label, re.IGNORECASE):
            severe_url = url
        elif re.search(r"flash\s+flooding", label, re.IGNORECASE):
            flood_url = url

    if not severe_url:
        print("ERROR: Could not find Severe Thunderstorm Potential image", file=sys.stderr)
        return 1
    if not flood_url:
        print("ERROR: Could not find Flash Flooding Potential image", file=sys.stderr)
        return 1

    download_image(severe_url, os.path.join(OUTPUT_DIR, "severe-risk.png"))
    download_image(flood_url, os.path.join(OUTPUT_DIR, "flood-risk.png"))

    return 0


if __name__ == "__main__":
    sys.exit(main())
