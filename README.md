# DATA-430 Project 3: Web Scraping and Multi-Format Output

## Project overview
This individual project scrapes every quote from https://quotes.toscrape.com/ and saves the same records in CSV, plain text, JSON, and YAML formats.

The scraper follows the website's `Next` link until no next-page link exists. It does not hardcode the number of pages. Each record contains:
- `quote`
- `author`
- `tags`
- `page`
- `scraped_at`

PySpark ingestion and database storage are not required for this project.

## Requirements
- Python 3.8 or later
- Internet connection

## Windows installation

1. Open Command Prompt in this project folder.
2. (Recommended) Create a virtual environment:

   ```bash
   py -m venv .venv
   ```

3. Activate it:

   ```bash
   .venv\Scripts\activate
   ```

4. Install the dependencies:

   ```bash
   py -m pip install -r requirements.txt
   ```

## Run the scraper

From the project folder, run:

```bash
py scraper.py
```

The script runs without command-line arguments. It fetches all pages, extracts quotes, authors, and tags, and overwrites the four files in `output/`.

## Output files
- `output/quotes.csv` — tags joined with semicolons
- `output/quotes.txt` — labelled fields, one block per quote
- `output/quotes.json` — canonical JSON array, indented two spaces
- `output/quotes.yaml` — YAML list of mappings

All four files contain the same records in the same order. The `scraped_at` timestamp is shared by all records in a run.

## Validation
After running the script:
1. Confirm the terminal summary reports the pages fetched and quotes extracted.
2. Open `output/quotes.json` and confirm each record has all five fields.
3. Confirm the CSV header is exactly `quote,author,tags,page,scraped_at`.
4. Confirm all four output files have been created or overwritten.

## Dependencies
Only `requests`, `beautifulsoup4`, and `PyYAML` are used. The project does not use Scrapy, pandas, or Selenium.
