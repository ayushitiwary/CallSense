"""
Streamlit UI for CallSense - Call Center Intelligence System
"""
import streamlit as st
import sys
from graph import process_call
from models import CallAnalysis
from utils import get_score_color, get_score_label, format_score_display, load_sample_transcript
from audio_utils import transcribe_audio, save_uploaded_audio, cleanup_temp_file
import config

# Page configuration
st.set_page_config(
    page_title="CallSense - Call Center Intelligence",
    page_icon="📞",
    layout="wide"
)

# Initialize session state variables
if 'transcript_input' not in st.session_state:
    st.session_state['transcript_input'] = ""
if 'sample_loaded' not in st.session_state:
    st.session_state['sample_loaded'] = False

# Title and description
st.title("📞 CallSense - Call Center Intelligence")
st.markdown("""
AI-powered multi-agent system for call transcription, summarization, and quality analysis.
**Upload an audio file** or paste a call transcript to get instant insights, QA scores, and recommendations.
""")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    # API Key check
    if not config.OPENAI_API_KEY:
        st.error("⚠️ OpenAI API Key not found!")
        st.info("Please set your OPENAI_API_KEY in a .env file or environment variable.")
        st.stop()
    else:
        st.success("✅ API Key configured")

    st.markdown("---")
    st.header("📊 About")
    st.markdown("""
    **CallSense** uses 5 specialized agents:
    - 🎯 **Call Intake**: Validates transcripts
    - 🎧 **Transcription**: Audio-to-text with Whisper
    - 📋 **Summarization**: Extracts key insights
    - ⭐ **Quality Scoring**: Evaluates performance
    - 🔀 **Routing**: Generates recommendations

    **Supported Audio Formats:**
    MP3, MP4, M4A, WAV, WebM
    """)

# Main content area
col1, col2 = st.columns([2, 1])

with col2:
    st.subheader("💡 Quick Actions")
    if st.button("📄 Load Sample Transcript", use_container_width=True):
        st.session_state['transcript_input'] = load_sample_transcript()
        st.session_state['sample_loaded'] = True
        st.rerun()

    if st.button("🗑️ Clear All", use_container_width=True):
        st.session_state['transcript_input'] = ""
        st.session_state['sample_loaded'] = False
        if 'analysis_result' in st.session_state:
            del st.session_state['analysis_result']
        if 'transcribed_audio' in st.session_state:
            del st.session_state['transcribed_audio']
        st.rerun()

with col1:
    st.subheader("📝 Input Call Data")

    # Show success message if sample was just loaded
    if st.session_state.get('sample_loaded', False):
        st.success("✅ Sample transcript loaded! Please switch to the '📝 Paste Transcript' tab to see it.")
        st.session_state['sample_loaded'] = False  # Clear the flag

    # Add tabs for audio upload vs text input
    tab1, tab2 = st.tabs(["🎤 Upload Audio", "📝 Paste Transcript"])

    with tab1:
        st.markdown("Upload an audio file of the call recording")
        audio_file = st.file_uploader(
            "Choose an audio file",
            type=['mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm'],
            help="Supported formats: MP3, MP4, MPEG, M4A, WAV, WebM"
        )

        if audio_file is not None:
            st.audio(audio_file, format=f'audio/{audio_file.type.split("/")[-1]}')
            st.info(f"📁 File: {audio_file.name} ({audio_file.size / 1024:.1f} KB)")

    with tab2:
        # Text area for transcript input
        transcript_text = st.text_area(
            "Paste your call transcript here:",
            value=st.session_state['transcript_input'],
            height=300,
            placeholder="Paste a call center transcript here...\n\nExample:\nAgent: Hello, how can I help you today?\nCustomer: I have a problem with my order..."
        )

        # Update session state only when text changes
        if transcript_text != st.session_state['transcript_input']:
            st.session_state['transcript_input'] = transcript_text

        # Show helpful message if sample is loaded
        if st.session_state['transcript_input'].startswith("Agent: Thank you for calling TechSupport Plus"):
            st.info("✅ Sample transcript loaded! Click 'Analyze Call' to process it.")

    # Process button
    if st.button("🚀 Analyze Call", type="primary", use_container_width=True):
        transcript_to_process = None
        temp_file_path = None

        # Check which input method was used
        if audio_file is not None:
            # Process audio file
            with st.spinner("🎧 Transcribing audio file..."):
                try:
                    temp_file_path = save_uploaded_audio(audio_file)
                    transcript_to_process = transcribe_audio(temp_file_path)
                    st.success(f"✅ Audio transcribed successfully!")

                    # Store the transcribed text in session state so it persists
                    st.session_state['transcribed_audio'] = transcript_to_process

                    # Show the transcribed text
                    with st.expander("📄 View Transcribed Text"):
                        st.text_area("Transcription:", transcript_to_process, height=150, disabled=True)

                except Exception as e:
                    st.error(f"❌ Transcription Error: {str(e)}")
                    if temp_file_path:
                        cleanup_temp_file(temp_file_path)
        elif transcript_text and transcript_text.strip():
            # Use text input
            transcript_to_process = transcript_text
            # Clear transcribed audio if using text input
            if 'transcribed_audio' in st.session_state:
                del st.session_state['transcribed_audio']
        else:
            st.error("⚠️ Please upload an audio file or enter a transcript first!")

        # Process the transcript if we have one
        if transcript_to_process:
            with st.spinner("🔄 Processing call through multi-agent system..."):
                try:
                    result = process_call(transcript_to_process)

                    if isinstance(result, dict) and "error" in result:
                        st.error(f"❌ Error: {result['error']}")
                    else:
                        st.session_state['analysis_result'] = result
                        st.session_state['last_transcript'] = transcript_to_process
                        st.success("✅ Analysis complete!")
                        st.rerun()
                finally:
                    # Clean up temp file
                    if temp_file_path:
                        cleanup_temp_file(temp_file_path)

