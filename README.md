# 🤖 AI 系统诊断 Agent

项目二：用 LangChain + 本地大模型 + psutil 构建的系统诊断 Agent。
用户描述电脑问题 → 模型自主决定调用哪些工具 → 基于真实数据给出诊断。

## 文件结构

| 文件 | 作用 |
|------|------|
| `tools.py` | 工具集：CPU/内存/磁盘/进程/系统信息（普通函数 + `@tool` 说明书） |
| `agent.py` | Agent 核心：手写循环（模型选工具 → 执行 → 结果回填 → 直到回答） |
| `main.py` | 命令行入口（交互模式 / 单次提问） |
| `test_tools.py` | 工具层自检（不调 LLM，秒级验证） |
| `test_agent.py` | 完整链路测试（真实调用 LLM） |

## 运行

```bash
cd ~/agent
/home/dwflm/RAG-env/bin/python main.py          # 交互模式
/home/dwflm/RAG-env/bin/python main.py -q "电脑卡怎么办"   # 单次提问
/home/dwflm/RAG-env/bin/python main.py -m qwen2.5:7b       # 指定模型
```

依赖：`langchain-core`、`langchain-ollama`、`psutil`（复用 RAG-env，已装好）。

## 核心原理（30 秒看懂）

```
用户问题 → LLM（带着工具菜单）→ 要调工具？→ 执行 Python 函数 → 结果塞回对话 → 循环
                               ↘ 不要 → 直接输出最终回答
```

工具本质 = 普通 Python 函数 + `@tool` 包装 + 一句写给模型看的 docstring。
模型靠 docstring 决定"这种情况该调哪个工具"。

## ⚠️ 踩坑记录

**deepseek-r1:8b 在 Ollama 上工具调用不可靠**——实测它不触发 `tool_calls` 协议，
直接编造数据（假的 CPU 28%、假的 8GB 内存、假的任务管理器 JSON）。
**Agent 必须依赖协议（bind_tools），不能依赖模型自觉。**
解决：换 qwen2.5:7b（Ollama 工具调用最成熟的模型）。

✅ **2026-08-02 验证：qwen2.5:7b 工具调用完全正常**
- 自动连续调用多工具（CPU+内存+磁盘+进程）
- 真实数据诊断：实测抓出 llama-server 占 85.6% CPU 的真凶
- 问内存 → 只调 get_memory_usage，选择精准

## 下一步（可选）

- 加 LangGraph 版：把循环改成 StateGraph（节点/边/条件分支）
- 加 Web UI：FastAPI + 前端（复用项目一经验）
- 加自动修复工具：kill 进程、清理缓存（小心操作，先 dry-run）
