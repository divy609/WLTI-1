import os
from dotenv import load_dotenv
from typing import TypedDict, Literal
from typing import Annotated, List
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.output_parsers import StrOutputParser
from langgraph.types import Command
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig, chain


from termcolor import colored

from langchain_openai import AzureChatOpenAI
import requests
import base64


from urllib.parse import quote
from langchain_community.utilities import SQLDatabase 
import os


OAUTH_URL = "https://id.cisco.com/oauth2/default/v1/token"
OPENAI_API_BASE = "https://chat-ai.cisco.com"
OPENAI_API_VERSION = "2024-07-01-preview"
OPENAI_API_MODEL = "gpt-4o-mini"
OPENAI_API_TYPE = "azure"


BRIDGEIT_CLIENT_ID = 
BRIDGEIT_CLIENT_SECRET = 
app_key = 


def get_bridgeit_access_token():
    payload = "grant_type=client_credentials"
    value = base64.b64encode(
        f"{BRIDGEIT_CLIENT_ID}:{BRIDGEIT_CLIENT_SECRET}".encode(
            "utf-8"
        )
    ).decode("utf-8")
    headers = {
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {value}",
    }

    token_response = requests.request("POST", OAUTH_URL, headers=headers, data=payload)
    return token_response.json()["access_token"]


# app_key = 'egai-prd-opex-sccos-reduce-rtb-quick-resolution-1'
# print(app_key)
llm = AzureChatOpenAI(
        azure_endpoint=OPENAI_API_BASE,
        api_version=OPENAI_API_VERSION,
        model=OPENAI_API_MODEL,
        deployment_name=OPENAI_API_MODEL,
        api_key=get_bridgeit_access_token(),
        openai_api_type=OPENAI_API_TYPE,
        model_kwargs=dict(
                      user=f'{{"appkey": "{app_key}"}}'
                    ),
        temperature=0,
        # verbose=True
    )
# print(llm)
# print("Connected to GPT 4-o LLM All Environment")
   

# Load environment variables
load_dotenv()

# API Keys
# openai_key = os.environ.get('OPENAI_API_KEY')
tavily_api_key = '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'

# Define the graph state
class State(TypedDict):
    messages: Annotated[List, add_messages] = []    
    next: str = ""

def python_finder(state: State) -> Command[Literal["Supervisor"]]:
    """Finds resources based on the user's query."""

    query = state["messages"][-1].content
    context = state["messages"]

    # Define prompt
    prompt = ChatPromptTemplate.from_template(
        f"""You are a  python resource finder. 
        You will find resources for the user based on their preferences 
        in the field of python programming language and related topics. 
        Use the context to help you build the response. You may also answer
        general questions or miscellaneous queries.Dont end your answer as a question.
        End your asnwer in a sentence.
        
        Question: {query}\n"""
    )
    
    # Define tool and bind LLM to Tavily tool
    # tavily_tool = TavilySearchResults(max_results=5, search_depth="advanced", include_answer=True, include_raw_content=True,tavily_api_key = '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')
    # llm = ChatOpenAI(model="gpt-4o").bind_tools([tavily_tool])

    # Define RAG chain
    rag_chain = (
        prompt
        | llm
    )

    @chain
    def tool_chain(user_input: str, config: RunnableConfig):
        input_ = {"user_input": user_input, "context": context}
        ai_msg = rag_chain.invoke(input_, config=config)
        return(ai_msg)
        tool_msgs = tavily_tool.batch(ai_msg.tool_calls, config=config)
        return rag_chain.invoke({**input_, "messages": [ai_msg, *tool_msgs]}, config=config)

    response = tool_chain.invoke(query)


    return Command(
        update={
            "messages": [
                AIMessage(content=response.content, name="Python-Finder")
            ]
        },
        goto="Supervisor",
    )



