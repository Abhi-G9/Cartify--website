import google.generativeai as genai

GEMINI_API_KEY = "A." 

genai.configure(api_key=GEMINI_API_KEY)

def get_product_support_response(product_data: dict, user_message: str, chat_history: list):
    system_prompt = f"""
    You are an AI support assistant for NovaCart. 
    You must ONLY use the following product facts to answer the user. 
    Do NOT invent, guess, or hallucinate information about prices, stock, or features.
    If the answer is not in the facts below, say: "I don't have enough information to answer that accurately. Would you like to contact our human support team?"

    --- PRODUCT FACTS ---
    Name: {product_data.get('name', 'N/A')}
    Price: ₹{product_data.get('price', 'N/A')}
    Category: {product_data.get('category', 'N/A')}
    Stock Available: {product_data.get('stock', 'N/A')}
    Description: {product_data.get('description', 'N/A')}
    """

    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_prompt
        )

        formatted_history = []
        for msg in chat_history:
            formatted_history.append({"role": "user", "parts": [msg.customer_message]})
            formatted_history.append({"role": "model", "parts": [msg.ai_response]})

        chat = model.start_chat(history=formatted_history)
        response = chat.send_message(user_message)
        return response.text

    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "Our AI is currently taking a break. Please contact human support."