import os

from dotenv import load_dotenv
from openai import OpenAI

from core.models import SpatialPlan
from core.rules import check_relationships


# ============================================================
# 1. 加载环境变量
# ============================================================

load_dotenv()


# ============================================================
# 2. 创建 DeepSeek 客户端
# ============================================================

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


# ============================================================
# 3. 项目 Brief
# ============================================================

project_brief = """
这是一个 5,000 平方米的社区中心。

主要服务：
- 儿童
- 老年人
- 家庭

项目需要包含：

- 图书馆
- 咖啡厅
- 儿童活动区
- 老年人活动区
- 多功能房间
- 户外公共空间

请分析这些空间之间的空间关系。

考虑以下因素：

1. 使用者之间的关系
2. 噪音
3. 公共性和私密性
4. 户外活动需求
5. 工作人员监督
6. 空间使用之间的便利性

请使用：

close
medium
far
avoid

表示两个空间之间的关系。

请使用中文。
"""


# ============================================================
# 4. 请求 DeepSeek
# ============================================================

response = client.chat.completions.create(
    model="deepseek-v4-flash",

    messages=[
        {
            "role": "system",
            "content": """
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
""",
        },
        {
            "role": "user",
            "content": project_brief,
        },
    ],

    response_format={
        "type": "json_object"
    },
)


# ============================================================
# 5. 获取 JSON
# ============================================================

raw_json = response.choices[0].message.content


print("\n========== AI 原始 JSON ==========\n")

print(raw_json)


# ============================================================
# 6. 使用 Pydantic 验证
# ============================================================

plan = SpatialPlan.model_validate_json(raw_json)


# ============================================================
# 7. 输出空间
# ============================================================

print("\n========== 空间 ==========\n")

for space in plan.spaces:

    print(
        f"{space.name} | "
        f"{space.area}㎡ | "
        f"{space.purpose}"
    )


# ============================================================
# 8. 输出空间关系
# ============================================================

print("\n========== 空间关系 ==========\n")

for relationship in plan.relationships:

    print(
        f"{relationship.space_a}"
        f" -- {relationship.relationship} -- "
        f"{relationship.space_b}"
    )

    print(
        f"原因：{relationship.reason}"
    )

    print()


# ============================================================
# 9. 运行空间规则检查
# ============================================================

warnings = check_relationships(plan)


print("\n========== 规则检查 ==========\n")


if not warnings:

    print("✓ 没有发现明显的空间关系冲突。")

else:

    for warning in warnings:

        print(warning)