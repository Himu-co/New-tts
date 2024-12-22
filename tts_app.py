import os
import json
from google.cloud import texttospeech
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env
def initialize_client():
    credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if not credentials_json:
        raise ValueError("Environment variable GOOGLE_APPLICATION_CREDENTIALS_JSON is not set!")
   
    # Write the credentials to a temporary file
    credentials_path = "/tmp/service_account_temp.json"
    with open(credentials_path, "w") as f:
        f.write(credentials_json)
    
    # Set the environment variable for the Google API client
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
    
    return texttospeech.TextToSpeechClient()


def main():
    """Streamlit app main function."""
    st.title("Text-to-Speech Converter")
    st.write("Convert your text to speech using Google Cloud Text-to-Speech API.")

    # Initialize client
    try:
        client = initialize_client()
    except ValueError as e:
        st.error(str(e))
        return

    # Input text
    text = st.text_area("Enter text to convert to speech:", "Hello, welcome to the Text-to-Speech app!")

    # Select language and voice
    languages = ["en-US", "en-GB", "bn-IN"]
    language_code = st.selectbox("Select language:", languages)

    voices = {
        "en-US": ["en-US-Standard-B", "en-US-Wavenet-D"],
        "en-GB": ["en-GB-Standard-A", "en-GB-Wavenet-B"],
        "bn-IN": ["bn-IN-Standard-A"]
    }

    voice_name = st.selectbox("Select voice:", voices[language_code])

    # Synthesize speech
    if st.button("Convert to Speech"):
        try:
            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice_params = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                name=voice_name
            )
            audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

            response = client.synthesize_speech(
                input=synthesis_input, voice=voice_params, audio_config=audio_config
            )

            # Save and provide download link
            output_path = "output.mp3"
            with open(output_path, "wb") as output_file:
                output_file.write(response.audio_content)

            st.audio(output_path, format="audio/mp3")
            st.success("Speech synthesis complete! Use the audio player above.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
