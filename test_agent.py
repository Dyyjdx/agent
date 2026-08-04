"""完整测试：真实调用 LLM，看模型能否自主决定调用工具"""
from agent import SystemDiagnoseAgent

agent = SystemDiagnoseAgent(model="qwen2.5:7b")

print("=== 测试1: 查 CPU ===")
print("你: 帮我看看 CPU 使用率高不高")
ans = agent.run("帮我看看 CPU 使用率高不高")
print(f"\n🤖 {ans}")

print("\n=== 测试2: 综合诊断 ===")
print("你: 电脑最近很卡，帮我诊断一下")
ans = agent.run("电脑最近很卡，帮我诊断一下")
print(f"\n🤖 {ans}")
