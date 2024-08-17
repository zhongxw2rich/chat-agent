from typing import Any, Dict
import chainlit as cl
from chainlit.types import ThreadDict

class BaseModel():

    def __init__(self) -> None:
        pass

    async def settings(self):
        pass

    async def start(self):
        pass

    async def message(self, message: cl.Message):
        pass

    async def resume(self, thread: ThreadDict):
        pass
