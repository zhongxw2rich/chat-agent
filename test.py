from autogen.coding import CodeBlock
from autogen.coding.jupyter import JupyterConnectionInfo, JupyterCodeExecutor

executor = JupyterCodeExecutor(
    jupyter_server=JupyterConnectionInfo(host='47.115.36.52', use_https=False, port=8888, token='v2JFwbgcYSPotwrVfRJIJmlKkceeywpR7SqFrbQGKz7Id9i4')
)
print(
    executor.execute_code_blocks(
        code_blocks=[
            CodeBlock(language="python", code="print('Hello, World!')"),
        ]
    )
)