from datetime import datetime, timedelta

SUBJECT_TOPICS = {
    "python": [
        "Variables & Data Types", "Control Flow (If/Else)", "Loops (For/While)",
        "Functions & Modules", "Data Structures (Lists/Dicts)", "File Handling",
        "Object Oriented Programming", "Error Handling & Debugging", "Mini Project: Calculator",
        "Libraries (NumPy/Pandas)", "Web Scraping Basics", "Final Project"
    ],
    "mathematics": [
        "Number Systems", "Algebra Basics", "Linear Equations",
        "Quadratic Equations", "Geometry & Shapes", "Trigonometry",
        "Calculus: Limits", "Calculus: Derivatives", "Calculus: Integrals",
        "Probability", "Statistics", "Revision & Mock Test"
    ],
    "science": [
        "Physics: Motion", "Physics: Force & Laws", "Physics: Gravitation",
        "Chemistry: Matter", "Chemistry: Atoms & Molecules", "Chemistry: Structure of Atom",
        "Biology: Cell Structure", "Biology: Tissues", "Biology: Diversity in Organisms",
        "Environmental Science", "Scientific Method", "Final Review"
    ],
    "english": [
        "Grammar: Tenses", "Grammar: Active/Passive Voice", "Vocabulary Building",
        "Reading Comprehension", "Writing: Essays", "Writing: Letters/Emails",
        "Literature: Fiction Analysis", "Literature: Poetry Analysis", "Speaking Skills",
        "Listening Skills", "Presentation Skills", "Final Assessment"
    ],
    "default": [
        "Chapter 1: Foundations", "Chapter 2: Core Concepts", "Chapter 3: Advanced Topics",
        "Chapter 4: Applications", "Chapter 5: Case Studies", "Chapter 6: Practical Exercises",
        "Chapter 7: Review & Assessment", "Chapter 8: Project Work"
    ]
}


def generate_roadmap(profile, mood_data=None):
    """
    Generates a weekly roadmap based on the profile inputs and current mood.
    Returns topics as objects: {'topic': str, 'completed': bool}
    """
    subject = profile.get("subject", "").lower()
    custom_subject = profile.get("custom_subject", "")
    daily_hours = int(profile.get("daily_hours", 1))
    
    # 1. Get Topics
    if subject == "other" and custom_subject:
        # Generate generic structure for custom subject
        topics = [
            f"Introduction to {custom_subject}",
            f"{custom_subject} Basics & Setup",
            f"Core Concepts of {custom_subject} - Part 1",
            f"Core Concepts of {custom_subject} - Part 2",
            f"Intermediate {custom_subject} Techniques",
            f"Advanced {custom_subject} Topics",
            f"Practical Application / Mini-Project",
            f"Final Review & Capstone Project"
        ]
        # Copy default if list is too short
        if len(topics) < 8:
             topics.extend(SUBJECT_TOPICS["default"][len(topics):])
             
    else:
        topics = SUBJECT_TOPICS.get(subject, [])
        if not topics:
            # Try finding partial match
            found = False
            for key in SUBJECT_TOPICS:
                if key in subject:
                    topics = SUBJECT_TOPICS[key]
                    found = True
                    break
            if not found:
                topics = SUBJECT_TOPICS["default"]
            
    # Convert string topics to objects
    topic_objects = [{"topic": t, "completed": False} for t in topics]
            
    # 2. Determine Capacity (Topics per week)
    # Base: 1 topic ~ 2.5 hours. 
    base_topics_per_week = max(1, int(daily_hours * 0.4 * 7)) # e.g. 1hr/day = 7hrs/week -> ~2.8 topics
    if base_topics_per_week < 1: base_topics_per_week = 1
    
    # 3. Adapt to Stress/Mood
    adaptation_msg = None
    if mood_data:
        # mood_data might have 'stress_score' (0-100) or 'stress_level'
        stress_score = mood_data.get("stress_score", 50)
        mood = mood_data.get("mood", "Neutral")
        
        # Mapping string level to score if score missing
        if isinstance(stress_score, str):
            if stress_score == "High": stress_score = 80
            elif stress_score == "Medium": stress_score = 50
            else: stress_score = 20
            
        if stress_score > 75 or mood in ["Sad", "Depressed", "Anxious", "Stressed"]:
            # High stress adaptation: Reduce workload significantly
            base_topics_per_week = max(1, int(base_topics_per_week * 0.6))
            adaptation_msg = "Workload reduced to help you manage high stress."
        elif stress_score > 50:
             # Medium stress: Slight reduction
             base_topics_per_week = max(1, int(base_topics_per_week * 0.8))
             adaptation_msg = "Balanced workload for sustainable progress."
        elif mood in ["Happy", "Excited", "Confident", "Motivated"]:
            base_topics_per_week = int(base_topics_per_week * 1.2)
            adaptation_msg = "Accelerated plan based on your positive momentum!"
            
    # 4. Distribute Topics
    roadmap = []
    current_week = 1
    current_date = datetime.now()
    
    # Ensure we don't index out of bounds if topics are few
    idx = 0
    while idx < len(topic_objects):
        week_topics = topic_objects[idx : idx + base_topics_per_week]
        
        week_data = {
            "week": current_week,
            "start_date": current_date.strftime("%d %b"),
            "end_date": (current_date + timedelta(days=6)).strftime("%d %b"),
            "topics": week_topics
        }
        roadmap.append(week_data)
        
        idx += base_topics_per_week
        current_week += 1
        current_date += timedelta(days=7)
        
    return {
        "roadmap": roadmap,
        "total_weeks": len(roadmap),
        "adaptation_message": adaptation_msg,
        "topics_per_week": base_topics_per_week,
        "total_topics": len(topic_objects),
        "completed_topics": 0,
        "progress": 0
    }

