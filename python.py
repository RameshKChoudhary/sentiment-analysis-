 
from flask import Flask, render_template, request, jsonify
import requests
import feedparser
import re
from urllib.parse import quote
from datetime import datetime

app = Flask(__name__)


# =========================================================
# SENTIMENT WORDS
# =========================================================

POSITIVE_WORDS = {
    "good", "great", "excellent", "amazing", "awesome",
    "love", "loved", "best", "happy", "beautiful",
    "fantastic", "wonderful", "success", "successful",
    "like", "liked", "helpful", "fast", "easy",
    "perfect", "positive", "enjoy", "enjoyed",
    "impressive", "cool", "nice", "fun", "better",
    "brilliant", "useful", "interesting", "excited",
    "exciting", "win", "winning", "favorite",
    "improve", "improved", "growth", "benefit"
}

NEGATIVE_WORDS = {
    "bad", "worst", "hate", "hated", "poor",
    "terrible", "awful", "horrible", "sad",
    "angry", "slow", "difficult", "problem",
    "problems", "fail", "failed", "failure",
    "negative", "disappointed", "disappointing",
    "boring", "issue", "issues", "expensive",
    "worse", "useless", "broken", "annoying",
    "scam", "fake", "wrong", "bug", "bugs",
    "toxic", "frustrating", "frustrated",
    "risk", "danger", "dangerous", "loss",
    "decline", "crisis", "concern"
}


# =========================================================
# SENTIMENT ANALYSIS
# =========================================================

def analyze_sentiment(text):

    text = text.lower()

    words = re.findall(
        r"\b[a-zA-Z]+\b",
        text
    )

    positive = 0
    negative = 0

    for word in words:

        if word in POSITIVE_WORDS:
            positive += 1

        if word in NEGATIVE_WORDS:
            negative += 1

    score = positive - negative

    if score > 0:
        sentiment = "positive"

    elif score < 0:
        sentiment = "negative"

    else:
        sentiment = "neutral"

    return sentiment, score


# =========================================================
# LIVE SEARCH
# =========================================================

def search_live(keyword):

    encoded = quote(keyword)

    # Google News RSS search
    url = (
        "https://news.google.com/rss/search?"
        f"q={encoded}"
        "&hl=en-IN"
        "&gl=IN"
        "&ceid=IN:en"
    )

    headers = {
        "User-Agent":
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "Chrome/131.0 Safari/537.36"
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        feed = feedparser.parse(
            response.content
        )

        results = []

        for entry in feed.entries[:20]:

            title = entry.get(
                "title",
                ""
            )

            description = entry.get(
                "description",
                ""
            )

            # Remove HTML
            description = re.sub(
                r"<[^>]+>",
                " ",
                description
            )

            text = (
                title +
                " " +
                description
            )

            sentiment, score = \
                analyze_sentiment(text)

            published = entry.get(
                "published",
                "Recently"
            )

            source = entry.get(
                "source",
                {}
            )

            source_name = ""

            if hasattr(
                source,
                "get"
            ):

                source_name = source.get(
                    "title",
                    ""
                )

            if not source_name:

                source_name = "News"


            results.append({

                "user": source_name,

                "time": published,

                "text": title,

                "sentiment": sentiment,

                "score": score,

                "link": entry.get(
                    "link",
                    "#"
                )

            })


        return results, None


    except Exception as error:

        print(
            "Search error:",
            error
        )

        return [], str(error)


# =========================================================
# CALCULATE RESULTS
# =========================================================

def calculate_results(posts):

    total = len(posts)

    if total == 0:

        return 0, 0, 0, 0


    positive_count = sum(
        1
        for p in posts
        if p["sentiment"] == "positive"
    )

    neutral_count = sum(
        1
        for p in posts
        if p["sentiment"] == "neutral"
    )

    negative_count = sum(
        1
        for p in posts
        if p["sentiment"] == "negative"
    )


    positive = round(
        positive_count / total * 100
    )

    neutral = round(
        neutral_count / total * 100
    )

    negative = 100 - positive - neutral


    return (
        positive,
        neutral,
        negative,
        total
    )


# =========================================================
# GET ANSWER
# =========================================================

def generate_answer(
    keyword,
    positive,
    neutral,
    negative,
    total
):

    if total == 0:

        return (
            f"No recent results were found "
            f"for '{keyword}'. Try another keyword."
        )


    if positive >= negative and positive >= neutral:

        overall = "Positive"

    elif negative >= positive and negative >= neutral:

        overall = "Negative"

    else:

        overall = "Neutral"


    return (
        f"Based on {total} recent search results "
        f"about '{keyword}', the overall sentiment "
        f"is {overall}. "
        f"Positive: {positive}%, "
        f"Neutral: {neutral}%, "
        f"Negative: {negative}%."
    )


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    keyword = "artificial intelligence"

    posts, error = search_live(
        keyword
    )

    positive, neutral, negative, total = \
        calculate_results(posts)

    answer = generate_answer(
        keyword,
        positive,
        neutral,
        negative,
        total
    )


    return render_template(
        "index.html",

        keyword=keyword,

        posts=posts,

        positive=positive,

        neutral=neutral,

        negative=negative,

        total=total,

        answer=answer,

        error=error
    )


# =========================================================
# SEARCH
# =========================================================

@app.route(
    "/analyze",
    methods=["POST"]
)
def analyze():

    keyword = request.form.get(
        "keyword",
        ""
    ).strip()


    if not keyword:

        keyword = "artificial intelligence"


    print(
        "Searching:",
        keyword
    )


    posts, error = search_live(
        keyword
    )


    positive, neutral, negative, total = \
        calculate_results(posts)


    answer = generate_answer(
        keyword,
        positive,
        neutral,
        negative,
        total
    )


    return render_template(
        "index.html",

        keyword=keyword,

        posts=posts,

        positive=positive,

        neutral=neutral,

        negative=negative,

        total=total,

        answer=answer,

        error=error
    )


# =========================================================
# LIVE JSON API
# =========================================================

@app.route("/api/analyze")
def api_analyze():

    keyword = request.args.get(
        "keyword",
        "artificial intelligence"
    ).strip()


    posts, error = search_live(
        keyword
    )


    positive, neutral, negative, total = \
        calculate_results(posts)


    answer = generate_answer(
        keyword,
        positive,
        neutral,
        negative,
        total
    )


    return jsonify({

        "keyword": keyword,

        "positive": positive,

        "neutral": neutral,

        "negative": negative,

        "total": total,

        "answer": answer,

        "posts": posts,

        "error": error

    })


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    ) 
