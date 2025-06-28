from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools.agent_tool import AgentTool
from google.genai import types
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime
import requests
from typing import Dict, Any, List
import json

# Load environment variables and set API key directly for robustness
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "your-google-api-key-here")

APP_NAME = "basic_agent_no_web"
USER_ID = "user_12345"
SESSION_ID = "session_12345"

def echo_tool(text: str) -> str:
    return text

def add_tool(a: float, b: float) -> float:
    return a + b

def current_time_tool() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def weather_tool(city: str) -> str:
    city_coords = {
        "new york": (40.7128, -74.0060),
        "london": (51.5074, -0.1278),
        "paris": (48.8566, 2.3522),
        "tokyo": (35.6895, 139.6917),
        "sydney": (-33.8688, 151.2093),
    }
    coords = city_coords.get(city.lower())
    if not coords:
        return f"Weather for '{city}' is not available. Try: New York, London, Paris, Tokyo, Sydney."
    lat, lon = coords
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        weather = data.get("current_weather", {})
        temp = weather.get("temperature")
        wind = weather.get("windspeed")
        desc = f"Current weather in {city.title()}: {temp}°C, wind {wind} km/h."
        return desc
    except Exception as e:
        return f"Weather API error: {e}"

async def get_math_specialist_agent():
    math_specialist_agent = LlmAgent(
        name="math_specialist_agent",
        description="Specialist agent for advanced math queries.",
        instruction="You are a math specialist. Answer only math-related questions as concisely as possible.",
        model="gemini-2.5-flash",
        tools=[add_tool],
    )
    return AgentTool(math_specialist_agent)

async def get_agents():
    prompt_file = "prompt.txt"
    if os.path.exists(prompt_file):
        with open(prompt_file, "r", encoding="utf-8") as f:
            instruction = f.read().strip()
    else:
        instruction = "You are a helpful assistant."
    math_specialist_tool = await get_math_specialist_agent()
    root_agent = LlmAgent(
        name="root_agent",
        description="Main user-facing agent with all tools.",
        instruction=instruction,
        model="gemini-2.5-flash",
        tools=[echo_tool, add_tool, current_time_tool, weather_tool, math_specialist_tool],
    )
    echo_agent = LlmAgent(
        name="echo_agent",
        description="Echoes user input.",
        instruction="Echo the user's message.",
        model="gemini-2.5-flash",
        tools=[echo_tool],
    )
    math_agent = LlmAgent(
        name="math_agent",
        description="Handles math queries.",
        instruction="Answer math questions.",
        model="gemini-2.5-flash",
        tools=[add_tool],
    )
    sequential_agent = SequentialAgent(
        name="sequential_agent",
        sub_agents=[echo_agent, math_agent],
        description="Runs echo_agent and math_agent in sequence."
    )
    echo_agent_parallel = LlmAgent(
        name="echo_agent_parallel",
        description="Echoes user input (parallel).",
        instruction="Echo the user's message.",
        model="gemini-2.5-flash",
        tools=[echo_tool],
    )
    current_time_agent_parallel = LlmAgent(
        name="current_time_agent_parallel",
        description="Returns current time (parallel).",
        instruction="Return the current time.",
        model="gemini-2.5-flash",
        tools=[current_time_tool],
    )
    parallel_agent = ParallelAgent(
        name="parallel_agent",
        sub_agents=[echo_agent_parallel, current_time_agent_parallel],
        description="Runs echo_agent_parallel and current_time_agent_parallel in parallel."
    )
    return root_agent, sequential_agent, parallel_agent

async def main():
    session_service = InMemorySessionService()
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    root_agent, sequential_agent, parallel_agent = await get_agents()
    agent_map = {
        "root": root_agent,
        "sequential": sequential_agent,
        "parallel": parallel_agent,
    }
    print("\nFORMAT21 Interactive CLI (type 'exit' to quit)")
    print("Choose agent type: root, sequential, parallel (default: root)")
    while True:
        agent_type = input("Agent type [root/sequential/parallel]: ").strip().lower() or "root"
        if agent_type not in agent_map:
            print("Invalid agent type. Try again.")
            continue
        query = input("Enter your query (or 'exit' to quit): ").strip()
        if query.lower() == "exit":
            print("Exiting.")
            break
        agent = agent_map[agent_type]
        runner = Runner(app_name=APP_NAME, agent=agent, session_service=session_service)
        content = types.Content(role="user", parts=[types.Part(text=query)])
        print(f"\nRunning {agent_type} agent with query: {query}")
        events = runner.run_async(
            new_message=content,
            user_id=USER_ID,
            session_id=SESSION_ID,
        )
        async for event in events:
            if event.is_final_response() and getattr(event, "content", None) and getattr(event.content, "parts", None):
                final_response = event.content.parts[0].text
                print(f"{agent_type.capitalize()} Agent Response:", final_response)
        print()

if __name__ == "__main__":
    asyncio.run(main()) 