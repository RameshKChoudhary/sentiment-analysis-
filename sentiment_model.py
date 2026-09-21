import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# =========================================================
# VADER SENTIMENT ANALYZER
# =========================================================

analyzer = SentimentIntensityAnalyzer()


# =========================================================
# CONTEXT PHRASES
# =========================================================

NEGATIVE_CONTEXT = {
    "terrorism": 3.0,
    "terrorist attack": 4.0,
    "terrorist attacks": 4.0,
    "war": 2.5,
    "armed conflict": 3.0,
    "invasion": 3.0,
    "airstrike": 3.0,
    "missile attack": 3.5,
    "bomb attack": 4.0,
    "violent attack": 3.5,
    "mass shooting": 4.0,
    "shooting": 3.0,
    "murder": 3.5,
    "killed": 3.0,
    "death": 2.5,
    "natural disaster": 3.0,
    "earthquake": 2.5,
    "flood": 2.5,
    "cyclone": 2.5,
    "disaster": 3.0,
    "crime": 2.5,
    "fraud": 2.5,
    "scam": 2.5,
    "corruption": 2.0,
    "kidnapping": 3.5,
    "crisis": 2.0,
    "economic crisis": 3.0,
    "health crisis": 2.5,
    "humanitarian crisis": 3.0,
    "tragedy": 3.0,
    "catastrophe": 3.5,
    "attack": 2.5,
    "threat": 2.0,
    "explosion": 3.0,
    "injured": 2.5,
    "injuries": 2.5,
    "victims": 2.5,
    "casualties": 3.0,
    "loss": 1.5,
    "collapse": 2.5,
    "decline": 1.5,
    "unemployment": 2.0,
    "violence": 3.0,
    "dead": 3.0,
}


POSITIVE_CONTEXT = {
    "indian freedom": 4.0,
    "freedom struggle": 3.5,
    "freedom fighters": 3.5,
    "independence day": 4.0,
    "indian independence": 4.0,
    "independence celebration": 4.0,
    "independence celebrations": 4.0,
    "celebration": 2.5,
    "celebrations": 2.5,
    "celebrates": 2.5,
    "celebrating": 2.5,
    "festival": 2.0,
    "festive": 2.0,
    "success": 2.5,
    "successful": 2.5,
    "achievement": 3.0,
    "achievements": 3.0,
    "historic achievement": 3.5,
    "major achievement": 3.5,
    "breakthrough": 3.0,
    "victory": 3.0,
    "won": 2.5,
    "winning": 2.5,
    "economic growth": 3.0,
    "growth": 1.5,
    "development": 1.5,
    "progress": 2.0,
    "innovation": 2.0,
    "innovative": 2.0,
    "record growth": 3.0,
    "strong growth": 2.5,
    "good news": 3.0,
    "great news": 3.0,
    "positive news": 3.0,
    "happy": 2.0,
    "happiness": 2.0,
    "hope": 1.5,
    "hopeful": 2.0,
    "peace": 2.5,
    "peaceful": 2.5,
    "unity": 2.5,
    "proud": 2.0,
    "pride": 2.0,
    "improvement": 2.0,
    "improved": 2.0,
    "improving": 2.0,
    "benefit": 1.5,
    "benefits": 1.5,
    "better": 1.5,
    "recovery": 2.0,
    "recovering": 2.0,
}


POSITIVE_WORDS = {
    "success",
    "successful",
    "achievement",
    "achieved",
    "victory",
    "growth",
    "progress",
    "improvement",
    "improved",
    "innovation",
    "breakthrough",
    "win",
    "won",
    "winning",
    "celebration",
    "celebrate",
    "happy",
    "hope",
    "peace",
    "unity",
    "proud",
    "benefit",
    "benefits",
    "better",
    "strong",
    "great",
    "excellent",
    "positive",
    "recovery",
}


NEGATIVE_WORDS = {
    "attack",
    "terrorism",
    "terrorist",
    "war",
    "violence",
    "violent",
    "murder",
    "killed",
    "killing",
    "death",
    "dead",
    "crime",
    "criminal",
    "disaster",
    "earthquake",
    "flood",
    "cyclone",
    "explosion",
    "injured",
    "injury",
    "victim",
    "victims",
    "casualties",
    "crisis",
    "threat",
    "danger",
    "collapse",
    "decline",
    "loss",
    "fraud",
    "scam",
    "corruption",
    "violence",
    "unemployment",
}


