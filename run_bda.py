import subprocess
import json
import os


OUTPUT_FILE = "bda_results.json"


def parse_hadoop_output():

    command = [
        "hdfs",
        "dfs",
        "-cat",
        "/sentiment/output/part-*"
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        print(
            "Unable to read Hadoop output."
        )

        print(
            result.stderr
        )

        return

    lines = result.stdout.splitlines()

    overall = {
        "positive": 0,
        "neutral": 0,
        "negative": 0
    }

    topics = {}

    mode = None

    for line in lines:

        if line == "RESULT\tOVERALL":

            mode = "overall"

            continue

        if line == "RESULT\tTOPICS":

            mode = "topics"

            continue

        parts = line.split("\t")

        if mode == "overall":

            if len(parts) != 2:
                continue

            sentiment = parts[0]

            count = int(
                parts[1]
            )

            if sentiment in overall:

                overall[sentiment] = count

        elif mode == "topics":

            if len(parts) != 3:
                continue

            topic = parts[0]

            sentiment = parts[1]

            count = int(
                parts[2]
            )

            if topic not in topics:

                topics[topic] = {
                    "positive": 0,
                    "neutral": 0,
                    "negative": 0
                }

            topics[
                topic
            ][sentiment] = count

    total = sum(
        overall.values()
    )

    if total > 0:

        positive = round(
            overall["positive"]
            / total * 100,
            2
        )

        neutral = round(
            overall["neutral"]
            / total * 100,
            2
        )

        negative = round(
            overall["negative"]
            / total * 100,
            2
        )

    else:

        positive = 0
        neutral = 0
        negative = 0

    result = {

        "total": total,

        "positive": positive,

        "neutral": neutral,

        "negative": negative,

        "counts": overall,

        "topics": topics,

        "processing": "Hadoop MapReduce",

        "storage": "HDFS"

    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=4
        )

    print(
        f"BDA results saved to {OUTPUT_FILE}"
    )


if __name__ == "__main__":

    parse_hadoop_output()