import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import base64
import time
import tempfile

# Load environment variables
load_dotenv()

# Initialize the OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize the ElevenLabs client
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY environment variable not set")
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

VOICE_ID = "o9HlFuTtE0sBJwrDEnVH"  # Josh voice ID

def generate_hype_pitch(resume_text, job_description):
    prompt = f"""
    Resume:
    {resume_text}

    Job Description:
    {job_description}

    Generate a concise 2 to 3 sentence hype statement that powerfully conveys why the candidate is awesome and why the company should hire them. Focus on their most impressive skills, experiences, or achievements that make them stand out for this specific role. Refer to them as you and not by name.
    """

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a motivational hype man and career coach. Your goal is to boost candidates' confidence before job interviews by highlighting their strengths and unique qualifications."},
            {"role": "user", "content": prompt},
            {"role": "user", "content": "always end the hype with strong encouragement to the user to go out and get the job."}
        ],
        max_tokens=500,
        n=1,
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()

def text_to_speech(text: str) -> bytes:
    try:
        response = client.text_to_speech.convert(
            voice_id=VOICE_ID,
            optimize_streaming_latency="0",
            output_format="mp3_44100_128",
            text=text,
            model_id="eleven_turbo_v2",
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.75,
                style=0.0,
                use_speaker_boost=True,
            ),
        )
        
        return b"".join(chunk for chunk in response if chunk)
    except Exception as e:
        st.error(f"Error generating audio: {str(e)}")
        return None

def get_audio_html(audio_data):
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    audio_tag = f'<audio controls autoplay><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
    return audio_tag

st.title("Resume Hype Pitch Generator")

resume_text = st.text_area("Paste your resume text here")
job_description = st.text_area("Paste the job description here")

if st.button("Generate Hype Pitch") and resume_text and job_description:
    hype_pitch = generate_hype_pitch(resume_text, job_description)
    st.subheader("Your Hype Pitch:")
    st.write(hype_pitch)

    audio_data = text_to_speech(hype_pitch)
    if audio_data:
        # Add a small delay
        time.sleep(1)
        
        # Use custom HTML5 audio player
        st.markdown(get_audio_html(audio_data), unsafe_allow_html=True)
        
        # Provide download button
        st.download_button(
            label="Download Audio",
            data=audio_data,
            file_name=f"hype_pitch_{int(time.time())}.mp3",
            mime="audio/mpeg"
        )
    else:
        st.error("Failed to generate audio")
