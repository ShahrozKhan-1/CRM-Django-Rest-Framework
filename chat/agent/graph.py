from langchain_google_genai import ChatGoogleGenerativeAI
from CRM.settings import GEMINI_API_KEY, GEMINI_MODEL, DATABASES
from langgraph.graph.state import END, START, StateGraph
from langgraph.graph import MessagesState
from langgraph.checkpoint.postgres import PostgresSaver
from .tools import toolkit
from langgraph.prebuilt import ToolNode, tools_condition
from .system_msg import SYSTEM_MESSAGE
from langchain_core.messages import SystemMessage


llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    temperature=0.7,
    api_key=GEMINI_API_KEY,
)

llm_with_tools = llm.bind_tools(toolkit)

db = DATABASES["default"]

DB_URI = (
    f"postgresql://{db['USER']}:{db['PASSWORD']}"
    f"@{db['HOST']}:{db['PORT']}/{db['NAME']}"
)


checkpoint_context = PostgresSaver.from_conn_string(conn_string=DB_URI)
checkpointer = checkpoint_context.__enter__()
checkpointer.setup()
builder = StateGraph(MessagesState)


def chat_node(state: MessagesState):
    messages = [SystemMessage(SYSTEM_MESSAGE), *state["messages"]]
    response = llm_with_tools.invoke(messages)
    return {
        "messages": [response]
    }


builder.add_node("chat_node", chat_node)
builder.add_node("tools", ToolNode(toolkit))
builder.add_edge(START, "chat_node")
builder.add_conditional_edges("chat_node", tools_condition)
builder.add_edge("tools", "chat_node")
graph = builder.compile(checkpointer=checkpointer)
