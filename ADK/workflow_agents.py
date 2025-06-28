from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools.agent_tool import AgentTool
from google.genai import types
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables and set API key directly for robustness
load_dotenv()

# Set API key from environment or use placeholder
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "your-google-api-key-here")

APP_NAME = "basic_agent_no_web"
USER_ID = "user_12345"
SESSION_ID = "session_12345"

# Step 0: Define multiple tools
def echo_tool(text: str) -> str:
    """Echoes the input text."""
    return text

def add_tool(a: float, b: float) -> float:
    """Returns the sum of two numbers."""
    return a + b

def current_time_tool() -> str:
    """Returns the current time as a string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Step 0.5: Define a math specialist agent as a tool
async def get_math_specialist():
    agent = LlmAgent(
        name="math_specialist",
        description="Handles advanced math queries.",
        instruction="You are a math specialist. Answer only math-related questions as concisely as possible.",
        model="gemini-2.5-flash",
        tools=[add_tool],
    )
    return AgentTool(agent)

# Step 1: get the agent
async def get_agent():
    # Try to load instruction from prompt.txt
    prompt_file = "prompt.txt"
    if os.path.exists(prompt_file):
        with open(prompt_file, "r", encoding="utf-8") as f:
            instruction = f.read().strip()
    else:
        instruction = "You are a helpful assistant."
    math_specialist_tool = await get_math_specialist()
    root_agent = LlmAgent(
        name="first_agent",
        description="This is my first agent",
        instruction=instruction,
        model="gemini-2.5-flash",
        tools=[echo_tool, add_tool, current_time_tool, math_specialist_tool],
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
    print("\n--- Echo Tool Test ---")
    asyncio.run(main("Echo this: FORMAT21 agent-as-tool!"))
    print("\n--- Add Tool Test ---")
    asyncio.run(main("What is 7.5 plus 2.5?"))
    print("\n--- Math Specialist Test ---")
    asyncio.run(main("What is the square root of 144?"))
    print("\n--- Current Time Tool Test ---")
    asyncio.run(main("What is the current time?")) 