#!/usr/bin/env python3

import sys
from collections import defaultdict


overall = defaultdict(int)

topic_sentiment = defaultdict(int)


for line in sys.stdin:

    line = line.strip()

    if not line:
        continue

    parts = line.split("\t")

    # -----------------------------------------
    # OVERALL
    # -----------------------------------------

    if parts[0] == "overall":

        sentiment = parts[1]

        count = int(
            parts[2]
        )

        overall[sentiment] += count

    # -----------------------------------------
    # TOPIC
    # -----------------------------------------

    elif parts[0] == "topic":

        topic = parts[1]

        sentiment = parts[2]

        count = int(
            parts[3]
        )

        topic_sentiment[
            (topic, sentiment)
        ] += count


# =========================================================
# OUTPUT OVERALL RESULTS
# =========================================================

print(
    "RESULT\tOVERALL"
)

for sentiment in [
    "positive",
    "neutral",
    "negative"
]:

    print(
        f"{sentiment}\t"
        f"{overall[sentiment]}"
    )


# =========================================================
# OUTPUT TOPIC RESULTS
# =========================================================

print(
    "RESULT\tTOPICS"
)

for (
    topic,
    sentiment
), count in sorted(
    topic_sentiment.items()
):

    print(
        f"{topic}\t"
        f"{sentiment}\t"
        f"{count}"
    )