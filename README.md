# Penny Scout Live — Trussville Home Depot #0887

A mobile-first installable web app for **community-reported penny-item leads**, UPC / SKU scanning, your own watchlist, and manual price notes. It is **not** an official Home Depot app and **cannot** access Home Depot's live checkout prices or local inventory.

## What is automated?

The included GitHub Actions workflow downloads the publicly linked [Penny Recon item JSON](https://www.pennyrecon.com/data/items.json) twice daily, curates up to 175 *recent* product leads, prioritizes Alabama reports, and publishes a fresh website to **GitHub Pages**. Leads include product name, SKU, UPC (when published), report date, and state-level report counts. There is NO verification that any product is 1¢ or stocked at Trussville #0887.

Your phone's app checks the latest published data on opening, after returning to the foreground, roughly every 20 minutes while open, and when you press **Refresh**. When offline, it keeps the previously cached snapshot and its date. When an item is newly added, the app marks it as a new feed lead while the app is open. **No background iPhone push alerts** are implemented.

## Turn on real automatic updates (GitHub Pages)

You need a GitHub account. The ZIP by itself is a starter snapshot; **uploading only to Netlify Drop will NOT run the update job**.

1. Download and **extract** `penny-scout-live-trussville.zip` on a computer. Extract files, not just the ZIP itself.
2. On [GitHub](https://github.com/new), create a **public** repository named `penny-scout-live`. Use branch `main` (GitHub's default). Don't add a separate README/license when creating it since this package includes one.
3. In the new repository, use **Add file → Upload files** and upload the package contents including the nested `.github/workflows/publish.yml` file and `scripts` folder. Keep the exact folder structure. On macOS, hidden `.github` may require `Cmd+Shift+.` to display. Alternatively use Git on desktop; the provided directory is already ready to commit.
4. Open **Settings → Pages → Build and deployment → Source → GitHub Actions**.
5. Open **Actions → Refresh penny leads and publish app → Run workflow → Run workflow**. Wait for it to finish successfully.
6. Your website appears at `https://YOUR_USERNAME.github.io/penny-scout-live/` (replace `YOUR_USERNAME` with your actual GitHub handle). Check **Actions** for the real deployment URL; don't assume it exists until publishing succeeds.
7. On iPhone, open your actual HTTPS website in Safari → Share → **Add to Home Screen**.

### Updating the previous Netlify version

The old Netlify ZIP deployment is static. GitHub Pages is the recommended path for scheduled refresh. This setup creates a new website URL; existing data saved on a different origin (such as Netlify) does not automatically move between sites. Export a **JSON backup** from your old app and import it in the new one under **Settings & backups**.

### If it stops refreshing

Go to **GitHub → Actions**. Check the latest run, re-run it manually if needed, and review any published error. Scheduled workflows can be delayed and may be disabled after prolonged repository inactivity (GitHub documents 60 days for public repositories). Upstream sources may change or block requests, in which case the last published dataset remains dated rather than being labeled fresh.

## Scope / privacy / interpretation

- Only public Penny Recon JSON is read by the scheduled Python updater. No secret credentials or Home Depot internal APIs are used. The linked data source updates independently; this website does **not** claim the feed is a real-time checkout signal.
- Alabama is a **state-wide** report, not a confirmed price in Trussville, Pell City, or another particular store. Neighboring-state signals are likewise not local.
- The app links reports back to Penny Recon and product identifiers to Home Depot. Community reports may be missing, mistyped, old, or duplicated.
- The app avoids selling or advertising penny-price certainty. Home Depot stores can pull merchandise and refuse to sell it.
- Your watchlist, scans, and observed prices stay on **your own browser** in localStorage; they are not submitted to GitHub or Penny Recon. Export a backup before clearing browser data or changing web domains.
- The scan camera needs HTTPS and loads `html5-qrcode` from a public CDN when you open it. Scanning a UPC identifies the item from published or saved identifiers; it does not query a checkout register.

## Developer notes

- `scripts/update_leads.py`: validates/normalizes source JSON and timestamps, drops old/invalid entries, assigns Alabama/neighboring/national tags and generates `data/leads.json`.
- `scripts/build_site.py`: copies safe public web files to `_site/` for GitHub Pages artifact deployment; private source files are not published.
- `.github/workflows/publish.yml`: schedule and manual publisher. Attempts to commit successful source-data updates so the repository has a visible update history, then explicitly deploys to Pages.
- `tests/test_update_leads.py`: offline data-logic tests. Run `python -m unittest discover -s tests -p 'test_*.py'`.
- Source UI generated as plain HTML, CSS, and JavaScript. No npm packages required to build.

Source: https://www.pennyrecon.com/data/items.json . No affiliation with Penny Recon, Home Depot, or Lowe's.
