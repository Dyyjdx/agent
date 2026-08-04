"""快速自检：不调 LLM，只验证工具层能否工作"""
from tools import ALL_TOOLS, TOOL_MAP

print("工具数:", len(ALL_TOOLS))
print("工具名:", [t.name for t in ALL_TOOLS])
print()
print(TOOL_MAP["get_cpu_usage"].invoke({}))
print()
print(TOOL_MAP["get_memory_usage"].invoke({}))
print()
print(TOOL_MAP["get_system_info"].invoke({}))
print()
print(TOOL_MAP["get_top_processes"].invoke({"n": 3}))
print()
print(TOOL_MAP["get_disk_usage"].invoke({}))
print()
print("✅ 工具层全部正常")
