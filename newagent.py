#!/usr/bin/env python
import sys
import json
import datetime
import os
import logging
import requests


# No logging to stdout - only use print for JSON output
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler(sys.stderr)])
logger = logging.getLogger("direct-openai-agent")


def call_openai_api(query, api_key):
   """Call OpenAI API directly"""
   url = "https://api.openai.com/v1/chat/completions"
  
   # Format the prompt for container architecture in financial services
   prompt = f"""
   Provide a comprehensive analysis of container-based architecture for financial services companies.
  
   Specifically address the following points regarding: {query}
  
   1. Benefits of container-based architecture in financial services
   2. Considerations and challenges
   3. Security and compliance implications
   4. Implementation best practices
   5. Technology recommendations
  
   Format your response with clear headings and bullet points.
   """
  
   headers = {
       "Content-Type": "application/json",
       "Authorization": f"Bearer {api_key}"
   }
  
   data = {
       "model": "gpt-3.5-turbo",
       "messages": [
           {"role": "system", "content": "You are an expert solutions architect specializing in container technologies for financial services."},
           {"role": "user", "content": prompt}
       ],
       "temperature": 0.7
   }
  
   try:
       response = requests.post(url, headers=headers, json=data)
       response.raise_for_status()
       result = response.json()
       return result["choices"][0]["message"]["content"]
   except Exception as e:
       logger.error(f"OpenAI API error: {str(e)}")
       return f"Error calling OpenAI API: {str(e)}"


def main(input_file):
   """
   Simple agent that directly calls OpenAI API.
   """
   try:
       # Read the input file
       with open(input_file,'r',encoding="ISO-8859-1") as f:
           input_data = json.load(f)
      
       # Get OpenAI API key
       openai_api_key = input_data.get('openai_api_key')
       if not openai_api_key:
           error_result = {
               "status": "error",
               "error_message": "OpenAI API key is required in input data",
               "timestamp": datetime.datetime.now().isoformat()
           }
           print(json.dumps(error_result))
           return error_result
      
       # Extract query
       query = input_data.get('query', 'What are the benefits and considerations of implementing container-based architecture for a financial services company?')
      
       # Call OpenAI API directly
       response_text = call_openai_api(query, openai_api_key)
      
       # Create result JSON
       result = {
           "status": "success",
           "query": query,
           "response": response_text,
           "timestamp": datetime.datetime.now().isoformat()
       }
      
       # Output only clean JSON to stdout
       print(json.dumps(result))
       return result
      
   except Exception as e:
       # Return error as JSON
       error_result = {
           "status": "error",
           "error_message": str(e),
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
