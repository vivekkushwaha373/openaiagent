import asyncio
import os
from dotenv import load_dotenv  # Import dotenv

# Load environment variables from .env
load_dotenv()

# Access the API key from the environment
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

from agents import Agent,AsyncOpenAI,Runner,OpenAIChatCompletionsModel

hindi_agent = Agent(
    name="hindi agent",
    instructions="You only speak Hindi.",
    model="gpt-4o", 
)

english_agent = Agent(
    name="English agent",
    instructions="You only speak English",
    model=OpenAIChatCompletionsModel( 
        model="gpt-4o",
        openai_client=AsyncOpenAI()
    ),
)

triage_agent = Agent(
    name="Triage agent",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[hindi_agent, english_agent],
    # model="gpt-3.5-turbo",
)

async def main():
    result = await Runner.run(triage_agent, input="namaste kya kar rahe ho")
    print(result.final_output)

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())

