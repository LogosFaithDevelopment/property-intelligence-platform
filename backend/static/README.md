# Static Assets for PDF Reports

## Logo Setup

To enable the logo on PDF reports, copy the `home-logos.png` file from the frontend to this directory:

```bash
# From the project root
cp frontend/public/home-logos.png backend/static/home-logos.png
```

The PDF report generator will automatically use this logo for the cover page.

## File Requirements

- **File name**: `home-logos.png`
- **Recommended size**: 800x260 pixels (or similar aspect ratio)
- **Format**: PNG with transparent background preferred
- **Location**: `/backend/static/home-logos.png`

## Fallback

If the logo file is not found, the PDF will display "LOGOS FAITH DEVELOPMENT" as text instead.
