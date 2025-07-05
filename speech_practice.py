import speech_recognition as sr
import tempfile
import os
import base64
from difflib import SequenceMatcher
import re

class SpeechPractice:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        
    def record_speech(self, timeout=5, phrase_time_limit=10):
        """Record user speech from microphone"""
        try:
            with sr.Microphone() as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen for speech
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
                return audio
        except sr.WaitTimeoutError:
            return None
        except Exception as e:
            print(f"Error recording speech: {e}")
            return None
    
    def speech_to_text(self, audio):
        """Convert speech to text using Google Speech Recognition"""
        try:
            text = self.recognizer.recognize_google(audio)
            return text.lower().strip()
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"Could not request results: {e}")
            return None
    
    def calculate_pronunciation_score(self, user_text, expected_text):
        """Calculate pronunciation accuracy score (0-100)"""
        if not user_text or not expected_text:
            return 0
        
        # Clean and normalize texts
        user_clean = re.sub(r'[^\w\s]', '', user_text.lower())
        expected_clean = re.sub(r'[^\w\s]', '', expected_text.lower())
        
        # Calculate similarity using SequenceMatcher
        similarity = SequenceMatcher(None, user_clean, expected_clean).ratio()
        
        # Convert to percentage
        score = similarity * 100
        
        return round(score, 1)
    
    def analyze_fluency(self, audio_duration, word_count):
        """Analyze speaking fluency"""
        if word_count == 0:
            return 0
        
        # Calculate words per minute
        wpm = (word_count / audio_duration) * 60
        
        # Score based on typical speaking rates
        if 120 <= wpm <= 160:  # Optimal range
            fluency_score = 100
        elif 100 <= wpm < 120 or 160 < wpm <= 180:
            fluency_score = 80
        elif 80 <= wpm < 100 or 180 < wpm <= 200:
            fluency_score = 60
        else:
            fluency_score = 40
            
        return round(fluency_score, 1)
    
    def get_feedback(self, pronunciation_score, fluency_score, user_text, expected_text):
        """Generate feedback based on scores"""
        feedback = []
        
        # Pronunciation feedback
        if pronunciation_score >= 90:
            feedback.append("🎯 Excellent pronunciation!")
        elif pronunciation_score >= 80:
            feedback.append("👍 Good pronunciation, keep practicing!")
        elif pronunciation_score >= 70:
            feedback.append("⚠️ Pronunciation needs improvement. Try speaking more clearly.")
        else:
            feedback.append("❌ Pronunciation needs significant work. Practice slowly and clearly.")
        
        # Fluency feedback
        if fluency_score >= 80:
            feedback.append("⚡ Great speaking pace!")
        elif fluency_score >= 60:
            feedback.append("📝 Good pace, try to speak more naturally.")
        else:
            feedback.append("🐌 Speaking too slowly or too fast. Aim for natural conversation pace.")
        
        # Specific word feedback
        if user_text and expected_text:
            user_words = set(user_text.split())
            expected_words = set(expected_text.split())
            missing_words = expected_words - user_words
            extra_words = user_words - expected_words
            
            if missing_words:
                feedback.append(f"🔍 Missing words: {', '.join(missing_words)}")
            if extra_words:
                feedback.append(f"➕ Extra words: {', '.join(extra_words)}")
        
        return feedback
    
    def practice_line(self, expected_text):
        """Practice a single conversation line"""
        result = {
            'success': False,
            'user_text': None,
            'pronunciation_score': 0,
            'fluency_score': 0,
            'feedback': [],
            'audio_duration': 0
        }
        
        try:
            # Record user speech
            audio = self.record_speech()
            if not audio:
                result['feedback'].append("❌ No speech detected. Please try again.")
                return result
            
            # Convert to text
            user_text = self.speech_to_text(audio)
            if not user_text:
                result['feedback'].append("❌ Could not understand speech. Please speak clearly.")
                return result
            
            # Calculate scores
            pronunciation_score = self.calculate_pronunciation_score(user_text, expected_text)
            audio_duration = len(audio.frame_data) / (audio.sample_rate * audio.sample_width)
            word_count = len(user_text.split())
            fluency_score = self.analyze_fluency(audio_duration, word_count)
            
            # Generate feedback
            feedback = self.get_feedback(pronunciation_score, fluency_score, user_text, expected_text)
            
            result.update({
                'success': True,
                'user_text': user_text,
                'pronunciation_score': pronunciation_score,
                'fluency_score': fluency_score,
                'feedback': feedback,
                'audio_duration': audio_duration
            })
            
        except Exception as e:
            result['feedback'].append(f"❌ Error during practice: {str(e)}")
        
        return result

# Global instance
speech_practice = SpeechPractice() 