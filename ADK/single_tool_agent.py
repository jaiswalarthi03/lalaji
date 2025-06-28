from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
import asyncio
import os
from dotenv import load_dotenv
from typing import Dict, Any, List
from datetime import datetime
import json

# Load environment variables and set API key directly for robustness
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "your-google-api-key-here")

APP_NAME = "basic_agent_no_web"
USER_ID = "user_12345"
SESSION_ID = "session_12345"

# Step 1: get the agent
async def get_agent():
    # Try to load instruction from prompt.txt
    prompt_file = "prompt.txt"
    if os.path.exists(prompt_file):
        with open(prompt_file, "r", encoding="utf-8") as f:
            instruction = f.read().strip()
    else:
        instruction = "You are a helpful assistant."
    root_agent = LlmAgent(
        name="first_agent",
        description="This is my first agent",
        instruction=instruction,
        model="gemini-2.5-flash",
    )
    return root_agent

# Step 2: run the agent
async def main(query):
    # create memory session
    session_service = InMemorySessionService()
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

    # get the agent
    root_agent = await get_agent()

    # create runner instance
    runner = Runner(app_name=APP_NAME, agent=root_agent, session_service=session_service)

    # format the query
    content = types.Content(role="user", parts=[types.Part(text=query)])

    print("Running agent with query:", query)
    # run the agent
    events = runner.run_async(
        new_message=content,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    # print the response
    async for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response:", final_response)

if __name__ == "__main__":
    asyncio.run(main("What is the advantage of using multi agent framework?")) 