import os
from gtts import gTTS
import tempfile
import base64
import speech_recognition as sr
import streamlit as st

def text_to_speech(text, lang='en', tld='com', voice_type='default'):
    """
    Convert text to speech and return audio data
    voice_type: 'default', 'british', 'australian', 'indian', 'irish'
    """
    try:
        # Voice configurations
        voice_configs = {
            'default': {'lang': 'en', 'tld': 'com'},
            'british': {'lang': 'en', 'tld': 'co.uk'},
            'australian': {'lang': 'en', 'tld': 'com.au'},
            'indian': {'lang': 'en', 'tld': 'co.in'},
            'irish': {'lang': 'en', 'tld': 'ie'},
            'canadian': {'lang': 'en', 'tld': 'ca'},
            'south_african': {'lang': 'en', 'tld': 'co.za'}
        }
        
        config = voice_configs.get(voice_type, voice_configs['default'])
        
        # Create gTTS object with specific voice
        tts = gTTS(text=text, lang=config['lang'], tld=config['tld'], slow=False)
        
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

def conversation_to_speech(conversation_lines, voice_a='default', voice_b='british'):
    """
    Convert a conversation (list of lines) to speech with different voices
    voice_a: voice for Speaker A
    voice_b: voice for Speaker B
    """
    audio_segments = []
    
    for i, line in enumerate(conversation_lines):
        if line.strip():  # Skip empty lines
            # Extract just the text part (remove speaker labels like "A:", "B:")
            text = line.strip()
            speaker = None
            
            if ': ' in text:
                speaker_label, text = text.split(': ', 1)
                speaker = speaker_label.strip()
            
            # Choose voice based on speaker
            if speaker == 'A':
                voice_type = voice_a
            elif speaker == 'B':
                voice_type = voice_b
            else:
                voice_type = 'default'  # fallback
            
            audio_data = text_to_speech(text, voice_type=voice_type)
            if audio_data:
                audio_segments.append({
                    'text': text,
                    'audio': audio_data,
                    'speaker': speaker,
                    'voice_type': voice_type
                })
    
    return audio_segments 

def record_user_speech():
    """Record user speaking and assess pronunciation"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Speak now...")
        audio = recognizer.listen(source, timeout=5)
    return audio

# Add practice buttons for each conversation line
if st.button("🎤 Practice Speaking"):
    audio = record_user_speech()
    # Compare with expected pronunciation
    # Give feedback on accuracy 