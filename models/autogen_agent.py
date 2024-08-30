import os
from typing import Dict, Optional, Union

from autogen import GroupChat, GroupChatManager
from autogen.coding.jupyter import JupyterCodeExecutor
from autogen.coding.jupyter import JupyterConnectionInfo
from autogen import Agent, ConversableAgent

import chainlit as cl
from chainlit.types import ThreadDict

start_system_message = "你好，请告诉我你的需求。我会帮你规划并执行。"

admin_prompt="""
管理员。与规划师交流讨论计划。计划执行需要得到管理员的批准。
"""

planner_prompt="""
规划师。提出一个计划。根据管理员和反馈修改计划，直到管理员批准。
计划可能涉及一个会写代码的工程师和一个不会写代码的科学家。
首先解释计划。清楚地说明哪个步骤由工程师执行，哪个步骤由科学家执行。
"""

engineer_prompt="""
工程师。你按照批准的计划行动。你编写 Python/Shell 代码来解决任务。将代码放在代码块中，指定脚本类型。用户无法修改你的代码。因此，不要提供需要其他人修改的不完整代码。如果不打算由执行者执行，请不要使用代码块。
一个回复中不要包含多个代码块。不要要求其他人复制粘贴结果。检查执行者返回的执行结果。
如果结果表明有错误，请修复错误并重新输出代码。建议提供完整的代码而不是部分代码或代码更改。如果错误无法修复，或者即使成功执行代码后任务仍未解决，请分析问题，重新审视假设，收集所需的额外信息，并考虑尝试不同的方法。
不要将程序运行结果写文件中。要将结果通过print函数打印出来。
"""
scientist_prompt="""
科学家。你按照批准的计划行动。你能够对执行结果进行数据分析。你不会写代码。
"""
executor_prompt="""
执行者。执行工程师编写的代码。
"""

chat_llm_config = {
    "config_list": [{
        "model": "deepseek-chat",
        "api_type": "openai",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": os.getenv("OPENAI_BASE_URL"),
    }],
    "temperature": 1,
    "cache_seed": None
}

coder_llm_config = {
    "config_list": [{
        "model": "deepseek-coder",
        "api_type": "openai",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": os.getenv("OPENAI_BASE_URL"),
    }],
    "temperature": 1,
    "cache_seed": None
}

os.makedirs(".coding", exist_ok=True)

class ChainlitConversableAgent(ConversableAgent):
    def get_human_input(self, prompt: str) -> str:
        if self.name == "Admin":
            response = cl.run_sync(cl.AskActionMessage(
                author=self.name,
                content=f"继续运行或提供反馈帮助{self.name}？",
                actions=[
                    cl.Action(
                        name="feedback",
                        value="feedback",
                        label="💬 给予建议",
                    ),
                    cl.Action(
                        name="exit",
                        value="exit",
                        label="🔚 退出"
                    ),
                ],
                timeout=300
            ).send())
        else:
            response = cl.run_sync(cl.AskActionMessage(
                author=self.name,
                content=f"继续运行或提供反馈帮助{self.name}？",
                actions=[
                    cl.Action(
                        name="continue", 
                        value="continue", 
                        label="✅ 继续运行"
                    ),
                    cl.Action(
                        name="feedback",
                        value="feedback",
                        label="💬 给予建议",
                    ),
                ],
                timeout=300
            ).send())
    
        if response:
            if response.get("value") == "continue":
                return ""
            if response.get("value") == "exit":
                print("exit")
                return "exit"
            if response.get("value") == "feedback":
                feedback = cl.run_sync(cl.AskUserMessage(
                    author=self.name,
                    content="为Autogen-Agent给予运行建议:",
                    timeout=300
                ).send())
                feedback_output = str(feedback['output'])
                if feedback_output:
                    cl.run_sync(cl.Message.from_dict(
                        feedback
                    ).remove())
                    return feedback_output
        return "exit"
    
    def send(
        self,
        message: Union[Dict, str],
        recipient: Agent,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False,
    ):
        content = message if isinstance(message, str) else message['content']
        cl.run_sync(cl.Message(author=self.name,content=content).send())
        super(ChainlitConversableAgent, self).send(
            message=content,
            recipient=recipient,
            request_reply=request_reply,
            silent=silent,
        )


