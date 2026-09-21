 
from transformers import pipeline
import re


# =========================================================
# AI SENTIMENT MODEL
# =========================================================

MODEL_NAME = (
    "cardiffnlp/twitter-roberta-base-sentiment-latest"
)


classifier = pipeline(
    "sentiment-analysis",
    model=MODEL_NAME,
    tokenizer=MODEL_NAME
)


# =========================================================
# STRONG NEGATIVE TOPICS
# =========================================================

NEGATIVE_TOPIC_PHRASES = {

    # Terrorism / violence
    "terrorism": 3.5,
    "terrorist attack": 4.0,
    "terrorist attacks": 4.0,
    "terrorist": 2.5,
    "terror attack": 4.0,
    "terror attacks": 4.0,

    # War / conflict
    "war": 3.0,
    "armed conflict": 3.0,
    "military conflict": 2.8,
    "invasion": 3.5,
    "airstrike": 3.5,
    "air strikes": 3.5,
    "missile attack": 3.5,
    "bomb attack": 4.0,

    # Violence
    "violent attack": 3.5,
    "violence": 2.8,
    "mass shooting": 4.0,
    "shooting": 3.0,
    "murder": 3.5,
    "murdered": 3.5,
    "killed": 2.8,
    "killing": 3.0,
    "death": 2.2,
    "deaths": 2.8,

    # Disaster
    "natural disaster": 3.0,
    "earthquake": 2.8,
    "flood": 2.5,
    "flooding": 2.5,
    "cyclone": 2.5,
    "storm": 2.0,
    "disaster": 3.0,

    # Crime
    "crime": 2.5,
    "criminal": 2.2,
    "fraud": 3.0,
    "scam": 3.0,
    "corruption": 2.8,
    "kidnapping": 3.5,

    # Serious negative situations
    "crisis": 2.5,
    "economic crisis": 3.0,
    "health crisis": 2.8,
    "humanitarian crisis": 3.5,
    "tragedy": 3.5,
    "tragedy strikes": 3.5,
    "catastrophe": 3.5,

    # Negative events
    "attack": 2.2,
    "threat": 2.0,
    "explosion": 3.0,
    "injured": 2.2,
    "injuries": 2.2,
    "victims": 2.0,
    "casualties": 3.0,
    "loss": 1.8,
    "collapse": 2.5,
    "decline": 1.8,
    "unemployment": 2.2

}


# =========================================================
# STRONG POSITIVE TOPICS
# =========================================================

POSITIVE_TOPIC_PHRASES = {

    # Freedom / independence
    "indian freedom": 4.0,
    "freedom struggle": 4.0,
    "freedom fighters": 4.0,
    "freedom fighter": 4.0,
    "independence day": 4.0,
    "indian independence": 4.0,
    "independence celebration": 4.0,
    "independence celebrations": 4.0,

    # Celebration
    "celebration": 2.5,
    "celebrations": 2.5,
    "celebrates": 2.5,
    "celebrating": 2.5,
    "celebrated": 2.5,
    "festival": 2.0,
    "festive": 2.0,

    # Success
    "success": 2.5,
    "successful": 2.5,
    "achievement": 3.0,
    "achievements": 3.0,
    "historic achievement": 3.5,
    "major achievement": 3.2,
    "breakthrough": 3.0,
    "victory": 3.0,
    "won": 2.5,
    "winning": 2.5,

    # Growth / development
    "economic growth": 3.0,
    "growth": 2.0,
    "development": 2.0,
    "progress": 2.5,
    "innovation": 2.5,
    "innovative": 2.5,
    "record growth": 3.0,
    "strong growth": 3.0,

    # Positive events
    "good news": 3.0,
    "great news": 3.0,
    "positive news": 3.0,
    "happy": 2.0,
    "happiness": 2.0,
    "hope": 1.8,
    "hopeful": 2.0,
    "peace": 2.5,
    "peaceful": 2.5,
    "unity": 2.5,
    "proud": 2.5,
    "pride": 2.5,

    # Improvement
    "improvement": 2.0,
    "improved": 2.0,
    "improving": 2.0,
    "benefit": 1.8,
    "benefits": 1.8,
    "better": 1.8,
    "recovery": 2.2,
    "recovering": 2.2

}


