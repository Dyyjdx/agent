"""入口：交互式系统诊断 Agent

用法：
    python main.py                 # 进入交互模式，随便问
    python main.py -q "电脑卡怎么办"   # 单次提问
    python main.py -m qwen2.5:7b   # 指定其他 Ollama 模型
"""

import argparse

from agent import SystemDiagnoseAgent


def main():
    parser = argparse.ArgumentParser(description="AI 系统诊断 Agent")
    parser.add_argument("-q", "--question", help="单次提问，不传则进入交互模式")
    parser.add_argument("-m", "--model", default="qwen2.5:7b", help="Ollama 模型名")
    args = parser.parse_args()

    agent = SystemDiagnoseAgent(model=args.model)
    print(f"🤖 系统诊断 Agent 就绪 (模型: {args.model})，输入问题回车，Ctrl+C / exit 退出\n")

    if args.question:
        print(f"你: {args.question}")
        answer = agent.run(args.question)
        print(f"\n🤖 {answer}")
        return

    while True:
        try:
            question = input("你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见 👋")
            break
        if not question:
            continue
        if question.lower() in ("exit", "quit", "退出"):
            print("再见 👋")
            break
        answer = agent.run(question)
        print(f"\n🤖 {answer}\n")


if __name__ == "__main__":
    main()
