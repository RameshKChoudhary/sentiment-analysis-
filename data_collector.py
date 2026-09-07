import requests
import feedparser
import csv
import re
import os
from urllib.parse import quote


TOPICS = [
    "Artificial Intelligence",
    "ChatGPT",
    "Machine Learning",
    "Generative AI",
    "Tesla",
    "iPhone",
    "Google",
    "Microsoft",
    "Cybersecurity",
    "Social Media",
    "Cloud Computing",
    "Robotics",
    "Data Science",
    "Technology",
    "Electric Vehicles"
]


def clean_text(text):

    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def collect_topic(topic):

    encoded = quote(topic)

    url = (
        "https://news.google.com/rss/search?"
        f"q={encoded}"
        "&hl=en-IN"
        "&gl=IN"
        "&ceid=IN:en"
    )

    headers = {
        "User-Agent":
            "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    feed = feedparser.parse(
        response.content
    )

    records = []

    for entry in feed.entries:

        title = clean_text(
            entry.get(
                "title",
                ""
            )
        )

        description = clean_text(
            entry.get(
                "description",
                ""
            )
        )

        text = (
            title +
            " " +
            description
        ).strip()

        if not text:
            continue

        source = entry.get(
            "source",
            {}
        )

        source_name = ""

        if hasattr(source, "get"):

            source_name = source.get(
                "title",
                "News"
            )

        records.append({

            "topic": topic,

            "text": text,

            "source": source_name,

            "published": entry.get(
                "published",
                ""
            ),

            "link": entry.get(
                "link",
                ""
            )

        })

    return records


def main():

    os.makedirs(
        "data",
        exist_ok=True
    )

    all_records = []

    for topic in TOPICS:

        print(
            f"Collecting: {topic}"
        )

        try:

            records = collect_topic(
                topic
            )

            all_records.extend(
                records
            )

            print(
                f"Collected {len(records)} records"
            )

        except Exception as error:

            print(
                f"Error collecting {topic}: {error}"
            )

    output_file = (
        "data/sentiment_data.csv"
    )

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "topic",
                "text",
                "source",
                "published",
                "link"
            ]
        )

        writer.writeheader()

        writer.writerows(
            all_records
        )

    print()
    print(
        "================================"
    )
    print(
        f"Total records: {len(all_records)}"
    )
    print(
        f"Dataset: {output_file}"
    )
    print(
        "================================"
    )


if __name__ == "__main__":
    main()