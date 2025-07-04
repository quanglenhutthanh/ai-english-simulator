import torch
import torchaudio
import tempfile
import os
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import soundfile as sf
import numpy as np

class FairseqTTS:
    def __init__(self):
        """Initialize Fairseq TTS with a simpler, more reliable approach"""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.tokenizer = None
        self.initialized = False
        
    def initialize_model(self):
        """Initialize the TTS model - using a simpler approach than the original"""
        try:
            # Using a simpler TTS model that's more reliable
            model_name = "facebook/fastspeech2-en-ljspeech"
            
            # For now, we'll use a fallback approach since Fairseq can be complex
            # This will use a simpler TTS solution
            print("Initializing TTS model...")
            
            # Alternative: Use torchaudio's TTS models if available
            try:
                # Try to use torchaudio's TTS
                bundle = torchaudio.pipelines.TACOTRON2_WAVERNN_CHAR_LJSPEECH
                self.model = bundle.get_tacotron2().to(self.device)
                self.vocoder = bundle.get_wavernn().to(self.device)
                self.initialized = True
                print("Using torchaudio TTS model")
                return True
            except:
                print("torchaudio TTS not available, using fallback")
                return False
                
        except Exception as e:
            print(f"Error initializing Fairseq TTS: {e}")
            return False
    
    def text_to_speech(self, text, output_path=None):
        """Convert text to speech using Fairseq/torchaudio"""
        if not self.initialized:
            if not self.initialize_model():
                return None
        
        try:
            if hasattr(self, 'model') and hasattr(self, 'vocoder'):
                # Use torchaudio TTS
                with torch.no_grad():
                    # Tokenize text
                    tokens, lengths = self.model.tokenizer(text)
                    tokens = tokens.to(self.device)
                    
                    # Generate mel spectrogram
                    mel_outputs, mel_output_lengths, alignments = self.model.infer(tokens, lengths)
                    
                    # Generate waveform
                    waveform, lengths = self.vocoder(mel_outputs, mel_output_lengths)
                    
                    # Convert to numpy and normalize
                    audio = waveform[0].cpu().numpy()
                    audio = audio / np.max(np.abs(audio))  # Normalize
                    
                    # Save to temporary file if no output path specified
                    if output_path is None:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as fp:
                            output_path = fp.name
                    
                    # Save audio
                    sf.write(output_path, audio, 22050)
                    
                    # Read back as bytes for Streamlit
                    with open(output_path, 'rb') as f:
                        audio_data = f.read()
                    
                    # Clean up temp file
                    if output_path.startswith('/tmp'):
                        os.unlink(output_path)
                    
                    return audio_data
            
            else:
                print("TTS model not properly initialized")
                return None
                
        except Exception as e:
            print(f"Error in text-to-speech: {e}")
            return None
    
    def conversation_to_speech(self, conversation_lines):
        """Convert a conversation to speech using Fairseq"""
        audio_segments = []
        
        for line in conversation_lines:
            if line.strip():
                # Extract just the text part (remove speaker labels)
                text = line.strip()
                if ': ' in text:
                    text = text.split(': ', 1)[1]
                
                audio_data = self.text_to_speech(text)
                if audio_data:
                    audio_segments.append({
                        'text': text,
                        'audio': audio_data
                    })
        
        return audio_segments

# Global instance
fairseq_tts = FairseqTTS() 