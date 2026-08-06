# JSU Art Collection

A clean GitHub Pages site for the Jackson State University Department of Art permanent collection.

## What is included

- CSV-backed artwork metadata at `_data/jsuart_metadata.csv`
- Artwork images in `objects/`
- Static site files in `index.html`, `styles.css`, and `app.js`
- Generated browser-ready collection data in `site-data/artworks.json`
- GitHub Pages deployment workflow in `.github/workflows/deploy-pages.yml`

## Refresh the browser data

When the CSV changes, regenerate `site-data/artworks.json`:

```bash
python3 scripts/build_data.py
```

## Deploy

This repository is configured for GitHub Pages via GitHub Actions on `main`.
