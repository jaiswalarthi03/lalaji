from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools.agent_tool import AgentTool
from google.genai import types
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, Any, List
import json

# Load environment variables and set API key directly for robustness
load_dotenv()
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

# Step 1: get the main agent, sequential agent, and parallel agent
async def get_agents():
    # Try to load instruction from prompt.txt
    prompt_file = "prompt.txt"
    if os.path.exists(prompt_file):
        with open(prompt_file, "r", encoding="utf-8") as f:
            instruction = f.read().strip()
    else:
        instruction = "You are a helpful assistant."
    math_specialist_tool = await get_math_specialist()
    # Main agent
    root_agent = LlmAgent(
        name="first_agent",
        description="This is my first agent",
        instruction=instruction,
        model="gemini-2.5-flash",
        tools=[echo_tool, add_tool, current_time_tool, math_specialist_tool],
    )
    # Sequential agent: echo then math specialist
    sequential_agent = SequentialAgent(
        name="sequential_agent",
        sub_agents=[
            LlmAgent(
                name="echo_agent",
                description="Echoes input.",
                instruction="Echo the user's message.",
                model="gemini-2.5-flash",
                tools=[echo_tool],
            ),
            LlmAgent(
                name="math_agent",
                description="Handles math queries.",
                instruction="Answer math questions.",
                model="gemini-2.5-flash",
                tools=[add_tool],
            ),
        ],
        description="Runs echo and math in sequence."
    )
    # Parallel agent: echo and current time in parallel
    parallel_agent = ParallelAgent(
        name="parallel_agent",
        sub_agents=[
            LlmAgent(
                name="echo_agent_parallel",
                description="Echoes input.",
                instruction="Echo the user's message.",
                model="gemini-2.5-flash",
                tools=[echo_tool],
            ),
            LlmAgent(
                name="time_agent_parallel",
                description="Returns current time.",
                instruction="Return the current time.",
                model="gemini-2.5-flash",
                tools=[current_time_tool],
            ),
        ],
        description="Runs echo and time in parallel."
    )
    return root_agent, sequential_agent, parallel_agent

# Step 2: run the agent
async def main(query, agent_type="root"):
    # create memory session
    session_service = InMemorySessionService()
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

    # get the agents
    root_agent, sequential_agent, parallel_agent = await get_agents()
    if agent_type == "root":
        agent = root_agent
    elif agent_type == "sequential":
        agent = sequential_agent
    elif agent_type == "parallel":
        agent = parallel_agent
    else:
        raise ValueError("Unknown agent_type")

    # create runner instance
    runner = Runner(app_name=APP_NAME, agent=agent, session_service=session_service)

    # format the query
    content = types.Content(role="user", parts=[types.Part(text=query)])

    print(f"\nRunning {agent_type} agent with query: {query}")
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
            print(f"{agent_type.capitalize()} Agent Response:", final_response)

if __name__ == "__main__":
    print("\n--- Root Agent Test ---")
    asyncio.run(main("Echo this: FORMAT21 workflow!", agent_type="root"))
    print("\n--- Sequential Agent Test ---")
    asyncio.run(main("What is 7.5 plus 2.5? Echo this: sequential!", agent_type="sequential"))
    print("\n--- Parallel Agent Test ---")
    asyncio.run(main("What is the current time? Echo this: parallel!", agent_type="parallel")) 