import os
from typing import Dict, Optional, Union

from autogen.agentchat import Agent, AssistantAgent, UserProxyAgent

import chainlit as cl
from chainlit.types import ThreadDict

from .base import BaseModel

class AutoGenAgent(BaseModel):

    def __init__(self) -> None:
        pass

    async def settings(self):
        pass

    async def message(self, message: cl.Message):
        pass

    async def resume(self, thread: ThreadDict):
        pass

    async def start(self):
        llm_config = {
            "config_list": [{
                "model": "deepseek-chat",
                "api_type": "openai",
                "api_key": os.getenv("OPENAI_API_KEY"),
                "base_url": os.getenv("OPENAI_BASE_URL"),
            }],
            "temperature": 0.5,
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

        task = await cl.AskUserMessage(
            content="你好，请问你想执行什么AutoGen任务？"
        ).send()
        
        await user_proxy.a_initiate_chat(
                assistant,
                message=task['output'],
        )

class ChainlitAssistantAgent(AssistantAgent):
    async def a_send(
        self,
        message: Union[Dict, str],
        recipient: Agent,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False,
    ) -> bool:
        await cl.Message(
                content=f'*Sending message to "{recipient.name}":*\n\n{message}',
                author="AssistantAgent",
        ).send()

        await super(ChainlitAssistantAgent, self).a_send(
            message=message,
            recipient=recipient,
            request_reply=request_reply,
            silent=silent,
        )

class ChainlitUserProxyAgent(UserProxyAgent):
    async def a_get_human_input(self, prompt: str) -> str:
        response = await cl.AskActionMessage(
                content="Continue or provide feedback?",
                actions=[
                    cl.Action(
                        name="continue", 
                        value="continue", 
                        label="✅ Continue Conversation"
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
        ).send()
        print(response)
        if response.get("value") == "continue":
            await cl.Message(author="UserAction", content="continue").send()
            return "continue"
        if response.get("value") == "exit":
            await cl.Message(author="UserAction", content="exit").send()
            return "exit"
        if response.get("value") == "feedback":
            feedback = await cl.AskUserMessage(content=prompt, timeout=60).send()
            if feedback:
                return feedback['output']
            

    async def a_send(
        self,
        message: Union[Dict, str],
        recipient: Agent,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False,
    ):
        await cl.Message(
                content=f'*Sending message to "{recipient.name}"*:\n\n{message}',
                author="UserProxyAgent",
        ).send()
        await super(ChainlitUserProxyAgent, self).a_send(
            message=message,
            recipient=recipient,
            request_reply=request_reply,
            silent=silent,
        )