# QuickBib website (docs)

This folder contains a small static website for QuickBib. Files:

- `index.html` — landing page
- `styles.css`, `script.js` — assets

Preview locally (simple HTTP server):

```bash
# from the repo root
python3 -m http.server --directory docs 8000
# then open http://localhost:8000 in your browser
```

Publish with GitHub Pages:

1. Ensure this repository's GitHub Pages is configured to serve from the `gh-pages` branch or the `docs/` folder on the `main` branch.
2. Commit the `docs/` folder and push. GitHub will serve `index.html` automatically.
