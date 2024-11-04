from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, trim_messages
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage
from dotenv import load_dotenv
load_dotenv("../.env")

model = ChatOpenAI(name="gpt-4o-mini", temperature=0, max_tokens=256)

# Define a new graph
workflow = StateGraph(state_schema=MessagesState)

trimmer = trim_messages(
    max_tokens=65,
    strategy="last",
    token_counter=model,
    include_system=True,
    allow_partial=False,
    start_on="human"
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Answer all questions to the best of your ability.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

# Define the function that calls the model
def call_model(state: MessagesState):
    chain = prompt | model 
    trimmed_messages = trimmer.invoke(state["messages"]) 
    response = chain.invoke({
        "messages": trimmed_messages,
    })
    
    return {"messages": response}


# Define the (single) node in the graph
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

# Add memory
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)



config = {"configurable": {"thread_id": "abc123"}}
while True:
    user_input = input("You: ")
    # response = app.invoke({
    #     "messages": user_input,
    # }, config)

    for chunk, metadata in app.stream(
            {"messages": user_input},
            config,
            stream_mode="messages",
        ):
        if isinstance(chunk, AIMessage):  # Filter to just model responses
            print(chunk.content, end="|")
    print()
    
    if user_input == "exit":
        break