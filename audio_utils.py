"""
Audio transcription utilities for CallSense.
"""
from openai import OpenAI
import config
import tempfile
import os


def transcribe_audio(audio_file_path: str) -> str:
    """
    Transcribe audio file using OpenAI Whisper API.

    Args:
        audio_file_path: Path to the audio file

    Returns:
        Transcribed text
    """
    client = OpenAI(api_key=config.OPENAI_API_KEY)

    try:
        with open(audio_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model=config.WHISPER_MODEL,
                file=audio_file,
                response_format="text"
            )
        return transcript
    except Exception as e:
        raise Exception(f"Audio transcription failed: {str(e)}")


def save_uploaded_audio(uploaded_file) -> str:
    """
    Save uploaded audio file to temporary location.

    Args:
        uploaded_file: Streamlit uploaded file object

    Returns:
        Path to saved temporary file
    """
    # Create temporary file with the same extension
    suffix = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        return tmp_file.name


def cleanup_temp_file(file_path: str):
    """
    Clean up temporary file.

    Args:
        file_path: Path to temporary file
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass  # Ignore cleanup errors
