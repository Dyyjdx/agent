"""系统诊断 Agent 工具集 —— 本质就是普通 Python 函数 + @tool 说明书"""

import datetime
import platform

import psutil
from langchain_core.tools import tool


@tool
def get_cpu_usage() -> str:
    """获取当前 CPU 使用率（百分比）。用户说电脑卡、慢、发热时调用。"""
    return f"CPU 使用率: {psutil.cpu_percent(interval=1)}%"


@tool
def get_memory_usage() -> str:
    """获取内存使用情况（总量/已用/可用/百分比）。用户说内存不够、开太多程序时调用。"""
    mem = psutil.virtual_memory()
    gb = 1024 ** 3
    return (
        f"内存: 总 {mem.total/gb:.1f} GB, 已用 {mem.used/gb:.1f} GB "
        f"({mem.percent}%), 可用 {mem.available/gb:.1f} GB"
    )


@tool
def get_disk_usage() -> str:
    """获取磁盘使用情况。用户说磁盘满了、存不下东西时调用。"""
    parts = []
    for p in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(p.mountpoint)
        except PermissionError:
            continue
        gb = 1024 ** 3
        parts.append(f"{p.mountpoint}: 总 {usage.total/gb:.1f} GB, 已用 {usage.used/gb:.1f} GB ({usage.percent}%)")
    return "\n".join(parts) if parts else "无法读取磁盘信息"


@tool
def get_top_processes(n: int = 5) -> str:
    """获取占用资源最多的前 n 个进程（默认5个）。用户说电脑卡、想找出占资源的程序时调用。"""
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            procs.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    procs.sort(key=lambda x: x["cpu_percent"], reverse=True)
    lines = [f"{'PID':>6}  {'CPU%':>5}  {'MEM%':>5}  名称"]
    for p in procs[:n]:
        lines.append(f"{p['pid']:>6}  {p['cpu_percent']:>5.1f}  {p['memory_percent']:>5.1f}  {p['name']}")
    return "\n".join(lines)


@tool
def get_system_info() -> str:
    """获取系统基本信息（操作系统、CPU核数、开机时长、Python版本）。用户问电脑配置、系统信息时调用。"""
    boot = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.datetime.now() - boot
    return (
        f"系统: {platform.system()} {platform.release()}\n"
        f"机器: {platform.machine()}\n"
        f"CPU 核数: {psutil.cpu_count()} (逻辑) / {psutil.cpu_count(logical=False)} (物理)\n"
        f"开机时间: {boot:%Y-%m-%d %H:%M}\n"
        f"已运行: {uptime.days}天 {uptime.seconds//3600}小时 {(uptime.seconds%3600)//60}分钟\n"
        f"Python: {platform.python_version()}"
    )


ALL_TOOLS = [get_cpu_usage, get_memory_usage, get_disk_usage, get_top_processes, get_system_info]
TOOL_MAP = {t.name: t for t in ALL_TOOLS}
