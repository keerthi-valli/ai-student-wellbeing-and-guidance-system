import google.generativeai as genai
import json
import os
import tempfile
import base64
from config import Config

def configure_genai():
    if not Config.GOOGLE_API_KEY or Config.GOOGLE_API_KEY == "YOUR_API_KEY_HERE":
        print("WARNING: GOOGLE_API_KEY not configured.")
        return False
    genai.configure(api_key=Config.GOOGLE_API_KEY)
    return True

def clean_json_response(text):
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text.strip("`")
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def analyze_content(content, input_type="text"):
    """
    Analyzes diary content (text or voice base64) to determine mood and stress.
    Returns a dictionary with mood, stress_level, and summary.
    """
    if not configure_genai():
        return {
            "mood": "Neutral",
            "stress_level": "Low",
            "summary": "AI Analysis Unavailable (API Key missing)"
        }

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = """
        Analyze the emotional content of this diary entry.
        Determine the user's Mood and Stress Level.
        
        Return a valid JSON object with EXACTLY these fields:
        {
            "mood": "Happy" | "Neutral" | "Sad" | "Anxious" | "Stressed",
            "stress_level": "Low" | "Medium" | "High",
            "summary": "A brief 1-sentence summary of the user's state."
        }
        """

        if input_type == "voice":
            # Handle Base64 Audio
            if "," in content:
                header, encoded = content.split(",", 1)
            else:
                encoded = content
            
            # Determine mime type from header if possible, else default to webm
            # header example: data:audio/webm;base64
            mime_type = "audio/webm"
            
            audio_data = base64.b64decode(encoded)
            
            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_audio:
                temp_audio.write(audio_data)
                temp_path = temp_audio.name
            
            try:
                print(f"DEBUG: Uploading audio file {temp_path} to Gemini...")
                myfile = genai.upload_file(temp_path, mime_type=mime_type)
                
                response = model.generate_content([prompt, myfile])
                
                # Cleanup file after upload (Gemini processes it)
                # Note: File API processing might take a moment, but generate_content awaits it usually?
                # Actually upload_file is synchronous but processing might be async. 
                # generate_content waits for processing.
                
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        else:
            # Text Analysis
            response = model.generate_content(f"{prompt}\n\nDiary Text:\n{content}")

        # Parse Response
        try:
            result_json = json.loads(clean_json_response(response.text))
            return result_json
        except json.JSONDecodeError:
            print(f"ERROR: Failed to parse AI response: {response.text}")
            return {
                "mood": "Neutral", 
                "stress_level": "Medium", 
                "summary": "AI Parsing Error"
            }

    except Exception as e:
        print(f"ERROR: AI Analysis failed: {e}")
        return {
            "mood": "Neutral",
            "stress_level": "Medium",
            "summary": f"Analysis Error: {str(e)}"
        }