class AutoGenAgent():
    def __init__(self) -> None:
        pass


    def state_transition(self, last_speaker, groupchat):
        select = cl.run_sync(
             cl.AskActionMessage(
                 author="Chat Agent",
                  content="请问下一步由谁执行？",
                  actions=[
                    cl.Action(
                        name="Planner", 
                        value="Planner", 
                        label="📝 规划师"
                    ),
                    cl.Action(
                        name="Engineer",
                        value="Engineer",
                        label="🛠️ 工程师",
                    ),
                    cl.Action(
                        name="Scientist",
                        value="Scientist",
                        label="🔬 科学家"
                    ),
                    cl.Action(
                        name="Executor",
                        value="Executor",
                        label="🚀 执行者"
                    ),
                    cl.Action(
                        name="Admin",
                        value="Admin",
                        label="🧑‍💼 管理员"
                    )
                ],
                timeout=300
            ).send()
        )
        if select:
            if select.get("value") == "Planner":
                return cl.user_session.get("planner")
            if select.get("value") == "Engineer":
                return cl.user_session.get("engineer")
            if select.get("value") == "Scientist":
                return cl.user_session.get("scientist")
            if select.get("value") == "Executor":
                return cl.user_session.get("executor")
            return cl.user_session.get("admin")
            
        
    async def settings(self):
            pass

    async def message(self, message: cl.Message):
        manager: GroupChatManager = cl.user_session.get("manager")
        manager.initiate_chat(
            manager,
            message=message.content,
        )
            
    async def resume(self, thread: ThreadDict):
        pass

    async def start(self):
        jupyter = JupyterCodeExecutor(
            jupyter_server = JupyterConnectionInfo(
                host=str(os.getenv("JUPYTER_SERVER").split(":")[0]),
                port=int(os.getenv("JUPYTER_SERVER").split(":")[1]),
                token=os.getenv("JUPYTER_TOKEN"),
                use_https=False
            ),
            output_dir=".coding"
        )
        cl.user_session.set("jupyter", jupyter)
        print("start jupyter kernel " + jupyter._kernel_id)

        planner = ChainlitConversableAgent(
            "Planner", 
            human_input_mode="NEVER",
            llm_config=chat_llm_config,
            system_message=planner_prompt,
        )
        cl.user_session.set("planner", planner)
        admin = ChainlitConversableAgent(
            "Admin",
            human_input_mode="ALWAYS",
            system_message=admin_prompt,
        )
        cl.user_session.set("admin", admin)
        engineer = ChainlitConversableAgent(
            "Engineer",
            human_input_mode="ALWAYS",
            llm_config=coder_llm_config,
            system_message=engineer_prompt,
        )
        cl.user_session.set("engineer", engineer)
        scientist = ChainlitConversableAgent(
            "Scientist",
            human_input_mode="ALWAYS",
            llm_config=coder_llm_config,
            system_message=scientist_prompt,
        )
        cl.user_session.set("scientist", scientist)
        executor = ChainlitConversableAgent(
            "Executor",
            human_input_mode="NEVER",
            code_execution_config={
                "last_n_messages": 3,
                "executor": jupyter
            },
        )
        cl.user_session.set("executor", executor)
        groupchat = GroupChat(
            agents=[admin, planner, engineer, executor, scientist],
            messages=[], max_round=20,
            speaker_selection_method=self.state_transition,
        )
        manager = GroupChatManager(groupchat=groupchat, llm_config=chat_llm_config)

        cl.user_session.set("manager",manager)

        await cl.Message(
            author="Chat Agent",content=start_system_message
        ).send()

    async def end(self):
        jupyter: JupyterCodeExecutor = cl.user_session.get("jupyter")
        jupyter.stop()
        print("stop jupyter kernel " + jupyter._kernel_id)
