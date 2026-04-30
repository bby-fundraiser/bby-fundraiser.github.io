#!/usr/bin/env python3
"""
Generate _posts markdown files from a CSV.

CSV must have columns: title, description, img, starting_bid, website
Optional columns: value (estimated value of the item)

Items are sorted alphabetically by title; A items get the most recent dates
so the website (which sorts by date descending) displays them first.

Usage:
    python make_posts.py <csv_path> [--output-dir <dir>] [--start-date <YYYY-MM-DD>]
"""

import csv
import re
import argparse
from datetime import datetime, timedelta
from pathlib import Path

TEMPLATE = """\
---
layout: post
title: {title}
date: {date} 12:00:00 +0000
description: {short_desc}
img: {img}
fig-caption:
tags: [auction]
starting_bid: {starting_bid}
value: {value}
---

{description}
"""
STARINGBID_LINE = "\n\n<b>Starting bid: {starting_bid}</b>"
VALUE_LINE = "\n\n<b>Estimated value: {value}</b>"
WEBSITE_LINE = "\n\n- [Visit their website for more info]({url})"


def slugify(title: str) -> str:
    slug = title.lower()
    slug = re.sub(r"[&'\"()]", "", slug)
    slug = re.sub(r"[\s/]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


def main():
    parser = argparse.ArgumentParser(description="Generate auction post markdown files from CSV.")
    parser.add_argument("csv_path", help="Path to the input CSV file")
    parser.add_argument(
        "--output-dir",
        default="_posts",
        help="Directory to write markdown files (default: _posts)",
    )
    parser.add_argument(
        "--start-date",
        default=datetime.utcnow().strftime("%Y-%m-%d"),
        help="Most recent date to assign (YYYY-MM-DD); defaults to today",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(args.csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Sort alphabetically by title so A → most recent date, Z → oldest
    rows.sort(key=lambda r: r["title"].strip().lower())

    start = datetime.strptime(args.start_date, "%Y-%m-%d")

    for i, row in enumerate(rows):
        include = row["include"].strip()
        if include != 'y':
            continue
        title = row["title"].strip()
        description = row["description"].strip()
        short_desc = description.split('\n\n')[0].strip()
        img = row["img"].strip()
        starting_bid = row["starting_bid"].strip()
        website = row["website"].strip()
        value = row.get("Value", "").strip() or row.get("value", "").strip()
        other_images = [n.strip() for n in row.get("other_images", "").split(";") if n.strip()]

        date = start - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")

        content = TEMPLATE.format(
            title=title,
            date=date_str,
            description=description,
            short_desc=short_desc,
            img=img,
            starting_bid=starting_bid,
            value=value,
        )

        if starting_bid:
            content += STARINGBID_LINE.format(starting_bid=starting_bid)

        if value:
            content += VALUE_LINE.format(value=value)

        for img_name in other_images:
            content += f"\n![{img_name}](/assets/img/{img_name})"

        if website:
            content += WEBSITE_LINE.format(url=website)

        filename = output_dir / f"{date_str}-{slugify(title)}.markdown"
        filename.write_text(content, encoding="utf-8")
        print(f"Wrote {filename}")

    print(f"\nDone. {len(rows)} files written to {output_dir}/")


if __name__ == "__main__":
    main()
