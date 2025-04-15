# agent.py
from crewai import Agent, Task, Crew
from langchain.llms import OpenAI
import os
import json
import sys

def create_crew(input_data):
    """
    Create a CrewAI crew based on the input data
    """
    # Extract parameters from input_data
    query = input_data.get('query', "What are the benefits and considerations of implementing container-based architecture with Kubernetes for a financial services company?")
    focus_areas = input_data.get('focus_areas', ["security", "scalability", "compliance", "cost"])
    target_companies = input_data.get('target_companies', ["Docker", "Red Hat", "HashiCorp", "AWS"])
    openai_api_key = input_data.get('openai_api_key')

    # Set OpenAI API key
    os.environ["OPENAI_API_KEY"] = openai_api_key
    
    # Initialize LLM
    llm = OpenAI(temperature=0.7)
    
    # Create agents based on the agent definitions in input_data
    agents_config = input_data.get('agents', [])
    agents = {}

    for agent_config in agents_config:
        name = agent_config.get('name')
        agents[name] = Agent(
            role=agent_config.get('role'),
            goal=agent_config.get('goal'),
            backstory=agent_config.get('backstory'),
            llm=llm,
            verbose=True
        )
    
    # Create tasks based on the task definitions in input_data
    tasks_config = input_data.get('tasks', [])
    tasks = []
    
    for task_config in tasks_config:
        agent_name = task_config.get('agent')
        if agent_name in agents:
            tasks.append(
                Task(
                    description=f"{task_config.get('description')} for the query: '{query}'. Focus on aspects: {', '.join(focus_areas)}. Target companies for analysis: {', '.join(target_companies)}.",
                    agent=agents[agent_name],
                    expected_output=task_config.get('expected_output')
                )
            )
    
    # Create the crew
    crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        verbose=True
    )
    
    return crew

def run_agent():
    """
    Main function to run the agent
    """
    try:
        # Get input data from environment or command line
        input_json = os.environ.get('INPUT_DATA')
        if not input_json and len(sys.argv) > 1:
            input_json = sys.argv[1]
        
        if not input_json:
            print("No input data provided")
            return {"error": "No input data provided"}
        
        # Parse input data
        input_data = json.loads(input_json) if isinstance(input_json, str) else input_json
        
        # Create and run the crew
        crew = create_crew(input_data)
        result = crew.kickoff()
        
        # Return the result
        return {"result": result}
    
    except Exception as e:
        print(f"Error running agent: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    result = run_agent()
    print(json.dumps(result))