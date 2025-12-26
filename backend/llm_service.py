import os
import openai
import datetime
# import google.generativeai as genai # Uncomment if using Gemini

# Initialize clients
openai_api_key = os.getenv("OPENAI_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

if openai_api_key:
    client = openai.OpenAI(api_key=openai_api_key, base_url="https://api.cerebras.ai/v1")

def summarize_text(text: str, length: str = "short"):
    """
    Summarizes text using an LLM.
    length: "short" (very big font summary) or "long" (detailed summary)
    """
    if not openai_api_key and not gemini_api_key:
        # Mock fallback
        if length == "short":
            return f"MOCK SHORT SUMMARY: {text[:50]}..."
        return f"MOCK LONG SUMMARY: {text[:200]}..."

    prompt = ""
    if length == "short":
        prompt = f"Summarize the following news article in a very short, catchy sentence (max 10 words) suitable for a TikTok-style feed overlay: \n\n{text[:1000]}"
    else:
        prompt = f"Keep in mind ze qre on the {datetime.date()}. Provide a detailed but concise summary of the following news article: \n\n{text[:2000]}."

    try:
        if openai_api_key:
            response = client.chat.completions.create(
                model="gpt-oss-120b",
                messages=[
                    {"role": "system", "content": "You are a helpful news summarizer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000
            )
            return response.choices[0].message.content.strip()
        # Add Gemini implementation here if needed
    except Exception as e:
        print(f"LLM Error: {e}")
        return f"Error generating summary: {text[:50]}..."

def answer_query(query: str, context_articles: list):
    """
    Answers a user query based on a list of relevant articles.
    context_articles: List of dicts with 'title' and 'summary'
    """
    if not openai_api_key:
        return "MOCK ANSWER: I found some articles but cannot generate a full answer without an API key."

    context_str = "\n\n".join([f"Title: {a['title']}\nSummary: {a['summary']}\nURL: {a['url']}" for a in context_articles])
    
    prompt = f"Answer the user's question based on the following news summaries:\n\n{context_str}\n\nQuestion: {query}"

    try:
        response = client.chat.completions.create(
            model="gpt-oss-120b",
            messages=[
                {"role": "system", "content": "You are a helpful news assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM Error: {e}")
        return "Sorry, I couldn't generate an answer at this time."

