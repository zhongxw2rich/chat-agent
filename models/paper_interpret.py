import os
import chainlit as cl
from typing import List, Dict, Any
from chainlit.types import ThreadDict
from langchain_postgres import PGVector
from langchain_core.documents import Document
from langchain_community.embeddings import DashScopeEmbeddings
from .utils.langchain_utils import get_collections, index_document
from chainlit.input_widget import Select, Slider, TextInput

conninfo = os.getenv('LANGCHAIN_DB_CONNINFO')
embeddings = DashScopeEmbeddings(
    model="text-embedding-v2",
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY")
)

class PaperInterpret():

    def __init__(self) -> None:
        pass

    async def settings(self) -> Dict[str, Any]:
        docs: List[str] = get_collections()
        docs.insert(0, "No Document")
        return await cl.ChatSettings(
            [
                Select(
                    id="Document",
                    label="请选择文档",
                    values=docs,
                    initial_index=0,
                ),
                Select(
                    id="Model",
                    label="Model",
                    values=["deepseek-chat", "deepseek-coder"],
                    initial_index=0,
                ),
                Slider(
                    id="Temperature",
                    label="Temperature",
                    initial=1,
                    min=0,
                    max=2,
                    step=0.1,
                ),
                TextInput(
                    id="Prompt",
                    label="Prompt",
                    initial="you are a helpful assistant.",
                    multiline=True,
                )
            ]
        ).send()


    async def start(self):
        action = await cl.AskActionMessage(
            content="请选择要执行的操作",
            actions=[
                cl.Action(
                    name="Ask",
                    value="Ask",
                    label="🚀 直接提问"
                ),
                cl.Action(
                    name="Upload",
                    value="Upload",
                    label="📤 文档上传"
                ),
                cl.Action(
                    name="Manage",
                    value="Manage",
                    label="📑 文档管理"
                )
            ]
        ).send()

        if action.get("value") == "Upload":
            files = await cl.AskFileMessage(
                content="请上传文档", 
                accept=["application/pdf", "text/plain"], 
                max_size_mb=10,
                timeout=300
            ).send()
            index_document(files[0])
            
        await self.settings()
        
    async def end(self):
        pass

    async def message(self, message: cl.Message):
        pass
        


    async def resume(self, thread: ThreadDict):
        await self.settings()