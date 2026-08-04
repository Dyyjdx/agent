"""零 LangChain 版：同一个诊断 Agent，只用 ollama 原生 SDK + 手写工具协议

和 agent.py 对比着看：核心循环几乎一模一样！
区别只是——LangChain 用消息对象类，这里用裸 dict。
证明：LangChain = 零件库，Agent 的发动机是你自己的循环逻辑。
"""

import psutil
import ollama

MODEL = "qwen2.5:7b"

SYSTEM_PROMPT = (
    "你是一个系统诊断助手。用户会描述电脑的问题（卡顿、内存不足、磁盘满等），"
    "你需要调用工具获取真实数据，然后基于数据给出诊断结论和建议。\n"
    "规则：\n"
    "1. 需要数据时先调用对应工具，不要凭空编造数字。\n"
    "2. 拿到工具结果后，用中文给出简洁的诊断结论和可操作建议。\n"
)

# ---------- 工具：就是普通函数（跟 LangChain 版一字不差） ----------

def get_cpu_usage() -> str:
    """获取当前 CPU 使用率（百分比）。用户说电脑卡、慢、发热时调用。"""
    return f"CPU 使用率: {psutil.cpu_percent(interval=1)}%"


def get_memory_usage() -> str:
    """获取内存使用情况（总量/已用/可用/百分比）。"""
    mem = psutil.virtual_memory()
    gb = 1024 ** 3
    return f"内存: 总 {mem.total/gb:.1f} GB, 已用 {mem.used/gb:.1f} GB ({mem.percent}%), 可用 {mem.available/gb:.1f} GB"


# ---------- 手写"菜单"：LangChain @tool 自动生成的就是这玩意儿 ----------

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_cpu_usage",
            "description": "获取当前 CPU 使用率（百分比）。用户说电脑卡、慢、发热时调用。",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_memory_usage",
            "description": "获取内存使用情况（总量/已用/可用/百分比）。",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

FUNC_MAP = {"get_cpu_usage": get_cpu_usage, "get_memory_usage": get_memory_usage}


# ---------- Agent 循环：跟 agent.py 里的 run() 结构一模一样 ----------

def run(question: str, max_steps: int = 5) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    for step in range(max_steps):
        resp = ollama.chat(model=MODEL, messages=messages, tools=TOOLS)
        msg = resp["message"]

        # 模型没要求调工具 → 最终回答
        if not msg.get("tool_calls"):
            return msg["content"]

        # 模型要求调工具 → 执行，结果塞回对话
        messages.append(msg)
        for tc in msg["tool_calls"]:
            name = tc["function"]["name"]
            args = tc["function"]["arguments"]
            print(f"  🔧 [step {step+1}] 调用工具: {name}({args})")
            try:
                result = FUNC_MAP[name](**args)
            except Exception as e:
                result = f"工具执行出错: {e}"
            messages.append({"role": "tool", "content": str(result)})

    return "（达到最大步数，诊断未完成）"


if __name__ == "__main__":
    print("你: 电脑有点卡，帮我看看")
    print(f"\n🤖 {run('电脑有点卡，帮我看看')}")
