# src/music_mapping.py

def map_sentiment(sentiment):
    """Map sentiment to mode, base note, and chord progression."""
    sentiment = sentiment.lower()
    if sentiment == "positive":
        return {
            "mode": "major",
            "base_note": 60,  # C4
            "chord_progression": [
                [60, 64, 67],  # C major (C, E, G)
                [65, 69, 72],  # F major (F, A, C)
                [67, 71, 74],  # G major (G, B, D)
                [60, 64, 67]   # back to C major
            ]
        }
    elif sentiment == "negative":
        return {
            "mode": "minor",
            "base_note": 57,  # A3
            "chord_progression": [
                [57, 60, 64],  # Am (A, C, E)
                [50, 53, 57],  # Dm (approximation)
                [52, 56, 59],  # Em (approximation)
                [57, 60, 64]   # back to Am
            ]
        }
    elif sentiment == "neutral":
        return {
            "mode": "modal",
            "base_note": 60,
            "chord_progression": [
                [60, 62, 67]   # an example modal chord
            ]
        }
    else:
        return {
            "mode": "minor",
            "base_note": 60,
            "chord_progression": [
                [60, 63, 67]
            ]
        }

def map_emotion(emotion):
    """Map emotion to melody shape, tempo, dynamics, and ornamentation."""
    emotion = emotion.lower()
    # Map tempo character to numerical tempo
    tempo_mapping = {
        "lively": (90, 110),
        "slow": (60, 80),
        "fast or irregular": (110, 130),
        "sudden shifts": (80, 120),
        "uneven": (70, 90),
        "unpredictable": (90, 120)
    }
    if emotion == "joy":
        tempo_range = tempo_mapping["lively"]
        return {
            "melody_shape": "ascending",
            "tempo": tempo_range[0] + (tempo_range[1] - tempo_range[0]) * 0.5,  # Midpoint
            "dynamics": "active",
            "ornamentation": "rich"
        }
    elif emotion == "sadness":
        tempo_range = tempo_mapping["slow"]
        return {
            "melody_shape": "descending",
            "tempo": tempo_range[0] + (tempo_range[1] - tempo_range[0]) * 0.5,
            "dynamics": "soft",
            "ornamentation": "minimal"
        }
    elif emotion == "anger":
        tempo_range = tempo_mapping["fast or irregular"]
        return {
            "melody_shape": "abrupt",
            "tempo": tempo_range[0] + (tempo_range[1] - tempo_range[0]) * 0.5,
            "dynamics": "strong and staccato",
            "ornamentation": "sporadic with dissonances"
        }
    elif emotion == "surprise":
        tempo_range = tempo_mapping["sudden shifts"]
        return {
            "melody_shape": "variable",
            "tempo": tempo_range[0] + (tempo_range[1] - tempo_range[0]) * 0.5,
            "dynamics": "unexpected",
            "ornamentation": "sporadic"
        }
    elif emotion == "fear":
        tempo_range = tempo_mapping["uneven"]
        return {
            "melody_shape": "unstable",
            "tempo": tempo_range[0] + (tempo_range[1] - tempo_range[0]) * 0.5,
            "dynamics": "tense",
            "ornamentation": "sparse, with suspenseful intervals"
        }
    elif emotion == "disgust":
        tempo_range = tempo_mapping["unpredictable"]
        return {
            "melody_shape": "irregular",
            "tempo": tempo_range[0] + (tempo_range[1] - tempo_range[0]) * 0.5,
            "dynamics": "uneven",
            "ornamentation": "dissonant"
        }
    else:
        return {
            "melody_shape": "smooth",
            "tempo": 90,
            "dynamics": "normal",
            "ornamentation": "minimal"
        }

def map_theme(theme):
    """Map theme to a list of instruments."""
    theme_mapping = {
        "nature": ["flute", "clarinet", "harp", "tubular_bells"],
        "love": ["piano", "violin", "cello", "guitar"],
        "death": ["cello", "contrabass", "organ", "tuba"],
        "war": ["timpani", "trumpet", "french_horn", "trombone"],
        "other": ["piano", "guitar", "violin", "alto_sax"]
    }
    return theme_mapping.get(theme.lower(), theme_mapping["other"])

def map_keywords(keywords):
    """Map keywords to background effects."""
    suggestions = {}
    keywords_lower = [kw.lower() for kw in keywords]
    nature_related = {"nests", "squirrels", "dormouse", "seeds", "autumn"}
    if nature_related.intersection(keywords_lower):
        suggestions["background_effects"] = ["bird chirps", "water flow", "wind rustle"]
    return suggestions

def map_rhyme_pattern(rhyme_pattern):
    """Map rhyme pattern to structure and time signature."""
    pattern = rhyme_pattern.lower()
    if pattern == "aabb":
        return {
            "structure": "symmetric paired repetition",
            "time_signature": "4/4"
        }
    elif pattern == "abab":
        return {
            "structure": "alternating thematic sections",
            "time_signature": "3/4"
        }
    elif pattern == "free verse":
        return {
            "structure": "free form",
            "time_signature": "4/4"
        }
    else:
        return {
            "structure": "free form",
            "time_signature": "4/4"
        }

def process_poem(config, poem):
    """
    Map poem features to music parameters.

    Args:
        config (dict): Configuration dictionary.
        poem (dict): Poem dictionary with NLP features.

    Returns:
        dict: Poem with added music parameters, or None if failed.
    """
    try:
        # Map features to music parameters
        music_params = {}
        sentiment_map = map_sentiment(poem.get("sentiment", "neutral"))
        emotion_map = map_emotion(poem.get("emotion", "joy"))
        rhyme_map = map_rhyme_pattern(poem.get("rhyme_pattern", "free verse"))

        music_params["mode"] = sentiment_map["mode"]
        music_params["base_note"] = sentiment_map["base_note"]
        music_params["chord_progression"] = sentiment_map["chord_progression"]
        music_params["melody_shape"] = emotion_map["melody_shape"]
        music_params["tempo"] = emotion_map["tempo"]
        music_params["dynamics"] = emotion_map["dynamics"]
        music_params["ornamentation"] = emotion_map["ornamentation"]
        music_params["instruments"] = map_theme(poem.get("theme", "other"))
        music_params["keyword_decorations"] = map_keywords(poem.get("keywords", []))
        music_params["structure"] = rhyme_map["structure"]
        music_params["time_signature"] = rhyme_map["time_signature"]

        # Add music_params to poem
        poem["music_params"] = music_params

        # Print mapping results
        print("\n=== Music Mapping Results ===")
        print(f"Mode: {music_params['mode']}")
        print(f"Base Note: {music_params['base_note']}")
        print(f"Chord Progression: {music_params['chord_progression']}")
        print(f"Melody Shape: {music_params['melody_shape']}")
        print(f"Tempo: {music_params['tempo']}")
        print(f"Dynamics: {music_params['dynamics']}")
        print(f"Ornamentation: {music_params['ornamentation']}")
        print(f"Instruments: {', '.join(music_params['instruments'])}")
        print(f"Background Effects: {music_params['keyword_decorations'].get('background_effects', [])}")
        print(f"Structure: {music_params['structure']}")
        print(f"Time Signature: {music_params['time_signature']}")
        print("===========================\n")

        return poem
    except Exception as e:
        print(f"[Error] Failed to map music parameters: {e}")
        return None