import sys
import os

# Mocking modules that might not be installed in the agent environment to avoid import errors during syntax check
from unittest.mock import MagicMock
sys.modules['flask'] = MagicMock()
sys.modules['extensions'] = MagicMock()
sys.modules['bson'] = MagicMock()
sys.modules['config'] = MagicMock()
sys.modules['speech_recognition'] = MagicMock()
sys.modules['pydub'] = MagicMock()

# Now trying to import the modified files to check for syntax errors
try:
    print("Checking routes/diary.py...")
    # We can't easily import routes.diary because it depends on 'app' context usually, 
    # but we can check if it compiles.
    with open(r'c:\Users\Admin\OneDrive\Desktop\4-2 project\AI-deiven student well being guidance system\code2\routes\diary.py', 'r') as f:
        compile(f.read(), 'routes/diary.py', 'exec')
    print("routes/diary.py syntax is OK.")

    print("Checking utils/voice_handler.py...")
    with open(r'c:\Users\Admin\OneDrive\Desktop\4-2 project\AI-deiven student well being guidance system\code2\utils\voice_handler.py', 'r') as f:
        compile(f.read(), 'utils/voice_handler.py', 'exec')
    print("utils/voice_handler.py syntax is OK.")
    
    # We can also attempt to import voice_handler as it has fewer deps
    # import utils.voice_handler 
    # print("utils.voice_handler imported successfully.")

except Exception as e:
    print(f"Syntax or Import Error found: {e}")
    sys.exit(1)

print("Verification Successful: Core files are syntactically correct.")
