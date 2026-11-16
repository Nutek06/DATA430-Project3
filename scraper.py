"""
Scrape every quote from quotes.toscrape.com and export the records
to CSV, plain text, JSON, and YAML.
"""

import csv
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin

import requests
import yaml
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"
OUTPUT_DIR = Path("output")
REQUEST_TIMEOUT = 15
MAX_ATTEMPTS = 3
REQUEST_DELAY_SECONDS = 1.5
USER_AGENT = (
    "DATA430-StudentWebScraper/1.0 "
    "(educational project; polite automated requests)"
)


def fetch_page(session: requests.Session, url: str) -> Optional[str]:
    """Fetch a webpage with retries; return HTML or None after failure."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.text
        except requests.RequestException as error:
            print(
                f"Request attempt {attempt}/{MAX_ATTEMPTS} failed "
                f"for {url}: {error}"
            )
            if attempt < MAX_ATTEMPTS:
                time.sleep(REQUEST_DELAY_SECONDS)

    print(f"Unable to fetch {url} after {MAX_ATTEMPTS} attempts. Stopping cleanly.")
    return None


def clean_quote(text: str) -> str:
    """Trim whitespace and remove quotation marks surrounding the full quote."""
    cleaned = text.strip()
    surrounding_quotes = ('"', "'", "“", "”", "‘", "’")
    while cleaned and cleaned[0] in ('“', '"', "‘"):
        cleaned = cleaned[1:].lstrip()
    while cleaned and cleaned[-1] in ('”', '"', "’"):
        cleaned = cleaned[:-1].rstrip()
    return cleaned.strip()


def parse_quotes(html: str, page_number: int, scraped_at: str) -> List[Dict]:
    """Extract quote text, author, tags, page number, and timestamp."""
    soup = BeautifulSoup(html, "html.parser")
    records = []

    for quote_block in soup.select("div.quote"):
        quote_element = quote_block.select_one("span.text")
        author_element = quote_block.select_one("small.author")

        if quote_element is None or author_element is None:
            print(f"Skipping an incomplete quote on page {page_number}.")
            continue

        tag_elements = quote_block.select("div.tags a.tag")
        tags = [tag.get_text(strip=True) for tag in tag_elements]

        records.append(
            {
                "quote": clean_quote(quote_element.get_text(" ", strip=True)),
                "author": author_element.get_text(" ", strip=True),
                "tags": tags,
                "page": page_number,
                "scraped_at": scraped_at,
            }
        )

    return records


def scrape_all_quotes() -> tuple:
    """Scrape pages until the website no longer provides a next-page link."""
    scraped_at = datetime.now().astimezone().replace(microsecond=0).isoformat()
    all_records = []
    pages_fetched = 0
    next_url = BASE_URL

    with requests.Session() as session:
        session.headers.update({"User-Agent": USER_AGENT})

        while next_url:
            if pages_fetched > 0:
                time.sleep(REQUEST_DELAY_SECONDS)

            html = fetch_page(session, next_url)
            if html is None:
                break

            pages_fetched += 1
            page_records = parse_quotes(html, pages_fetched, scraped_at)
            all_records.extend(page_records)
            print(
                f"Page {pages_fetched}: extracted "
                f"{len(page_records)} quote(s)."
            )

            soup = BeautifulSoup(html, "html.parser")
            next_link = soup.select_one("li.next a")
            next_url = (
                urljoin(next_url, next_link.get("href"))
                if next_link and next_link.get("href")
                else None
            )

    return all_records, pages_fetched


def write_csv(records: List[Dict], path: Path) -> None:
    """Write records to CSV using the required header and semicolon tags."""
    fieldnames = ["quote", "author", "tags", "page", "scraped_at"]
    with path.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            row = record.copy()
            row["tags"] = ";".join(record["tags"])
            writer.writerow(row)


def write_text(records: List[Dict], path: Path) -> None:
    """Write one labelled, blank-line-separated text block per quote."""
    blocks = []
    for record in records:
        blocks.append(
            "\n".join(
                [
                    f"Quote: {record['quote']}",
                    f"Author: {record['author']}",
                    f"Tags: {', '.join(record['tags'])}",
                    f"Page: {record['page']}",
                    f"Scraped: {record['scraped_at']}",
                ]
            )
        )
    path.write_text("\n\n".join(blocks), encoding="utf-8")


def write_json(records: List[Dict], path: Path) -> None:
    """Write the canonical JSON array with two-space indentation."""
    path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_yaml(records: List[Dict], path: Path) -> None:
    """Write records as YAML using safe_dump."""
    path.write_text(
        yaml.safe_dump(
            records,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        ),
        encoding="utf-8",
    )


def write_output_files(records: List[Dict]) -> List[Path]:
    """Create the output directory and overwrite all four output files."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    files = [
        OUTPUT_DIR / "quotes.csv",
        OUTPUT_DIR / "quotes.txt",
        OUTPUT_DIR / "quotes.json",
        OUTPUT_DIR / "quotes.yaml",
    ]

    write_csv(records, files[0])
    write_text(records, files[1])
    write_json(records, files[2])
    write_yaml(records, files[3])

    return files


def main() -> int:
    """Run the scraper and print a completion summary."""
    print("Starting Quotes to Scrape...")
    records, pages_fetched = scrape_all_quotes()

    if not records:
        print("No quotes were extracted. Check your internet connection and try again.")
        return 1

    written_files = write_output_files(records)

    print("\nScraping summary")
    print("----------------")
    print(f"Pages fetched: {pages_fetched}")
    print(f"Quotes extracted: {len(records)}")
    print("Files written:")
    for file_path in written_files:
        print(f"  - {file_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
