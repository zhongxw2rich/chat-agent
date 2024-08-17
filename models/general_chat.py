from typing import Any, Dict
from openai import AsyncOpenAI

import chainlit as cl
from chainlit.input_widget import Select, Slider, TextInput

from .base import BaseModel

client = AsyncOpenAI()

class GeneralChat(BaseModel):
    def __init__(self) -> None:
        pass

    async def settings(self) -> Dict[str, Any]:
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
                    initial=1,
                    min=0,
                    max=2,
                    step=0.1,
                ),
                TextInput(
                    id="Prompt",
                    label="Deepseek - Prompt",
                    initial="you are a helpful assistant.",
                    multiline=True,
                )
            ]
        ).send()
    
    async def start(self):
        await self.settings()
        content = "你好，我是 DeepSeek 通用对话助手，有问题尽管问我。"
        start_message = cl.Message(type="system_message", content=content)
        await start_message.send()

    async def message(self, message):
        settings = cl.context.session.chat_settings
        model = settings["Model"]
        temperature = settings["Temperature"]
        prompt = settings["Prompt"]
        history_messages = [{"role":"system", "content": prompt}]
        history_messages.extend(cl.chat_context.to_openai())

        return_message = cl.Message(content="")
        await return_message.send()
        stream = await client.chat.completions.create(
            model=model, 
            messages=history_messages, 
            temperature=temperature, 
            stream=True
        )
        async for part in stream:
            if token := part.choices[0].delta.content or "":
                await return_message.stream_token(token)

        await return_message.update()

    async def resume(self, thread):
        await self.settings()
        
    
