import os
import utils.app_util as util
from typing import List, Optional

import chainlit as cl
import chainlit.data as cl_data
from chainlit.types import ThreadDict
from chainlit.data import BaseStorageClient
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer

from models import GeneralChat
from models import AutoGenAgent
from models import PaperInterpret

conninfo = os.getenv('POSTGRESQL_CONNINFO')
auth_password = os.getenv('AUTH_PASSOWRD')

cl_data._data_layer = SQLAlchemyDataLayer(
    conninfo=conninfo, storage_provider=BaseStorageClient
)

def switch_model():
    profile = cl.user_session.get("chat_profile")
    if "General Chat" == profile:
        return GeneralChat()
    if "AutoGen Agent" == profile:
        return AutoGenAgent()
    if "Paper Interpret" == profile:
        return PaperInterpret()

@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name="General Chat",
            markdown_description="使用DeepSeek通用对话助手完成对话",
        ),
        cl.ChatProfile(
            name="AutoGen Agent",
            markdown_description="使用AutoGen对话生成任务并执行",
        ),
        cl.ChatProfile(
            name="Paper Interpret",
            markdown_description="使用GraphRAG对文章进行解读",
        ),
    ]

@cl.password_auth_callback
def auth_callback(username: str, password: str) -> Optional[cl.User]:
    if (username, util.hmac_sha256(password)) == ("admin", auth_password):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None
    
@cl.on_settings_update
async def settings_update(settings):
    print("settings_update", settings)

@cl.on_chat_start
async def chat_start():
    await switch_model().start()

@cl.on_chat_end
async def chat_end():
    await switch_model().end()

@cl.on_message
async def message(message: cl.Message):
    await switch_model().message(message)

@cl.on_chat_resume
async def chat_resume(thread: ThreadDict):
    await switch_model().resume(thread)
