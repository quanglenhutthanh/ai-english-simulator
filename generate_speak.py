import torch
import argparse
import tempfile
import os
import soundfile as sf
import nltk
from fairseq.checkpoint_utils import load_model_ensemble_and_task_from_hf_hub
from fairseq.models.text_to_speech.hub_interface import TTSHubInterface

# Download required NLTK data
try:
    nltk.download('averaged_perceptron_tagger_eng', quiet=True)
except:
    pass

# Add safe globals for torch serialization
torch.serialization.add_safe_globals([argparse.Namespace])

def initialize_fairseq_tts():
    """Initialize Fairseq TTS model"""
    try:
        print("Loading Fairseq TTS model...")
        models, cfg, task = load_model_ensemble_and_task_from_hf_hub(
            "facebook/fastspeech2-en-ljspeech",
            arg_overrides={"vocoder": "hifigan", "fp16": False}
        )
        
        if task is None:
            print("Error: Task is None. Trying alternative initialization...")
            return None, None, None
            
        # Update configuration
        TTSHubInterface.update_cfg_with_data_cfg(cfg, task.data_cfg)
        generator = task.build_generator(models, cfg)
        
        print("Fairseq TTS model loaded successfully!")
        return models, task, generator
        
    except Exception as e:
        print(f"Error initializing Fairseq TTS: {e}")
        return None, None, None

def text_to_speech_fairseq(text, models, task, generator):
    """Convert text to speech using Fairseq"""
    try:
        if models is None or task is None or generator is None:
            print("TTS model not properly initialized")
            return None
            
        # Get model input
        sample = TTSHubInterface.get_model_input(task, text)
        
        # Generate prediction
        wav, rate = TTSHubInterface.get_prediction(task, models[0], generator, sample)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as fp:
            temp_filename = fp.name
        
        # Save audio
        sf.write(temp_filename, wav, rate)
        
        # Read back as bytes for Streamlit
        with open(temp_filename, 'rb') as f:
            audio_data = f.read()
        
        # Clean up temp file
        os.unlink(temp_filename)
        
        return audio_data
        
    except Exception as e:
        print(f"Error in text-to-speech: {e}")
        return None

def conversation_to_speech_fairseq(conversation_lines):
    """Convert conversation to speech using Fairseq"""
    # Initialize model
    models, task, generator = initialize_fairseq_tts()
    
    if models is None:
        print("Failed to initialize Fairseq TTS")
        return []
    
    audio_segments = []
    
    for line in conversation_lines:
        if line.strip():
            # Extract just the text part (remove speaker labels)
            text = line.strip()
            if ': ' in text:
                text = text.split(': ', 1)[1]
            
            audio_data = text_to_speech_fairseq(text, models, task, generator)
            if audio_data:
                audio_segments.append({
                    'text': text,
                    'audio': audio_data
                })
    
    return audio_segments

# Test function
if __name__ == "__main__":
    text = "Hello Quang, how are you today?"
    
    # Initialize model
    models, task, generator = initialize_fairseq_tts()
    
    if models is not None:
        # Test single text
        audio_data = text_to_speech_fairseq(text, models, task, generator)
        if audio_data:
            print("TTS test successful!")
            # Save test file
            with open('test_output.wav', 'wb') as f:
                f.write(audio_data)
            print("Test audio saved as 'test_output.wav'")
        else:
            print("TTS test failed!")
    else:
        print("Model initialization failed!")