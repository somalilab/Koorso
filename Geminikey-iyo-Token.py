import google.generativeai as genai

# Ku dar API key-gaaga
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
genai.configure(api_key=GEMINI_API_KEY)

def chat_with_gemini(message):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(f"Soomaali: {message}")
    return response.text

# Bot-ka ku xidh
def ai_chat(update, context):
    user_message = update.message.text
    ai_response = chat_with_gemini(user_message)
    update.message.reply_text(f"🤖: {ai_response}")