# GSC Weather Channel — NWS Weather Story Edition

This is a copy of the main GSC Weather Channel with an added feature: it pulls **all images** from the Philadelphia NWS Weather Story page tabs and rotates them with the live radar.

## What's different from the main version

- The live radar still animates as before.
- Every 30 seconds the radar is replaced by one of the NWS Weather Story images.
- It grabs **every image under every tab** for that day, not just severe/flood.
- The rotation order is: **radar → image 1 → radar → image 2 → radar → image 3 → repeat**.
- A GitHub Actions workflow automatically downloads fresh images every hour from 10:00 UTC to 22:00 UTC (6 AM - 6 PM Eastern Time).
- Images are saved in a date-stamped folder (`assets/YYYY-MM-DD/`) for archiving, and also copied to `assets/` as the latest version for the live site.

## Files to upload to GitHub

Upload the entire contents of this folder to a new GitHub repository, including the hidden `.github` folder:

- `index.html`
- `logo.png`
- `assets/` (contains the scraped images; the workflow will update these daily)
- `.github/workflows/scrape-weatherstory.yml`
- `scripts/scrape_weatherstory.py`

## How to enable GitHub Pages

1. Create a new public repo on GitHub.
2. Upload all files above.
3. Go to **Settings → Pages**.
4. Source: **Deploy from a branch** → **main** → **/ (root)**.
5. Save.

## How to enable the daily image scraper

The scraper is controlled by `.github/workflows/scrape-weatherstory.yml`. It runs automatically once the file is on the `main` branch.

To run it manually the first time:

1. Go to **Actions** in the repo.
2. Click **Scrape NWS Weather Story Images**.
3. Click **Run workflow**.

## Notes

- The scraper fetches images from `https://www.weather.gov/phi/weatherstory`.
- If NWS changes the page layout, the scraper may break and need updating.
- GitHub disables scheduled workflows after 60 days of inactivity. A push or manual run re-enables them.
