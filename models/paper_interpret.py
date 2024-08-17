import chainlit as cl

from .base import BaseModel

class PaperInterpret(BaseModel):
    def __init__(self) -> None:
        pass

    async def settings(self):
        pass

    async def start(self):
        response = await cl.AskActionMessage(
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
        if response.get("value") == "continue":
            await cl.Message(content="continue").send()
        if response.get("value") == "exit":
            await cl.Message(content="exit").send()
        if response.get("value") == "feedback":
            feedback = await cl.AskUserMessage(
                content="Provide feedback to assistant. Press enter to skip and use auto-reply"
            ).send()
            if feedback:
                await cl.Message(
                    content=feedback['output']
                ).send()

        

    async def message(self):
        pass

    async def resume(self):
        pass