"""
Pydantic models for structured data in CallSense.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class SentimentType(str, Enum):
    """Sentiment classification."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class CallCategory(str, Enum):
    """Call category types."""
    COMPLAINT = "complaint"
    INQUIRY = "inquiry"
    TECHNICAL_SUPPORT = "technical_support"
    BILLING = "billing"
    GENERAL = "general"


class QAScore(BaseModel):
    """Quality assurance scores for a call."""
    empathy: float = Field(ge=0, le=10, description="Empathy score (0-10)")
    professionalism: float = Field(ge=0, le=10, description="Professionalism score (0-10)")
    resolution: float = Field(ge=0, le=10, description="Resolution quality score (0-10)")
    compliance: float = Field(ge=0, le=10, description="Compliance score (0-10)")
    overall: float = Field(ge=0, le=10, description="Overall quality score (0-10)")

    @property
    def average_score(self) -> float:
        """Calculate average of all scores."""
        return (self.empathy + self.professionalism + self.resolution + self.compliance) / 4


class CallSummary(BaseModel):
    """Structured summary of a call."""
    key_points: List[str] = Field(description="Main points from the call")
    customer_issue: str = Field(description="Primary customer issue or request")
    resolution: str = Field(description="How the issue was resolved")
    sentiment: SentimentType = Field(description="Overall sentiment of the call")
    category: CallCategory = Field(description="Category of the call")
    action_items: List[str] = Field(default_factory=list, description="Follow-up actions needed")


class CallTranscript(BaseModel):
    """Structured transcript of a call."""
    text: str = Field(description="Full transcript text")
    speaker_count: Optional[int] = Field(default=2, description="Number of speakers")
    duration: Optional[str] = Field(default=None, description="Call duration")


class CallAnalysis(BaseModel):
    """Complete analysis of a call."""
    transcript: CallTranscript
    summary: CallSummary
    qa_scores: QAScore
    recommendations: List[str] = Field(description="Recommendations for improvement")
    tags: List[str] = Field(description="Tags for categorization and search")

