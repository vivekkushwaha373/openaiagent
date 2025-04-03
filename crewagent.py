import os

from crewai import Agent
from crewai_tools import SerperDevTool
# Create an agent with all available parameters
from crewai import Task
from crewai import Crew


import json

from dotenv import load_dotenv  # Import dotenv

# Load environment variables from .env
load_dotenv()

# Access the API key from the environment
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

research_agent = Agent(
    role="Research Analyst",
    goal="Find and summarize information about specific topics",
    backstory="You are an experienced researcher with attention to detail",
    tools=[SerperDevTool()],
    verbose=True  # Enable logging for debugging
)

# Example task
search_tool = SerperDevTool()

task = Task(
    description='Find and summarize the latest AI news',
    expected_output='A bullet list summary of the top 5 most important AI news',
    agent=research_agent,
    tools=[search_tool]
)

# Execute the crew
crew = Crew(
    agents=[research_agent],
    tasks=[task],
    verbose=True
)

result = crew.kickoff()

# Accessing the task output
task_output = task.output

print(f"Task Description: {task_output.description}")
print(f"Task Summary: {task_output.summary}")
print(f"Raw Output: {task_output.raw}")
if task_output.json_dict:
    print(f"JSON Output: {json.dumps(task_output.json_dict, indent=2)}")
if task_output.pydantic:
    print(f"Pydantic Output: {task_output.pydantic}")