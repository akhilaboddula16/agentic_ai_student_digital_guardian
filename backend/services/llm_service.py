from groq import Groq

from backend.config import GROQ_API_KEY, GROQ_MODEL


def ask_llm(question: str, usage_summary: dict) -> str:
    if not GROQ_API_KEY:
        return fallback_answer(question, usage_summary)

    try:
        client = Groq(api_key=GROQ_API_KEY)

        prompt = f"""
You are an Agentic AI Student Digital Guardian chatbot for parents.
Explain mobile usage in simple English.
Suggest whether social media should be reduced.
Do not be harsh. Be practical.
Keep the answer short and helpful.

Usage summary:
{usage_summary}

Parent question:
{question}
"""
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You explain student app usage to parents in a calm, practical tone.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        return response.choices[0].message.content or fallback_answer(question, usage_summary)
    except Exception:
        return (
            fallback_answer(question, usage_summary)
            + "\n\nAI provider fallback used: Groq is unavailable or rate-limited right now."
        )


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
