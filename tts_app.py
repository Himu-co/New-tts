import os
import json
import streamlit as st
from google.cloud import texttospeech

# Function to load and validate credentials
def load_credentials():
    try:
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not credentials_path:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")

        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"Credentials file not found at: {credentials_path}")

        # Check if the file is readable
        with open(credentials_path, "r") as file:
            content = file.read().strip()
            if not content:
                raise ValueError("Credentials file is empty!")
            credentials = json.loads(content)

        # Write credentials to a temporary file
        with open("service_account_temp.json", "w") as temp_file:
            json.dump(credentials, temp_file)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service_account_temp.json"

    except (FileNotFoundError, ValueError, json.JSONDecodeError, PermissionError) as e:
        st.error(f"Failed to load credentials: {e}")
        st.stop()

# Initialize Google Cloud Text-to-Speech client
def initialize_client():
    return texttospeech.TextToSpeechClient()

# Fetch available voices
def get_voice_options(client):
    voices = client.list_voices().voices
    voice_options = {"English": [], "Bengali": []}
    for voice in voices:
        if any(code.startswith("en-") for code in voice.language_codes):
            voice_options["English"].append(voice.name)
        if any(code.startswith("bn-") for code in voice.language_codes):
            voice_options["Bengali"].append(voice.name)
    return voice_options

# Streamlit App
def main():
    st.title("Text-to-Speech Converter")
    load_credentials()
    client = initialize_client()

    # Get available voices
    voice_options = get_voice_options(client)

    # User inputs
    st.subheader("Input Text")
    text_input = st.text_area("Enter text to convert to speech:")

    st.subheader("Voice Options")
    language = st.selectbox("Select Language", ["English", "Bengali"])
    if voice_options[language]:
        voice = st.selectbox("Select Voice", voice_options[language])
    else:
        st.warning(f"No voices available for {language}. Please check your Google Cloud setup.")
        return

    if st.button("Convert to Speech"):
        if text_input.strip():
            # Dynamically get the correct language code for the selected voice
            selected_voice = next(
                (v for v in client.list_voices().voices if v.name == voice), None
            )
            if not selected_voice:
                st.error("Selected voice not found. Please select a valid voice.")
                return

            voice_language_code = selected_voice.language_codes[0]  # Use the first language code
            synthesis_input = texttospeech.SynthesisInput(text=text_input)
            voice_params = texttospeech.VoiceSelectionParams(
                language_code=voice_language_code, name=voice
            )
            audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
            response = client.synthesize_speech(
                input=synthesis_input, voice=voice_params, audio_config=audio_config
            )

            # Save MP3 file
            output_path = "output.mp3"
            with open(output_path, "wb") as out:
                out.write(response.audio_content)

            # Display audio player and download link
            st.audio(output_path, format="audio/mp3", start_time=0)
            with open(output_path, "rb") as file:
                st.download_button(
                    label="Download MP3",
                    data=file,
                    file_name="output.mp3",
                    mime="audio/mp3",
                )
        else:
            st.warning("Please enter text to convert.")

if __name__ == "__main__":
    main()
