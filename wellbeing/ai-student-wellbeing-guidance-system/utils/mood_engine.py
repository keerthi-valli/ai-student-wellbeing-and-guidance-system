
def calculate_mood_and_stress(text):
    """
    Analyzes text to determine mood, stress level, and a wellbeing score (0-100)
    using weighted keyword scoring and dominance logic.
    """
    if not text:
        return {
            "mood": "Neutral",
            "stress_level": "Medium",
            "score": 50,
            "breakdown": {"pos": 0, "neg": 0, "stress": 0}
        }

    text_lower = text.lower()
    tokens = text_lower.split()
    
    # --- 1. Dictionaries & Weights ---
    
    # Higher magnitude = stronger emotion
    
    # POSITIVE (Weights: 1 to 3)
    happy_weights = {
        "happy": 2, "happiness": 2, "joy": 3, "joyful": 3, "excited": 2, 
        "amazing": 3, "wonderful": 3, "fantastic": 3, "great": 2, "good": 1,
        "love": 3, "proud": 2, "confident": 2, "grateful": 2, "hopeful": 2,
        "best": 3, "better": 1, "calm": 2, "relaxed": 2, "content": 2, "peace": 2,
        "productive": 2, "achieved": 2, "success": 3, "fun": 2, "enjoyed": 2
    }
    
    # NEGATIVE (Weights: -1 to -3)
    sad_weights = {
        "sad": -2, "sadness": -2, "unhappy": -2, "depressed": -3, "depressing": -3,
        "hopeless": -3, "grief": -3, "sorrow": -3, "miserable": -3, "crying": -3,
        "low": -1, "down": -1, "lonely": -2, "bad": -1, "terrible": -2, "awful": -2,
        "horrible": -2, "worst": -3, "hurt": -2, "pain": -2, "painful": -2,
        "fail": -2, "failed": -3, "failure": -3, "rejected": -3, "rejection": -3,
        "unlucky": -2, "unfortunately": -1
    }
    
    # ANXIOUS / STRESS (Weights: -1 to -3)

    # These contribute to negative score AND stress score
    anxious_weights = {
        "anxious": -2, "anxiety": -2, "stressed": -2, "stress": -2, "worried": -2,
        "worry": -2, "panic": -3, "fear": -3, "scared": -3, "nervous": -1, "tense": -1,
        "overwhelmed": -3, "pressure": -2, "deadline": -2, "busy": -1, "hectic": -2,
        "burden": -2, "struggle": -2, "struggling": -2, "tired": -1, "exhausted": -2,
        "sleepless": -2, "insomnia": -3, "headache": -1
    }

    # ANGER / FRUSTRATION (Mapped to Negative Mood usually, but tracks as neg score)
    angry_weights = {
        "angry": -2, "anger": -2, "mad": -2, "furious": -3, "hate": -3, 
        "frustrated": -2, "frustration": -2, "annoyed": -1, "upset": -2, "irritated": -1
    }

    # DISTRESS PHRASES (High Negative Impact)
    distress_phrases = [
        ("why me", -4), ("give up", -4), ("no hope", -4), ("wish i could", -2),
        ("feel empty", -3), ("can't go on", -4), ("end it", -5), ("not good enough", -3),
        ("why is this happening", -3)
    ]

    # --- 2. Scoring ---
    
    pos_score = 0
    neg_score = 0
    stress_score_raw = 0 # Tracks specifically stress-related words
    
    # Helper to check negation
    def is_negated(index, tokens):
        if index > 0:
            prev = tokens[index-1]
            if prev in ["not", "no", "never", "don't", "cant", "cannot", "won't"]:
                return True
        return False

    # A. Phrase Matching
    for phrase, weight in distress_phrases:
        if phrase in text_lower:
            neg_score += abs(weight) # Add to negative tally (absolute value for magnitude)
            stress_score_raw += 2 # Distress implies stress

    # B. Word Matching
    matched_words = []
    
    for i, word in enumerate(tokens):
        clean_word = word.strip(".,!?\"'()")
        weight = 0
        category = "neutral"
        
        # Check dictionaries
        if clean_word in happy_weights:
            weight = happy_weights[clean_word]
            category = "happy"
        elif clean_word in sad_weights:
            weight = sad_weights[clean_word]
            category = "sad"
        elif clean_word in anxious_weights:
            weight = anxious_weights[clean_word]
            category = "anxious"
        elif clean_word in angry_weights:
            weight = angry_weights[clean_word]
            category = "angry"
            
        # Handle Negation
        if weight != 0:
            if is_negated(i, tokens):
                # Flip polarity broadly
                # "not happy" (2) -> -1.5 (mildly negative)
                # "not sad" (-2) -> 1 (mildly positive/neutral)
                if weight > 0:
                    weight = -1.5 
                    category = "negated_pos"
                else:
                    weight = 1
                    category = "negated_neg"
            
            # Aggregate Scores
            if weight > 0:
                pos_score += weight
            else:
                neg_score += abs(weight) # Keep positive magnitude for comparison
                
            # Specific Stress Tracking
            if category == "anxious":
                stress_score_raw += abs(weight) # Full weight
            elif category == "sad" or category == "angry":
                stress_score_raw += abs(weight) * 0.5 # Partial weight for other neg emotions
            
            matched_words.append((clean_word, weight, category))

    # --- 3. Dominance & Mood Logic ---
    
    # Normalize Stress Score (0-100 logic)
    # Explicit stress words + inferred from neg words
    # Cap raw stress at some reasonable number per sentence (e.g., 10-15) then map to 0-100
    # Let's say max expected raw stress in a short text is ~15.
    computed_stress_score = min(100, (stress_score_raw * 8) + 20) if stress_score_raw > 0 else 10
    
    # Calculate Wellbeing Score
    # Start at 50
    # Add pos, subtract neg
    net_score = pos_score - neg_score
    final_score = 50 + (net_score * 5) # Scale factor 5
    final_score = max(0, min(100, final_score))
    
    # DOMINANCE CHECK
    # If negative score is significantly higher than positive, mood is negative
    # regardless of some positive words.
    dominant_mood = "Neutral"
    
    # Logic:
    if neg_score == 0 and pos_score == 0:
        dominant_mood = "Neutral"
    elif neg_score > pos_score * 1.2: # Negative dominates
        # Sub-classify negative
        # Find which negative category contributed most? 
        # For simplicity, check matching density
        sad_count = sum(1 for w in matched_words if w[2] == 'sad')
        anx_count = sum(1 for w in matched_words if w[2] == 'anxious')
        ang_count = sum(1 for w in matched_words if w[2] == 'angry')
        
        if anx_count >= sad_count and anx_count >= ang_count:
            dominant_mood = "Anxious"
        elif ang_count > sad_count and ang_count > anx_count:
            dominant_mood = "Stressed" # Group anger/stress often
        else:
            dominant_mood = "Sad" # Default negative
            
    elif pos_score > neg_score: # Positive dominates
        dominant_mood = "Happy"
    else:
        # Balanced / Mixed
        dominant_mood = "Neutral"
        
    # --- 4. Stress Level Bucketing ---
    if computed_stress_score >= 70:
        stress_level = "High"
    elif computed_stress_score >= 40:
        stress_level = "Medium"
    else:
        stress_level = "Low"

    # --- 5. Override/Refinement ---
    # If mood is Happy but stress is High -> Unusual, but possible? 
    # Usually highly stressed means not "Happy" in a wellbeing context.
    # Let's degrade mood if stress is very high.
    if stress_level == "High" and dominant_mood == "Happy":
        dominant_mood = "Anxious" # "Manic" or just overwhelmed?
        final_score = min(final_score, 60) # Cap score
        
    return {
        "mood": dominant_mood,
        "stress_level": stress_level,
        "score": int(final_score),
        "stress_score": int(computed_stress_score),
        "breakdown": {
            "pos_raw": pos_score,
            "neg_raw": neg_score,
            "stress_raw": stress_score_raw
        }
    }
