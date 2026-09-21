from transformers import pipeline


# =========================================================
# AI SENTIMENT MODEL
# =========================================================

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"


classifier = pipeline(
    "sentiment-analysis",
    model=MODEL_NAME,
    tokenizer=MODEL_NAME
)


# =========================================================
# SENTIMENT ANALYSIS
# =========================================================

def analyze_sentiment(text):

    if not text or not text.strip():

        return {
            "sentiment": "neutral",
            "score": 0.0
        }

    try:

        # Limit extremely long articles
        text = text[:2000]

        result = classifier(
            text,
            truncation=True
        )[0]

        label = result["label"].upper()
        confidence = float(result["score"])

        if label == "LABEL_0":
            sentiment = "negative"

        elif label == "LABEL_1":
            sentiment = "neutral"

        elif label == "LABEL_2":
            sentiment = "positive"

        else:
            sentiment = label.lower()

        return {
            "sentiment": sentiment,
            "score": round(confidence, 4)
        }

    except Exception as error:

        print(
            "Sentiment model error:",
            error
        )

        return {
            "sentiment": "neutral",
            "score": 0.0
        }