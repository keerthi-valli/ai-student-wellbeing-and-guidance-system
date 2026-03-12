import base64
import os
import time
from datetime import datetime
import speech_recognition as sr
from pydub import AudioSegment

def process_voice_entry(base64_audio):
    """
    Decodes base64 audio, saves it to a file, and returns transcription with confidence.
    """
    if not base64_audio:
        return None

    try:
        # 1. Create directory if not exists
        upload_dir = os.path.join("static", "uploads", "voice")
        os.makedirs(upload_dir, exist_ok=True)

        # 2. Decode Base64
        if "," in base64_audio:
            header, encoded = base64_audio.split(",", 1)
        else:
            encoded = base64_audio

        audio_data = base64.b64decode(encoded)

        # 3. Save File
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"voice_{timestamp}.webm"
        file_path = os.path.join(upload_dir, filename)
        
        with open(file_path, "wb") as f:
            f.write(audio_data)

        # 4. Transcribe
        transcription_result = _transcribe_audio(file_path)

        return {
            "text": transcription_result["text"],
            "confidence": transcription_result["confidence"],
            "audio_path": f"static/uploads/voice/{filename}" # Relative path for DB
        }

    except Exception as e:
        print(f"Error processing voice: {e}")
        return None

def _transcribe_audio(file_path):
    """
    Attempts real transcription using SpeechRecognition.
    Returns dict with 'text' and 'confidence'.
    """
    try:
        recognizer = sr.Recognizer()
        
        # Convert WebM to WAV (requires ffmpeg)
        wav_filename = file_path.replace(".webm", ".wav")
        
        try:
            audio = AudioSegment.from_file(file_path)
            audio.export(wav_filename, format="wav")
            
            with sr.AudioFile(wav_filename) as source:
                audio_data_sr = recognizer.record(source)
                
                # Request full response to get confidence
                # recognize_google returns a list of alternatives if show_all=True
                response = recognizer.recognize_google(audio_data_sr, show_all=True)
                
                text = ""
                confidence = 0.0
                
                if isinstance(response, dict) and "alternative" in response:
                    # Get best alternative
                    best = response["alternative"][0]
                    text = best.get("transcript", "")
                    confidence = best.get("confidence", 0.0)
                elif isinstance(response, list) and len(response) > 0:
                     # Sometimes it returns a list directly?
                    best = response[0]
                    text = best.get("transcript", "")
                    confidence = best.get("confidence", 0.0)
                else:
                    # Fallback for empty or complex structure
                    text = str(response) if response else ""
                
                print(f"Transcription: '{text}' (Confidence: {confidence})")
                return {"text": text, "confidence": confidence}
                
        except Exception as conversion_error:
            print(f"Audio conversion/transcription failed: {conversion_error}")
            return {
                "text": "(Transcription unavailable - ffmpeg missing or audio unclear)",
                "confidence": 0.0
            }
        finally:
            # Cleanup WAV
            if os.path.exists(wav_filename):
                os.remove(wav_filename)

    except Exception as e:
        print(f"General transcription error: {e}")
        return {"text": "(Transcription error)", "confidence": 0.0}

