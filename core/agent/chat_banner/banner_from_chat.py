from io import BytesIO
from typing import Any, List, Literal, Optional
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command, Send
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.tools import tool  # type: ignore
from langchain_core.messages import SystemMessage, HumanMessage
from PIL import Image

from config.env_variables import get_settings
from core.agent.chat_banner.state import BannerChatState
from core.utils import logger


class BannerGenerationNodes:
    log = logger.Logger.get_logger(__name__)
    settings = get_settings()
    google_api_key = settings.GOOGLE_API_KEY
    # llm = ChatVertexAI(model_name="google_genai:gemini-2.0-flash", api_key=google_api_key, temperature=0, project='banner-ai-466817')
    llm = ChatVertexAI(
        model_name="gemini-2.0-flash-lite-001",
        temperature=0,
        project="banner-ai-466817",
        location="us-central1",
    )

    @classmethod
    def ask_human_tool(cls, state: BannerChatState):
        """
        user input
        """
        cls.log.info("user input added")
        # user_response = interrupt(state.get("message", []))  # type: ignore
        return {"messages": state.get("messages")}

    @classmethod
    def validate_all_info_required(cls, state: dict[str, list[Any]]) -> dict[str, Any]:
        """graph node. getting all information for banner generation"""

        human_message = state.get("messages")

        assert human_message is not None, "Expected user message is bout found empty"

        message: list[Any] = [
            SystemMessage(
                content="You are a AI generator for banner, from the provided message list extract the banner category, product info, etc. If missing any info ask for required message in polite manner"
            ),
            *human_message,
        ]
        response = cls.llm.invoke(input=message)
        return {"messages": [response]}


class ChatAgentWorker:
    def __init__(self) -> None:
        settings = get_settings()
        self.google_api_key = settings.GOOGLE_API_KEY
        self.graph: StateGraph | None = None
        self.compiled_graph: Any = None

    def _get_workflow_state(self):
        return StateGraph(BannerChatState)

    def get_graph(self) -> "StateGraph":
        workflow = self._get_workflow_state()

        workflow.add_node(
            "validate_message", BannerGenerationNodes.validate_all_info_required
        )
        workflow.add_node("ask_human", BannerGenerationNodes.ask_human_tool)

        workflow.add_edge(START, "ask_human")

        workflow.add_edge("ask_human", "validate_message")
        workflow.add_edge("validate_message", END)

        self.graph = workflow

        return self.graph

    def compile_graph(self, thread_id: str, start_message: list[HumanMessage]) -> Any:
        if self.graph is None:
            raise Exception("workflow not created")
        memory = InMemorySaver()

        thread_config = {"configurable": {"thread_id": thread_id}}
        self.compiled_graph = self.graph.compile(checkpointer=memory)

        response = self.compiled_graph.invoke(
            {"messages": start_message}, config=thread_config
        )
        return self.compiled_graph, response

    def display_graph(self):
        if self.compiled_graph is None:
            raise Exception("Can not display graph without creating it")

        png_bytes = self.compiled_graph.get_graph().draw_mermaid_png()

        img = Image.open(BytesIO(png_bytes))
        img.show()

    def resume_graph(
        self, message: dict[str, list[HumanMessage]], send_to: str
    ) -> Command[Any]:
        return Command(resume=message, goto=send_to)

    @property
    def get_complied_graph(self):
        return self.compiled_graph

    def user_send_message(self, msg: str, node: str):
        pass
