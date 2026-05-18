from backend.config import GEMINI_API_KEY


def ask_gemini(question: str, usage_summary: dict) -> str:
    if not GEMINI_API_KEY:
        return fallback_answer(question, usage_summary)

    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)

        prompt = f"""
You are an Agentic AI Student Digital Guardian chatbot for parents.
Explain mobile usage in simple English.
Suggest whether social media should be reduced.
Do not be harsh. Be practical.

Usage summary:
{usage_summary}

Parent question:
{question}
"""
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return fallback_answer(question, usage_summary) + f"\n\nGemini error fallback used: {str(e)}"


def fallback_answer(question: str, usage_summary: dict) -> str:
    if not usage_summary:
        return "No usage data found for this student. Please add app usage first."

    total = sum(usage_summary.values())
    highest_app = max(usage_summary, key=usage_summary.get)
    return (
        f"Student total mobile usage is {total} minutes. "
        f"Most used app is {highest_app} with {usage_summary[highest_app]} minutes. "
        "If social media crosses the limit, reduce usage during study hours."
    )
