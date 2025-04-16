#!/usr/bin/env python
import sys
import json
import datetime
import os
import logging
import traceback


# Configure logging to stderr only
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler(sys.stderr)])
logger = logging.getLogger("minimal-chromadb-test")


def main(input_file):
   """Minimal ChromaDB test agent."""
   try:
       # Read the input file
       with open(input_file, 'r') as f:
           input_data = json.load(f)
      
       # Get OpenAI API key
       openai_api_key = input_data.get('openai_api_key')
       if not openai_api_key:
           raise ValueError("OpenAI API key is required in input data")
      
       # Set OpenAI API key as environment variable
       os.environ['OPENAI_API_KEY'] = openai_api_key
      
       # Extract query
       query = input_data.get('query', 'No query provided')
      
       # Test SQLite and ChromaDB versions
       import sqlite3
       sqlite_version = sqlite3.sqlite_version
       logger.info(f"SQLite version: {sqlite_version}")
      
       # Test ChromaDB import and basic functionality
       try:
           import chromadb
           chromadb_version = getattr(chromadb, "__version__", "Unknown")
           logger.info(f"ChromaDB version: {chromadb_version}")
          
           # Basic ChromaDB test
           client = chromadb.Client()
           collection = client.create_collection("test_collection")
           collection.add(documents=["Test document about containers"], ids=["id1"])
          
           # Success indicator
           chromadb_working = True
       except Exception as e:
           logger.error(f"ChromaDB test failed: {str(e)}")
           chromadb_working = False
      
       # Create a single agent with CrewAI
       from crewai import Agent, Task, Crew, Process
       from langchain_openai import ChatOpenAI
      
       llm = ChatOpenAI(
           model="gpt-3.5-turbo",
           temperature=0.7,
           api_key=openai_api_key
       )
      
       # Create minimal agent and task
       researcher = Agent(
           role="Technology Analyst",
           goal="Provide a brief analysis of container architecture",
           backstory="You are an expert in container technologies.",
           verbose=False,  # Reduce verbosity
           llm=llm
       )
      
       analysis_task = Task(
           description=f"Very briefly summarize the top 3 benefits of container architecture for financial services in response to: '{query}'",
           expected_output="Short bullet-point list of 3 benefits",
           agent=researcher
       )
      
       # Create crew with minimal config
       crew = Crew(
           agents=[researcher],
           tasks=[analysis_task],
           verbose=False,
           process=Process.sequential,
           memory_enabled=False  # Turn off memory for faster execution
       )
      
       # Execute with timeout control
       logger.info("Executing crew with timeouts")
       result_str = "Default response if timeout occurs"
      
       import threading
       import time
      
       def run_crew():
           nonlocal result_str
           try:
               crew_result = crew.kickoff()
               if hasattr(crew_result, 'raw_output'):
                   result_str = crew_result.raw_output
               elif hasattr(crew_result, '__str__'):
                   result_str = str(crew_result)
               else:
                   result_str = f"Unknown result type: {type(crew_result)}"
           except Exception as e:
               result_str = f"Error in crew execution: {str(e)}"
      
       # Run with a timeout
       thread = threading.Thread(target=run_crew)
       thread.start()
       thread.join(timeout=60)  # 1 minute timeout
      
       if thread.is_alive():
           logger.warning("CrewAI execution timed out, using fallback response")
           result_str = "Execution timed out. Using fallback response: Container architecture offers scalability, consistency, and improved resource utilization."
      
       # Create final result with environment info
       result = {
           "status": "success",
           "query": query,
           "response": result_str,
           "environment": {
               "sqlite_version": sqlite_version,
               "chromadb_version": chromadb_version if 'chromadb_version' in locals() else "Unknown",
               "chromadb_working": chromadb_working if 'chromadb_working' in locals() else False
           },
           "timestamp": datetime.datetime.now().isoformat()
       }
      
       print(json.dumps(result))
       return result
      
   except Exception as e:
       # Log the error and return a clean error JSON
       logger.error(f"Error in main function: {str(e)}")
       logger.error(traceback.format_exc())
      
       error_result = {
           "status": "error",
           "error_message": str(e),
           "traceback": traceback.format_exc(),
           "timestamp": datetime.datetime.now().isoformat()
       }
      
       print(json.dumps(error_result))
       return error_result


if __name__ == "__main__":
   if len(sys.argv) != 2:
       error_result = {
           "status": "error",
           "error_message": "Usage: python agent.py <input_file>",
           "timestamp": datetime.datetime.now().isoformat()
       }
       print(json.dumps(error_result))
       sys.exit(1)
  
   main(sys.argv[1])


# # agent.py
# from crewai import Agent, Task, Crew
# from langchain.llms import OpenAI
# import os
# import json
# import sys

# def create_crew(input_data):
#     """
#     Create a CrewAI crew based on the input data
#     """
#     # Extract parameters from input_data
#     query = input_data.get('query', "What are the benefits and considerations of implementing container-based architecture with Kubernetes for a financial services company?")
#     focus_areas = input_data.get('focus_areas', ["security", "scalability", "compliance", "cost"])
#     target_companies = input_data.get('target_companies', ["Docker", "Red Hat", "HashiCorp", "AWS"])
#     openai_api_key = input_data.get('openai_api_key')

#     # Set OpenAI API key
#     os.environ["OPENAI_API_KEY"] = openai_api_key
    
#     # Initialize LLM
#     llm = OpenAI(temperature=0.7)
    
#     # Create agents based on the agent definitions in input_data
#     agents_config = input_data.get('agents', [])
#     agents = {}

#     for agent_config in agents_config:
#         name = agent_config.get('name')
#         agents[name] = Agent(
#             role=agent_config.get('role'),
#             goal=agent_config.get('goal'),
#             backstory=agent_config.get('backstory'),
#             llm=llm,
#             verbose=True
#         )
    
#     # Create tasks based on the task definitions in input_data
#     tasks_config = input_data.get('tasks', [])
#     tasks = []
    
#     for task_config in tasks_config:
#         agent_name = task_config.get('agent')
#         if agent_name in agents:
#             tasks.append(
#                 Task(
#                     description=f"{task_config.get('description')} for the query: '{query}'. Focus on aspects: {', '.join(focus_areas)}. Target companies for analysis: {', '.join(target_companies)}.",
#                     agent=agents[agent_name],
#                     expected_output=task_config.get('expected_output')
#                 )
#             )
    
#     # Create the crew
#     crew = Crew(
#         agents=list(agents.values()),
#         tasks=tasks,
#         verbose=True
#     )
    
#     return crew

# def run_agent():
#     """
#     Main function to run the agent
#     """
#     try:
#         # Get input data from environment or command line
#         input_json = os.environ.get('INPUT_DATA')
#         if not input_json and len(sys.argv) > 1:
#             input_json = sys.argv[1]
        
#         if not input_json:
#             print("No input data provided")
#             return {"error": "No input data provided"}
        
#         # Parse input data
#         input_data = json.loads(input_json) if isinstance(input_json, str) else input_json
        
#         # Create and run the crew
#         crew = create_crew(input_data)
#         result = crew.kickoff()
        
#         # Return the result
#         return {"result": result}
    
#     except Exception as e:
#         print(f"Error running agent: {str(e)}")
#         return {"error": str(e)}

# if __name__ == "__main__":
#     result = run_agent()
#     print(json.dumps(result))