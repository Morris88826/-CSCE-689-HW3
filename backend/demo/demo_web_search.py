import os
from dotenv import load_dotenv

load_dotenv()

from langchain_core.tools import Tool
from langchain_google_community import GoogleSearchAPIWrapper

search = GoogleSearchAPIWrapper()

tool = Tool(
    name="google_search",
    description="Search Google for recent results.",
    func=search.run,
)

result = tool.run("What is the stock price of Apple today?")
print(tool)