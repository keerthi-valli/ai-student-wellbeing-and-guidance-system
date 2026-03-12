def analyze_sentiment(text):
    """
    Analyzes text for sentiment and stress using a keyword-based approach.
    Returns a dictionary with 'mood', 'stress_level', and 'score'.
    """
    if not text:
        return {"mood": "Neutral", "stress_level": "Medium", "score": 0}

    text = text.lower()
    
    # Keyword Dictionaries
    positive_words = [
        "happy", "good", "great", "excellent", "amazing", "wonderful", 
        "productive", "excited", "love", "joy", "peace", "calm", 
        "confident", "achieved", "completed", "satisfied", "fun", 
        "enjoyed", "best", "fantastic", "success", "grateful"
    ]
    
    negative_words = [
        "sad", "bad", "terrible", "awful", "horrible", "frustrated", 
        "angry", "hate", "upset", "depressed", "anxious", "worried", 
        "scared", "fear", "fail", "failed", "tired", "exhausted", 
        "lonely", "bored", "annoyed", "difficult", "tough", "hard"
    ]
    
    stress_words = [
        "stress", "pressure", "deadline", "exam", "overwhelmed", 
        "busy", "hectic", "anxiety", "panic", "nervous", "tension", 
        "burden", "load", "struggle", "late", "rush", "urgent",
        "sleepless", "insomnia", "headache"
    ]
    
    # Scoring
    score = 0
    stress_score = 0
    
    tokens = text.split()
    
    for word in tokens:
        # Simple stemming/cleaning (very basic)
        clean_word = word.strip(".,!?")
        
        if clean_word in positive_words:
            score += 1
        elif clean_word in negative_words:
            score -= 1
            
        if clean_word in stress_words:
            stress_score += 1
            score -= 0.5 # Stress often correlates with negative sentiment
            
    # Determine Mood
    if score >= 2:
        mood = "Happy"
    elif score >= 1:
        mood = "Calm"
    elif score == 0:
        mood = "Neutral"
    elif score >= -1:
        mood = "Sad"
    else:
        mood = "Anxious" # or Angry
        
    # Determine Stress Level
    if stress_score >= 2:
        stress_level = "High"
    elif stress_score == 1:
        stress_level = "Medium"
    else:
        # If sentiment is very negative, assume some stress
        if score <= -2:
             stress_level = "Medium"
        else:
             stress_level = "Low"

    return {
        "mood": mood,
        "stress_level": stress_level,
        "score": score
    }
