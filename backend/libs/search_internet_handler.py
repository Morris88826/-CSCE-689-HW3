from dotenv import load_dotenv
from langchain import hub
from langchain_core.tools import Tool
from langchain_google_community import GoogleSearchAPIWrapper
from langchain.agents import create_structured_chat_agent, AgentExecutor

load_dotenv(".env")
# Initialize the search tool
search = GoogleSearchAPIWrapper()
search_tool = Tool(
    name="google_search",
    description="Search Google for recent results.",
    func=search.run,
)
# Create an agent prompt from LangChain Hub
agent_prompt = hub.pull("hwchase17/structured-chat-agent")

def load_search_internet_agent(llm, max_iterations=10):
    # Create a structured chat agent with tools
    agent = create_structured_chat_agent(
        llm=llm,
        tools=[search_tool],
        prompt=agent_prompt
    )
    # Create an AgentExecutor to manage tool usage
    return AgentExecutor(
        agent=agent,
        tools=[search_tool],
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=max_iterations
    )

def search_internet(query, agent_executor):
    try:
        agent_response = agent_executor.invoke({"input": query})
        response = agent_response
        return response['output']
    except Exception as e:
        print(f"Error searching the internet: {e}")
        return "I'm sorry, you are currently out of limit for the day. Please try again tomorrow."

