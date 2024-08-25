import chainlit as cl
from chainlit.types import ThreadDict
from chainlit.step import StepDict

from .base import BaseModel

class PaperInterpret(BaseModel):

    def __init__(self) -> None:
        self._lock_message = None
        self._lock_action = None

    async def settings(self):
        pass

    async def start(self):
        await cl.Message(content="开场").send()

    async def end(self):
        pass

    async def message(self, message: cl.Message):
        task: str = cl.user_session.get("task")
        if not task:
            async with cl.Step(name="autogen-task", type="llm") as autogen_task:
                while True:
                    await cl.sleep(2)
                    anything = cl.AskUserMessage(
                        content="随便说点啥"
                    )
                    feedback = await anything.send()
                    if feedback:
                        await cl.Message(content=feedback['output']).send()
                        await cl.Message.from_dict(feedback).remove()
                
        
        
            
            

    async def resume(self, thread: ThreadDict):
        pass