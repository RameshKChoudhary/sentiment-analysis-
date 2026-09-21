 
from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
import feedparser
import re

from urllib.parse import quote
from html import unescape

from sentiment_model import analyze_sentiment


# =========================================================
# FLASK CONFIGURATION
# =========================================================

app = Flask(
    __name__,
    template_folder="."
)


# =========================================================
# TEXT CLEANING
# =========================================================

def clean_text(text):
    """
    Clean HTML/RSS text before sending it to the
    sentiment model.
    """

    if not text:
        return ""

    text = unescape(str(text))

    # Remove HTML tags
    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    # Remove URLs
    text = re.sub(
        r"https?://\S+|www\.\S+",
        " ",
        text
    )

    # Remove excessive whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# LIVE NEWS SEARCH
# =========================================================

def search_live(keyword):

    encoded = quote(keyword)

    url = (
        "https://news.google.com/rss/search?"
        f"q={encoded}"
        "&hl=en-IN"
        "&gl=IN"
        "&ceid=IN:en"
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/131.0 Safari/537.36"
        )
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

        # Prevent duplicate news
        seen_links = set()
        seen_titles = set()

        for entry in feed.entries[:30]:

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

            if not title:
                continue

            # Remove duplicate articles
            normalized_title = re.sub(
                r"[^a-z0-9]+",
                " ",
                title.lower()
            ).strip()

            link = entry.get(
                "link",
                "#"
            )

            if (
                normalized_title in seen_titles
                or link in seen_links
            ):
                continue

            seen_titles.add(
                normalized_title
            )

            seen_links.add(
                link
            )

            # Combine title and description
            text = (
                f"{title}. "
                f"{description}"
            ).strip()

            # =================================================
            # AI + CONTEXTUAL SENTIMENT ANALYSIS
            # =================================================

            sentiment_result = analyze_sentiment(
                text,
                topic=keyword
            )

            sentiment = sentiment_result[
                "sentiment"
            ]

            confidence = sentiment_result[
                "score"
            ]

            # Signed sentiment score
            # Positive = positive
            # Negative = negative
            # Neutral = 0
            if sentiment == "positive":

                score = round(
                    confidence * 100,
                    2
                )

            elif sentiment == "negative":

                score = round(
                    -confidence * 100,
                    2
                )

            else:

                score = 0

            published = entry.get(
                "published",
                "Recently"
            )

            source = entry.get(
                "source",
                {}
            )

            source_name = ""

            if hasattr(source, "get"):

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

                "description": description,

                "sentiment": sentiment,

                "score": score,

                "confidence": confidence,

                "link": link

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
        for post in posts
        if post.get("sentiment") == "positive"
    )

    neutral_count = sum(
        1
        for post in posts
        if post.get("sentiment") == "neutral"
    )

    negative_count = sum(
        1
        for post in posts
        if post.get("sentiment") == "negative"
    )

    positive = round(
        positive_count / total * 100
    )

    neutral = round(
        neutral_count / total * 100
    )

    negative = round(
        negative_count / total * 100
    )

    # Ensure total is exactly 100
    values = [
        positive,
        neutral,
        negative
    ]

    difference = 100 - sum(values)

    if difference != 0:

        largest_index = values.index(
            max(values)
        )

        values[largest_index] += difference

    return (
        values[0],
        values[1],
        values[2],
        total
    )


# =========================================================
# GENERATE AI ANALYSIS
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
            f"No recent news results were "
            f"found for '{keyword}'."
        )

    if (
        positive > negative
        and positive > neutral
    ):

        overall = "positive"

    elif (
        negative > positive
        and negative > neutral
    ):

        overall = "negative"

    else:

        overall = "neutral"

    return (

        f"AI sentiment analysis of {total} "
        f"recent news results about '{keyword}' "
        f"shows an overall {overall} trend. "

        f"The distribution is "
        f"{positive}% positive, "
        f"{neutral}% neutral, and "
        f"{negative}% negative."

    )


# =========================================================
# RENDER DASHBOARD
# =========================================================

def dashboard_response(
    keyword,
    posts,
    error
):

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

@app.route("/index.css")
def serve_css():
    return send_from_directory(".", "index.css")

# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    keyword = "artificial intelligence"

    posts, error = search_live(
        keyword
    )

    return dashboard_response(
        keyword,
        posts,
        error
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

    return dashboard_response(
        keyword,
        posts,
        error
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

    if not keyword:

        keyword = "artificial intelligence"

    print(
        "Live search:",
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
# LOCAL DEVELOPMENT
# =========================================================

if __name__ == "__main__":

    app.run(

        debug=True,

        host="0.0.0.0",

        port=5000

    ) 
