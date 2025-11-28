"""
Configuration file for CallSense application.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Model Configuration
MODEL_NAME = "gpt-3.5-turbo"
WHISPER_MODEL = "whisper-1"
TEMPERATURE = 0.7

# QA Scoring Thresholds
EXCELLENT_THRESHOLD = 8.0
GOOD_THRESHOLD = 6.0
NEEDS_IMPROVEMENT_THRESHOLD = 4.0
