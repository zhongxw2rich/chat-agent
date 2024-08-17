import os
from typing import Dict, Optional, Union

from autogen.agentchat import Agent, AssistantAgent, UserProxyAgent

import chainlit as cl
from chainlit.types import ThreadDict
from chainlit.input_widget import Select, Slider, TextInput

from .base import BaseModel

class AutoGenAgent(BaseModel):

    def __init__(self) -> None:
        pass

    async def settings(self):
        return await cl.ChatSettings(
            [
                Select(
                    id="Model",
                    label="Deepseek - Model",
                    values=["deepseek-chat", "deepseek-coder"],
                    initial_index=0,
                ),
                Slider(
                    id="Temperature",
                    label="Deepseek - Temperature",
                    initial=0.7,
                    min=0,
                    max=2,
                    step=0.1,
                )
            ]
        ).send()

    async def start(self):
        await self.settings()
        settings = cl.context.session.chat_settings
        llm_config = {
            "model": settings["Model"],
            "temperature": settings["Temperature"],
            "api_key": os.getenv("OPENAI_API_KEY"),
            "base_url": os.getenv("OPENAI_BASE_URL"),
        }

        assistant = ChainlitAssistantAgent(
            "assistant", llm_config=llm_config
        )
        user_proxy = ChainlitUserProxyAgent(
            "user_proxy",
            code_execution_config= {
                "work_dir": "workspace",
                "use_docker": False,
            },
        )

        task = "Tell me a joke about NVDA and TESLA stock prices."
        await cl.Message(content=f"Starting agents on task: {task}...").send()
        await cl.make_async(user_proxy.initiate_chat)(
                assistant,
                message=task,
        )

    async def message(self, message: cl.Message):
        pass

    async def resume(self, thread: ThreadDict):
        await self.settings()

async def ask_helper(func, **kwargs):
    res = await func(**kwargs).send()
    while not res:
        res = await func(**kwargs).send()
    return res

class ChainlitAssistantAgent(AssistantAgent):
    def send(
        self,
        message: Union[Dict, str],
        recipient: Agent,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False,
    ) -> bool:
        cl.run_sync(
            cl.Message(
                content=f'*Sending message to "{recipient.name}":*\n\n{message}',
                author="AssistantAgent",
            ).send()
        )
        super(ChainlitAssistantAgent, self).send(
            message=message,
            recipient=recipient,
            request_reply=request_reply,
            silent=silent,
        )

class ChainlitUserProxyAgent(UserProxyAgent):
    def get_human_input(self, prompt: str) -> str:
        if prompt.startswith(
            "Provide feedback to assistant. Press enter to skip and use auto-reply"
        ):
            res = cl.run_sync(
                ask_helper(
                    cl.AskActionMessage,
                    content="Continue or provide feedback?",
                    actions=[
                        cl.Action(
                            name="continue", value="continue", label="✅ Continue"
                        ),
                        cl.Action(
                            name="feedback",
                            value="feedback",
                            label="💬 Provide feedback",
                        ),
                        cl.Action(
                            name="exit",
                            value="exit",
                            label="🔚 Exit Conversation"
                        ),
                    ],
                )
            )
            if res.get("value") == "continue":
                return ""
            if res.get("value") == "exit":
                return "exit"

        reply = cl.run_sync(ask_helper(cl.AskUserMessage, content=prompt, timeout=60))

        print(reply)
        return "continue"

    def send(
        self,
        message: Union[Dict, str],
        recipient: Agent,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False,
    ):
        cl.run_sync(
            cl.Message(
                content=f'*Sending message to "{recipient.name}"*:\n\n{message}',
                author="UserProxyAgent",
            ).send()
        )
        super(ChainlitUserProxyAgent, self).send(
            message=message,
            recipient=recipient,
            request_reply=request_reply,
            silent=silent,
        )