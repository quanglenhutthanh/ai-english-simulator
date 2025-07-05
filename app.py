import streamlit as st
import time
from conversation_generator import get_response
from tts_generator import conversation_to_speech
from generate_speak import conversation_to_speech_fairseq
from speech_practice import speech_practice
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

# Voice Selection (only show if using gTTS)
if tts_engine == "Google TTS (gTTS)":
    col1, col2 = st.columns(2)
    with col1:
        voice_a = st.selectbox(
            "🎤 Speaker A Voice",
            ["default", "british", "australian", "indian", "irish", "canadian", "south_african"],
            help="Choose voice for Speaker A"
        )
    with col2:
        voice_b = st.selectbox(
            "🎤 Speaker B Voice", 
            ["british", "default", "australian", "indian", "irish", "canadian", "south_african"],
            index=1,
            help="Choose voice for Speaker B"
        )
else:
    voice_a = "default"
    voice_b = "british"

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
            audio_segments = conversation_to_speech(st.session_state['conversation'], voice_a, voice_b)
        else:  # Fairseq TTS
            audio_segments = conversation_to_speech_fairseq(st.session_state['conversation'])
        
        if audio_segments:
            st.markdown(f"### 🔊 Audio Playback ({tts_engine})")
            
            for i, segment in enumerate(audio_segments):
                # Convert audio data to base64 for HTML audio player
                audio_b64 = base64.b64encode(segment['audio']).decode()
                audio_html = f"""
                <audio controls style="width: 100%; margin: 10px 0;">
                    <source src="data:audio/wav;base64,{audio_b64}" type="audio/wav">
                    Your browser does not support the audio element.
                </audio>
                """
                st.markdown(audio_html, unsafe_allow_html=True)
                
                # Display the text after the audio player
                st.markdown(f"**{segment['text']}**")
                
                # Add a small delay between segments for better UX
                if i < len(audio_segments) - 1:
                    st.markdown("---")
        else:
            st.error(f"Failed to generate speech using {tts_engine}. Please try again.")

# Speech Practice Section
if 'conversation' in st.session_state:
    st.markdown("---")
    st.markdown("### 🎤 Practice Speaking")
    st.info("Click 'Practice' next to any line to record your speech and get feedback!")
    
    # Initialize practice states if not exists
    if 'practice_states' not in st.session_state:
        st.session_state.practice_states = {}
    
    for i, line in enumerate(st.session_state['conversation']):
        # Extract just the text part for practice
        practice_text = line.strip()
        if ': ' in practice_text:
            practice_text = practice_text.split(': ', 1)[1]
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**{line}**")
        
        with col2:
            practice_key = f"practice_{i}"
            
            # Check if practice is active for this line
            is_practicing = st.session_state.practice_states.get(practice_key, False)
            
            if not is_practicing:
                if st.button(f"🎤 Practice", key=practice_key):
                    st.session_state.practice_states[practice_key] = True
                    st.rerun()
            else:
                # Practice mode is active
                st.markdown(f"**Practice this line:** {practice_text}")
                st.info("🎤 Click 'Start Recording' and speak clearly...")
                
                if st.button("🎙️ Start Recording", key=f"record_{i}"):
                    with st.spinner("🎤 Recording your speech..."):
                        result = speech_practice.practice_line(practice_text)
                    
                    if result['success']:
                        # Display results
                        st.success("✅ Speech recorded successfully!")
                        
                        # Scores
                        col_score1, col_score2 = st.columns(2)
                        with col_score1:
                            st.metric("Pronunciation", f"{result['pronunciation_score']}/100")
                        with col_score2:
                            st.metric("Fluency", f"{result['fluency_score']}/100")
                        
                        # What you said
                        st.markdown(f"**You said:** {result['user_text']}")
                        st.markdown(f"**Expected:** {practice_text}")
                        
                        # Feedback
                        st.markdown("**Feedback:**")
                        for feedback in result['feedback']:
                            st.markdown(f"• {feedback}")
                        
                        # Overall score
                        overall_score = (result['pronunciation_score'] + result['fluency_score']) / 2
                        if overall_score >= 80:
                            st.success(f"🎉 Overall Score: {overall_score:.1f}/100 - Great job!")
                        elif overall_score >= 60:
                            st.warning(f"📈 Overall Score: {overall_score:.1f}/100 - Keep practicing!")
                        else:
                            st.error(f"📚 Overall Score: {overall_score:.1f}/100 - More practice needed!")
                    
                    else:
                        st.error("❌ Failed to record speech. Please try again.")
                        for feedback in result['feedback']:
                            st.markdown(f"• {feedback}")
                
                # Add a button to exit practice mode
                if st.button("❌ Exit Practice", key=f"exit_{i}"):
                    st.session_state.practice_states[practice_key] = False
                    st.rerun()
        
        # Add separator between lines
        if i < len(st.session_state['conversation']) - 1:
            st.markdown("---")

