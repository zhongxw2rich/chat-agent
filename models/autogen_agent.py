import os
from typing import Dict, Optional, Union

from autogen.agentchat import Agent, AssistantAgent, UserProxyAgent

import chainlit as cl
from chainlit.types import ThreadDict
from chainlit.input_widget import Select, Slider, TextInput

from .base import BaseModel

@cl.action_callback("")
async def on_action(action):
    await cl.Message(content="{action.name}").send()


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
            "config_list":[{
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
            content="Please tell me the task you want to perform?"
        ).send()
        
        await cl.make_async(user_proxy.initiate_chat)(
                assistant,
                message=task['output'],
        )

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
            response = cl.run_sync(
                cl.AskActionMessage(
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
                ).send()
            )
            if response.get("value") == "continue":
                cl.run_sync(
                    cl.Message(content="continue").send()
                )
                return "continue"
            if response.get("value") == "exit":
                cl.run_sync(
                    cl.Message(content="exit").send()
                )
                return "exit"

            feedback = cl.run_sync(
                cl.AskUserMessage(content=prompt).send()
            )
            return feedback['output']

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