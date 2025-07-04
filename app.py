import streamlit as st
import time
from conversation_generator import get_response
from tts_generator import conversation_to_speech
from generate_speak import conversation_to_speech_fairseq
import base64

# Page config
st.set_page_config(page_title="AI English Conversation Simulator", layout="centered")

# Title
st.title("🗣️ AI English Conversation Simulator")

# TTS Engine Selection
tts_engine = st.selectbox(
    "🔊 Choose TTS Engine", 
    ["Google TTS (gTTS)", "Fairseq TTS (Local)"],
    help="Google TTS: Cloud-based, high quality. Fairseq TTS: Local, works offline."
)

user_requirement = st.text_area(
    "📝 Enter your conversation requirement",
    height=100
)

# Simulate speaking UI
col1, col2 = st.columns(2)

with col1:
    generate_conv = st.button("🎬 Generate Conversation")
with col2:
    generate_speech = st.button("🔊 Generate Speech")

if generate_conv:
    prompt = f"{user_requirement}\n Format as alternating lines for two speakers, e.g., 'A: ...', 'B: ...'."
    conversation_text = get_response(prompt)
    if not conversation_text:
        st.error("No response from the AI. Please check your API settings or try again.")
    else:
        conversation_lines = conversation_text.strip().split('\n')
        st.markdown("### 💬 Conversation")
        for line in conversation_lines:
            st.markdown(f"**{line}**")
        st.session_state['conversation'] = conversation_lines

# Generate Speech Button
if 'conversation' in st.session_state and generate_speech:
    with st.spinner(f"🗣️ Generating speech using {tts_engine}..."):
        if tts_engine == "Google TTS (gTTS)":
            audio_segments = conversation_to_speech(st.session_state['conversation'])
        else:  # Fairseq TTS
            audio_segments = conversation_to_speech_fairseq(st.session_state['conversation'])
        
        if audio_segments:
            st.markdown(f"### 🔊 Audio Playback ({tts_engine})")
            
            for i, segment in enumerate(audio_segments):
                st.markdown(f"**{segment['text']}**")
                
                # Convert audio data to base64 for HTML audio player
                audio_b64 = base64.b64encode(segment['audio']).decode()
                audio_html = f"""
                <audio controls style="width: 100%; margin: 10px 0;">
                    <source src="data:audio/wav;base64,{audio_b64}" type="audio/wav">
                    Your browser does not support the audio element.
                </audio>
                """
                st.markdown(audio_html, unsafe_allow_html=True)
                
                # Add a small delay between segments for better UX
                if i < len(audio_segments) - 1:
                    st.markdown("---")
        else:
            st.error(f"Failed to generate speech using {tts_engine}. Please try again.")

