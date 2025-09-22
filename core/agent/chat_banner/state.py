from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph


class BannerChatState(TypedDict):
    messages: Annotated[list, add_messages]  # type: ignore


banner_graph = StateGraph(BannerChatState)
