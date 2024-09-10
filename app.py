import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import requests
import json
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import uuid

# Load environment variables
load_dotenv()

# Initialize the OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

XI_API_KEY = os.getenv("ELEVENLABS_API_KEY")
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
            voice_id="o9HlFuTtE0sBJwrDEnVH",  # Adam pre-made voice
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
        
        audio_data = b"".join(chunk for chunk in response if chunk)
        return audio_data
    except Exception as e:
        st.error(f"Error generating audio: {str(e)}")
        return None

# Load environment variables
load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY environment variable not set")

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

st.title("Resume Hype Pitch Generator")

resume_text = st.text_area("Paste your resume text here")
job_description = st.text_area("Paste the job description here")

if st.button("Generate Hype Pitch") and resume_text and job_description:
    hype_pitch = generate_hype_pitch(resume_text, job_description)
    st.subheader("Your Hype Pitch:")
    st.write(hype_pitch)

    audio = text_to_speech(hype_pitch)
    if audio:
        st.audio(audio, format="audio/mp3")
    else:
        st.error("Failed to generate audio")
