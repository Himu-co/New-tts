import os
import json
from google.cloud import texttospeech
import streamlit as st

# Load credentials from environment variable
def load_credentials():
    credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_json:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set or empty!")

    try:
        # Parse JSON credentials
        credentials = json.loads(credentials_json)
    except json.JSONDecodeError as e:
        st.error("Failed to parse JSON credentials: " + str(e))
        raise e

    # Write to temporary file for Google SDK
    credentials_path = "/tmp/service_account_temp.json"
    with open(credentials_path, "w") as temp_file:
        json.dump(credentials, temp_file)

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
    st.write(f"Credentials loaded to: {credentials_path}")

# Initialize the Google TTS client
def initialize_client():
    load_credentials()
    return texttospeech.TextToSpeechClient()

# Main function
def main():
    st.title("Text-to-Speech Converter")
    st.write("Convert your text to speech using Google Cloud Text-to-Speech API.")

    client = initialize_client()

    # Input Text
    text = st.text_area("Enter text to convert to speech", "")
    if not text:
        st.warning("Please enter some text.")
        return

    # Language Selection
    language = st.selectbox("Select Language", ["en-US", "bn-BD"])

    # Voice Selection
    voices = client.list_voices()
    available_voices = [
        voice.name for voice in voices.voices if language in voice.language_codes
    ]
    voice_name = st.selectbox("Select Voice", available_voices)

    # Synthesize Speech
    if st.button("Convert to Speech"):
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice_params = texttospeech.VoiceSelectionParams(
            language_code=language, name=voice_name
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

        try:
            response = client.synthesize_speech(
                input=synthesis_input, voice=voice_params, audio_config=audio_config
            )
            audio_file = "output.mp3"
            with open(audio_file, "wb") as out:
                out.write(response.audio_content)
            st.audio(audio_file, format="audio/mp3")
            st.success("Speech conversion successful!")
        except Exception as e:
            st.error("Error during speech synthesis: " + str(e))

if __name__ == "__main__":
    main()
