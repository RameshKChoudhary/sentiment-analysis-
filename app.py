from flask import Flask, render_template, request, jsonify

import requests
import feedparser
import re

from urllib.parse import quote

from sentiment_model import analyze_sentiment


# =========================================================
# FLASK CONFIGURATION
# =========================================================

app = Flask(
    __name__,
    template_folder=".",
    static_folder=".",
    static_url_path=""
)


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


        for entry in feed.entries[:20]:

            title = entry.get(
                "title",
                ""
            )

            description = entry.get(
                "description",
                ""
            )


            # Remove HTML from description

            description = re.sub(
                r"<[^>]+>",
                " ",
                description
            )


            # Combine title + description

            text = (
                title +
                " " +
                description
            )


            # =================================================
            # AI SENTIMENT ANALYSIS
            # =================================================

            sentiment_result = analyze_sentiment(
                text
            )

            sentiment = sentiment_result[
                "sentiment"
            ]

            confidence = sentiment_result[
                "score"
            ]


            # Convert confidence into
            # a dashboard-friendly score

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

                "sentiment": sentiment,

                "score": score,

                "confidence": confidence,

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

        for post in posts

        if post["sentiment"] == "positive"

    )


    neutral_count = sum(

        1

        for post in posts

        if post["sentiment"] == "neutral"

    )


    negative_count = sum(

        1

        for post in posts

        if post["sentiment"] == "negative"

    )


    positive = round(
        positive_count / total * 100
    )

    neutral = round(
        neutral_count / total * 100
    )

    negative = (
        100 -
        positive -
        neutral
    )


    return (
        positive,
        neutral,
        negative,
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


    if positive >= negative and positive >= neutral:

        overall = "Positive"

    elif negative >= positive and negative >= neutral:

        overall = "Negative"

    else:

        overall = "Neutral"


    return (

        f"AI sentiment analysis of {total} "
        f"recent news results about '{keyword}' "
        f"shows an overall {overall.lower()} trend. "

        f"The distribution is "

        f"{positive}% positive, "
        f"{neutral}% neutral, and "
        f"{negative}% negative."

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


    if not keyword:

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