# Display results if available
if 'analysis_result' in st.session_state:
    analysis = st.session_state['analysis_result']

    if isinstance(analysis, CallAnalysis):
        st.markdown("---")
        st.header("📊 Analysis Results")

        # Show transcribed audio text if it exists
        if 'transcribed_audio' in st.session_state:
            with st.expander("📄 View Transcribed Text", expanded=False):
                st.text_area(
                    "Audio Transcription:",
                    st.session_state['transcribed_audio'],
                    height=150,
                    disabled=True,
                    key='transcribed_display'
                )

        # Summary Section
        st.subheader("📋 Call Summary")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Category", analysis.summary.category.value.replace("_", " ").title())
        with col2:
            sentiment_emoji = {
                "positive": "😊",
                "neutral": "😐",
                "negative": "😞"
            }
            st.metric(
                "Sentiment",
                f"{sentiment_emoji.get(analysis.summary.sentiment.value, '')} {analysis.summary.sentiment.value.title()}"
            )
        with col3:
            st.metric("Speakers", analysis.transcript.speaker_count or 2)

        # Key details
        st.markdown("**Customer Issue:**")
        st.info(analysis.summary.customer_issue)

        st.markdown("**Resolution:**")
        st.success(analysis.summary.resolution)

        # Key Points
        st.markdown("**Key Points:**")
        for i, point in enumerate(analysis.summary.key_points, 1):
            st.markdown(f"{i}. {point}")

        # Action Items
        if analysis.summary.action_items:
            st.markdown("**Action Items:**")
            for item in analysis.summary.action_items:
                st.markdown(f"- ✓ {item}")

        # QA Scores Section
        st.markdown("---")
        st.subheader("⭐ Quality Assurance Scores")

        # Overall score highlight
        overall_color = get_score_color(analysis.qa_scores.overall)
        overall_label = get_score_label(analysis.qa_scores.overall)

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                "Overall Score",
                format_score_display(analysis.qa_scores.overall),
                delta=overall_label
            )

        with col2:
            st.metric(
                "Empathy",
                format_score_display(analysis.qa_scores.empathy)
            )

        with col3:
            st.metric(
                "Professionalism",
                format_score_display(analysis.qa_scores.professionalism)
            )

        with col4:
            st.metric(
                "Resolution",
                format_score_display(analysis.qa_scores.resolution)
            )

        with col5:
            st.metric(
                "Compliance",
                format_score_display(analysis.qa_scores.compliance)
            )

        # Score visualization
        st.markdown("**Score Breakdown:**")
        scores_data = {
            "Empathy": analysis.qa_scores.empathy,
            "Professionalism": analysis.qa_scores.professionalism,
            "Resolution": analysis.qa_scores.resolution,
            "Compliance": analysis.qa_scores.compliance
        }

        for label, score in scores_data.items():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.write(f"**{label}**")
            with col2:
                st.progress(score / 10)
                st.caption(f"{score:.1f}/10 - {get_score_label(score)}")

        # Recommendations Section
        st.markdown("---")
        st.subheader("💡 Recommendations")

        for i, rec in enumerate(analysis.recommendations, 1):
            st.markdown(f"{i}. {rec}")

        # Tags Section
        st.markdown("---")
        st.subheader("🏷️ Tags")

        tag_cols = st.columns(len(analysis.tags) if len(analysis.tags) > 0 else 1)
        for idx, tag in enumerate(analysis.tags):
            with tag_cols[idx % len(tag_cols)]:
                st.markdown(f"`{tag}`")

        # Export Section
        st.markdown("---")
        st.subheader("📥 Export Results")

        export_data = {
            "summary": {
                "category": analysis.summary.category.value,
                "sentiment": analysis.summary.sentiment.value,
                "customer_issue": analysis.summary.customer_issue,
                "resolution": analysis.summary.resolution,
                "key_points": analysis.summary.key_points,
                "action_items": analysis.summary.action_items
            },
            "qa_scores": {
                "overall": analysis.qa_scores.overall,
                "empathy": analysis.qa_scores.empathy,
                "professionalism": analysis.qa_scores.professionalism,
                "resolution": analysis.qa_scores.resolution,
                "compliance": analysis.qa_scores.compliance
            },
            "recommendations": analysis.recommendations,
            "tags": analysis.tags
        }

        import json
        st.download_button(
            label="📥 Download Analysis (JSON)",
            data=json.dumps(export_data, indent=2),
            file_name="call_analysis.json",
            mime="application/json",
            use_container_width=True
        )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>CallSense v1.0 - Built with LangChain, LangGraph, and Streamlit</div>",
    unsafe_allow_html=True
)