def java_finder(state: State) -> Command[Literal["Supervisor"]]:
    """Finds resources based on the user's query."""

    query = state["messages"][-1].content
    context = state["messages"]

    # Define prompt
    prompt = ChatPromptTemplate.from_template(
        f"""You are a java resource finder. 
        You will find resources for the user based on their preferences 
        in the field of java  programming language and related topics. 
        Use the context to help you build the response. You may also answer
        general questions or miscellaneous queries.Dont end your answer as a question. 
        End your asnwer in a sentence
        
        Question: {query}\n"""
    )
    
    # Define tool and bind LLM to Tavily tool
    # tavily_tool = TavilySearchResults(max_results=5, search_depth="advanced", include_answer=True, include_raw_content=True,tavily_api_key = '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')
    # llm = ChatOpenAI(model="gpt-4o").bind_tools([tavily_tool])

    # Define RAG chain
    rag_chain = (
        prompt
        | llm
    )

    @chain
    def tool_chain(user_input: str, config: RunnableConfig):
        input_ = {"user_input": user_input, "context": context}
        ai_msg = rag_chain.invoke(input_, config=config)
        return(ai_msg)
        tool_msgs = tavily_tool.batch(ai_msg.tool_calls, config=config)
        return rag_chain.invoke({**input_, "messages": [ai_msg, *tool_msgs]}, config=config)

    response = tool_chain.invoke(query)


    return Command(
        update={
            "messages": [
                AIMessage(content=response.content, name="Java-Finder")
            ]
        },
        goto="Supervisor",
    )
def static_agent(state: State) -> Command[Literal["Supervisor"]]:
    print("Static agent")
    return Command(
        update={
            "messages": [
                AIMessage(content="Hi, Greetings to the user logged in , Have a nice day!", name="static")
            ]
        },
        goto="Supervisor",
    )



class Router(TypedDict):
    next: Literal["Python-Finder", "Java-Finder","Static", "FINISH"]


def supervisor_agent(state: State) -> Command[Literal["Python-Finder", "Java-Finder", "__end__"]]:
    """Supervisor agent that manages the conversation between workers."""

    question = state["messages"][-1].content

    # Include the system prompt and the current conversation state in the messages
    members = ["Python-Finder","Java-Finder","Static"]
    system_prompt = (
            "You are a supervisor tasked with managing a conversation between the"
            f" following workers:  {members}. Given the following user request {question}," 
            " respond with the worker to act next. Each worker will perform a"
            " task and respond with their results and status. When you determine a task to be finished,"
            " respond with FINISH."
            " Here are the uses of each worker:\n"
            "1. Python-Finder: Find resources based on the user's query which is about python programming language.\n"
            "2. Java-Finder: Find resources based on the user's query which is about java programming language.\n"
            "3. Static: For any hi message and complete the task\n"
        )

    messages = [
        {"role": "system", "content": system_prompt},
    ] + state["messages"]

    

    # llm = ChatOpenAI(model="gpt-4o")

    # Use the LLM to decide the next step
    response = llm.with_structured_output(Router).invoke(messages)

    print(response)

    # Extract the next node from the response
    next_node = response.get("next", None)

    if not next_node:
        raise ValueError("Supervisor failed to determine the next step.")

    if next_node == "FINISH":
        next_node = END
    # Return a Command with the target node in the goto field.
    return Command(goto=next_node, update={"next": next_node})

def create_graph():
    workflow = StateGraph(State)

    workflow.add_node("Python-Finder", python_finder)
    workflow.add_node("Java-Finder", java_finder)
    workflow.add_node("Supervisor", supervisor_agent)
    # workflow.add_node("Static", static_agent)

    workflow.add_edge(START, "Supervisor")

    graph = workflow.compile()

    return graph


def main():
    # Create the state graph
    graph = create_graph()

    # Print out the LangGraph as ASCII
    graph.get_graph().print_ascii()

    # Continuous input and LLM interaction
    print(colored("You can start interacting with the coding assistant. Type 'exit' to end the conversation.", "blue"))

    while True:
        user_message = input("> ")

        if user_message == "exit":
            print(colored("Goodbye!", "blue"))
            break

        input_state = {"messages": [{"role": "user", "content": user_message}]}

        # Verbose output
        for event in graph.stream(input_state):
            print(colored(event, "red"))
            print("------------------------------------")

        # # Concise output
        # final_state = graph.invoke(input_state, config)
        # print(colored(final_state["messages"][-1].content, "red"))
        # print("------------------------------------")


if __name__ == "__main__":
    main()
