# PDF Creator Integration for Autohive

Create and update PDFs with no authentication required.

- Creation powered by ReportLab (robust layout engine: paragraphs, tables, images, headers/footers).
- Updating powered by pypdf (merge/overlay for watermarking, append pages).

## Actions

### create_pdf
Generate a PDF from structured inputs.

Inputs:
- `title` (string, required)
- `table_data` (array of array of strings, optional)
- `image_base64` (string, optional)
- `image_url` (string, optional)
- `header_text` (string, optional)
- `footer_text` (string, optional)
- `page_size` ("LETTER" | "A4", default: "LETTER")

Outputs:
- `pdf_base64` (string) – Base64-encoded PDF
- `pages` (integer)

### update_pdf
Update an existing PDF (apply a text watermark and/or append a page with text).

Inputs:
- `pdf_base64` (string, required)
- `watermark_text` (string, optional)
- `append_text` (string, optional)

Outputs:
- `pdf_base64` (string)
- `pages` (integer)

## Requirements

Install dependencies into a local `dependencies` folder (or per your environment):

```
pip install -r requirements.txt -t dependencies
```

## Notes
- If both `image_base64` and `image_url` are provided, `image_base64` is preferred.
- Watermark is applied diagonally, semi-transparent, across all pages.
- Appended page is simple text; extend as needed for richer content.
