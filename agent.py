"""Agent 核心：模型看工具说明书 → 决定调哪个 → 执行 → 结果给回模型 → 直到给出最终回答

手写循环版（不依赖 LangGraph），把"模型怎么选工具"这个核心原理暴露得明明白白：
1. 把工具列表 bind 给模型（相当于把菜单递给它）
2. 模型返回：要么是工具调用指令，要么是最终回答
3. 是工具调用 → 执行对应 Python 函数 → 结果以 ToolMessage 塞回对话
4. 循环，直到模型给出最终回答
"""

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_ollama import ChatOllama

from tools import ALL_TOOLS, TOOL_MAP

SYSTEM_PROMPT = (
    "你是一个系统诊断助手。用户会描述电脑的问题（卡顿、内存不足、磁盘满等），"
    "你需要调用工具获取真实数据，然后基于数据给出诊断结论和建议。\n"
    "规则：\n"
    "1. 需要数据时先调用对应工具，不要凭空编造数字。\n"
    "2. 一次可以调用多个工具（如 CPU + 内存一起查）。\n"
    "3. 拿到工具结果后，用中文给出简洁的诊断结论和可操作建议。\n"
)


class SystemDiagnoseAgent:
    def __init__(self, model: str = "qwen2.5:7b", base_url: str = "http://localhost:11434"):
        self.llm = ChatOllama(model=model, base_url=base_url, temperature=0).bind_tools(ALL_TOOLS)

    def run(self, question: str, max_steps: int = 5) -> str:
        messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=question)]
        for step in range(max_steps):
            response = self.llm.invoke(messages)

            # 模型没要求调工具 → 这就是最终回答
            if not response.tool_calls:
                return response.content

            # 模型要求调工具 → 执行，把结果塞回对话
            messages.append(response)
            for call in response.tool_calls:
                print(f"  🔧 [step {step+1}] 调用工具: {call['name']}({call['args']})")
                try:
                    result = TOOL_MAP[call["name"]].invoke(call["args"])
                except Exception as e:  # 工具本身出错也不能让 Agent 崩
                    result = f"工具执行出错: {e}"
                messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))

        return "（达到最大步数，诊断未完成，请换个问法或重试）"
