"""
Specialized agents for CallSense multi-agent system.
"""
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from models import CallTranscript, CallSummary, QAScore, SentimentType, CallCategory
import config
import json


class CallIntakeAgent:
    """Agent for processing initial call intake and validation."""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=config.MODEL_NAME,
            temperature=config.TEMPERATURE,
            openai_api_key=config.OPENAI_API_KEY
        )

    def process(self, raw_input: str) -> dict:
        """Process raw input and validate it's a call transcript."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a call intake specialist. Validate if the input is a valid call transcript and extract basic metadata."),
            ("user", "Analyze this input and determine if it's a valid call center transcript:\n\n{input}\n\nRespond with JSON containing: is_valid (boolean), reason (string), estimated_speakers (int)")
        ])

        response = self.llm.invoke(prompt.format_messages(input=raw_input))

        try:
            result = json.loads(response.content)
            return {
                "is_valid": result.get("is_valid", True),
                "reason": result.get("reason", "Valid transcript"),
                "estimated_speakers": result.get("estimated_speakers", 2),
                "transcript": raw_input
            }
        except:
            # Fallback if JSON parsing fails
            return {
                "is_valid": True,
                "reason": "Transcript accepted",
                "estimated_speakers": 2,
                "transcript": raw_input
            }


class TranscriptionAgent:
    """Agent for handling transcription (simplified - assumes text input)."""

    def process(self, intake_data: dict) -> CallTranscript:
        """Process transcription from intake data."""
        return CallTranscript(
            text=intake_data["transcript"],
            speaker_count=intake_data.get("estimated_speakers", 2),
            duration=None
        )


class SummarizationAgent:
    """Agent for generating structured summaries from transcripts."""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=config.MODEL_NAME,
            temperature=config.TEMPERATURE,
            openai_api_key=config.OPENAI_API_KEY
        )

    def process(self, transcript: CallTranscript) -> CallSummary:
        """Generate structured summary from transcript."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert call summarizer. Analyze the call transcript and provide a structured summary.

Respond ONLY with valid JSON in this exact format:
{{
    "key_points": ["point1", "point2", "point3"],
    "customer_issue": "brief description",
    "resolution": "how it was resolved",
    "sentiment": "positive" or "neutral" or "negative",
    "category": "complaint" or "inquiry" or "technical_support" or "billing" or "general",
    "action_items": ["action1", "action2"]
}}"""),
            ("user", "Transcript:\n\n{transcript}")
        ])

        response = self.llm.invoke(prompt.format_messages(transcript=transcript.text))

        try:
            data = json.loads(response.content)
            return CallSummary(
                key_points=data.get("key_points", ["No key points extracted"]),
                customer_issue=data.get("customer_issue", "Not identified"),
                resolution=data.get("resolution", "Not specified"),
                sentiment=SentimentType(data.get("sentiment", "neutral")),
                category=CallCategory(data.get("category", "general")),
                action_items=data.get("action_items", [])
            )
        except Exception as e:
            # Fallback summary if parsing fails
            return CallSummary(
                key_points=["Summary generation failed - using fallback"],
                customer_issue="Unable to parse",
                resolution="Unable to parse",
                sentiment=SentimentType.NEUTRAL,
                category=CallCategory.GENERAL,
                action_items=[]
            )


class QualityScoringAgent:
    """Agent for scoring call quality on multiple dimensions."""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=config.MODEL_NAME,
            temperature=config.TEMPERATURE,
            openai_api_key=config.OPENAI_API_KEY
        )

    def process(self, transcript: CallTranscript, summary: CallSummary) -> QAScore:
        """Score the call quality."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a call quality expert. Score this call on multiple dimensions (0-10 scale).

Respond ONLY with valid JSON in this exact format:
{{
    "empathy": 7.5,
    "professionalism": 8.0,
    "resolution": 6.5,
    "compliance": 9.0,
    "overall": 7.75
}}

Scoring guidelines:
- Empathy: Did the agent show understanding and care?
- Professionalism: Was communication clear and professional?
- Resolution: Was the issue effectively resolved?
- Compliance: Did the agent follow proper procedures?
- Overall: General quality of the interaction"""),
            ("user", "Transcript:\n{transcript}\n\nSummary:\nIssue: {issue}\nResolution: {resolution}\nSentiment: {sentiment}")
        ])

        response = self.llm.invoke(prompt.format_messages(
            transcript=transcript.text,
            issue=summary.customer_issue,
            resolution=summary.resolution,
            sentiment=summary.sentiment.value
        ))

        try:
            data = json.loads(response.content)
            return QAScore(
                empathy=float(data.get("empathy", 7.0)),
                professionalism=float(data.get("professionalism", 7.0)),
                resolution=float(data.get("resolution", 7.0)),
                compliance=float(data.get("compliance", 7.0)),
                overall=float(data.get("overall", 7.0))
            )
        except Exception as e:
            # Fallback scores
            return QAScore(
                empathy=7.0,
                professionalism=7.0,
                resolution=7.0,
                compliance=7.0,
                overall=7.0
            )


class RoutingAgent:
    """Agent for routing and generating recommendations."""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=config.MODEL_NAME,
            temperature=config.TEMPERATURE,
            openai_api_key=config.OPENAI_API_KEY
        )

    def process(self, summary: CallSummary, qa_scores: QAScore) -> dict:
        """Generate recommendations and tags based on analysis."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a call routing and improvement specialist. Based on the call analysis, provide recommendations and tags.

Respond ONLY with valid JSON in this exact format:
{{
    "recommendations": ["recommendation1", "recommendation2", "recommendation3"],
    "tags": ["tag1", "tag2", "tag3", "tag4"]
}}

Recommendations should be specific, actionable improvements for the agent or process.
Tags should be useful for categorization and searching."""),
            ("user", """Call Analysis:
Category: {category}
Sentiment: {sentiment}
Issue: {issue}
Resolution: {resolution}
Empathy Score: {empathy}/10
Professionalism Score: {professionalism}/10
Resolution Score: {resolution_score}/10
Compliance Score: {compliance}/10""")
        ])

        response = self.llm.invoke(prompt.format_messages(
            category=summary.category.value,
            sentiment=summary.sentiment.value,
            issue=summary.customer_issue,
            resolution=summary.resolution,
            empathy=qa_scores.empathy,
            professionalism=qa_scores.professionalism,
            resolution_score=qa_scores.resolution,
            compliance=qa_scores.compliance
        ))

        try:
            data = json.loads(response.content)
            return {
                "recommendations": data.get("recommendations", ["Continue current approach"]),
                "tags": data.get("tags", [summary.category.value, summary.sentiment.value])
            }
        except Exception as e:
            # Fallback
            return {
                "recommendations": ["Review call quality", "Follow up with customer"],
                "tags": [summary.category.value, summary.sentiment.value, "needs_review"]
            }