# =========================================================
# TEXT NORMALIZATION
# =========================================================

def normalize_text(text):
    if not text:
        return ""

    text = str(text).lower()

    text = re.sub(
        r"https?://\S+|www\.\S+",
        " ",
        text
    )

    text = re.sub(
        r"[^a-z0-9\s'-]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# CONTEXT SCORE
# =========================================================

def calculate_context_score(text, topic=""):

    combined_text = normalize_text(
        f"{topic} {text}"
    )

    topic_text = normalize_text(topic)

    positive_score = 0.0
    negative_score = 0.0

    # -----------------------------------------------------
    # Strong topic-level context
    # -----------------------------------------------------

    for phrase, weight in NEGATIVE_CONTEXT.items():

        if phrase in topic_text:
            negative_score += weight

        elif phrase in combined_text:
            negative_score += weight * 0.65

    for phrase, weight in POSITIVE_CONTEXT.items():

        if phrase in topic_text:
            positive_score += weight

        elif phrase in combined_text:
            positive_score += weight * 0.65

    # -----------------------------------------------------
    # General word context
    # -----------------------------------------------------

    words = set(
        combined_text.split()
    )

    positive_score += (
        len(words.intersection(POSITIVE_WORDS))
        * 0.35
    )

    negative_score += (
        len(words.intersection(NEGATIVE_WORDS))
        * 0.45
    )

    return positive_score, negative_score


# =========================================================
# SENTIMENT ANALYSIS
# =========================================================

def analyze_sentiment(
    text,
    topic=""
):

    if not text:

        return {
            "sentiment": "neutral",
            "score": 0.0,
            "positive": 0.0,
            "neutral": 1.0,
            "negative": 0.0,
        }

    text = str(text)[:5000]

    try:

        # -------------------------------------------------
        # VADER
        # -------------------------------------------------

        vader = analyzer.polarity_scores(text)

        vader_positive = vader["pos"]
        vader_negative = vader["neg"]
        vader_neutral = vader["neu"]

        # -------------------------------------------------
        # Context
        # -------------------------------------------------

        positive_context, negative_context = \
            calculate_context_score(
                text,
                topic
            )

        context_total = (
            positive_context
            + negative_context
        )

        if context_total > 0:

            context_positive = (
                positive_context
                / context_total
            )

            context_negative = (
                negative_context
                / context_total
            )

            context_neutral = 0.0

        else:

            context_positive = 0.0
            context_negative = 0.0
            context_neutral = 1.0

        # -------------------------------------------------
        # Blend VADER + Context
        # -------------------------------------------------

        if context_total > 0:

            positive = (
                vader_positive * 0.70
                + context_positive * 0.30
            )

            negative = (
                vader_negative * 0.70
                + context_negative * 0.30
            )

            neutral = (
                vader_neutral * 0.70
                + context_neutral * 0.30
            )

        else:

            positive = vader_positive
            negative = vader_negative
            neutral = vader_neutral

        # -------------------------------------------------
        # Strong topic adjustment
        # -------------------------------------------------

        if negative_context >= 2.0 and \
           negative_context > positive_context:

            negative += 0.20
            neutral *= 0.55

        elif positive_context >= 2.0 and \
             positive_context > negative_context:

            positive += 0.20
            neutral *= 0.55

        # -------------------------------------------------
        # Normalize
        # -------------------------------------------------

        total = (
            positive
            + neutral
            + negative
        )

        if total <= 0:

            positive = 0.0
            neutral = 1.0
            negative = 0.0

        else:

            positive /= total
            neutral /= total
            negative /= total

        # -------------------------------------------------
        # Final sentiment
        # -------------------------------------------------

        probabilities = {
            "positive": positive,
            "neutral": neutral,
            "negative": negative,
        }

        sentiment = max(
            probabilities,
            key=probabilities.get
        )

        score = probabilities[
            sentiment
        ]

        return {

            "sentiment": sentiment,

            "score": round(
                score,
                4
            ),

            "positive": round(
                positive,
                4
            ),

            "neutral": round(
                neutral,
                4
            ),

            "negative": round(
                negative,
                4
            ),

        }

    except Exception as error:

        print(
            "Sentiment error:",
            error
        )

        return {

            "sentiment": "neutral",

            "score": 0.0,

            "positive": 0.0,

            "neutral": 1.0,

            "negative": 0.0,

        }