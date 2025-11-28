# CallSense - Call Center Intelligence System

AI-powered multi-agent system for call transcription, summarization, and quality analysis.

## Overview

CallSense is an intelligent call center analysis platform that processes call transcripts through a multi-agent workflow to provide comprehensive insights, quality scores, and actionable recommendations.

## Architecture

### Multi-Agent System

CallSense uses **LangGraph** to orchestrate 5 specialized agents in a sequential workflow:

1. **Call Intake Agent** - Validates and processes raw input
2. **Transcription Agent** - Handles transcript structuring
3. **Summarization Agent** - Extracts key insights and context
4. **Quality Scoring Agent** - Evaluates call performance
5. **Routing Agent** - Generates recommendations and tags

### Workflow

```
Raw Input → Intake → Transcription → Summarization → Quality Scoring → Routing → Analysis Output
```

The workflow uses conditional edges to handle validation failures gracefully.

### AI Models

- **LLM**: OpenAI GPT-3.5-turbo (configurable)
- **Audio Transcription**: OpenAI Whisper API
- **Framework**: LangChain + LangGraph

### Data Models

Built with Pydantic for type safety and validation:

- **CallTranscript** - Structured transcript data
- **CallSummary** - Key points, issue, resolution, sentiment, category
- **QAScore** - Empathy, professionalism, resolution, compliance scores
- **CallAnalysis** - Complete analysis output

### Key Components

#### Agents (`agents.py`)
- `CallIntakeAgent` - Input validation with LLM
- `TranscriptionAgent` - Transcript processing
- `SummarizationAgent` - AI-powered summarization
- `QualityScoringAgent` - Multi-dimensional QA scoring
- `RoutingAgent` - Recommendation generation

#### Graph (`graph.py`)
- LangGraph workflow orchestration
- State management between agents
- Error handling and recovery

#### Models (`models.py`)
- `SentimentType` - positive/neutral/negative
- `CallCategory` - complaint/inquiry/technical_support/billing/general
- Structured Pydantic models for all data

#### UI (`app.py`)
- Streamlit web interface
- Audio file upload support
- Real-time transcript analysis
- Visual dashboards for results

#### Audio Processing (`audio_utils.py`)
- OpenAI Whisper integration
- Audio file handling
- Format support: MP3, MP4, M4A, WAV, WebM

## Features

- 🎤 **Audio Transcription** - Upload audio files for automatic transcription
- 📝 **Text Input** - Paste existing transcripts for analysis
- 📊 **Quality Scoring** - Multi-dimensional QA metrics (0-10 scale)
- 🎯 **Smart Categorization** - Automatic call classification
- 😊 **Sentiment Analysis** - Emotional tone detection
- 💡 **Recommendations** - AI-generated improvement suggestions
- 🏷️ **Auto-Tagging** - Searchable tags for organization
- 📥 **Export** - Download results as JSON

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd CallSense
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_actual_api_key_here
```

**Required Configuration:**
- `OPENAI_API_KEY` - Your OpenAI API key (get one at https://platform.openai.com)

**Optional Configuration:**
- `OPENAI_MODEL` - Model to use (default: gpt-4o-mini)
- `OPENAI_TEMPERATURE` - Response creativity (default: 0.3)
- `MAX_AUDIO_SIZE_MB` - Maximum audio file size (default: 25)
- See `.env.example` for all available options

## Usage

### Run the Streamlit App

```bash
python3 -m streamlit run app.py
```

### Programmatic Usage

```python
from graph import process_call

transcript = """
Agent: Hello, how can I help you today?
Customer: I have a problem with my order...
"""

result = process_call(transcript)
print(result.summary.customer_issue)
print(result.qa_scores.overall)
```

## Configuration

Edit `config.py` to customize:

- **MODEL_NAME** - LLM model (default: gpt-3.5-turbo)
- **TEMPERATURE** - Creativity level (default: 0.7)
- **WHISPER_MODEL** - Transcription model (default: whisper-1)
- **QA Thresholds** - Score rating boundaries

## Quality Metrics

Calls are scored on 4 dimensions (0-10 scale):

- **Empathy** - Understanding and care shown
- **Professionalism** - Communication quality
- **Resolution** - Issue handling effectiveness
- **Compliance** - Adherence to procedures

**Overall Score** = Average of all dimensions

## Tech Stack

- **LangChain** - LLM framework
- **LangGraph** - Multi-agent orchestration
- **OpenAI** - GPT-3.5-turbo & Whisper
- **Streamlit** - Web UI
- **Pydantic** - Data validation
- **Python 3.8+**

## Project Structure

```
CallSense/
├── app.py              # Streamlit UI
├── graph.py            # LangGraph workflow
├── agents.py           # Specialized agents
├── models.py           # Pydantic data models
├── config.py           # Configuration
├── audio_utils.py      # Audio processing
├── utils.py            # Helper functions
├── requirements.txt    # Dependencies
└── test_system.py      # Test suite
```

## Requirements

- Python 3.8+
- OpenAI API key
- Dependencies listed in `requirements.txt`

## License

[Add your license here]

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
