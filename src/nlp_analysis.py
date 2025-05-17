# src/nlp_analysis.py
from textblob import TextBlob
from transformers import pipeline
from keybert import KeyBERT
import pronouncing

def analyze_sentiment(poem_text, sentiment_threshold):
    """Analyze sentiment of poem text using TextBlob."""
    try:
        polarity = TextBlob(poem_text).sentiment.polarity
        if polarity > sentiment_threshold:
            return "Positive"
        elif polarity < -sentiment_threshold:
            return "Negative"
        else:
            return "Neutral"
    except Exception as e:
        print(f"[Warning] Sentiment analysis failed: {e}")
        return "Neutral"

def classify_emotion(poem_text, model_name, device):
    """Classify emotion of poem text using a Hugging Face pipeline."""
    try:
        emotion_classifier = pipeline(
            "text-classification",
            model=model_name,
            top_k=None,
            device=device
        )
        result_list = emotion_classifier(poem_text[:512])
        if result_list and isinstance(result_list[0], list):
            top = max(result_list[0], key=lambda x: x["score"])
            return top["label"].capitalize()
        elif result_list and isinstance(result_list, list):
            top = max(result_list, key=lambda x: x["score"])
            return top["label"].capitalize()
    except Exception as e:
        print(f"[Warning] Emotion classification failed: {e}")
    return "Unknown"

def extract_keywords_and_theme(poem_text, kw_model, top_n, theme_categories):
    """Extract keywords and theme from poem text using KeyBERT."""
    try:
        keywords = kw_model.extract_keywords(poem_text, top_n=top_n)
        poem_keywords = [kw[0].lower() for kw in keywords]
        theme = "Other"
        for t, word_list in theme_categories.items():
            if any(word in poem_keywords for word in word_list):
                theme = t
                break
        return poem_keywords, theme
    except Exception as e:
        print(f"[Warning] Keyword extraction failed: {e}")
        return [], "Other"

def detect_rhyme_scheme(poem_lines):
    """Detect rhyme scheme of poem lines."""
    def get_rhyme(line):
        words = line.strip().split()
        return pronouncing.rhymes(words[-1]) if words else []

    try:
        rhymes = [get_rhyme(line) for line in poem_lines if line.strip()]
        if len(rhymes) < 2:
            return "Free Verse"
        pairs = zip(rhymes[::2], rhymes[1::2])
        rhyme_matches = [bool(set(a) & set(b)) for a, b in pairs]
        if all(rhyme_matches):
            return "AABB"
        elif any(rhyme_matches):
            return "ABAB"
        return "Free Verse"
    except Exception as e:
        print(f"[Warning] Rhyme detection failed: {e}")
        return "Free Verse"

def process_poem(config, poem):
    """
    Process a single poem to extract NLP features.

    Args:
        config (dict): Configuration dictionary with parameters.
        poem (dict): Poem dictionary to process.

    Returns:
        dict: Poem with added NLP features, or None if failed.
    """
    # Initialize models
    kw_model = KeyBERT()

    try:
        full_text = " ".join(poem["lines"])
        poem["sentiment"] = analyze_sentiment(full_text, config["sentiment_threshold"])
        poem["emotion"] = classify_emotion(full_text, config["emotion_model"], config["device"])
        poem["keywords"], poem["theme"] = extract_keywords_and_theme(
            full_text, kw_model, config["keyword_top_n"], config["theme_categories"]
        )
        poem["rhyme_pattern"] = detect_rhyme_scheme(poem["lines"])

        # Print NLP analysis results
        print("\n=== NLP Analysis Results ===")
        print(f"Title: {poem['title']}")
        print(f"Author: {poem['author']}")
        print(f"Sentiment: {poem['sentiment']}")
        print(f"Emotion: {poem['emotion']}")
        print(f"Keywords: {', '.join(poem['keywords'])}")
        print(f"Theme: {poem['theme']}")
        print(f"Rhyme Pattern: {poem['rhyme_pattern']}")
        print("===========================\n")

        return poem
    except Exception as e:
        print(f"[Error] Failed to process poem: {e}")
        return None