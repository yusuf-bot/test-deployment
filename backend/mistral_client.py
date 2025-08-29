import os
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()  # loads .env into environment
api_key = os.getenv("MISTRAL_API_KEY")

if not api_key:
    raise ValueError("❌ MISTRAL_API_KEY not found in .env")

client = Mistral(api_key=api_key)

# Create a web search agent
websearch_agent = client.beta.agents.create(
    model="mistral-medium-2505",
    description="Agent able to search information over the web",
    name="Websearch Agent",
    instructions="You can search the web using the `web_search` tool to answer queries.",
    tools=[{"type": "web_search"}],
    completion_args={
        "temperature": 0.3,
        "top_p": 0.95,
    }
)
