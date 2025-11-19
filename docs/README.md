# Documentation

This directory contains the source files for the Diabetes Tracker documentation, which is automatically built and deployed to GitHub Pages.

## Building Documentation Locally

To build and preview the documentation locally:

1. **Install documentation dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Serve the documentation locally:**
   ```bash
   mkdocs serve
   ```
   
   The documentation will be available at `http://127.0.0.1:8000`

3. **Build static documentation:**
   ```bash
   mkdocs build
   ```
   
   This creates a `site/` directory with the static HTML files.

## Documentation Structure

- `index.md` - Home page
- `overview.md` - Project overview and setup instructions
- `api/` - API reference documentation
  - `app.md` - Flask application routes
  - `auth.md` - Authentication module
  - `database.md` - Database module
  - `ai_recommendations.md` - AI recommendations module
  - `unit_converter.md` - Unit converter module

## Automatic Updates

The documentation automatically extracts docstrings from the Python source code using `mkdocstrings`. When you update docstrings in `src/**/*.py` files, the documentation will reflect those changes after the next build.

## GitHub Pages Deployment

The documentation is automatically deployed to GitHub Pages when:
- Changes are pushed to `main` or `master` branch
- Files in `src/**/*.py`, `docs/**/*.md`, `*.md`, or `mkdocs.yml` are modified

The workflow is defined in `.github/workflows/docs.yml`.

## Viewing Documentation

Once deployed, the documentation will be available at:
`https://YC-1412.github.io/diabetes_tracker`

