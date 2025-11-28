"""
Test script for CallSense system.
Run this to verify all components are working correctly.
"""
import sys
from graph import process_call
from utils import load_sample_transcript
import config


def test_system():
    """Test the CallSense system end-to-end."""

    print("=" * 60)
    print("CallSense System Test")
    print("=" * 60)

    # Check API key
    print("\n1. Checking API key configuration...")
    if not config.OPENAI_API_KEY:
        print("❌ FAILED: OpenAI API key not found!")
        print("Please set OPENAI_API_KEY in your .env file or environment.")
        return False
    else:
        print("✅ PASSED: API key configured")

    # Load sample transcript
    print("\n2. Loading sample transcript...")
    try:
        transcript = load_sample_transcript()
        print(f"✅ PASSED: Loaded transcript ({len(transcript)} characters)")
        print(f"Preview: {transcript[:100]}...")
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

    # Process call
    print("\n3. Processing call through multi-agent system...")
    print("   This may take 30-60 seconds...")

    try:
        result = process_call(transcript)

        if isinstance(result, dict) and "error" in result:
            print(f"❌ FAILED: {result['error']}")
            return False

        print("✅ PASSED: Call processed successfully")

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

    # Verify results
    print("\n4. Verifying analysis results...")

    try:
        # Check transcript
        if not result.transcript or not result.transcript.text:
            print("❌ FAILED: Transcript missing")
            return False
        print("✅ Transcript: OK")

        # Check summary
        if not result.summary:
            print("❌ FAILED: Summary missing")
            return False
        print(f"✅ Summary: OK")
        print(f"   - Category: {result.summary.category.value}")
        print(f"   - Sentiment: {result.summary.sentiment.value}")
        print(f"   - Key Points: {len(result.summary.key_points)}")

        # Check QA scores
        if not result.qa_scores:
            print("❌ FAILED: QA scores missing")
            return False
        print(f"✅ QA Scores: OK")
        print(f"   - Overall: {result.qa_scores.overall:.1f}/10")
        print(f"   - Empathy: {result.qa_scores.empathy:.1f}/10")
        print(f"   - Professionalism: {result.qa_scores.professionalism:.1f}/10")
        print(f"   - Resolution: {result.qa_scores.resolution:.1f}/10")
        print(f"   - Compliance: {result.qa_scores.compliance:.1f}/10")

        # Check recommendations
        if not result.recommendations:
            print("⚠️  WARNING: No recommendations generated")
        else:
            print(f"✅ Recommendations: {len(result.recommendations)} items")
            for i, rec in enumerate(result.recommendations[:3], 1):
                print(f"   {i}. {rec}")

        # Check tags
        if not result.tags:
            print("⚠️  WARNING: No tags generated")
        else:
            print(f"✅ Tags: {', '.join(result.tags)}")

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

    # Success
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 60)
    print("\nYou can now run the application with: streamlit run app.py")

    return True


if __name__ == "__main__":
    success = test_system()
    sys.exit(0 if success else 1)

