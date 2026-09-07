#!/usr/bin/env python3

import sys
import csv
import re


POSITIVE_WORDS = {
    "good", "great", "excellent", "amazing",
    "awesome", "love", "best", "happy",
    "beautiful", "fantastic", "wonderful",
    "success", "successful", "helpful",
    "fast", "easy", "perfect", "positive",
    "impressive", "cool", "nice", "fun",
    "better", "brilliant", "useful",
    "interesting", "excited", "exciting",
    "win", "winning", "favorite",
    "improve", "improved", "growth",
    "benefit", "innovative", "innovation",
    "progress", "secure", "strong",
    "effective", "efficient", "powerful"
}


NEGATIVE_WORDS = {
    "bad", "worst", "hate", "poor",
    "terrible", "awful", "horrible",
    "sad", "angry", "slow",
    "difficult", "problem", "problems",
    "fail", "failed", "failure",
    "negative", "disappointed",
    "disappointing", "boring",
    "issue", "issues", "expensive",
    "worse", "useless", "broken",
    "annoying", "scam", "fake",
    "wrong", "bug", "bugs",
    "toxic", "frustrating",
    "frustrated", "risk", "danger",
    "dangerous", "loss", "decline",
    "crisis", "concern", "attack",
    "threat", "error", "errors",
    "weak", "controversy"
}


def analyze_sentiment(text):

    words = re.findall(
        r"\b[a-zA-Z]+\b",
        text.lower()
    )

    positive = sum(
        1
        for word in words
        if word in POSITIVE_WORDS
    )

    negative = sum(
        1
        for word in words
        if word in NEGATIVE_WORDS
    )

    if positive > negative:
        return "positive"

    if negative > positive:
        return "negative"

    return "neutral"


reader = csv.DictReader(
    sys.stdin
)

for row in reader:

    text = row.get(
        "text",
        ""
    )

    topic = row.get(
        "topic",
        "unknown"
    )

    if not text:
        continue

    sentiment = analyze_sentiment(
        text
    )

    # Overall sentiment count
    print(
        f"overall\t{sentiment}\t1"
    )

    # Topic-level sentiment count
    print(
        f"topic\t{topic}\t{sentiment}\t1"
    )