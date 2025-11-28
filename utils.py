"""
Utility functions for CallSense.
"""
from models import QAScore
import config


def get_score_color(score: float) -> str:
    """
    Get color code for a score.

    Args:
        score: Score value (0-10)

    Returns:
        Color string for Streamlit
    """
    if score >= config.EXCELLENT_THRESHOLD:
        return "green"
    elif score >= config.GOOD_THRESHOLD:
        return "orange"
    else:
        return "red"


def get_score_label(score: float) -> str:
    """
    Get label for a score.

    Args:
        score: Score value (0-10)

    Returns:
        Label string
    """
    if score >= config.EXCELLENT_THRESHOLD:
        return "Excellent"
    elif score >= config.GOOD_THRESHOLD:
        return "Good"
    elif score >= config.NEEDS_IMPROVEMENT_THRESHOLD:
        return "Needs Improvement"
    else:
        return "Poor"


def format_score_display(score: float) -> str:
    """
    Format score for display.

    Args:
        score: Score value

    Returns:
        Formatted string
    """
    return f"{score:.1f}/10"


def load_sample_transcript() -> str:
    """Load a sample transcript for demo purposes."""
    return """Agent: Thank you for calling TechSupport Plus. My name is Sarah. How may I help you today?

Customer: Hi Sarah, I'm having trouble with my internet connection. It keeps dropping every few minutes.

Agent: I'm sorry to hear you're experiencing issues with your internet connection. I understand how frustrating that can be, especially if you're working from home or streaming. Let me help you resolve this right away.

Customer: Yes, exactly! I have an important video meeting in an hour and I really need this fixed.

Agent: I completely understand the urgency. Let's troubleshoot this together. First, can you tell me what type of modem you have?

Customer: It's the one you provided, the XR500 model.

Agent: Perfect, thank you. Let me check your connection status from our end. I can see there have been some intermittent drops in the past 24 hours. Let's try a few things. First, could you unplug your modem for about 30 seconds and then plug it back in?

Customer: Okay, doing that now... Alright, it's back on and the lights are stabilizing.

Agent: Great! Now, can you try connecting to the internet and let me know if it's stable?

Customer: Yes! It seems to be working now. The connection feels faster too.

Agent: Wonderful! I'm glad we could resolve this quickly. I've also applied a firmware update to your modem remotely which should prevent this issue from happening again. Is there anything else I can help you with today?

Customer: No, that's perfect. Thank you so much for your help, Sarah. You've been really patient and helpful.

Agent: You're very welcome! I'm happy I could help. If you experience any issues before your meeting, please don't hesitate to call us back. Have a great day and good luck with your meeting!

Customer: Thank you! You too. Goodbye.

Agent: Goodbye!"""

