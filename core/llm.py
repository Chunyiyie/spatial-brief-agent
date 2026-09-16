import os

from dotenv import load_dotenv
from openai import OpenAI

from core.models import SpatialPlan
from core.settings import get_deepseek_api_key

load_dotenv()

def _get_client():
    api_key = get_deepseek_api_key()
    if not api_key:
        raise RuntimeError(
            '未设置 DEEPSEEK_API_KEY。本地用 .env；'
            'Streamlit Cloud 用 Secrets：DEEPSEEK_API_KEY = "sk-..." '
            '或 [secrets] 小节下同名键。'
        )
    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )


SYSTEM_PROMPT = """
你是一名建筑空间规划助手。

你的任务是分析建筑项目中的空间关系。

请输出 JSON。

JSON 必须包含：

project_name
target_area
spaces
relationships

spaces 中每一个空间必须包含：

name
area
purpose

area 和 target_area 必须是纯数字，不要带单位。
正确：850
错误：850平方米、850㎡、850 sqm

relationships 中每一个关系必须包含：

space_a
space_b
relationship
reason

relationship 只能使用：

close
medium
far
avoid

不要输出 Markdown。
不要输出解释。
只输出 JSON。
"""


def analyze_brief(project_brief: str) -> SpatialPlan:
    """
    输入建筑 Brief，返回验证后的 SpatialPlan。
    """

    client = _get_client()
    response = _get_client().chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": project_brief},
        ],
        response_format={"type": "json_object"},
    )

    raw_json = response.choices[0].message.content
    return SpatialPlan.model_validate_json(raw_json)

MODIFY_SYSTEM_PROMPT = """
你是一名建筑空间规划助手。

用户已经有一个 SpatialPlan（JSON 格式）。
现在用户想要修改这个方案。

你的任务：
1. 理解用户的修改意图
2. 在现有方案基础上做最小必要修改
3. 输出完整更新后的 JSON

必须输出 JSON，结构不变：

project_name
target_area
spaces
relationships

area 和 target_area 必须是纯数字，不要带单位。

relationship 只能使用：
close
medium
far
avoid

不要输出 Markdown。
不要输出解释。
只输出 JSON。
"""


def modify_plan(current_plan: SpatialPlan, modification: str) -> SpatialPlan:
    """
    基于当前方案和用户修改指令，返回新的 SpatialPlan。
    """

    current_json = current_plan.model_dump_json(ensure_ascii=False)

    user_message = f"""
当前方案 JSON：

{current_json}

用户的修改要求：

{modification}

请输出修改后的完整 JSON。
"""

    response = _get_client().chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {"role": "system", "content": MODIFY_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": "json_object"},
    )

    raw_json = response.choices[0].message.content
    return SpatialPlan.model_validate_json(raw_json)
