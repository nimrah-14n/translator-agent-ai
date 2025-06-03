import os
from dotenv import load_dotenv
import chainlit as cl
from litellm import completion
import json

# Load environment variables
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is missing in .env file")

# On chat start
@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("chat_history", [])
    await cl.Message(
        content="Welcome to the Translator Agent by Nimrah Hussain!\n\nPlease *provide the text you want to translate and select the language you want to translate to.*"
    ).send()

# On each user message
@cl.on_message
async def on_message(message: cl.Message):
    msg = cl.Message(content="Translating.....!")
    await msg.send()

    history = cl.user_session.get("chat_history") or []

    # Add user's message to history
    history.append({"role": "user", "content": message.content})

    # Convert history to Gemini-compatible format
    gemini_history = []
    for h in history:
        gemini_history.append({
            "role": h["role"],
            "content": h["content"]
        })

    try:
        # Call Gemini API via LiteLLM
        response = completion(
            model="gemini/gemini-1.5-flash",
            api_key=gemini_api_key,
            messages=gemini_history
        )

        response_content = response.choices[0].message.content

        # Show translated result
        msg.content = response_content
        await msg.update()

        # Add assistant's response to history
        history.append({"role": "assistant", "content": response_content})
        cl.user_session.set("chat_history", history)

    except Exception as e:
        msg.content = f"❌ Error: {str(e)}"
        await msg.update()

# On chat end
@cl.on_chat_end
async def on_chat_end():
    history = cl.user_session.get("chat_history") or []

    with open("translation_chat_history.json", "w") as f:
        json.dump(history, f, indent=2)

    print("✅ Chat history saved.")