# =========================================================
# GENERAL POSITIVE / NEGATIVE WORDS
# =========================================================

POSITIVE_WORDS = {
    "good",
    "great",
    "excellent",
    "amazing",
    "awesome",
    "love",
    "best",
    "happy",
    "beautiful",
    "fantastic",
    "wonderful",
    "success",
    "successful",
    "helpful",
    "perfect",
    "positive",
    "impressive",
    "nice",
    "brilliant",
    "useful",
    "excited",
    "exciting",
    "win",
    "winning",
    "favorite",
    "improve",
    "improved",
    "growth",
    "benefit",
    "innovative",
    "innovation",
    "progress",
    "secure",
    "strong",
    "effective",
    "efficient",
    "powerful",
    "peace",
    "hope",
    "proud",
    "celebrate",
    "celebration",
    "achievement",
    "victory",
    "success"
}


NEGATIVE_WORDS = {
    "bad",
    "worst",
    "hate",
    "poor",
    "terrible",
    "awful",
    "horrible",
    "sad",
    "angry",
    "slow",
    "difficult",
    "problem",
    "problems",
    "fail",
    "failed",
    "failure",
    "negative",
    "disappointed",
    "disappointing",
    "boring",
    "issue",
    "issues",
    "expensive",
    "worse",
    "useless",
    "broken",
    "annoying",
    "scam",
    "fake",
    "wrong",
    "bug",
    "bugs",
    "toxic",
    "frustrating",
    "frustrated",
    "risk",
    "danger",
    "dangerous",
    "loss",
    "decline",
    "crisis",
    "concern",
    "attack",
    "threat",
    "error",
    "errors",
    "weak",
    "controversy",
    "war",
    "violence",
    "terrorism",
    "terrorist",
    "murder",
    "killed",
    "killing",
    "death",
    "deaths",
    "disaster",
    "crime",
    "fraud",
    "corruption",
    "victim",
    "victims",
    "injured",
    "injuries",
    "casualties",
    "explosion"
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
        r"[^a-zA-Z0-9\s'-]",
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
# FIND PHRASE SCORE
# =========================================================

def calculate_context_score(
    text,
    topic=""
):

    text = normalize_text(text)

    topic = normalize_text(topic)

    positive_score = 0.0
    negative_score = 0.0

    # -----------------------------------------------------
    # Topic-level positive signals
    # -----------------------------------------------------

    for phrase, weight in POSITIVE_TOPIC_PHRASES.items():

        if phrase in topic:

            positive_score += weight

        elif phrase in text:

            positive_score += (
                weight * 0.65
            )

    # -----------------------------------------------------
    # Topic-level negative signals
    # -----------------------------------------------------

    for phrase, weight in NEGATIVE_TOPIC_PHRASES.items():

        if phrase in topic:

            negative_score += weight

        elif phrase in text:

            negative_score += (
                weight * 0.65
            )

    # -----------------------------------------------------
    # General words
    # -----------------------------------------------------

    words = re.findall(
        r"\b[a-zA-Z]+\b",
        text
    )

    for word in words:

        if word in POSITIVE_WORDS:

            positive_score += 0.35

        if word in NEGATIVE_WORDS:

            negative_score += 0.45

    return (
        positive_score,
        negative_score
    )


# =========================================================
# NORMALIZE MODEL LABEL
# =========================================================

def normalize_model_label(label):

    label = str(label).lower().strip()

    if label in {
        "negative",
        "neg",
        "label_0"
    }:

        return "negative"

    if label in {
        "neutral",
        "neu",
        "label_1"
    }:

        return "neutral"

    if label in {
        "positive",
        "pos",
        "label_2"
    }:

        return "positive"

    return "neutral"


# =========================================================
# SENTIMENT ANALYSIS
# =========================================================

def analyze_sentiment(
    text,
    topic=""
):

    if not text or not text.strip():

        return {
            "sentiment": "neutral",
            "score": 0.0
        }

    try:

        # -------------------------------------------------
        # Limit text length
        # -------------------------------------------------

        text = text[:3000]

        # -------------------------------------------------
        # Get ALL model probabilities
        # -------------------------------------------------

        model_results = classifier(
            text,
            truncation=True,
            top_k=None
        )

        # Some transformers versions return:
        # [[...]]
        # while others return:
        # [...]
        if (
            isinstance(model_results, list)
            and len(model_results) > 0
            and isinstance(model_results[0], list)
        ):

            model_results = model_results[0]

        probabilities = {

            "positive": 0.0,

            "neutral": 0.0,

            "negative": 0.0

        }

        for result in model_results:

            label = normalize_model_label(
                result.get("label", "")
            )

            score = float(
                result.get("score", 0.0)
            )

            if label in probabilities:

                probabilities[label] = score

        # -------------------------------------------------
        # Contextual score
        # -------------------------------------------------

        positive_context, negative_context = \
            calculate_context_score(
                text,
                topic
            )

        # -------------------------------------------------
        # Convert contextual evidence into
        # a bounded adjustment.
        # -------------------------------------------------

        context_total = (
            positive_context +
            negative_context
        )

        if context_total > 0:

            positive_context_ratio = (
                positive_context /
                context_total
            )

            negative_context_ratio = (
                negative_context /
                context_total
            )

        else:

            positive_context_ratio = 0.0
            negative_context_ratio = 0.0

        # -------------------------------------------------
        # Start with model probabilities.
        #
        # The model remains the main signal.
        # Context is used to correct topic-level
        # situations where the model often predicts
        # neutral for factual news.
        # -------------------------------------------------

        positive_probability = (
            probabilities["positive"] * 0.70
            +
            positive_context_ratio * 0.30
        )

        negative_probability = (
            probabilities["negative"] * 0.70
            +
            negative_context_ratio * 0.30
        )

        neutral_probability = (
            probabilities["neutral"] * 0.70
        )

        # -------------------------------------------------
        # Strong contextual topics
        #
        # This prevents topics such as terrorism,
        # war, attacks, freedom celebrations, etc.
        # from becoming overwhelmingly neutral.
        # -------------------------------------------------

        strong_negative = (
            negative_context >= 2.0
            and negative_context > positive_context
        )

        strong_positive = (
            positive_context >= 2.0
            and positive_context > negative_context
        )

        if strong_negative:

            negative_probability += 0.20

            neutral_probability *= 0.55

        elif strong_positive:

            positive_probability += 0.20

            neutral_probability *= 0.55

        # -------------------------------------------------
        # Normalize
        # -------------------------------------------------

        total_probability = (
            positive_probability +
            neutral_probability +
            negative_probability
        )

        if total_probability <= 0:

            return {
                "sentiment": "neutral",
                "score": 0.0
            }

        positive_probability /= total_probability
        neutral_probability /= total_probability
        negative_probability /= total_probability

        # -------------------------------------------------
        # Determine final sentiment
        # -------------------------------------------------

        probabilities_final = {

            "positive":
                positive_probability,

            "neutral":
                neutral_probability,

            "negative":
                negative_probability

        }

        sentiment = max(
            probabilities_final,
            key=probabilities_final.get
        )

        confidence = probabilities_final[
            sentiment
        ]

        # -------------------------------------------------
        # Extra protection against weak neutral
        # classifications when strong context exists.
        # -------------------------------------------------

        if strong_negative:

            if negative_probability >= 0.42:

                sentiment = "negative"

                confidence = negative_probability

        elif strong_positive:

            if positive_probability >= 0.42:

                sentiment = "positive"

                confidence = positive_probability

        return {

            "sentiment": sentiment,

            "score": round(
                float(confidence),
                4
            ),

            "positive_probability": round(
                positive_probability,
                4
            ),

            "neutral_probability": round(
                neutral_probability,
                4
            ),

            "negative_probability": round(
                negative_probability,
                4
            )

        }

    except Exception as error:

        print(
            "Sentiment model error:",
            error
        )

        return {

            "sentiment": "neutral",

            "score": 0.0,

            "positive_probability": 0.0,

            "neutral_probability": 1.0,

            "negative_probability": 0.0

        } 
