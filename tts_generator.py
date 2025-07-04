import os
from gtts import gTTS
import tempfile
import base64

def text_to_speech(text, lang='en'):
    """
    Convert text to speech and return audio data
    """
    try:
        # Create gTTS object
        tts = gTTS(text=text, lang=lang, slow=False)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            temp_filename = fp.name
        
        # Save the audio file
        tts.save(temp_filename)
        
        # Read the audio file and convert to base64
        with open(temp_filename, 'rb') as audio_file:
            audio_data = audio_file.read()
        
        # Clean up the temporary file
        os.unlink(temp_filename)
        
        return audio_data
        
    except Exception as e:
        print(f"Error in text-to-speech: {e}")
        return None

def conversation_to_speech(conversation_lines):
    """
    Convert a conversation (list of lines) to speech
    Returns a list of audio data for each line
    """
    audio_segments = []
    
    for line in conversation_lines:
        if line.strip():  # Skip empty lines
            # Extract just the text part (remove speaker labels like "A:", "B:")
            text = line.strip()
            if ': ' in text:
                text = text.split(': ', 1)[1]  # Remove speaker label
            
            audio_data = text_to_speech(text)
            if audio_data:
                audio_segments.append({
                    'text': text,
                    'audio': audio_data
                })
    
    return audio_segments 