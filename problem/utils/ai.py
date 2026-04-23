# problem/utils/ai.py
import json
import re
from spark_ai.utils import ask_spark  # 假设 ask_spark 接收一个字符串参数

def generate_problem_by_ai(prompt: str) -> dict:
    """
    调用星火大模型生成题目，返回符合题目格式的字典。
    """
    system_prompt = """你是一个编程题目的生成助手。请根据用户给出的提示，生成一道完整的编程题目，并以 JSON 格式返回。
JSON 必须包含以下字段：
- title: 题目标题（字符串）
- description: 题目描述（支持 HTML 格式，可以用 <p> 等标签）
- input_description: 输入说明（HTML 格式）
- output_description: 输出说明（HTML 格式）
- hint: 提示（可选，HTML 格式，如果不需要可留空）
- samples: 样例列表，每个样例是一个对象，包含 input 和 output 字段
- tags: 标签列表，例如 ["动态规划", "字符串"]
- difficulty: 难度，只能是 "High"、"Mid"、"Low" 之一
- source: 题目来源（可选）
- time_limit: 时间限制（整数，单位毫秒，建议 1000~3000）
- memory_limit: 内存限制（整数，单位 MB，建议 128~512）

请只返回 JSON，不要包含其他说明文字。"""

    # 构造发送给 AI 的消息
    user_message = f"生成一道题目：{prompt}"
    # 将系统提示和用户消息合并，因为 ask_spark 可能只接受一个字符串
    full_message = f"{system_prompt}\n\n{user_message}"
    response = ask_spark(full_message)  # 返回字符串

    # 提取 JSON
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    if not json_match:
        raise ValueError("AI 返回的内容不包含有效的 JSON")
    json_str = json_match.group()
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 解析失败: {e}")

    # 可选的默认值处理
    data.setdefault("hint", "")
    data.setdefault("source", "")
    data.setdefault("time_limit", 1000)
    data.setdefault("memory_limit", 256)
    return data